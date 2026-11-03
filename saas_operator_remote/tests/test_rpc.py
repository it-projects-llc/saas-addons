# License AGPL-3.0 or later.
from json import dumps
from unittest.mock import patch
from odoo import tools
from odoo.tests import HttpCase, tagged


@tagged("post_install", "-at_install")
class TestRemoteOperator(HttpCase):
    def test_remote_provisioning_rpc(self):
        if tools.config["admin_passwd"] != "local-audit-only":
            self.skipTest("Remote HTTP fixture requires the isolated audit configuration.")
        operator = self.env["saas.operator"].create({
            "name": "Isolated HTTP operator", "type": "remote",
            "global_url": self.base_url(), "remote_instance_url": self.base_url(),
            "remote_master_pwd": "local-audit-only", "db_url_template": "http://{db_name}.localhost",
        })
        dbname = "saas20_remote_audit"
        def local_post(url, json, timeout):
            return self.url_open(url, data=dumps(json), headers={"Content-Type": "application/json"}, timeout=timeout)

        with patch("odoo.addons.saas_operator_remote.models.saas_operator.requests.post", side_effect=local_post):
            self._exercise_operator(operator, dbname)

    def _exercise_operator(self, operator, dbname):
        try:
            operator._create_db(None, dbname, False)
            operator._install_modules(dbname, [("name", "in", ["auth_quick"])])
            operator._post_init(dbname, "env['res.partner'].create({'name': 'Remote audit partner'})")
            count = operator._build_execute_kw(dbname, "res.partner", "search_count", [[("name", "=", "Remote audit partner")]], {})
            self.assertEqual(count, 1)
        finally:
            operator._drop_db(dbname)
