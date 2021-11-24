from odoo import fields, models


class SaasDb(models.Model):
    _inherit = "saas.db"

    installed_apps = fields.Many2many(
        "saas.module", "saas_db_installed_apps_rel", readonly=1
    )

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
