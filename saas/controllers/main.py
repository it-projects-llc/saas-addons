# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import odoo
from odoo.http import route, request
from odoo.addons.auth_quick_master.tools.build_redirection import build_redirection


class SaasController(odoo.http.Controller):
    @route('/saas/auth-to-build/<int:build_id>', type='http', auth='user')
    def auth_to_build(self, build_id=None, **kwargs):
        if not build_id:
            return False
        build = request.env['saas.db'].browse(build_id)
        _, _, build_admin_id = build.xmlid_lookup("base.user_admin")
        build_url = request.env['saas.db'].browse(build_id).get_url() + '/auth_quick/login?build_user_id={}'.format(build_admin_id)
        return build_redirection(build_url)
