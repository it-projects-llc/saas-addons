# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, models, fields
from odoo.exceptions import ValidationError


class CreateBuildByTemplate(models.TransientModel):
    _name = 'saas.template.create_build'
    _description = 'Wizard to create build by template'

    def _default_template_operator_id(self):
        template_id = self.env.context.get('active_id')
        template = self.env['saas.template'].browse(template_id)
        template_operator = template.operator_ids.filtered(lambda r: r.state == 'done')
        if len(template_operator) == 1:
            return template_operator

    def _default_template_id(self):
        return self.env.context.get('active_id')

    template_operator_id = fields.Many2one(
        'saas.template.operator',
        'Template\'s Deployment', required=True,
        ondelete='cascade',
        default=_default_template_operator_id)
    random = fields.Boolean(string='Use random operator')
    build_post_init_ids = fields.One2many('build.post_init.line', 'build_creation_id',
                                          string="Build Initialization Values",
                                          help="These values will be used on execution "
                                               "template's Build Initialization code")
    build_name = fields.Char(string="Build name", required=True)
    template_id = fields.Many2one('saas.template', default=_default_template_id)
    template_operator_count = fields.Integer(compute="_compute_count")

    @staticmethod
    def _convert_to_dict(key_values):
        if isinstance(key_values, dict):
            key_value_dict = key_values
        else:
            key_value_dict = {}
            for r in key_values:
                if r.key:
                    key_value_dict.update({r.key: r.value})
        return key_value_dict

    @api.depends('template_id')
    def _compute_count(self):
        for rec in self:
            rec.template_operator_count = len(self.template_id.operator_ids)

    def create_build(self):
        key_value_dict = self._convert_to_dict(self.build_post_init_ids)
        build_name = self.build_name + ".getaperp.com"
        existing_db = [db[0] for db in self.list_databases()]
        if build_name in existing_db:
            raise ValidationError("Une base de données avec ce nom existe déjà.")
        build = self.template_operator_id.sudo().create_db(key_value_dict, self.build_name)
        return {
            'type': 'ir.actions.act_window',
            'name': 'SaaS DB',
            'res_model': 'saas.db',
            'res_id': build.id,
            'view_mode': 'form',
            'target': 'main',
        }

    def list_databases(self):
        """Liste toutes les bases de données disponibles."""
        # Remplacer 'your_postgresql_connection_string' par votre chaîne de connexion PostgreSQL
        self.env.cr.execute("SELECT datname FROM pg_catalog.pg_database")
        return self.env.cr.fetchall()


    @api.onchange('random')
    def change_operator(self):
        if self.random:
            random_operator = self.template_id.operator_ids.random_ready_operator()
            self.template_operator_id = random_operator


class BuildPostInit(models.TransientModel):
    _name = 'build.post_init.line'
    _description = 'Build post init line'
    build_creation_id = fields.Many2one('saas.template.create_build', readonly=True)
    key = fields.Char()
    value = fields.Char()
