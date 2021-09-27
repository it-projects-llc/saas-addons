# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import shutil

from odoo.tests.common import HttpCase, tagged
from odoo.addons.saas_demo.os import analysis_dir, repos_dir


@tagged('post_install', 'at_install')
class TestSaasDemo(HttpCase):

    def setUp(self):
        super(TestSaasDemo, self).setUp()

        self.env = self.env(context=dict(
            self.env.context,
            test_queue_job_no_delay=True,
        ))
        self.saas_demo = self.env['saas.demo'].create({'name': 'SaaS Demo Test'})
        self.saas_operator = self.env['saas.operator'].create({
            'name': 'Same Instance Test',
            'type': 'local',
            'db_url_template': 'http://{db_name}.{db_id}.127.0.0.1.nip.io',
            'global_url': 'http://{}.127.0.0.1.nip.io:8069'.format(self.env.cr.dbname),
            'demo_id': self.saas_demo.id,
        })
        self.saas_demo_repo = self.env['saas.demo.repo'].create({
            'demo_id': self.saas_demo.id,
            'url': 'https://gitlab.com/itpp/dev/saas-demo-test.git',
            'branch': '12.0',
        })

    def test_saas_demo(self):
        self.saas_demo.fetch_and_generate_templates()

    def tearDown(self):
        super(TestSaasDemo, self).tearDown()
        shutil.rmtree(analysis_dir())
        shutil.rmtree(repos_dir())
