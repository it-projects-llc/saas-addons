# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields


class Template(models.Model):
    _inherit = 'saas.template'

    demo_id = fields.Many2one('saas.demo')
    demo_module = fields.Char()
    demo_url = fields.Char()
    demo_addons = fields.Char(help='Comma-separated list. Will be used as default filter in Apps section of the builds')

    _sql_constraints = [
        ('name_uniq', 'unique (demo_id, demo_module)', 'Template for that demo already exists.'),
    ]
