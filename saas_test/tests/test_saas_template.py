# Copyright 2018 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from odoo.tests.common import TransactionCase, tagged
from odoo.service import db


@tagged('post_install', 'at_install')
class TestSaasTemplate(TransactionCase):
    def setUp(self):
        super(TestSaasTemplate, self).setUp()
        self.saas_template = self.env['saas.template'].create({
            'template_modules_domain': 'mail',
            'template_post_init': "self.env['mail.message'].create({'message_type': 'notification',}).message_format()"
        })
        self.saas_operator = self.env['saas.operator'].create({})
        self.saas_template_operator = self.env['saas.template.operator'].create({
            'template_id': self.saas_template.id,
            'operator_id': self.saas_operator.id,
            'operator_db_name': 'test_db_name',
            'to_rebuild': True,
            'state': 'draft'
        })

    def test_template_operator(self):
        self.saas_template_operator.preparing_template_next()
        self.saas_template_operator.operator_db_id.create_db(
            None,
            self.saas_template_operator.template_id.template_demo
        )
        self.assertTrue(self.saas_template_operator.operator_db_id.name)
        self.assertEqual(self.saas_template_operator.operator_db_id.name, 'test_db_name')
        self.assertIn('test_db_name', db.list_dbs())
