# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError


class SaasDb(models.Model):

    _inherit = "saas.db"

    max_users_limit = fields.Integer("Max Users Allowed")
    users_count = fields.Integer("Current No. Of Users", readonly=1)

    @api.constrains("max_users_limit")
    def _check_max_users_limit(self):
        for record in self:
            if record.max_users_limit < 1:
                raise ValidationError(
                    _("Number of allowed max users must be at least 1")
                )

    def write(self, vals):
        templates = self.filtered(lambda x: x.type == "template")
        if vals.get("state") != "done" or not templates:
            return super(SaasDb, self).write(vals)

        # deactivate demo user and portal user
        for template in templates:
            for row in template.execute_kw(
                "ir.model.data",
                "search_read",
                [("module", "=", "base"), ("name", "in", ["user_demo", "demo_user0"])],
                ["model", "res_id"],
            ):
                template.execute_kw(
                    row["model"], "write", row["res_id"], {"active": False}
                )

        return super(SaasDb, self).write(vals)

    def write_values_to_build(self):
        super(SaasDb, self).write_values_to_build()

        if not self.max_users_limit:
            return

        self.execute_kw(
            "base.limit.records_number",
            "set_max_records",
            "access_limit_max_users.max_users_limit",
            self.max_users_limit,
        )

    def read_values_from_build(self):
        vals = super(SaasDb, self).read_values_from_build()

        vals.update(
            users_count=self.execute_kw(
                "res.users",
                "search_count",
                [(("is_excluded_from_limiting", "=", False))],
            )
        )

        if not self.max_users_limit:
            model, res_id = self.xmlid_to_res_model_res_id(
                "access_limit_max_users.max_users_limit"
            )
            if model and res_id:
                vals.update(
                    max_users_limit=self.execute_kw(
                        model, "search_read", [("id", "=", res_id)], ["max_records"]
                    )[0]["max_records"]
                )
            else:
                # TODO: maybe warning or something?
                pass

        return vals
