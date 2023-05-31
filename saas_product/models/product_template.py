# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    is_saas_product = fields.Boolean("Is SaaS product?", default=False)

    @api.model
    def create(self, vals):
        if vals.get("is_saas_product"):
            vals["taxes_id"] = [(5,)]
            vals["supplier_taxes_id"] = [(5,)]
        return super(ProductTemplate, self).create(vals)
