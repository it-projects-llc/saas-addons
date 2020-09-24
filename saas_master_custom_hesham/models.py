from odoo import models


class SaasOperator(models.Model):

    _inherit = "saas.operator"

    def get_mandatory_modules(self):
        return super(SaasOperator, self).get_mandatory_modules() + [
            "saas_client_custom"
        ]
