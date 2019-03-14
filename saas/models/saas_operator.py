# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api, tools, registry, SUPERUSER_ID, sql_db
from odoo.service import db
from odoo.addons.queue_job.job import job


class SAASOperator(models.Model):
    _name = 'saas.operator'
    _description = 'Database Operator'

    # list of types can be extended via selection_add
    type = fields.Selection([
        ('local', 'Same Instance'),
    ], 'Type')
    host = fields.Char()
    port = fields.Char()
    db_url_template = fields.Char('DB URLs', help='Avaialble variables: {db_id}, {db_name}')
    db_name_template = fields.Char('DB Names', help='Avaialble variables: {db_id}')
    template_operator_ids = fields.One2many('saas.template.operator', 'operator_id')

    @api.multi
    def _create_db(self, template_db, db_name, demo, password=None, lang='en_US'):
        """Synchronous db creation"""
        # to avoid installing extra modules we need this condition
        if tools.config['init'] and self.type == 'local':
            tools.config['init'] = {}
        for r in self:
            if r.type != 'local':
                continue

            if template_db:
                db._drop_conn(self.env.cr, template_db)
                db.exp_duplicate_database(template_db, db_name)
            else:
                db.exp_create_database(
                    db_name, demo, lang, user_password=password)

    @api.multi
    def _drop_db(self, db_name):
        for r in self:
            if r.type != 'local':
                continue

            db.exp_drop(db_name)

    def get_db_url(self, db):
        # TODO: use mako for url templating
        self.ensure_one()
        return self.db_url_template.format(db_id=db.id, db_name=db.name)

    def get_db_name(self, db):
        # TODO: use mako for url templating
        self.ensure_one()
        return self.db_url_template.format(db_id=db.id)

    @api.multi
    @job
    def auth_build_post_init(self, master_url=None, build_url=None):
        # TODO: add custom build post init handling
        if self.type == 'local':
            if not master_url:
                master_url = self.env['ir.config_parameter'].get_param('web.base.url')

            if not build_url:
                build_url = self.get_url()

            db = sql_db.db_connect(self.name) #
            registry(self.name).check_signaling()
            with api.Environment.manage(), db.cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                # Mandatory post init
                env['ir.config_parameter'].create([
                    {'key': 'auth_quick.master', 'value': master_url},
                    {'key': 'auth_quick.build', 'value': build_url}
                ])
