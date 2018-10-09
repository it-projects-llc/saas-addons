# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import random
import string

import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


def random_password(len=32):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(len))


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

    # TODO: post hook, modules to install, saas.log


class SAASTemplateLine(models.Model):
    _name = 'saas.template.operator'

    template_id = fields.Many2one('saas.template')
    operator_id = fields.Many2one('saas.operator')
    db_name = fields.Char(required=True)
    db_id = fields.Many2one('saas.db', readonly=True)
    state = fields.Selection([
        ('draft', 'No template'),
        ('progress', 'Template is being built'),
        ('done', 'Ready'),
    ])

    def prepare_template(self):
        for r in self:
            # delete db is there is one
            r.db_id.drop_db()
            r.state = 'progress'
            if not r.db_id or r.operator_id != r.db_id.operator_id:
                r.db_id = self.env['saas.db'].create({
                    'name': r.db_name,
                    'operator_id': r.operator_id,
                })
            password = random_password()
            self.env['saas.log'].log_db_creating(self)
            r.db_id.create_db(None, r.template_id.template_demo, password)
