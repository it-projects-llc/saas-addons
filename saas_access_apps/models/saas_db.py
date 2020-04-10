# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaasDb(models.Model):

    _inherit = "saas.db"

    installed_apps = fields.Many2many(
        "saas.module", "saas_db_installed_apps_rel", readonly=1
    )

    def write_values_to_build(self):
        super(SaasDb, self).write_values_to_build()

        _, model, res_id = self.xmlid_lookup("access_apps.group_allow_apps")

        # disallowing all users to install apps
        self.execute_kw(model, "write", [res_id], {"users": [(5,)]})

    def read_values_from_build(self):
        vals = super(SaasDb, self).read_values_from_build()

        installed_apps_names = list(
            map(
                lambda item: item["name"],
                self.execute_kw(
                    "ir.module.module",
                    "search_read",
                    [("state", "=", "installed"), ("application", "=", True)],
                    ["name"],
                ),
            )
        )

        vals.update(
            installed_apps=[
                (
                    6,
                    0,
                    self.env["saas.module"]._search(
                        [("name", "in", installed_apps_names)]
                    ),
                )
            ]
        )
        return vals
