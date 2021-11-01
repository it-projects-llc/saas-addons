# Copyright 2020 Vildan Safin <https://www.it-projects.info/team/Enigma228322>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.http import route, request, Controller
from odoo.addons.website_sale.controllers.main import WebsiteSale


class SaaSAppsController(Controller):
    @route("/price", type="http", auth="public", website=True)
    def user_page(self, **kw):
        res = request.env["res.config.settings"].sudo().get_values()
        show_apps = bool(res["show_apps"])
        show_packages = bool(res["show_packages"])

        apps = (
            request.env["saas.app"].sudo().search([("allow_to_sell", "=", True)])
            if show_apps
            else []
        )
        packages = (
            request.env["saas.template"].sudo().search([("is_package", "=", True)])
            if show_packages
            else []
        )
        return request.render(
            "saas_apps.price",
            {
                "apps": apps,
                "packages": packages,
                "show_apps": show_apps,
                "show_packages": show_packages,
                "show_buy_now_button": bool(res["show_buy_now_button"]),
                "show_try_trial_button": bool(res["show_try_trial_button"]),
                "currency": request.website.currency_id,
                "user_month_product": request.env.ref(
                    "saas_product.product_users_monthly"
                ),
                "user_year_product": request.env.ref(
                    "saas_product.product_users_annually"
                ),
            },
        )

    @route(["/check_saas_template"], type="json", auth="public")
    def check_saas_template(self, **kw):
        # TODO: надо бы ошибки выводить
        # TODO: если указанный template_id не найден, то не надо использовать базовый шаблон
        template_id = kw.get("template_id")
        templates = request.env["saas.template"].sudo()

        # If package exist, use package saas_template
        template = templates.search(
            [("is_package", "=", True), ("id", "=", template_id)]
        )
        if not template:
            # If package wasn't selected, use base saas_template
            template = templates.env.ref("saas_apps.base_template")

        if not template.operator_ids.random_ready_operator():
            return {"id": template.id, "state": "creating"}
        return {"id": template.id, "state": "ready"}


# TODO: он нужен?
class SaasAppsCart(WebsiteSale):
    def clear_cart(self):
        order = request.website.sale_get_order()
        if order:
            for line in order.website_order_line:
                line.unlink()

    @route(
        "/price/cart/update_json",
        type="json",
        auth="public",
        methods=["POST"],
        website=True,
        csrf=False,
    )
    def cart_update_price_page(self, **kw):
        self.clear_cart()
        period = kw.get("period")
        sale_order = request.website.sale_get_order(force_create=True)
        # Adding user as product in cart
        if period == "month":
            user_product = request.env.ref("saas_product.product_users_monthly")
        elif period == "year":
            user_product = request.env.ref("saas_product.product_users_annually")
        else:
            raise NotImplementedError(
                "No 'Users' product for period '{}'".format(period)
            )

        user_cnt = int(kw.get("user_cnt"))
        sale_order._cart_update(product_id=int(user_product.id), add_qty=user_cnt)

        for product_id in kw.get("product_ids", []):
            sale_order._cart_update(product_id=int(product_id), add_qty=1)
        return {"link": "/shop/cart"}

    @route()
    def shop(self, **post):
        return request.redirect("/price")
