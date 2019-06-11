# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import odoo
from odoo.http import route, request
from odoo.addons.auth_quick_master.tools.build_redirection import build_redirection


class SaasController(odoo.http.Controller):
    @route('/saas/auth-to-build/<int:build_id>', type='http', auth='user')
    def auth_to_build(self, build_id=None):
        if not build_id:
            return False
        build_url = request.env['saas.db'].browse(build_id).get_url() + '/auth_quick/login?build_login=admin'
        return build_redirection(build_url)

    @route('/saas/<model("saas.template"):template_id>/create-fast-build', type='http', auth='public')
    def create_fast_build(self, template_id, **kwargs):
        if not kwargs:
            kwargs = {}
        template_operator_id = template_id.sudo().operator_ids.random_ready_operator()
        build = template_operator_id.sudo().create_db(kwargs, with_delay=False)
        build_url = build.get_url()
        return request.env['auth_quick_master.token'].sudo().redirect_with_token(build_url, build.id, build_login='admin')
