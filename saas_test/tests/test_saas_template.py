# Copyright 2018 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

import odoo
from odoo import SUPERUSER_ID
from odoo.tests.common import TransactionCase, tagged
from odoo.service import db
from odoo.addons.queue_job.job import Job, ENQUEUED, PENDING

_logger = logging.getLogger(__name__)
DB_TEMPLATE = 'db_template'
DB_INSTANCE = 'db_instance'

def is_module_installed(db_name, module_name):
    db = odoo.sql_db.db_connect(db_name)
    odoo.registry(db_name).check_signaling()
    with odoo.api.Environment.manage(), db.cursor() as cr:
        try:
            _logger.debug('%s: %s', db_name, module_name)
            env = odoo.api.Environment(cr, SUPERUSER_ID, {})
            return getattr(env['ir.module.module'], 'search')([('name', '=', module_name), ('state', '=', 'installed')])
        except:
            _logger.error('Error while searching module %s in %s', module_name, db_name)


@tagged('post_install', 'at_install')
class TestSaasTemplate(TransactionCase):
    # TODO: add second optional argument - method_name
    def perform_last_job(self, model_name):
        job_id = self.env['queue.job'].search([('model_name', '=', model_name)])
        if job_id:
            job = Job.load(self.env, job_id[-1].uuid)
            if job.state == ENQUEUED or job.state == PENDING:
                job.perform()

    def setUp(self):
        super(TestSaasTemplate, self).setUp()
        self.saas_template = self.env['saas.template'].create({
            'template_modules_domain': 'mail',
            'template_post_init': "self.env['mail.message'].create({'message_type': 'notification',}).message_format()",
        })
        self.saas_operator = self.env['saas.operator'].create({
            'type': 'local',
        })
        self.saas_template_operator = self.env['saas.template.operator'].create({
            'template_id': self.saas_template.id,
            'operator_id': self.saas_operator.id,
            'operator_db_name': DB_TEMPLATE,
        })

    def test_template_operator(self):
        # FIXME: that check needed when last tests didn't pass, not sure that it is correct way to drop db
        if DB_TEMPLATE in db.list_dbs():
            db.exp_drop(DB_TEMPLATE)
        self.saas_template_operator.preparing_template_next()
        self.perform_last_job('saas.db')
        self.perform_last_job('saas.template.operator')
        self.perform_last_job('saas.template.operator')


        # Tests that template db created correctly
        self.assertTrue(self.saas_template_operator.operator_db_id.name)
        self.assertEqual(self.saas_template_operator.operator_db_id.name, DB_TEMPLATE)
        self.assertIn(DB_TEMPLATE, db.list_dbs())

        # Check that module from template_modules_domain is installed
        self.assertTrue(is_module_installed(DB_TEMPLATE, 'mail'))

        # self.saas_template_operator.create_db()
