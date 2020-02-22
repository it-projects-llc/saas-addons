# Copyright 2020 Vildan Safin <https://github.com/Enigma228322>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SAASApps(models.Model):
    _name = 'saas.apps'
    _description = 'Module for selecting applications'

    users = fields.Integer(default=0)
