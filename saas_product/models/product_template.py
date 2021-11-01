# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import api, fields, models
from datetime import timedelta


class ProductTemplate(models.Model):

    _inherit = "product.template"

    is_saas_product = fields.Boolean("Is SaaS product?", default=False)

    @api.model
    def create(self, vals):
        if vals.get("is_saas_product"):
            vals["taxes_id"] = [(5,)]
            vals["supplier_taxes_id"] = [(5,)]
            vals["invoice_policy"] = "order"
        return super(ProductTemplate, self).create(vals)


class Product(models.Model):

    _inherit = "product.product"

    def _get_expiration_timedelta(self):
        self.ensure_one()
        self = self.sudo()
        if self == self.env.ref("saas_product.product_users_annually"):
            return timedelta(days=365)
        elif self == self.env.ref("saas_product.product_users_monthly"):
            return timedelta(days=30)
        else:
            raise NotImplementedError
