from odoo import api, models, fields


class SaasPeriodProductMixin(models.AbstractModel):
    _name = "saas.period.product.mixin"
    _description = "Period Product Mixin"

    product_tmpl_id = fields.Many2one("product.template", ondelete="cascade", readonly=True)

    month_product_id = fields.Many2one("product.product", string="Product for monthly subscription", compute="_compute_product_ids", store=True)
    year_product_id = fields.Many2one("product.product", string="Product for annually subscription", compute="_compute_product_ids", store=True)
    currency_id = fields.Many2one("res.currency", related="product_tmpl_id.currency_id")

    # TODO: when following fields are written, you need to update prices on product.product
    month_price = fields.Float("Month price", default=0.0)
    year_price = fields.Float("Year price", default=0.0)

    @api.depends("product_tmpl_id")
    def _compute_product_ids(self):
        patvs_month = self.env.ref("saas_product.product_attribute_value_subscription_monthly")
        patvs_year = self.env.ref("saas_product.product_attribute_value_subscription_annually")
        attr = self.env.ref("saas_product.product_attribute_subscription")

        for app in self:
            if not app.product_tmpl_id:
                app.month_product_id = app.year_product_id = self.env["product.product"]
                continue

            line = self.env["product.template.attribute.line"].sudo().search([
                ("product_tmpl_id", "=", app.product_tmpl_id.id),
                ("attribute_id", "=", attr.id),
            ])
            if not line:
                line = line.create({
                    "product_tmpl_id": app.product_tmpl_id.id,
                    "attribute_id": attr.id,
                    "value_ids": [(6, 0, [
                        patvs_year.id, patvs_month.id,
                    ])]
                })

            ptv_ids = line.product_template_value_ids

            month_ptv = ptv_ids.filtered(lambda x: x.product_attribute_value_id == patvs_month)
            month_ptv.write({
                "price_extra": app.month_price
            })
            app.month_product_id = month_ptv.ptav_product_variant_ids[:1]

            year_ptv = ptv_ids.filtered(lambda x: x.product_attribute_value_id == patvs_year)
            year_ptv.write({
                "price_extra": app.year_price
            })
            app.year_product_id = year_ptv.ptav_product_variant_ids[:1]
