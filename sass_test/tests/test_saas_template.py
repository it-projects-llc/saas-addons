# Copyright 2018 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).


from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', 'at_install')
class TestSaasTemplate(TransactionCase):
    def setUp(self):
        super(TestSaasTemplate, self).setUp()
        self.saas_template = self.env['saas.template'].create({
            'template_modules_domain': 'mail',
            'template_post_init': "self.env['mail.message'].create({'message_type': 'notification',}).message_format()"
        })
        self.saas_operator = self.env['saas.operator'].create()
        self.saas_template_operator = self.env['saas.template.operator'].create({
            'template_id': self.saas_template,
            'operator_id': self.saas_operator,
            'db_name': 'test_db_name',
        })

    def test_template_operator(self):
        self.saas_template_operator.preparing_template_next()
        self.saas_template_operator.db_id.create_db()
