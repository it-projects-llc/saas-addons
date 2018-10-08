# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields


class SAASLog(models.Model):
    _name = 'saas.log'

    name = fields.Char('Log type')
    description = fields.Char('Extra data')
    db_id = fields.Many2one('saas.db')
