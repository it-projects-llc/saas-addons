# License AGPL-3.0 or later. Odoo 20 checkout integration.
from urllib.parse import urlencode
from odoo import models


class WebsiteCheckoutStep(models.Model):
    _inherit = "website.checkout.step"

    def validate_checkout_progress(self, step_href, order_sudo, **kwargs):
        redirect = super().validate_checkout_progress(step_href, order_sudo, **kwargs)
        if not order_sudo or not order_sudo.order_line.product_id.product_tmpl_id.filtered("is_saas_product"):
            return redirect
        if step_href not in ("/shop/address", "/shop/checkout", "/shop/payment"):
            return redirect
        if self.env.user._is_public():
            return "/web/signup?" + urlencode({"sale_order_id": order_sudo.id})
        if redirect:
            return redirect
        if not order_sudo.build_id:
            build = self.env["saas.db"].search([
                ("type", "=", "build"), ("state", "=", "draft"),
                ("admin_user", "=", self.env.uid),
            ], order="id desc", limit=1)
            if not build:
                return "/my/builds/create?" + urlencode({"redirect": step_href})
            order_sudo.build_id = build
        return None
