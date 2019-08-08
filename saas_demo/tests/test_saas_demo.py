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
        self.env['ir.config_parameter'].set_param('test', 'True')
        self.saas_demo = self.env.ref('saas_demo.saas_demo')

    def test_saas_demo(self):
        # for some reason, when you restart the tests, the template is not deleted
        self.env['saas.template'].search([('name', '=', 'Demo Title')]).unlink()
        repo = self.env['saas.demo.repo'].search([('demo_id', '=', self.saas_demo.id)])
        if repo.commit:
            repo.commit = None
        self.saas_demo.fetch_and_generate_templates()
