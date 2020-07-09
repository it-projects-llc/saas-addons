# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class SaasDb(models.Model):

    _inherit = 'saas.db'

    database_limit_size = fields.Float(default=lambda self: self.env["ir.config_parameter"].get_param("saas_apps_signup.database_limit_size_default", 0.0))

    def create(self, vals):

        if not self.env.user.has_group("saas.group_manager"):
            if self.env['saas.db']._search([
                ("state", "=", "draft"),
                ("admin_user", "=", self.env.user.id),
            ], limit=1):
                raise Exception("You cannot create more than one draft database")

        return super(SaasDb, self).create(vals)

    def write_values_to_build(self):
        super(SaasDb, self).write_values_to_build()

        web_base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        if not web_base_url:
            return

        self.execute_kw(
            "ir.config_parameter",
            "set_param",
            "database_expiration_details_link",
            web_base_url + self.access_url + "/renew_subscription",
        )

        self.execute_kw(
            "ir.config_parameter",
            "set_param",
            "database_expiration_details_link_label",
            "Renew subscribtion",
        )

        Config = self.env["ir.config_parameter"].sudo()

        database_expiration_warning_delay = Config.get_param("saas_apps_signup.database_expiration_warning_delay")
        if database_expiration_warning_delay:
            self.execute_kw(
                "ir.config_parameter",
                "set_param",
                "database_expiration_warning_delay",
                database_expiration_warning_delay
            )
