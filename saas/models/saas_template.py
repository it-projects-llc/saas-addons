# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# Copyright 2019 Anvar Kildebekov <https://it-projects.info/team/fedoranvar>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import random
import string
import logging

from odoo import models, fields, api, _
from odoo.tools.safe_eval import test_python_expr
from odoo.addons.http_routing.models.ir_http import slugify
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)

DEFAULT_TEMPLATE_PYTHON_CODE = """# Available variables:
#  - env: Odoo Environment on which the action is triggered
#  - time, datetime, dateutil, timezone: useful Python libraries
#  - log: log(message, level='info'): logging function to record debug information in ir.logging table
#  - Warning: Warning Exception to use with raise
# To return an action, assign: action = {...}\n\n\n\n"""

DEFAULT_BUILD_PYTHON_CODE = """# Available variables:
#  - env: Odoo Environment on which the action is triggered
#  - time, datetime, dateutil, timezone: useful Python libraries
#  - log: log(message, level='info'): logging function to record debug information in ir.logging table
#  - Warning: Warning Exception to use with raise
# To return an action, assign: action = {{...}}
# You can specify places for variables that can be passed when creating a build like this:
# env['{key_name_1}'].create({{'subject': '{key_name_2}', }})
# When you need curly braces in build post init code use doubling for escaping\n\n\n\n"""


def random_password(length=32):
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(length))


class SAASTemplate(models.Model):
    _name = 'saas.template'
    _description = 'Database Template'

    name = fields.Char(copy=False)
    template_demo = fields.Boolean('Install demo data', default=False)
    template_module_ids = fields.Many2many('saas.module', string="Modules to install")
    template_post_init = fields.Text(
        'Template Initialization',
        default=DEFAULT_TEMPLATE_PYTHON_CODE,
        help='Python code to be executed once db is created and modules are installed')
    # TODO: need additional check on the possibility of using with format().
    #  Normal use of curly braces will cause an error
    build_post_init = fields.Text(
        'Build Initialization',
        default=DEFAULT_BUILD_PYTHON_CODE,
        help='Python code to be executed once build db is created from template')
    operator_ids = fields.One2many('saas.template.operator', 'template_id', string="Template's deployments")
    is_technical_template = fields.Boolean("Is technical template?")

    @api.constrains('template_post_init')
    def _check_python_code(self):
        for r in self.sudo():
            msg = test_python_expr(expr=r.template_post_init.strip(), mode="exec")
            if msg:
                raise ValidationError(msg)

    def write(self, vals):
        # if the following fields are updated, then we need to rebuild the template database
        trigger_fields = ['template_demo', 'template_module_ids', 'template_post_init']
        updated = any(val in vals for val in trigger_fields)
        if updated:
            self.operator_ids.write({'to_rebuild': True})
        return super(SAASTemplate, self).write(vals)

    def action_create_build(self):
        self.ensure_one()
        if any([rec.state == 'done' for rec in self.operator_ids]):
            return {
                'type': 'ir.actions.act_window',
                'name': 'Create Build',
                'res_model': 'saas.template.create_build',
                'src_model': 'saas.template',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': self.env.ref('saas.saas_template_create_build').id,
                'target': 'new',
            }
        else:
            raise UserError(_('There are no ready template\'s deployments. Create new one or wait until it\'s done.'))

    def refresh_page(self):
        # Empty-function for purpose of refreshing page
        pass


class SAASModules(models.Model):
    _name = 'saas.module'
    _description = 'Template\'s modules to install'
    name = fields.Char('Technical name', required=True)
    description = fields.Char()
    template_ids = fields.Many2many('saas.template')

    def name_get(self):
        result = []
        for rec in self:
            if rec.description:
                result.append((rec.id, '%s (%s)' % (rec.description, rec.name)))
            else:
                result.append((rec.id, rec.name))
        return result


