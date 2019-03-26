# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api, tools, SUPERUSER_ID
from odoo.service import db
from odoo.service.model import execute
from odoo.addons.queue_job.job import job

MANDATORY_BUILD_POST_INIT = """
action = env['ir.config_parameter'].create([ \
{{'key': 'auth_quick.master', 'value': '{}'}}, {{'key': 'auth_quick.build', 'value': '{}'}} \
])
"""


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

    def _get_auth_urls(self, db):
        self.ensure_one()
        if self.type == 'local':
            master_url = self.env['ir.config_parameter'].get_param('web.base.url')
            build_url = self.get_db_url(db)
        return master_url, build_url

    def build_execute_kw(self, build, model, method, args=None, kwargs=None):
        args = args or []
        kwargs = kwargs or {}
        if self.type == 'local':
            return execute(build.name, SUPERUSER_ID, model, method, *args, **kwargs)

    @job
    def build_post_init(self, build, post_init=None):
        post_init = post_init or []
        master_url, build_url = self._get_auth_urls(build)
        vals = {
            'name': 'Build Code Eval',
            'state': 'code',
            'model_id': 1,
            'code': MANDATORY_BUILD_POST_INIT.format(master_url, build_url)
        }

        post_init.append(vals)
        action_ids = self.build_execute_kw(build, 'ir.actions.server', 'create', [post_init])
        self.build_execute_kw(build, 'ir.actions.server', 'run', [action_ids])
