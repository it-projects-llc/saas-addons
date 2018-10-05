# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import uuid
from dateutil.relativedelta import relativedelta

from odoo import models, fields


class Token(models.Model):
    _name = 'auth_quick_master.token'

    user_id = fields.Many2one('res.users', 'Master User', default=lambda s: s.env.user.id)
    build = fields.Char('Build Reference')
    build_login = fields.Char('User Login')
    build_user_id = fields.Integer('User ID')
    token = fields.Char(default=lambda self: str(uuid.uuid4()))

    def is_obsolete(self):
        self.ensure_one()
        return self.create_date + relativedelta(minutes=5) < fields.Datetime.now()

    def user_has_access(self):
        """Can be extended"""
        self.ensure_one()
        return self.user_id.has_group('auth_quick_master.group_auth_quick')

    def get_build_url(self):
        """To be extended"""
        self.ensure_one()
        return None
