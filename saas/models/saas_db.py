# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api
from odoo.addons.queue_job.job import job


class SAASDB(models.Model):
    _name = 'saas.db'

    name = fields.Char('Name', help='Technical Database name')
    operator_id = fields.Many2one('saas.operator')
    type = fields.Selection([
        ('template', 'Templated DB'),
        ('build', 'Normal Build'),
    ], string='DB Type', default='build')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Ready'),
    ], default='draft')

    @api.multi
    @job
    def create_db(self, template_db, demo, password=None, lang='en_US', callback_obj=None, callback_method=None):
        self.ensure_one()
        db_name = self.name
        self.operator_id._create_db(template_db, db_name, demo, password, lang)
        self.state = 'done'
        self.env['saas.log'].log_db_created(self)
        if callback_obj and callback_method:
            getattr(callback_obj, callback_method)()

    @api.multi
    @job
    def drop_db(self):
        for r in self:
            r.operator_id._drop_db(r.name)
            self.state = 'draft'
            self.env['saas.log'].log_db_dropped(self)

    def get_url(self):
        self.ensure_one()
        return self.operator_id.get_build_url(self)
