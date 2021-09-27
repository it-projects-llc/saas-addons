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
        self.env['saas.template.operator'].search([]).unlink()
        self.setup_saas_env()
        self.saas_template_1.write({
            'public_access': True,
        })
        self.public_template = self.saas_template_1
        self.private_template = self.saas_template_2

    def test_saas_public(self):
        drop_db_list = [build for build in db.list_dbs() if build.startswith('fast-build')]
        self.drop_dbs(drop_db_list)
        self.env['saas.template.operator'].preparing_template_next()
        params = urllib.parse.urlencode({
            'mail_message': 'mail.message',
        })
        url_1 = '/saas_public/{template_id}/create-fast-build?{params}'.format(template_id=self.public_template.id, params=params)
        public_template_response = self.url_open(url_1)
        self.assertIn(public_template_response.status_code, [200, 204], 'User must be redirected to the build')
        created_builds = [build for build in db.list_dbs() if build.startswith('fast-build')]
        self.assertTrue(created_builds)
        url_2 = '/saas_public/{}/create-fast-build'.format(self.private_template.id)
        private_template = self.url_open(url_2)
        self.assertIn(private_template.status_code, [404, 403], 'User should not have access to a private template')
