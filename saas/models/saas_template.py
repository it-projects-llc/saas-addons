# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import random
import string
import logging

from odoo import models, fields, api
from odoo.tools.safe_eval import test_python_expr
from odoo.exceptions import ValidationError
from odoo.addons.queue_job.job import job
from ..xmlrpc import rpc_auth, rpc_execute_kw, rpc_install_modules, rpc_code_eval

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
    template_post_init = fields.Text(
        'Template Initialization',
        default=lambda s: s.env['ir.actions.server'].DEFAULT_PYTHON_CODE,
        help='Python code to be executed once db is created and modules are installed')
    operator_ids = fields.One2many(
        'saas.template.operator',
        'template_id')

    @api.constrains('code')
    def _check_python_code(self):
        for r in self.sudo():
            msg = test_python_expr(expr=r.code.strip(), mode="exec")
            if msg:
                raise ValidationError(msg)


class SAASTemplateLine(models.Model):
    _name = 'saas.template.operator'

    template_id = fields.Many2one('saas.template')
    operator_id = fields.Many2one('saas.operator')
    password = fields.Char('DB Password')
    db_name = fields.Char(required=True)
    db_id = fields.Many2one('saas.db', readonly=True)
    creating = fields.Boolean()
    db_state = fields.Selection(related='db_id.state')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('creating', 'Database Creating'),
        ('installing_modules', 'Modules installation'),
        ('post_init', 'Extra initialization'),
        ('done', 'Ready'),

    ])

    def prepare_template(self):
        for r in self:
            # delete db is there is one
            r.db_id.drop_db()
            if not r.db_id or r.operator_id != r.db_id.operator_id:
                r.db_id = self.env['saas.db'].create({
                    'name': r.db_name,
                    'operator_id': r.operator_id,
                    'type': 'template',
                })
            password = random_password()
            self.env['saas.log'].log_db_creating(self)

            r.write({
                'state': 'creating',
                'password': password,
            })

            r.db_id.with_delay().create_db(
                None,
                r.template_id.template_demo,
                password,
                callback_obj=r,
                callback_method='on_template_created')

    def on_template_created(self):
        self.state = 'installing_modules'
        self.with_delay().install_modules()

    @job
    def install_modules(self):
        self.ensure_one()
        auth = self._rpc_auth()
        rpc_install_modules(auth, self.template_id.template_modules_domain)
        self.state = 'post_init'
        self.with_delay().post_init.with_delay()

    @job
    def post_init(self):
        auth = self._rpc_auth()
        rpc_install_modules(auth, self.template_id.template_post_init)
        self.state = 'done'

    def _rpc_auth(self):
        self.ensure_one()
        url = self.db_id.get_url()
        return rpc_auth(
            url,
            self.db_name,
            admin_username='admin',
            admin_password=self.password)
