# Copyright 2020 Vildan Safin <https://github.com/Enigma228322>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.http import route, request, Controller
from odoo import http
from openerp.http import request
import json

class SaaSAppsController(Controller):
    @route('/price', auth='public', website=True)
    def user_page(self, **kw):
        import wdb
        wdb.set_trace()
        apps = http.request.env['saas.lines']
        return http.request.render('saas_apps.index', {
            'apps': apps.search([])
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
    
    @http.route(['/test'], type='json', auth='public', website=True)
    def catch_app_click(self, **kw):
        import wdb
        wdb.set_trace()
        # Mark choosen module as saleable
        http.request.env['ir.module.module'].search([('name', '=', kw['args'][0])]).allow_to_sell = True
        apps = http.request.env['saas.lines']
        apps.add_new_module(kw['args'][0])
        # request.redirect('/manage/%s' % name)
        return {
            'apps': kw['args'][0]
        }
