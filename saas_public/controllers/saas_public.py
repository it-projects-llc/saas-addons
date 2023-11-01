# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID
from odoo.http import route, request, Controller


class SaaSPublicController(Controller):
    @route('/saas_public/<int:template_id>/create-fast-build', type='http', auth='public')
    def create_fast_build(self, template_id, **kwargs):
        if not kwargs:
            kwargs = {}
        template = request.env['saas.template'].browse(template_id).sudo()
        return self._redirect_to_build(template, kwargs)

    def _redirect_to_build(self, template, kwargs):
        if template and template.public_access:
            template_operator_id = template.operator_ids.random_ready_operator()
            build = template_operator_id.create_db(kwargs, with_delay=False)
            build_url = build.get_url()
            return (
                request.env["auth_quick_master.token"]
                .with_user(SUPERUSER_ID)
                .redirect_with_token(build_url, build.id, build_login="admin")
            )
        else:
            return request.not_found()
