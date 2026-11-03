# License AGPL-3.0 or later.
from datetime import timedelta
from unittest.mock import patch

from odoo import fields
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestMigrationPayments(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context={**cls.env.context, "writing_from_refresh_data": True})
        cls.users_product = cls.env.ref("saas_product.product_users_monthly")
        cls.buyer = cls.env["res.users"].with_context(no_reset_password=True).create({
            "name": "Audit Buyer", "login": "audit-buyer", "partner_id": cls.partner_a.id,
            "group_ids": [(6, 0, cls.env.ref("base.group_portal").ids)],
        })

    def _build(self, name):
        return self.env["saas.db"].sudo().create({
            "name": name, "operator_id": self.env.ref("saas.local_operator").id,
            "admin_user": self.buyer.id,
        })

    def _pay(self, invoice):
        self.env["account.payment.register"].with_context(
            active_model="account.move", active_ids=invoice.ids,
        ).create({
            "journal_id": self.company_data["default_journal_bank"].id,
            "payment_date": fields.Date.today(), "amount": invoice.amount_residual,
        })._create_payments()
        self.assertEqual(invoice.payment_state, "paid")

    def test_paid_purchase_creates_one_contract_and_job(self):
        build = self._build("audit-paid-purchase")
        order = self.env["sale.order"].sudo().create({
            "partner_id": self.partner_a.id, "build_id": build.id,
            "order_line": [(0, 0, {"product_id": self.users_product.id, "product_uom_qty": 2, "price_unit": 12.5})],
        })
        order.action_confirm()
        invoice = order._create_invoices()
        invoice.action_post()
        self._pay(invoice)
        contracts = self.env["contract.contract"].sudo().search([("build_id", "=", build.id)])
        self.assertEqual(len(contracts), 1)
        self.assertEqual(contracts.contract_line_ids.quantity, 2)
        jobs = self.env["queue.job"].sudo().search([("model_name", "=", "contract.contract"), ("method_name", "=", "_create_build")])
        self.assertTrue(jobs.filtered(lambda job: contracts.id in job.records.ids))
        self.assertTrue(invoice.saas_purchase_processed)
        self.assertTrue(invoice.saas_renewal_applied)
        expiration_before_retry = build.expiration_date
        invoice._invoice_paid_hook()
        self.assertEqual(build.expiration_date, expiration_before_retry)
        self.assertEqual(self.env["contract.contract"].sudo().search_count([("build_id", "=", build.id)]), 1)

    def test_paid_renewal_extends_once(self):
        build = self._build("audit-paid-renewal")
        expiration = fields.Datetime.now() + timedelta(days=5)
        build.write({"state": "done", "expiration_date": expiration})
        contract = self.env["contract.contract"].sudo().create({
            "name": "Renewal migration audit", "partner_id": self.partner_a.id,
            "build_id": build.id, "line_recurrence": False,
            "contract_line_fixed_ids": [(0, 0, {"name": "Users", "product_id": self.users_product.id,
                "quantity": 1, "price_unit": 12.5, "uom_id": self.users_product.uom_id.id})],
        })
        invoice = self.init_invoice("out_invoice", partner=self.partner_a, products=self.users_product, amounts=[12.5], invoice_date=fields.Date.today())
        invoice.invoice_line_ids.contract_line_id = contract.contract_line_ids
        invoice.action_post()
        self._pay(invoice)
        self.assertEqual(build.expiration_date, expiration + timedelta(days=30))
        invoice._invoice_paid_hook()
        self.assertEqual(build.expiration_date, expiration + timedelta(days=30))
        self.assertTrue(invoice.saas_renewal_applied)

    def test_signup_result_uses_login_not_password(self):
        values = {"login": "audit-new-customer@example.com", "name": "New audit customer", "password": "local-test-password",
            "company_id": self.env.company.id, "company_ids": [(6, 0, self.env.companies.ids)],
            "period": "month", "max_users_limit": 1, "operator_id": self.env.ref("saas.local_operator").id,
            "database_name": "audit-signup-result", "installing_modules": "crm"}
        self.env["ir.config_parameter"].set_str("auth_signup.invitation_scope", "b2c")
        with patch.object(type(self.env["contract.contract"]), "_create_saas_contract_for_trial"):
            result = self.env["res.users"].with_context(create_user=True, host_id=self.env.ref("base.default_website").id).signup(values)
        build = self.env["saas.db"].sudo().search([("name", "=", "audit-signup-result")])
        self.assertEqual(result[0], "audit-new-customer@example.com")
        self.assertEqual(build.admin_user.login, result[0])
