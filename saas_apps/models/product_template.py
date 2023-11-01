from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    saas_app_id = fields.Many2one("saas.app", ondelete="cascade", index=True)
    saas_package_id = fields.Many2one("saas.template", ondelete="cascade", index=True)
