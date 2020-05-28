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
            response.update(link="/web/signup?sale_order_id={}".format(sale_order.id))
        return response
