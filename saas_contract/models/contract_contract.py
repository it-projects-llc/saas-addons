# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Contract(models.Model):

    _inherit = 'contract.contract'

    build_id = fields.Many2one("saas.db", readonly=True)
