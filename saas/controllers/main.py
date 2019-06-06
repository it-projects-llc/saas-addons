# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import werkzeug
import urllib.parse

import odoo
from odoo.http import route, request


class SaasController(odoo.http.Controller):
    @route('/saas/auth-to-build/<int:build_id>', type='http', auth='user')
    def auth_to_build(self, build_id=None):
        if not build_id:
            return False
        build_url = request.env['saas.db'].browse(build_id).get_url() + '/auth_quick/login?build_login=admin'
        params = urllib.parse.urlencode({
            'build_url': build_url,
        })

        return werkzeug.utils.redirect('/auth_quick_master/build-redirect?{}'.format(params))

    @route('/saas/<model("saas.template"):template_id>/create-fast-build', type='http', auth='public')
    def create_fast_build(self, template_id, **kwargs):
        if not kwargs:
            kwargs = {}
        template_operator_id = template_id.sudo().operator_ids.random_ready_operator()
        build = template_operator_id.sudo().create_db(kwargs, with_delay=False, is_public=True)
        build_url = build.get_url()
        params = urllib.parse.urlencode({
            'build_id': build.id,
            'build_login': 'admin',
            'build_url': build_url,
        })

        return werkzeug.utils.redirect('/auth_quick_master/get-public-token?{}'.format(params))
