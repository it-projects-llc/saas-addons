# Copyright 2020 Vildan Safin <https://www.it-projects.info/team/Enigma228322>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.http import route, request, Controller
from odoo.addons.saas_public.controllers.saas_public import SaaSPublicController
from odoo.addons.website_sale.controllers.main import WebsiteSale
import urllib.parse

DB_TEMPLATE = 'template_database_'

class SaaSAppsController(Controller):


    @route('/price', type='http', auth='public', website=True)
    def user_page(self, **kw):
        res = request.env['res.config.settings'].sudo().get_values()
        apps = request.env['saas.line'].sudo()
        packages = request.env['saas.template'].sudo()
        if not apps.search_count([]):
            apps.refresh_lines()
        return request.render('saas_apps.Price', {
            'apps': apps.search([('allow_to_sell', '=', True)]),
            'packages': packages.search([('set_as_package', '=', True)]),
            'show_apps': bool(res['show_apps']),
            'show_packages': bool(res['show_packages'])
        })

    @route(['/refresh'], type='json', auth='public')
    def catch_app_click(self, **kw):
        apps = request.env['saas.line']
        apps.refresh_lines()
        return {}

    @route(['/what_dependencies'], type='json', auth='public')
    def search_incoming_app_dependencies(self, **kw):
        app_tech_name = kw.get('root')
        app = request.env['saas.line'].sudo().search([('name', '=', app_tech_name)])
        return {
            'dependencies': app.dependencies_info('root')
        }

    @route(['/check_currency'], type='json', auth='public')
    def what_company_curency_to_use(self, **kw):
        apps = request.env['saas.line'].sudo()
        return {
            'currency': apps.search([])[0].currency_id.display_name,
            'symbol': apps.search([])[0].currency_id.symbol
        }

    @route(['/take_template_id'], type='json', auth='public')
    def is_build_created(self, **kw):
        package = kw.get('package')
        templates = request.env['saas.template'].sudo()
        # If package exist, use package saas_template
        template = templates.search([('set_as_package', '=', True), ('name', '=', package)])
        if not template:
            # If package wasn't selected, use base saas_template
            template = templates.search([('set_as_base', '=', True)])
        if not template:
            template, saas_template_operator = self.create_new_template()
            return {
                'id': template.id,
                'state': 'creating'
            }
        if not template.operator_ids.random_ready_operator_check():
            return {
                'id': template.id,
                'state': 'creating'
            }
        return {
            'id': template.id,
            'state': 'ready'
        }

    def create_new_template(self):
        saas_template = request.env['saas.template'].sudo().create({
                'name': 'Base',
                'template_demo': True,
                'public_access': True,
                'set_as_base': True,
                'template_module_ids': request.env['saas.module'].sudo().search([('name', '=', 'mail')]),
                'build_post_init': "env['ir.module.module'].search([('name', 'in', {installing_modules})]).button_immediate_install()"
            })
        saas_operator = request.env.ref("saas.local_operator")
        saas_template_operator = request.env['saas.template.operator'].sudo().create({
            'template_id': saas_template.id,
            'operator_id': saas_operator.id,
            'operator_db_name': DB_TEMPLATE + str(saas_template.operator_ids.search_count([]) + 1),
        })
        saas_template_operator.sudo().preparing_template_next()
        return saas_template, saas_template_operator

    @route(['/price/take_product_ids'], type='json', auth='public')
    def take_product_ids(self, **kw):
        module_names = kw.get('module_names', [])
        modules = request.env['saas.line'].sudo()
        apps_product_ids = []
        apps = modules.search([('name', 'in', module_names), ('application', '=', True)])
        templates = request.env['saas.template'].sudo().search([('name', 'in', module_names)])
        for app in apps.product_id + templates.product_id:
            apps_product_ids.append(app.product_variant_id.id)

        return {
            'ids': apps_product_ids
        }


class SaasAppsCart(WebsiteSale):


    @route('/price/cart_update', type='json', auth='public', website=True)
    def cart_update_price_page(self, **kw):
        period = kw.get('period')
        sale_order = request.website.sale_get_order(force_create=True)
        product_ids = kw.get('old_apps_ids', [])
        # Adding user as product in cart
        user_product_tmp = request.env.ref("saas_apps.product_user").sudo()
        user_product = user_product_tmp.product_variant_id
        user_product.price = kw.get('user_price')
        if not period == 'm':
            user_product.price *= 12
        old_user_cnt = 0
        if kw.get('old_user_cnt'):
            old_user_cnt = float(kw.get('old_user_cnt'))
        user_cnt = float(kw.get('user_cnt'))
        if not old_user_cnt:
            old_user_cnt = 0
        sale_order._cart_update(
                product_id=int(user_product.id),
                add_qty=(user_cnt - old_user_cnt)
            )

        # Delete old products from cart
        for id in product_ids:
            sale_order._cart_update(
                product_id=int(id),
                add_qty=-1
            )

        # Changing prices
        product_ids = kw.get('product_ids', [])
        pr_tmp = request.env['product.template'].sudo()
        for id in product_ids:
            product = pr_tmp.browse(id).product_variant_id
            app = request.env['saas.line'].sudo().search([('module_name', '=', product.name)])
            packages = request.env['saas.template'].sudo().search([('name', '=', product.name)])
            if period == 'm':
                app.change_product_price(app, app.month_price)
                packages.change_product_price(packages, packages.month_price)
            else:
                app.change_product_price(app, app.year_price)
                packages.change_product_price(packages, packages.year_price)

        # Add new ones
        for id in product_ids:
            sale_order._cart_update(
                product_id=int(id),
                add_qty=1
            )
        return {
            "link": "/shop/cart"
        }
