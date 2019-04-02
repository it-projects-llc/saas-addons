# Copyright 2018 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


import odoo
from odoo import SUPERUSER_ID
from odoo.tests.common import TransactionCase, tagged
from odoo.service import db
from odoo.tools.safe_eval import safe_eval

DB_TEMPLATE = 'db_template'
DB_INSTANCE = 'db_instance'
MODULES = '[\'mail\']'
TEMPLATE_TEST_SUBJECT = 'Dummy subject name to test that code is applied on template database'
BUILD_TEST_SUBJECT = 'Dummy subject name to test that code is applied on build database'


@tagged('post_install', 'at_install')
class TestSaasTemplate(TransactionCase):

    def assert_modules_is_installed(self, db_name, modules):
        db = odoo.sql_db.db_connect(db_name)
        odoo.registry(db_name).check_signaling()
        modules = safe_eval(modules)
        with odoo.api.Environment.manage(), db.cursor() as cr:
            env = odoo.api.Environment(cr, SUPERUSER_ID, {})
            for module in modules:
                self.assertTrue(env['ir.module.module'].search([('name', '=', module)]))

    def assert_record_is_created(self, db_name, model_name, search_domain):
        db = odoo.sql_db.db_connect(db_name)
        odoo.registry(db_name).check_signaling()
        with odoo.api.Environment.manage(), db.cursor() as cr:
            env = odoo.api.Environment(cr, SUPERUSER_ID, {})
            return self.assertTrue(env[model_name].search(search_domain))

    def assert_no_error_in_db(self, dbname):
        # In order for the following tests to work correctly, you need to run odoo with parameter:
        # --log-db={db-name-where-tests-are-run}
        template_db_log = self.env['ir.logging'].search([
            ('dbname', '=', dbname),
            ('level', 'in', ['WARNING', 'ERROR', 'CRITICAL']),
            ('message', 'not like', 'test_queue_job_no_delay'),
        ])
        self.assertFalse(template_db_log)

    def setUp(self):
        super(TestSaasTemplate, self).setUp()
        self.env = self.env(context=dict(
            self.env.context,
            test_queue_job_no_delay=True,
        ))

        self.saas_template = self.env['saas.template'].create({
            'template_modules_domain': MODULES,
            'template_post_init': 'action = env[\'mail.message\'].create({\'subject\': \'' + TEMPLATE_TEST_SUBJECT + '\', })',
            'build_post_init': 'action = env[\'{mail_message}\'].create({{\'subject\': \'' + BUILD_TEST_SUBJECT + '\', }})',
        })

        self.saas_operator = self.env['saas.operator'].create({
            'type': 'local',
            'db_url_template': 'http://{db_name}.{db_id}.127.0.0.1.nip.io:8069',
        })
        self.saas_template_operator = self.env['saas.template.operator'].create({
            'template_id': self.saas_template.id,
            'operator_id': self.saas_operator.id,
            'operator_db_name': DB_TEMPLATE,
        })

        self.build_post_init_line = self.env['build.post_init.line'].create({
            'key': 'mail_message',
            'value': 'mail.message'
        })

    def test_template_operator(self):
        # FIXME: that check needed when last tests didn't pass, not sure that it is correct way to drop db
        if DB_TEMPLATE in db.list_dbs():
            db.exp_drop(DB_TEMPLATE)

        self.saas_template_operator.preparing_template_next()
        # Tests that template db created correctly
        self.assertTrue(self.saas_template_operator.operator_db_id.name)
        self.assertEqual(self.saas_template_operator.operator_db_id.name, DB_TEMPLATE)
        self.assertIn(DB_TEMPLATE, db.list_dbs())
        self.assert_no_error_in_db(DB_TEMPLATE)

        # Check that module from template_modules_domain is installed
        self.assert_modules_is_installed(DB_TEMPLATE, MODULES)
        self.assert_record_is_created(DB_TEMPLATE, 'mail.message', [('subject', '=', TEMPLATE_TEST_SUBJECT)])

        # Check that database instance created correctly
        if DB_INSTANCE in db.list_dbs():
            db.exp_drop(DB_INSTANCE)
        self.saas_template_operator.create_db(DB_INSTANCE, self.build_post_init_line)
        self.assertIn(DB_INSTANCE, db.list_dbs())
        self.assert_no_error_in_db(DB_INSTANCE)
        self.assert_record_is_created(DB_INSTANCE, 'ir.config_parameter', [('key', '=', 'auth_quick.master')])
        self.assert_record_is_created(DB_INSTANCE, 'ir.config_parameter', [('key', '=', 'auth_quick.build')])
        self.assert_record_is_created(DB_INSTANCE, 'mail.message', [
            ('subject', '=', BUILD_TEST_SUBJECT)
        ])
