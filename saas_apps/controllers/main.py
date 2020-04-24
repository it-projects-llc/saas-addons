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
        apps = request.env['saas.line'].sudo()
        # apps.delete_app_duplicates()
        if not apps.search_count([]):
            apps.refresh_lines()
        return request.render('saas_apps.index', {
            'apps': apps.search([('allow_to_sell', '=', True)])
        })

    @route(['/refresh'], type='json', auth='public')
    def catch_app_click(self, **kw):
        apps = request.env['saas.line']
        apps.refresh_lines()
        return {}

    @route(['/what_dependencies'], type='json', auth='public')
    def search_incoming_app_dependencies(self, **kw):
        app_tech_name = kw.get('root')[0]
        app = request.env['saas.line'].sudo().search([('name', '=', app_tech_name)])
        return {
            'dependencies': app.dependencies_info('root')
        }

    @route(['/check_currency'], type='json', auth='public')
    def what_company_cuurency_to_use(self, **kw):
        apps = request.env['saas.line'].sudo()
        return {
            'currency': apps.search([])[0].currency_id.display_name,
            'symbol': apps.search([])[0].currency_id.symbol
        }

    @route(['/take_template_id'], type='json', auth='public')
    def is_build_created(self, **kw):
        templates = request.env['saas.template'].sudo()
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
        for app in apps:
            apps_product_ids.append(app.product_id.id)
        return {
            'ids': apps_product_ids
        }


class SaasAppsCart(WebsiteSale):


    @route('/price/cart_update', type='json', auth='public', website=True)
    def cart_update(self, **kw):
        sale_order = request.website.sale_get_order(force_create=True)
        pr_pr = request.env['product.product'].sudo()
        product_ids = kw.get('old_apps_ids', [])
        # Adding user as product in cart
        user_product = request.env.ref("saas_apps.product_user").sudo()
        user_product.price = kw.get('user_price')
        sale_order._cart_update(
                product_id=int(user_product.id),
                add_qty=(float(kw.get('user_cnt')) - float(kw.get('old_user_cnt')))
            )

        # Delete old products from cart
        for id in product_ids:
            sale_order._cart_update(
                product_id=int(id),
                add_qty=-1
            )

        # Changing prices
        product_ids = kw.get('product_ids', [])
        period = kw.get('period')
        for id in product_ids:
            product = pr_pr.browse(id)
            app = request.env['saas.line'].sudo().search([('module_name', '=', product.name)])
            if period == 'm':
                app.change_product_price(app, app.month_price)
            else:
                app.change_product_price(app, app.year_price)

        # Add new ones
        sale_order = request.website.sale_get_order(force_create=True)
        for id in product_ids:
            sale_order._cart_update(
                product_id=int(id),
                add_qty=1
            )
        return {
            "link": "/shop/cart"
        }
