# Copyright 2018-2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import tagged, HttpCase
from odoo.service import db


# @tagged('post_install', 'at_install')
# class TestSaas(HttpCase):
#     def test_saas_public(self):
#         template_id = self.saas_template_1.id
#         url = '/saas/{}/create-fast-build'.format(template_id)
#         r = self.url_open(url)
#         self.assertEqual(r.status_code, 200, 'User must be redirected to the build')
#         self.assertIn('fast_build_001', db.list_dbs())
#         self.assert_no_error_in_db('fast_build_001')
