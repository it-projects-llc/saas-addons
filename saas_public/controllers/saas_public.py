# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.http import route, request, Controller


class SaaSPublicController(Controller):
    @route('/saas_public/<model("saas.template"):template_id>/create-fast-build', type='http', auth='public')
    def create_fast_build(self, template_id, **kwargs):
        if not kwargs:
            kwargs = {}
        if template_id and template_id.sudo().public_access:
            template_operator_id = template_id.sudo().operator_ids.random_ready_operator()
            build = template_operator_id.sudo().create_db(kwargs, with_delay=False)
            build_url = build.get_url()
            return request.env['auth_quick_master.token'].sudo().redirect_with_token(build_url, build.id,
                                                                                     build_login='admin')
        else:
            return False
