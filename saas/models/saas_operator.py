# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from collections import defaultdict
import string

from odoo import models, fields, api, tools, SUPERUSER_ID, sql_db, registry
from odoo.service import db
from odoo.service.model import execute
from odoo.addons.queue_job.job import job
from odoo.http import _request_stack

MANDATORY_MODULES = ['auth_quick']


class SAASOperator(models.Model):
    _name = 'saas.operator'
    _description = 'Database Operator'

    name = fields.Char()
    # list of types can be extended via selection_add
    type = fields.Selection([
        ('local', 'Same Instance'),
    ], 'Type')
    global_url = fields.Char('Master URL (Server-to-Server)', required=True, help='URL for server-to-server communication ')
    # host = fields.Char()
    # port = fields.Char()
    db_url_template = fields.Char('DB URLs', help='Avaialble variables: {db_id}, {db_name}')
    db_name_template = fields.Char('DB Names', required=True, help='Avaialble variables: {unique_id}')
    template_operator_ids = fields.One2many('saas.template.operator', 'operator_id')

    def _create_db(self, template_db, db_name, demo, lang='en_US'):
        """Synchronous db creation"""
        if self.type == 'local':
            # to avoid installing extra modules we need this condition
            if tools.config['init']:
                tools.config['init'] = {}

            # we don't need tests in templates and builds
            test_enable = tools.config['test_enable']
            if test_enable:
                tools.config['test_enable'] = {}

        for r in self:
            if r.type != 'local':
                continue

            if template_db:
                db._drop_conn(self.env.cr, template_db)
                db.exp_duplicate_database(template_db, db_name)
            else:
                db.exp_create_database(
                    db_name, demo, lang)

        if test_enable:
            tools.config['test_enable'] = test_enable

    def _drop_db(self, db_name):
        for r in self:
            if r.type != 'local':
                continue

            db.exp_drop(db_name)

    @job
    def install_modules(self, template_id, template_operator_id):
        self.ensure_one()
        modules = [module.name for module in template_id.template_module_ids]
        modules = [('name', 'in', MANDATORY_MODULES + modules)]
        if self.type == 'local':
            db = sql_db.db_connect(template_operator_id.operator_db_name)
            with api.Environment.manage(), db.cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})

                # Set odoo.http.request to None.
                #
                # Odoo tries to use its values in translation system, which may eventually
                # change currentThread().dbname to saas master value.
                _request_stack.push(None)

                module_ids = env['ir.module.module'].search([('state', '=', 'uninstalled')] + modules)
                module_ids.button_immediate_install()

                # Some magic to force reloading registry in other workers
                env.registry.registry_invalidated = True
                env.registry.signal_changes()

                # return request back
                _request_stack.pop()

            template_operator_id.state = 'post_init'
            self.with_delay().post_init(template_id, template_operator_id)

    @job
    def post_init(self, template_id, template_operator_id):
        if self.type == 'local':
            db = sql_db.db_connect(template_operator_id.operator_db_name)
            registry(template_operator_id.operator_db_name).check_signaling()
            with api.Environment.manage(), db.cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                action = env['ir.actions.server'].create({
                    'name': 'Local Code Eval',
                    'state': 'code',
                    'model_id': 1,
                    'code': template_id.template_post_init
                })
                action.run()
            template_operator_id.state = 'done'

    def get_db_url(self, db):
        # TODO: use mako for url templating
        self.ensure_one()
        return self.db_url_template.format(db_id=db.id, db_name=db.name)

    def generate_db_name(self):
        self.ensure_one()
        sequence = self.env['ir.sequence'].next_by_code('saas.db')
        return self.db_name_template.format(unique_id=sequence)

    def _get_mandatory_args(self, db):
        self.ensure_one()
        return {
            'master_url': self.global_url,
            'build_id': db.id
        }

    @staticmethod
    def _get_mandatory_code():
        master = "env['ir.config_parameter'].create([{{'key': 'auth_quick.master', 'value': '{master_url}'}}])\n"
        build = "env['ir.config_parameter'].create([{{'key': 'auth_quick.build', 'value': '{build_id}'}}])\n"
        return master + build

    def build_execute_kw(self, build, model, method, args=None, kwargs=None):
        args = args or []
        kwargs = kwargs or {}
        if self.type == 'local':
            return execute(build.name, SUPERUSER_ID, model, method, *args, **kwargs)

    @job
    def build_post_init(self, build, post_init_action, key_value_dict):
        key_value_dict.update(self._get_mandatory_args(build))
        code = self._get_mandatory_code() + post_init_action
        action = {
            'name': 'Build Code Eval',
            'state': 'code',
            'model_id': 1,
            'code': string.Formatter().vformat(code, (), SafeDict(**key_value_dict))
        }
        action_ids = self.build_execute_kw(build, 'ir.actions.server', 'create', [action])
        self.build_execute_kw(build, 'ir.actions.server', 'run', [action_ids])

    def write(self, vals):
        if 'global_url' in vals:
            self._update_global_url(vals['global_url'])
        return super(SAASOperator, self).write(vals)

    def _update_global_url(self, url):
        self.ensure_one()
        code = "env['ir.config_parameter'].set_param('auth_quick.master', '{}')\n".format(url)
        builds = self.env['saas.db'].search([('operator_id', '=', self.id), ('type', '=', 'build')])
        action = {
            'name': 'Build Code Eval',
            'state': 'code',
            'model_id': 1,
            'code': code,
        }
        for build in builds:
            action_ids = self.build_execute_kw(build, 'ir.actions.server', 'create', [action])
            self.build_execute_kw(build, 'ir.actions.server', 'run', [action_ids])

    def notify_users(self, message, title=None, message_type=None):
        manager_users = self.env.ref('saas.group_manager').users
        if message_type == 'success':
            manager_users.notify_success(message=message, title=title, sticky=True)
        elif message_type == 'info':
            manager_users.notify_info(message=message, title=title, sticky=True)
        else:
            manager_users.notify_default(message=message, title=title, sticky=True)


class SafeDict(defaultdict):
    def __missing__(self, key):
        return '{' + key + '}'
