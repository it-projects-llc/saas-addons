# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields


class SAASDB(models.Model):
    _name = 'saas.db'

    name = fields.Char('Name', help='Technical Database name')
    operator_id = fields.Many2one('saas.operator')
