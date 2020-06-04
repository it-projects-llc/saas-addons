# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.addons.saas_apps.controllers.main import SaasAppsCart
from odoo.http import route, request


class MySaasAppsCart(SaasAppsCart):
    @route()
    def cart_update_price_page(self, **kw):
        response = super(MySaasAppsCart, self).cart_update_price_page(**kw)
        sale_order = request.website.sale_get_order(force_create=False)
        if sale_order:
            if request.env.user == request.env.ref("base.public_user"):
                response.update(link="/web/signup?sale_order_id={}".format(sale_order.id))
            else:
                if request.env["saas.db"].search_count([("state", "=", "draft")]) == 0:
                    response.update(link="/my/builds/create?redirect=/shop/checkout")
                else:
                    response.update(link="/shop/checkout")
        return response
