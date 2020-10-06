# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons.website_sale.controllers.main import WebsiteSale as BaseWebsiteSale
from odoo.http import request


class WebsiteSale(BaseWebsiteSale):
    def checkout_redirection(self, order):
        response = super(WebsiteSale, self).checkout_redirection(order)
        if response:
            return response

        if order:
            if request.env.user == request.env.ref("base.public_user"):
                return request.redirect("/web/signup?sale_order_id={}".format(order.id))
            else:
                if request.env["saas.db"].search_count([
                    ("type", "=", "build"),
                    ("state", "=", "draft"),
                    ("admin_user", "=", request.env.user.id),
                ]) == 0:
                    return request.redirect("/my/builds/create?redirect=/shop/checkout")
