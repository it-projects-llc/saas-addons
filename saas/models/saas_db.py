# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api


class SAASDB(models.Model):
    _name = 'saas.db'

    name = fields.Char('Name', help='Technical Database name')
    operator_id = fields.Many2one('saas.operator')
    type = fields.Selection([
        ('template', 'Templated DB'),
        ('build', 'Normal Build'),
    ], string='DB Type')

    @api.multi
    def create_db(self, template_db, demo, password=None, lang='en_US'):
        self.ensure_one()
        db_name = self.name
        self.operator_id._create_db(template_db, db_name, demo, password, lang)
        self.env['saas.log'].log_db_created(self)

    @api.multi
    def drop_db(self):
        for r in self:
            r.operator_id._drop_db(r.name)
            self.env['saas.log'].log_db_dropped(self)
