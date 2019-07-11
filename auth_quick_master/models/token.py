# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import uuid
from dateutil.relativedelta import relativedelta
import logging
import urllib.parse
from ..tools.build_redirection import build_redirection

from odoo import models, fields

_logger = logging.getLogger(__name__)


class Token(models.Model):
    _name = 'auth_quick_master.token'
    _description = 'Authentication Token'

    user_id = fields.Many2one('res.users', 'Master User', default=lambda s: s.env.user.id)
    build = fields.Char('Build Reference')
    build_login = fields.Char('User Login')
    build_user_id = fields.Integer('User ID')
    token = fields.Char(default=lambda self: str(uuid.uuid4()))

    def is_obsolete(self):
        self.ensure_one()
        is_obsolete = self.create_date + relativedelta(minutes=5) < fields.Datetime.now()
        if is_obsolete:
            _logger.info('Token is obsolete: %s', self.token)
        return is_obsolete

    def user_has_access(self):
        """Can be extended"""
        self.ensure_one()
        has_access = self.user_id.has_group('auth_quick_master.group_auth_quick')
        if not has_access:
            _logger.info('User doesn\'t have access: %s', self.user_id.login)
        return has_access

    def get_build_url(self):
        """To be extended"""
        self.ensure_one()
        return None

    def redirect_with_token(self, build_url, build_id, build_login):
        token_obj = self.create({
            'build': build_id,
            'build_login': build_login,
        })
        url = urllib.parse.urljoin(build_url, '/auth_quick/check-token?token={}'.format(token_obj.token))

        return build_redirection(url)
