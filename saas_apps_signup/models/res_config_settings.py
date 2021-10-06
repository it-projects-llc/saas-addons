from odoo import api, fields, models


class SaasConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    database_limit_size_default = fields.Float("Default limit size for all builds (megabytes)", config_parameter="saas_apps_signup.database_limit_size_default")
    database_expiration_warning_delay = fields.Integer("Expiration warning delay (days)", config_parameter="saas_apps_signup.database_expiration_warning_delay")
    number_of_days_for_trial = fields.Integer("Trial period (days)", config_parameter="saas_expiration.number_of_days_for_trial", default=7)

    @api.model
    def set_values(self):
        super(SaasConfigSettings, self).set_values()
