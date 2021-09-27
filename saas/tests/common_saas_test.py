# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.service import db

DB_TEMPLATE_1 = 'db_template_1'
DB_TEMPLATE_2 = 'db_template_2'
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


class Common(object):
    def setup_saas_env(self):
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
            'name': 'Test local operator 1',
            'type': 'local',
            'db_url_template': 'http://{db_name}.127.0.0.1.nip.io:8069',
            'global_url': 'http://saas.127.0.0.1.nip.io:8069',
        })

        self.saas_operator_2 = self.env['saas.operator'].create({
            'name': 'Test local operator 2',
            'type': 'local',
            'db_url_template': 'http://{db_name}.127.0.0.1.nip.io:8069',
            'global_url': 'http://saas.127.0.0.1.nip.io:8069',
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

    def drop_dbs(self, db_list=None):
        if not db_list:
            db_list = []
        db_list += [DB_TEMPLATE_1, DB_TEMPLATE_2, 'template_database']
        for i in db_list:
            if i in db.list_dbs():
                db.exp_drop(i)
