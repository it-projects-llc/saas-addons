# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import random
from odoo import models, fields, api


class SAASTemplate(models.Model):
    _inherit = 'saas.template'

    public_access = fields.Boolean(default=False)
