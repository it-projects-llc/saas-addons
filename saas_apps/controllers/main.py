# Copyright 2020 Vildan Safin <https://github.com/Enigma228322>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.http import route, request, Controller
from odoo.addons.saas_public.controllers.saas_public import SaaSPublicController
import urllib.parse

DB_TEMPLATE = 'template_database_'

class SaaSAppsController(Controller):


    @route('/price', type='http', auth='public', website=True)
    def user_page(self, **kw):
        apps = request.env['saas.line'].sudo()
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
        app_tech_name = kw['root'][0]
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

class SaaSAppsPublicController(SaaSPublicController):
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
