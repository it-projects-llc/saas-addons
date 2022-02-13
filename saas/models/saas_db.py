# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields


class SAASDB(models.Model):
    _name = 'saas.db'
    _inherit = 'mail.thread'
    _description = 'Build'

    name = fields.Char('Name', help='Technical Database name', readonly=True)
    operator_id = fields.Many2one('saas.operator', required=True)
    type = fields.Selection([
        ('template', 'Template DB'),
        ('build', 'Normal Build'),
    ], string='DB Type', default='build')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Ready'),
    ], default='draft')

    def unlink(self):
        self.drop_db()
        return super(SAASDB, self).unlink()

    def create_db(self, template_db, demo, lang='en_US', callback_obj=None, callback_method=None):
        self.ensure_one()
        db_name = self.name
        self.operator_id._create_db(template_db, db_name, demo, lang)
        self.state = 'done'
        self.env['saas.log'].log_db_created(self)
        if callback_obj and callback_method:
            getattr(callback_obj, callback_method)()

    def drop_db(self):
        for r in self:
            r.operator_id._drop_db(r.name)
            r.state = 'draft'
            self.env['saas.log'].log_db_dropped(r)

    def get_url(self):
        # TODO: need possibility to use custom domain
        self.ensure_one()
        return self.sudo().operator_id.get_db_url(self)

    def action_get_build_access(self):
        auth_url = '/saas/auth-to-build/' + str(self.id)
        return {
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': auth_url,
        }

    def write(self, vals):
        res = super(SAASDB, self).write(vals)
        if not self.env.context.get("writing_from_refresh_data"):  # Do not run "refresh_data", if already running it
            self.refresh_data()
        return res

    def refresh_data(self, should_read_from_build=True, should_write_to_build=True):
        self.flush()
        for record in self.filtered(lambda record: (record.type, record.state) == ("build", "done")).with_context(writing_from_refresh_data=True):
            if should_read_from_build:
                vals = record.read_values_from_build()
                if vals:
                    record.write(vals)

            if should_write_to_build:
                record.write_values_to_build()

    def write_values_to_build(self):
        pass

    def read_values_from_build(self):
        return {}

    def execute_kw(self, model, method, *args, **kwargs):
        return self.operator_id.build_execute_kw(self, model, method, args, kwargs)

    def xmlid_lookup(self, xmlid):
        return self.execute_kw("ir.model.data", "xmlid_lookup", xmlid)

    def xmlid_to_res_model_res_id(self, xmlid, raise_if_not_found=False):
        return self.execute_kw("ir.model.data", "xmlid_to_res_model_res_id", xmlid, raise_if_not_found=raise_if_not_found)

    def action_install_missing_mandatory_modules(self):
        for build in self.filtered(lambda x: x.state == "done"):
            operator = build.operator_id
            operator._install_modules(build.name, [('name', 'in', operator.get_mandatory_modules())])
