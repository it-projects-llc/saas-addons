# License AGPL-3.0 or later.
import json
from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestBuildPortal(HttpCase):
    def setUp(self):
        super().setUp()
        group = self.env.ref("base.group_portal")
        self.owner, self.other = self.env["res.users"].with_context(no_reset_password=True).create([
            {"name": "Portal Owner", "login": "portal-owner-audit", "password": "local-audit", "group_ids": [(6, 0, group.ids)]},
            {"name": "Other Owner", "login": "portal-other-audit", "password": "local-audit", "group_ids": [(6, 0, group.ids)]},
        ])
        self.build = self.env["saas.db"].create({"name": "portal-audit-own", "operator_id": self.env.ref("saas.local_operator").id, "admin_user": self.owner.id})
        self.other_build = self.env["saas.db"].create({"name": "portal-audit-other", "operator_id": self.env.ref("saas.local_operator").id, "admin_user": self.other.id})
        self.authenticate(self.owner.login, "local-audit")

    def test_home_has_builds_entry_and_counter(self):
        page = self.url_open("/my/home")
        self.assertEqual(page.status_code, 200)
        self.assertIn('href="/my/builds"', page.text)
        response = self.url_open("/my/counters", data=json.dumps({"jsonrpc": "2.0", "params": {"counters": {"build_count": "common_category"}}}), headers={"Content-Type": "application/json"}).json()
        self.assertEqual(response["result"]["build_count"], 1)

    def test_build_list_and_status_respect_ownership(self):
        page = self.url_open("/my/builds")
        self.assertIn(self.build.name, page.text)
        self.assertNotIn(self.other_build.name, page.text)
        response = self.url_open(f"/my/build/{self.other_build.id}/status", data=json.dumps({"jsonrpc": "2.0", "params": {}}), headers={"Content-Type": "application/json"}).json()
        self.assertIn("error", response)
