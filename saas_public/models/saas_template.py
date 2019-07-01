# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import random
from odoo import models, fields, api


class SAASTemplateOPerator(models.Model):
    _inherit = 'saas.template.operator'

    public_access = fields.Boolean(default=False)

    @api.multi
    def random_ready_operator(self):
        ready_operators = self.filtered(lambda r: r.state == 'done' and r.public_access)
        return random.choice(ready_operators)
