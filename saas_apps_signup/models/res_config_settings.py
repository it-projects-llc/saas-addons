from odoo import fields, models


class SaasConfigSettings(models.TransientModel):
    _name = "saas.config.settings"
    _inherit = "res.config.settings"

    database_limit_size_default = fields.Float("Default limit size for all builds", config_parameter="saas_apps_signup.database_limit_size_default")