class SAASTemplateLine(models.Model):
    _name = 'saas.template.operator'
    _description = 'Template\'s Deployment'
    _rec_name = 'operator_db_name'

    template_id = fields.Many2one('saas.template', required=True, ondelete='cascade')
    operator_id = fields.Many2one('saas.operator', required=True)
    operator_db_name = fields.Char(required=True, string="Template database name")
    operator_db_id = fields.Many2one('saas.db', readonly=True)
    operator_db_state = fields.Selection(related='operator_db_id.state', string='Database operator state')
    to_rebuild = fields.Boolean(default=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('creating', 'Database Creating'),
        ('installing_modules', 'Modules installation'),
        ('post_init', 'Extra initialization'),
        ('done', 'Ready'),

    ], default='draft')

    @api.model
    def unlink(self):
        for rec in self:
            rec.operator_db_id.unlink()
        return super(SAASTemplateLine, self).unlink()

    @api.model
    def get_to_rebuild(self):
        return self.search([('to_rebuild', '=', True)])

    @api.model
    def preparing_template_next(self):
        template_operators = self.get_to_rebuild()
        operators = template_operators.mapped('operator_id')

        # filter out operators which already have template creating
        def filter_free_operators(op):
            states = op.template_operator_ids.mapped('state')
            return all((s in ['draft', 'done'] for s in states))

        operators = operators.filtered(filter_free_operators)
        if not operators:
            # it's not a time to start
            return
        for t_op in template_operators:
            if t_op.operator_id not in operators:
                continue
            t_op._prepare_template()

            # only one template per operator
            operators -= t_op.operator_id

    def _prepare_template(self):
        for r in self:
            message = '''Template\'s deployment with name {} is creating
            and will be ready in a few minutes.'''.format(r.operator_db_name)
            self.operator_id.notify_users(message, message_type='info')
            # delete db is there is one
            r.operator_db_id.drop_db()
            if not r.operator_db_id or r.operator_id != r.operator_db_id.operator_id:
                r.operator_db_id = self.env['saas.db'].create({
                    'name': r.operator_db_name,
                    'operator_id': r.operator_id.id,
                    'type': 'template',
                })
            self.env['saas.log'].log_db_creating(r.operator_db_id)

            r.write({
                'state': 'creating',
            })
            r.flush()
            r.operator_db_id.with_delay().create_db(
                None,
                r.template_id.template_demo,
                callback_obj=r,
                callback_method='_on_template_created')

    def _on_template_created(self):
        self.ensure_one()
        self.to_rebuild = False
        self.state = 'installing_modules'
        self.operator_id.with_delay().install_modules(self.template_id, self)

    def prepare_name(self, db_name):
        self.ensure_one()
        return slugify(db_name)

    def create_db(self, key_values=None, db_name=None, with_delay=True, draft_build_id=None):
        self.ensure_one()
        if not key_values:
            key_values = {}

        assert not (draft_build_id and db_name), "Both db_name and draft_build_id are given"

        if draft_build_id:
            build = self.env["saas.db"].browse(draft_build_id)
            assert build.state == "draft", "Given build is not draft"
            assert build.operator_id == self.operator_id, "Given build uses other operator"

        else:
            if not db_name:
                db_name = self.operator_id.generate_db_name()
            else:
                db_name = self.prepare_name(db_name)

            build = self.env['saas.db'].create({
                'name': db_name,
                'operator_id': self.operator_id.id,
                'type': 'build',
            })

        self.env['saas.log'].log_db_creating(build, self.operator_db_id)
        if with_delay:
            build.with_delay().create_db(
                self.operator_db_name,
                self.template_id.template_demo,
            )
            build.with_delay().action_install_missing_mandatory_modules()

            self.operator_id.with_delay().build_post_init(build, self.template_id.build_post_init, key_values)
        else:
            build.create_db(
                self.operator_db_name,
                self.template_id.template_demo,
            )
            build.action_install_missing_mandatory_modules()

            self.operator_id.build_post_init(build, self.template_id.build_post_init, key_values)

        return build

    def random_ready_operator(self):
        ready_operators = self.filtered(lambda r: r.state == 'done')
        if not ready_operators:
            return ready_operators
        return random.choice(ready_operators)

    def action_install_missing_mandatory_modules(self):
        for record in self:
            record.operator_db_id.action_install_missing_mandatory_modules()
