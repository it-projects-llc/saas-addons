from odoo.addons.saas.tests.common_saas_test import Common

from odoo import SUPERUSER_ID
from odoo.tests.common import tagged, SavepointCase
from datetime import date, timedelta
from unittest.mock import patch


@tagged('post_install', 'at_install')
class TestSaasContract(SavepointCase, Common):
    @classmethod
    def setUpClass(cls):
        super(TestSaasContract, cls).setUpClass()
        cls.setup_saas_env(cls)

    def setUp(self):
        super(TestSaasContract, self).setUp()
        self.user = user = self.env.ref("base.user_demo")
        self.build = self.env["saas.db"].with_user(user).sudo().create({
            "name": "test_build_1",
            "admin_user": self.user.id,
            "operator_id": self.env.ref("saas.local_operator").id,
        })

    def tearDown(self):
        self.build.unlink()
        super(TestSaasContract, self).tearDown()

    def test_contract_expiration_flow(self):
        partner = self.user.partner_id
        subscription_period = "monthly"
        recurring_rule_type = "monthly"
        today = date.today()
        recurring_next_date = today + timedelta(days=30)

        product_user = self.env.ref("saas_product.product_users_monthly")

        contract = self.env["contract.contract"].with_context(create_build=True).create({
            "name": "{}'s SaaS Contract".format(partner.name),
            "partner_id": partner.id,
            "contract_template_id": self.env.ref("saas_contract.contract_template_{}".format(subscription_period)).id,
            "build_id": self.build.id,
            "contract_line_ids": [(0, 0, {
                "name": product_user.name,
                "product_id": product_user.id,
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "quantity": 1,
                "recurring_interval": 1,
                "recurring_rule_type": recurring_rule_type,
                "recurring_invoicing_type": "post-paid",
                "recurring_next_date": recurring_next_date,
                "date_start": today,
                "date_end": today + timedelta(days=365),
            })],
        })

        with patch("odoo.fields.Date.context_today", lambda *args, **kw: recurring_next_date + timedelta(days=1)):
            self.assertFalse(contract._get_related_invoices())
            self.env["contract.contract"].with_user(SUPERUSER_ID).cron_recurring_create_invoice()
            invoice = contract._get_related_invoices()
            invoice.ensure_one()
            self.assertEqual(invoice.state, "posted")
