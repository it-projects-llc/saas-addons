# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
from odoo import models, fields


class SAASTemplate(models.Model):
    _name = 'saas.template'

    name = fields.Char()
    template_demo = fields.Boolean('Install demo data', default=False)
    template_modules_domain = fields.Text(
        'Modules to install',
        help='Domain to search for modules to install after template database creation',
        defalt="[]")
    template_post_hook = fields.Text(
        'Template Creation Hook',
        help='Python code to be executed once db is created and modules are installed')
    operator_ids = fields.One2many(
        'saas.template.operator',
        'template_id')


class SAASTemplateLine(models.Model):
    _name = 'saas.template.operator'

    template_id = fields.Many2one('saas.template')
    operator_id = fields.Many2one('saas.operator')
    db_name = fields.Char()
    state = fields.Selection([
        ('draft', 'No template'),
        ('progress', 'Template is being built'),
        ('done', 'Ready'),
    ])
