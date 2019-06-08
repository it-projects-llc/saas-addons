# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import werkzeug
import urllib.parse
import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class AuthQuickMaster(http.Controller):

    @http.route('/auth_quick_master/get-token', type="http", auth='user')
    def get_token(self, build, build_user_id, build_login, build_url):
        _logger.debug('Request for token: build reference = %s, build_user_id = %s, build_login = %s, build_url = %s', build, build_user_id, build_login, build_url)
        token_obj = request.env['auth_quick_master.token'].create({
            'build': build,
            'build_login': build_login,
            'build_user_id': build_user_id,
        }).sudo()

        if not token_obj.user_has_access():
            return """{"error": "You don't have access"}"""

        build_url = token_obj.get_build_url() or build_url

        if not build_url:
            return """{"error": "Build url is unknown"}"""

        url = urllib.parse.urljoin(build_url, '/auth_quick/check-token?token=%s' % token_obj.token)
        return werkzeug.utils.redirect(url, 302)

    @http.route('/auth_quick_master/check-token', type="json", auth='public')
    def check_token(self, token):
        _logger.debug('Checking for token: %s', token)
        token_obj = request.env['auth_quick_master.token'].sudo().search([
            ('token', '=', token)
        ])
        if token_obj.is_obsolete():
            return {"error": "Token is obsolete"}

        if not token_obj.user_has_access():
            return {"error": "User doesn't have access"}

        return {"success": "ok", "data": {
            "build_user_id": token_obj.build_user_id,
            "build_login": token_obj.build_login,
        }}
