# Copyright 2018 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo.tests.common import TransactionCase, tagged
from odoo.service import db
from odoo.addons.queue_job.job import Job, ENQUEUED


@tagged('post_install', 'at_install')
class TestSaasTemplate(TransactionCase):
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
            'operator_db_name': 'test_db_name',
        })

    def test_template_operator(self):
        self.saas_template_operator.preparing_template_next()
        job_id = self.env['queue.job'].search([('model_name', '=', 'saas.db')])
        job = Job.load(self.env, job_id.uuid)
        if job.state == ENQUEUED:
            job.perform()
        # when preparing_template_next is called, a database is created. To check create_db separately,
        # we first need to delete the old one.
        self.saas_template_operator.operator_db_id.drop_db()
        self.saas_template_operator.operator_db_id.create_db(
            None,
            self.saas_template_operator.template_id.template_demo
        )
        self.assertTrue(self.saas_template_operator.operator_db_id.name)
        self.assertEqual(self.saas_template_operator.operator_db_id.name, 'test_db_name')
        self.assertIn('test_db_name', db.list_dbs())
        self.saas_template_operator.operator_db_id.drop_db()
