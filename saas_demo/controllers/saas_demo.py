# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.http import route, request, Controller


class SaasDemoController(Controller):
    @route('/demo/<string:vendor>/<string:repo>/<string:branch>/<string:module>', type='http', auth='public')
    def create_demo_build(self, vendor, repo, branch, module, **kwargs):
        if not kwargs:
            kwargs = {}
        template_id = request.env['saas.template'].sudo().search([
            ('demo_main_addon_id.name', '=', module),
            ('repo_id.branch', '=', branch),
            ('repo_id.vendor', '=', vendor),
            ('repo_id.repo_name', '=', repo)
        ], limit=1)
        if template_id and template_id.public_access:
            template_operator_id = template_id.operator_ids.random_ready_operator()
            build = template_operator_id.create_db(kwargs, with_delay=False)
            build_url = build.get_url()
            return request.env['auth_quick_master.token'].sudo().redirect_with_token(build_url, build.id,
                                                                                     build_login='admin')
        else:
            return request.not_found()
