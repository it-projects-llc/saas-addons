# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.addons.saas.tests.common_saas_test import Common
from odoo.tests.common import TransactionCase, tagged
from odoo.service import db


@tagged('post_install', 'at_install')
class TestSaasDemo(TransactionCase, Common):
    def setUp(self):
        super(TestSaasDemo, self).setUp()
        self.env = self.env(context=dict(
            self.env.context,
            test_queue_job_no_delay=True,
        ))
        self.env['ir.config_parameter'].set_param('test_saas_demo', 'True')
        self.setup_saas_env()
        self.env.ref('saas.local_operator').write({
            'db_name_template': 'test-db-{unique_id}',
        })
        # No need to test it again
        self.env.ref('saas.saas_template_operator').write({
            'to_rebuild': False,
        })
        self.saas_template_operator_1.write({
            'to_rebuild': False,
        })
        self.saas_template_operator_2.write({
            'to_rebuild': False,
        })
        self.saas_demo = self.env.ref('saas_demo.saas_demo')

    def test_saas_demo(self):
        drop_db_list = [build for build in db.list_dbs() if build.startswith('test-db')]
        self.drop_dbs(drop_db_list)
        # for some reason, when you restart the tests, the template is not deleted
        self.env['saas.template'].search([('name', '=', 'Demo Title')]).unlink()
        repo = self.env['saas.demo.repo'].search([('demo_id', '=', self.saas_demo.id)])
        if repo.commit:
            repo.commit = None
        self.saas_demo.fetch_and_generate_templates()
        self.env['saas.template.operator'].preparing_template_next()
