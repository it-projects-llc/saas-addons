# Copyright 2020 Vildan Safin <https://github.com/Enigma228322>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.http import route, request, Controller
from odoo import http
from openerp.http import request
import json

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
        app_name, which_price = kw['args']
        app = http.request.env['saas.line'].search([('name', '=', app_name)])
        month = False
        if which_price == 'month':
            month = True
        return {
            'dependencies': app.dependencies_info(month)
        }
