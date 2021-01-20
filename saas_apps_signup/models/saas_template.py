from odoo import models


class SaasTemplate(models.Model):
    _inherit = "saas.template"

    def _random_ready_operator_id(self):
        self.ensure_one()
        template_operators = self.sudo().operator_ids
        assert template_operators, "No template operators in template %s. Contact administrator" % (self,)

        template_operator = template_operators.random_ready_operator()
        assert template_operator, "No operators are ready. Please try again later"

        return template_operator.operator_id.id
