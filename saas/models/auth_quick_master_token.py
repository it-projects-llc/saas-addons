# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, api


class Token(models.Model):
    _inherit = 'auth_quick_master.token'

    @api.model_create_multi
    def create(self, vals_list):
        res = super(Token, self).create(vals_list)
        self.env['saas.log'].log_db_authed(res)
        return res
