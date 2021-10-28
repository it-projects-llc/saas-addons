from odoo import api, models, fields


class SaasPeriodProductMixin(models.AbstractModel):
    _name = "saas.period.product.mixin"
    _description = "Period Product Mixin"

    product_tmpl_id = fields.Many2one("product.template", ondelete="cascade", readonly=True)

    month_product_id = fields.Many2one("product.product", string="Product for monthly subscription", compute="_compute_product_ids", store=True)
    year_product_id = fields.Many2one("product.product", string="Product for annually subscription", compute="_compute_product_ids", store=True)
    currency_id = fields.Many2one("res.currency", related="product_tmpl_id.currency_id")

    month_ptv = fields.Many2one("product.template.attribute.value", compute="_compute_product_ids", store=True)
    year_ptv = fields.Many2one("product.template.attribute.value", compute="_compute_product_ids", store=True)

    month_price = fields.Float("Month price", compute="_compute_prices", inverse="_inverse_month_price")
    year_price = fields.Float("Year price", compute="_compute_prices", inverse="_inverse_year_price")

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
            app.month_ptv = month_ptv
            app.month_product_id = month_ptv.ptav_product_variant_ids[:1]

            year_ptv = ptv_ids.filtered(lambda x: x.product_attribute_value_id == patvs_year)
            app.year_ptv = year_ptv
            app.year_product_id = year_ptv.ptav_product_variant_ids[:1]

    @api.depends("product_tmpl_id.list_price", "month_ptv", "year_ptv")
    def _compute_prices(self):
        for app in self:
            app.month_price = app.product_tmpl_id.list_price + app.month_ptv.price_extra
            app.year_price = app.product_tmpl_id.list_price + app.year_ptv.price_extra

    def _inverse_month_price(self):
        for app in self:
            app.month_ptv.price_extra = app.month_price - app.product_tmpl_id.list_price

    def _inverse_year_price(self):
        for app in self:
            app.year_ptv.price_extra = app.year_price - app.product_tmpl_id.list_price
