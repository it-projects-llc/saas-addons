# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.addons.saas_public.controllers.saas_public import SaaSPublicController
from odoo.http import route, request


class SaasDemoController(SaaSPublicController):
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

        return self._redirect_to_build(template_id, kwargs)
