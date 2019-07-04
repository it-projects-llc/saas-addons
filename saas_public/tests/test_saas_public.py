# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.addons.saas.tests.common_saas_test import Common, DB_TEMPLATE_1, DB_TEMPLATE_2
from odoo.tests.common import tagged, HttpCase
from odoo.service import db


@tagged('post_install', 'at_install')
class TestSaasPublic(HttpCase, Common):
    def setUp(self):
        super(TestSaasPublic, self).setUp()
        self.setup_saas_env()

    def test_saas_public(self):
        if DB_TEMPLATE_1 in db.list_dbs():
            db.exp_drop(DB_TEMPLATE_1)
        if DB_TEMPLATE_2 in db.list_dbs():
            db.exp_drop(DB_TEMPLATE_2)
        if 'template_database' in db.list_dbs():
            db.exp_drop('template_database')
        self.env['saas.template.operator'].preparing_template_next()
        template_id = self.saas_template_1.id
        url = '/saas_public/{}/create-fast-build'.format(template_id)
        r = self.url_open(url)
        self.assertIn(r.status_code, [200, 204], 'User must be redirected to the build')
