# Copyright 2018-2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


import odoo
from odoo import SUPERUSER_ID
from odoo.tests.common import tagged, HttpCase
from odoo.service import db

DB_TEMPLATE_1 = 'db_template_1'
DB_TEMPLATE_2 = 'db_template_2'
DB_INSTANCE_1 = 'db_instance_1'
DB_INSTANCE_2 = 'db_instance_2'
MODULE_TO_INSTALL = 'mail'
TEMPLATE_TEST_SUBJECT = 'Dummy subject name to test that code is applied on template database'
BUILD_TEST_SUBJECT = 'Dummy subject name to test that code is applied on build database'
DEFAULT_BUILD_PYTHON_CODE = """# Available variables:
#  - env: Odoo Environment on which the action is triggered
#  - time, datetime, dateutil, timezone: useful Python libraries
#  - log: log(message, level='info'): logging function to record debug information in ir.logging table
#  - Warning: Warning Exception to use with raise
# To return an action, assign: action = {{...}}
# You can specify places for variables that can be passed when creating a build like this:
# env['{key_name_1}'].create({{'subject': '{key_name_2}', }})
# When you need curly braces in build post init code use doubling for escaping\n\n\n\n"""


@tagged('post_install', 'at_install')
class TestSaas(HttpCase):

    def assert_modules_is_installed(self, db_name, module):
        db = odoo.sql_db.db_connect(db_name)
        odoo.registry(db_name).check_signaling()
        with odoo.api.Environment.manage(), db.cursor() as cr:
            env = odoo.api.Environment(cr, SUPERUSER_ID, {})
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
        super(TestSaas, self).setUp()
        self.env = self.env(context=dict(
            self.env.context,
            test_queue_job_no_delay=True,
        ))

        self.saas_template_1 = self.env['saas.template'].create({
            'template_module_ids': [(0, 0, {
                'name': MODULE_TO_INSTALL,
            })],
            'template_post_init': 'env[\'mail.message\'].create({\'subject\': \'' + TEMPLATE_TEST_SUBJECT + '\', })',
            'build_post_init': DEFAULT_BUILD_PYTHON_CODE + 'env[\'{mail_message}\'].create({{\'subject\': \'' + BUILD_TEST_SUBJECT + '\', }})',
        })

        self.saas_template_2 = self.env['saas.template'].create({
            'template_module_ids': [(0, 0, {
                'name': 'mail',
            })],
            'template_post_init': 'env[\'mail.message\'].create({\'subject\': \'' + TEMPLATE_TEST_SUBJECT + '\', })',
        })

        self.saas_operator_1 = self.env['saas.operator'].create({
            'type': 'local',
            'db_url_template': 'http://{db_name}.{db_id}.127.0.0.1.nip.io:8069',
            'master_url': 'http://saas.127.0.0.1.nip.io:8069',
        })

        self.saas_operator_2 = self.env['saas.operator'].create({
            'type': 'local',
            'db_url_template': 'http://{db_name}.{db_id}.127.0.0.1.nip.io:8069',
            'master_url': 'http://saas.127.0.0.1.nip.io:8069',
        })

        self.saas_template_operator_1 = self.env['saas.template.operator'].create({
            'template_id': self.saas_template_1.id,
            'operator_id': self.saas_operator_1.id,
            'operator_db_name': DB_TEMPLATE_1,
        })

        self.saas_template_operator_2 = self.env['saas.template.operator'].create({
            'template_id': self.saas_template_2.id,
            'operator_id': self.saas_operator_2.id,
            'operator_db_name': DB_TEMPLATE_2,
        })

        self.build_post_init_line_1 = self.env['build.post_init.line'].create({
            'key': 'mail_message',
            'value': 'mail.message'
        })
        self.build_post_init_line_2 = self.env['build.post_init.line'].create({})

    def test_template_operator(self):
        # FIXME: that check needed when last tests didn't pass, not sure that it is correct way to drop db
        if DB_TEMPLATE_1 in db.list_dbs():
            db.exp_drop(DB_TEMPLATE_1)
        if DB_TEMPLATE_2 in db.list_dbs():
            db.exp_drop(DB_TEMPLATE_2)
        if 'template_database' in db.list_dbs():
            db.exp_drop('template_database')
        # Template 1
        self.saas_template_operator_1.preparing_template_next()
        # Tests that template db created correctly
        self.assertTrue(self.saas_template_operator_1.operator_db_id.name)
        self.assertEqual(self.saas_template_operator_1.operator_db_id.name, DB_TEMPLATE_1)
        self.assertIn(DB_TEMPLATE_1, db.list_dbs())
        self.assert_no_error_in_db(DB_TEMPLATE_1)

        # Check that module from template_module_ids is installed
        self.assert_modules_is_installed(DB_TEMPLATE_1, MODULE_TO_INSTALL)
        self.assert_record_is_created(DB_TEMPLATE_1, 'mail.message', [('subject', '=', TEMPLATE_TEST_SUBJECT)])

        # Template 2. Actually second template is done by calling preparing_template_next first time but that call
        # is needed to emulate calling by crone every few minutes. This is done to make sure that the repeated method
        # call does not cause errors.
        self.saas_template_operator_2.preparing_template_next()

        # Tests that template db created correctly
        self.assertTrue(self.saas_template_operator_2.operator_db_id.name)
        self.assertEqual(self.saas_template_operator_2.operator_db_id.name, DB_TEMPLATE_2)
        self.assertIn(DB_TEMPLATE_2, db.list_dbs())
        self.assert_no_error_in_db(DB_TEMPLATE_2)

        # Check that module from template_module_ids is installed
        self.assert_modules_is_installed(DB_TEMPLATE_2, MODULE_TO_INSTALL)
        self.assert_record_is_created(DB_TEMPLATE_2, 'mail.message', [('subject', '=', TEMPLATE_TEST_SUBJECT)])

        # Check that database instance created correctly
        if DB_INSTANCE_1 in db.list_dbs():
            db.exp_drop(DB_INSTANCE_1)
        if DB_INSTANCE_2 in db.list_dbs():
            db.exp_drop(DB_INSTANCE_2)

        url = '/saas/1/create-fast-build'
        r = self.url_open(url)
        self.assertEqual(r.status_code, 302, 'User must be redirected')

        self.saas_template_operator_1.create_db(self.build_post_init_line_1, DB_INSTANCE_1)
        self.assertIn(DB_INSTANCE_1, db.list_dbs())
        self.assert_no_error_in_db(DB_INSTANCE_1)
        self.assert_record_is_created(DB_INSTANCE_1, 'ir.config_parameter', [('key', '=', 'auth_quick.master')])
        self.assert_record_is_created(DB_INSTANCE_1, 'ir.config_parameter', [('key', '=', 'auth_quick.build')])
        self.assert_record_is_created(DB_INSTANCE_1, 'mail.message', [('subject', '=', BUILD_TEST_SUBJECT)])

        self.saas_template_operator_2.create_db(self.build_post_init_line_2, DB_INSTANCE_2)
        self.assertIn(DB_INSTANCE_2, db.list_dbs())
        self.assert_no_error_in_db(DB_INSTANCE_2)
        self.assert_record_is_created(DB_INSTANCE_2, 'ir.config_parameter', [('key', '=', 'auth_quick.master')])
        self.assert_record_is_created(DB_INSTANCE_2, 'ir.config_parameter', [('key', '=', 'auth_quick.build')])
