# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models, fields


class CreateBuildByTemplate(models.TransientModel):
    _name = 'saas.template.create_build'
    _description = 'Wizard to create build by template'

    def _default_template_id(self):
        return self.env.context.get('active_id')

    template_operator_id = fields.Many2one(
        'saas.template.operator', 'Template\'s Deployment', required=True, ondelete='cascade'
    )
    random = fields.Boolean(string='Use random operator')
    build_post_init_ids = fields.One2many('build.post_init.line', 'build_creation_id',
                                          string="Build Initialization Values",
                                          help="These values will be used on execution "
                                               "template's Build Initialization code")
    build_name = fields.Char(string="Build name", required=True)
    template_id = fields.Many2one('saas.template', default=_default_template_id)
    template_operator_count = fields.Integer(compute="_compute_count")

    @api.depends('template_id')
    def _compute_count(self):
        for rec in self:
            rec.template_operator_count = len(self.template_id.operator_ids)

    def create_build(self):
        build = self.template_operator_id.sudo().create_db(self.build_name, self.build_post_init_ids)
        return {
            'type': 'ir.actions.act_window',
            'name': 'SaaS DB',
            'res_model': 'saas.db',
            'res_id': build.id,
            'view_mode': 'form',
            'target': 'main',
        }

    @api.onchange('random')
    def change_operator(self):
        if self.random:
            random_operator = self.template_id.operator_ids.get_ready_random_operator()
            self.template_operator_id = random_operator


class BuildPostInit(models.TransientModel):
    _name = 'build.post_init.line'
    _description = 'Build post init line'
    build_creation_id = fields.Many2one('saas.template.create_build', readonly=True)
    key = fields.Char()
    value = fields.Char()
