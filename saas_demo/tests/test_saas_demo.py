# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', 'at_install')
class TestSaasDemo(TransactionCase):
    def setUp(self):
        super(TestSaasDemo, self).setUp()
        self.env = self.env(context=dict(
            self.env.context,
            test_queue_job_no_delay=True,
        ))
        self.saas_demo = self.env['saas.demo'].create({
            'name': 'SaaS Demo Test'
        })

        self.saas_operator = self.env['saas.operator'].create({
            'type': 'local',
            'demo_id': self.saas_demo.id,
            'master_url': 'http://saas_demo.127.0.0.1.nip.io:8069',
        })

        self.saas_module = self.env['saas.module'].create({
            'name': 'web_login_background',
        })

        self.saas_template = self.env['saas.template'].create({
            'demo_id': self.saas_demo.id,
            'demo_main_addon_id': self.saas_module.id,
            'demo_branch': '12.0',
        })

        self.saas_demo_repo = self.env['saas.demo.repo'].create({
            'demo_id': self.saas_demo.id,
            'url': 'https://gitlab.com/itpp/dev/saas-demo-test.git',
            'branch': '12.0',
        })

    def test_saas_demo(self):
        self.saas_demo.fetch_and_generate_templates()
