# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import jinja2
import os

import odoo
from odoo.http import route, request


class SaasController(odoo.http.Controller):
    @route('/saas/auth-to-build/<int:build_id>', type='http', auth='user')
    def auth_to_build(self, build_id=None):
        if not build_id:
            return False
        build_url = request.env['saas.db'].browse(build_id).get_url() + '/auth_quick/login?build_login=admin'
        path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'views'))
        loader = jinja2.FileSystemLoader(path)
        env = jinja2.Environment(loader=loader, autoescape=True)

        return env.get_template('saas_auth.html').render({'build_url': build_url})

    @route('/saas/create-fast-build/<int:template_operator_id>', type='http', auth='public')
    def create_fast_build(self, template_operator_id, **kwargs):
        if not kwargs:
            kwargs = {}
        t_op = request.env['saas.template.operator'].sudo().browse(template_operator_id)
        if not t_op or t_op.state != 'done':
            return False
        db_ids = request.env['saas.db'].sudo().search([]).mapped('id')
        build_name = 'fast_build_{}'.format(len(db_ids))
        build = t_op.sudo().create_db(build_name, kwargs, with_delay=False)
        token_obj = request.env['auth_quick_master.token'].sudo().create({
            'build': build.id,
            'build_login': 'admin',
        })
        build_url = build.get_url() + '/auth_quick/check-token?token={}'.format(token_obj.token)
        path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'views'))
        loader = jinja2.FileSystemLoader(path)
        env = jinja2.Environment(loader=loader, autoescape=True)

        return env.get_template('saas_auth.html').render({'build_url': build_url})
