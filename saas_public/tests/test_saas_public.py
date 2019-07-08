# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import urllib

from odoo.addons.saas.tests.common_saas_test import Common
from odoo.tests.common import tagged, HttpCase
from odoo.service import db


@tagged('post_install', 'at_install')
class TestSaasPublic(HttpCase, Common):
    def setUp(self):
        super(TestSaasPublic, self).setUp()
        self.setup_saas_env()
        self.saas_template_1.write({
            'public_access': True,
        })
        self.saas_operator_1.write({
            'db_name_template': 'test_fast_build_{unique_id}',
        })
        self.saas_operator_2.write({
            'db_name_template': 'test_fast_build_{unique_id}',
        })

    def test_saas_public(self):
        drop_db_list = [build for build in db.list_dbs() if build.startswith('test_fast_build')]
        self.drop_dbs(drop_db_list)
        self.env['saas.template.operator'].preparing_template_next()
        public_template_id = self.saas_template_1.id
        params = urllib.parse.urlencode({
            'mail_message': 'mail.message',
        })
        url_1 = '/saas_public/{template_id}/create-fast-build?{params}'.format(template_id=public_template_id, params=params)
        public_template = self.url_open(url_1.format(public_template_id))
        self.assertIn(public_template.status_code, [200, 204], 'User must be redirected to the build')
        created_builds = [build for build in db.list_dbs() if build.startswith('test_fast_build')]
        self.assertTrue(created_builds)
        private_template_id = self.saas_operator_2.id
        url_2 = '/saas_public/{}/create-fast-build'
        private_template = self.url_open(url_2.format(private_template_id))
        self.assertIn(private_template.status_code, [404, 403], 'User should not have access to a private template')
