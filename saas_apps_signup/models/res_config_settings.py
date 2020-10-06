from odoo import api, fields, models


class SaasConfigSettings(models.TransientModel):
    _name = "saas.config.settings"
    _inherit = "res.config.settings"

    database_limit_size_default = fields.Float("Default limit size for all builds (megabytes)", config_parameter="saas_apps_signup.database_limit_size_default")
    database_expiration_warning_delay = fields.Integer("Expiration warning delay (days)", config_parameter="saas_apps_signup.database_expiration_warning_delay")

    @api.model
    def set_values(self):
        super(SaasConfigSettings, self).set_values()
        self.env["saas.db"].sudo().search([("state", "=", "done"), ("type", "=", "build")]).refresh_data()
