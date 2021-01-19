from odoo import models, fields


class SaasTemplate(models.Model):
    _name = "saas.template"
    _inherit = ["saas.template", "saas.period.product.mixin"]

    is_package = fields.Boolean("Is package?")
    package_image = fields.Image(
        string='Package image'
    )

    def write(self, vals):
        res = super(SaasTemplate, self).write(vals)

        ProductTemplate = self.env["product.template"].sudo().with_context(active_test=False)
        for record in self:
            if record.is_package and not record.product_tmpl_id:
                product_tmpl_id = ProductTemplate.search([("saas_package_id", "=", record.id)])
                if not product_tmpl_id:
                    product_tmpl_id = ProductTemplate.create({
                        "name": record.name,
                        "image_1920": record.package_image,
                        "saas_package_id": record.id,
                        "is_saas_product": True,
                        "website_published": True,
                        "list_price": 0,
                    })
                else:
                    product_tmpl_id.write({"active": True})
                record.product_tmpl_id = product_tmpl_id

        return res
