# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api


class Template(models.Model):
    _inherit = 'saas.template'

    demo_id = fields.Many2one('saas.demo')
    demo_main_addon_id = fields.Many2one('saas.module')
    # demo_url = fields.Char()
    demo_addon_ids = fields.Many2many('saas.module', help='Will be used as default filter in Apps section of the builds')
    demo_branch = fields.Char()

    _sql_constraints = [
        ('demo_uniq', 'unique (demo_id, demo_main_addon_id, demo_branch)', 'Template for that demo already exists.'),
    ]


class TemplateOperator(models.Model):
    _inherit = 'saas.template.operator'

    @api.model
    def get_to_rebuild(self):
        to_rebuild = super(TemplateOperator, self).get_to_rebuild()
        return to_rebuild.filtered(
            lambda r: r.operator_id.update_repos_state == 'rebuilding' and r.operator_id.is_restarted
        )
