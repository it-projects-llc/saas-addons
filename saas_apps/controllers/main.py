# Copyright 2020 Vildan Safin <https://github.com/Enigma228322>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.http import route, request, Controller
from odoo import http
from openerp.http import request
import json
from odoo.addons.saas_public.controllers.saas_public import SaaSPublicController

class SaaSAppsController(Controller):
    @route('/price', auth='public', website=True)
    def user_page(self, **kw):
        apps = http.request.env['saas.line']
        return http.request.render('saas_apps.index', {
            'apps': apps.search([('allow_to_sell', '=', True)])
        })

    @http.route(['/refresh'], type='json', auth='public', website=True)
    def catch_app_click(self, **kw):
        apps = http.request.env['saas.line']
        apps.refresh()
        return {}

    @http.route(['/what_dependencies'], type='json', auth='public', website=True)
    def what_dependencies(self, **kw):
        app_tech_name = kw['args'][0]
        app = http.request.env['saas.line'].search([('name', '=', app_tech_name)])
        return {
            'dependencies': app.dependencies_info('root')
        }

class SaaSAppsPublicController(SaaSPublicController):
    @http.route(['/create_saas_template'], type='json', auth='public', website=True)
    def what_dependencies(self, **kw):
        templates = http.request.env['saas.template']
        installing_modules_names = kw['args'][0]
        import wdb
        wdb.set_trace()
        installing_modules = []
        for name in installing_modules_names:
            installing_modules += http.request.env['saas.lines'].search([('name', '=', name)])
        new_template = templates.create({
            'name': 'Template ' + str(len(templates.search([]))),
            'template_demo': True,
            'public_access': True,
            'template_module_ids': installing_modules,
        })
        new_template.operator_ids += templates.action_create_build()
        self.create_fast_build(new_template.id)
