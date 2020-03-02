# Copyright 2020 Vildan Safin <https://github.com/Enigma228322>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.http import route, request, Controller
from odoo import http
from openerp.http import request
import json

class SaaSAppsController(Controller):
    @route('/price', auth='public', website=True)
    def user_page(self, **kw):
        apps = http.request.env['saas.lines']
        return http.request.render('saas_apps.index', {
            'apps': apps.search([('allow_to_sell', '=', True)])
        })

    @route('/manage', auth='public', website=True)
    def manager_page(self, **kw):
        apps = http.request.env['ir.module.module']
        return http.request.render('saas_apps.manage', {
            'apps': apps.search([])
        })
    
    # @route('/manage/<name>', auth='public', website=True)
    # def module_information(self, name):
    #     return http.request.render('saas_apps.info', {})
    
    @http.route(['/refresh'], type='json', auth='public', website=True)
    def catch_app_click(self, **kw):
        apps = http.request.env['saas.lines']
        apps.refresh()
        # request.redirect('/manage/%s' % name)
        return {}

    @http.route(['/what_dependencies'], type='json', auth='public', website=True)
    def put_in_basket(self, **kw):
        app_name = kw['args'][0]
        app = http.request.env['saas.lines'].search([('module_name', '=', app_name)])
        return {
            'dependencies': app.dependencies_info(),
            'price': app.final_set_price
        }
