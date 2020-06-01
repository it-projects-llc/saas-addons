# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import fields, models


class ProductTemplate(models.Model):

    _inherit = "product.template"

    is_saas_product = fields.Boolean("Is SaaS product?", default=False)
