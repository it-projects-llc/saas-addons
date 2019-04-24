# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from random import choice

from odoo import api, models, fields


class CreateBuildByTemplate(models.TransientModel):
    _name = 'create.build.by.template'
    _description = 'Wizard to create build by template'
    template_operator_id = fields.Many2one('saas.template.operator', 'Operator', required=True)
    random = fields.Boolean(string='Random operator')
    build_post_init_ids = fields.One2many('build.post_init.line', 'build_creation_id')
    build_name = fields.Char(string="Build name", required=True)

    def create_build(self):
        build = self.template_operator_id.sudo().create_db(self.build_name, self.build_post_init_ids)
        template_id = self.env.context.get('template_id')
        return {
            'type': 'ir.actions.act_window',
            'name': 'SaaS DB',
            'res_model': 'saas.db',
            'res_id': build.id,
            'view_mode': 'form',
            'target': 'main',
            'context': template_id,
        }

    @api.onchange('random')
    def change_operator(self):
        if self.random:
            template_id = self.env.context.get('template_id')
            template = self.env['saas.template'].browse(template_id)
            random_operator = choice(template.operator_ids)
            self.template_operator_id = random_operator.id


class BuildPostInit(models.TransientModel):
    _name = 'build.post_init.line'
    _description = 'Build post init line'
    build_creation_id = fields.Many2one('create.build.by.template', readonly=True)
    key = fields.Char()
    value = fields.Char()
