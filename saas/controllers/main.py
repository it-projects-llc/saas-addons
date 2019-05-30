# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import jinja2
import os
from random import choice

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

    @route(['/saas/<model("saas.template"):template_id>/create-fast-build',
            '/saas/<model("saas.template"):template_id>/<model("saas.template.operator"):template_operator_id>'
            '/create-fast-build'], type='http', auth='public')
    def create_fast_build(self, template_id, template_operator_id=None, **kwargs):
        if not kwargs:
            kwargs = {}
        if not template_operator_id:
            template_operator_id = template_id.operator_ids.get_ready_random_operator()

        if template_operator_id.state != 'done':
            return False
        db_count = request.env['saas.db'].search_count([])
        build_name = 'fast_build_{}'.format(db_count)
        build = template_operator_id.sudo().create_db(build_name, kwargs, with_delay=False)
        token_obj = request.env['auth_quick_master.token'].sudo().create({
            'build': build.id,
            'build_login': 'admin',
        })
        build_url = build.get_url() + '/auth_quick/check-token?token={}'.format(token_obj.token)
        path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'views'))
        loader = jinja2.FileSystemLoader(path)
        env = jinja2.Environment(loader=loader, autoescape=True)

        return env.get_template('saas_auth.html').render({'build_url': build_url})
