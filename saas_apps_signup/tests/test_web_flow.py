# License AGPL-3.0 or later.
import json
from urllib.parse import urlencode, urlparse, parse_qs
from unittest.mock import patch
from lxml import html
from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestCheckoutSignup(HttpCase):
    def setUp(self):
        super().setUp()
        self.env["ir.config_parameter"].set_str("auth_signup.invitation_scope", "b2c")
        self.product = self.env.ref("saas_product.product_users_monthly")
        self.operator = self.env.ref("saas.local_operator")

    def _add_to_cart(self):
        response = self.url_open("/shop/cart/add", data=json.dumps({"jsonrpc": "2.0", "params": {
            "product_template_id": self.product.product_tmpl_id.id, "product_id": self.product.id, "quantity": 1,
        }}), headers={"Content-Type": "application/json"})
        self.assertNotIn("error", response.json())

    def _signup(self, query, login):
        query = {**query, "operator_id": self.operator.id}
        page = self.url_open("/web/signup?" + urlencode(query, doseq=True))
        self.assertEqual(page.status_code, 200)
        csrf = html.fromstring(page.content).xpath("//input[@name='csrf_token']/@value")[0]
        with patch("odoo.addons.auth_signup_verify_email.controllers.main.validate_email"):
            response = self.url_open("/web/signup", data={**query, "csrf_token": csrf,
                "name": "Audit web customer", "login": login, "phone": "+15551234567", "database_lang": "en_US",
                "country_code": "US", "company_name": "Audit company",
            })
        self.assertIn("Check your email to activate your account!", response.text)
        user = self.env["res.users"].search([("login", "=", login)])
        self.assertEqual(user.partner_id.parent_id.name, "Audit company")
        return user

    def test_passwordless_trial_preserves_selected_options(self):
        with patch.object(type(self.env["contract.contract"]), "_create_saas_contract_for_trial") as create_trial:
            user = self._signup({"period": "month", "max_users_limit": 2, "installing_modules": "crm", "database_name": "audit-web-trial"}, "audit-web-trial@example.com")
        build = self.env["saas.db"].search([("name", "=", "audit-web-trial")])
        self.assertEqual(build.admin_user, user)
        self.assertEqual(user.database_lang, "en_US")
        self.assertEqual(user.country_id.code, "US")
        create_trial.assert_called_once()
        self.assertEqual(create_trial.call_args.args[1:3], (2, "month"))
        self.assertEqual(create_trial.call_args.kwargs["installing_modules"], ["crm"])

    def test_trial_signup_preserves_multiple_languages(self):
        with patch.object(type(self.env["contract.contract"]), "_create_saas_contract_for_trial"):
            self._signup({
                "period": "month", "max_users_limit": 1, "installing_modules": "contacts",
                "database_name": "audit-web-languages", "database_languages": ["fr_FR", "de_DE"],
            }, "audit-web-languages@example.com")
        build = self.env["saas.db"].search([("name", "=", "audit-web-languages")])
        self.assertEqual(set(build.database_language_ids.mapped("code")), {"en_US", "fr_FR", "de_DE"})

    def test_anonymous_purchase_creates_owned_draft_and_links_cart(self):
        self._add_to_cart()
        response = self.url_open("/shop/checkout", allow_redirects=False)
        self.assertEqual(response.status_code, 303)
        redirect = response.headers["Location"]
        self.assertIn("/web/signup?", redirect)
        order_id = int(parse_qs(urlparse(redirect).query)["sale_order_id"][0])
        user = self._signup({"sale_order_id": order_id, "database_name": "audit-web-purchase", "database_languages": ["fr_FR", "de_DE"]}, "audit-web-purchase@example.com")
        order = self.env["sale.order"].browse(order_id)
        self.assertEqual(order.partner_id, user.partner_id)
        self.assertEqual(order.build_id.admin_user, user)
        self.assertEqual(order.build_id.state, "draft")
        self.assertEqual(set(order.build_id.database_language_ids.mapped("code")), {"en_US", "fr_FR", "de_DE"})

    def test_logged_customer_selects_own_draft_before_checkout(self):
        user = self.env["res.users"].with_context(no_reset_password=True).create({"name": "Cart customer", "login": "audit-cart", "password": "local-audit", "group_ids": [(6, 0, self.env.ref("base.group_portal").ids)]})
        self.authenticate(user.login, "local-audit")
        self._add_to_cart()
        response = self.url_open("/shop/address", allow_redirects=False)
        self.assertEqual(response.status_code, 303)
        self.assertIn("/my/builds/create?", response.headers["Location"])
        build = self.env["saas.db"].create({"name": "audit-owned-draft", "operator_id": self.operator.id, "admin_user": user.id})
        response = self.url_open("/shop/address")
        self.assertEqual(response.status_code, 200)
        order = self.env["sale.order"].search([("partner_id", "=", user.partner_id.id)], order="id desc", limit=1)
        self.assertEqual(order.build_id, build)
