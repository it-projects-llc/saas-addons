# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import shutil

from odoo.tests.common import TransactionCase, tagged
from odoo.addons.saas_demo.os import analysis_dir, repos_dir


@tagged('post_install', 'at_install')
class TestSaasDemo(TransactionCase):

    def setUp(self):
        super(TestSaasDemo, self).setUp()

        self.env = self.env(context=dict(
            self.env.context,
            test_queue_job_no_delay=True,
        ))
        self.saas_demo = self.env.ref('saas_demo.saas_demo')

    def test_saas_demo(self):
        self.saas_demo.fetch_and_generate_templates()

    def tearDown(self):
        super(TestSaasDemo, self).tearDown()
        shutil.rmtree(analysis_dir())
        shutil.rmtree(repos_dir())
