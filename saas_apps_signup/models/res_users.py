# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models, sql_db, SUPERUSER_ID
from odoo.addons.queue_job.job import job
import logging

from ..exceptions import OperatorNotAvailable

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):

    _inherit = 'res.users'

    @classmethod
    def prepare_signup_values(cls, values, env):
        if values['lang'] not in env['res.lang'].sudo().search([]).mapped('code'):
            env['base.language.install'].sudo().create({
                'lang': values["lang"],
                "overwrite": False,
            }).lang_install()

        country_code = values.pop("country_code")
        if country_code:
            country_code = str(country_code).upper()
            country_ids = env['res.country']._search([('code', '=', country_code)])
            if country_ids:
                values['country_id'] = country_ids[0]

    @job
    def set_admin_on_build(self, db_record, values, admin_user):
        _logger.debug("Setting admin password on %s" % (db_record,))
        values = values.copy()
        values.pop("login", None)
        if admin_user.country_id:
            values['country_code'] = admin_user.country_id.code

        db = sql_db.db_connect(db_record.name)
        with api.Environment.manage(), db.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            if "lang" not in values:
                values["lang"] = admin_user.lang
            self.prepare_signup_values(values, env)
            env.ref('base.user_admin').write(values)

    @api.model
    def signup(self, values, *args, **kwargs):

        if values.get("password"):
            self = self.with_user(SUPERUSER_ID)

            # TODO: это очень шарлатанский метод вычисления базы данных, в которой нужно пароль установить
            admin_user = self.env['res.users'].search([('login', '=', values["login"])], limit=1)
            db_record = self.env['saas.db'].search([('admin_user', '=', admin_user.id)])
            db_record.ensure_one()

            if db_record.type == "done":
                self.set_admin_on_build(db_record, values, admin_user)
            else:
                _logger.warning("%s is not ready for setting admin on it" % (db_record,))
                self.with_delay().set_admin_on_build(db_record, values.copy(), admin_user)

            return super(ResUsers, self).signup(values, *args, **kwargs)

        elif not self.env.context.get("create_user"):
            return super(ResUsers, self).signup(values, *args, **kwargs)

        template_operators = self.env.ref("saas_apps.base_template").operator_ids
        if not template_operators:
            raise OperatorNotAvailable("No template operators in base template. Contact administrator")

        template_operator = template_operators.random_ready_operator()
        if not template_operator:
            raise OperatorNotAvailable("No template operators are ready. Try again later")

        # popping out values before creating user
        database_name = values.pop("database_name", None)
        build_installing_modules = values.pop("installing_modules", "").split(",")
        build_max_users_limit = int(values.pop("max_users_limit", 1))
        subscription_period = values.pop("period", "")

        self.prepare_signup_values(values, self.env)

        res = super(ResUsers, self).signup(values, *args, **kwargs)

        if database_name:
            installing_modules_var = "[" + ",".join(map(
                lambda item: '"{}"'.format(item.strip().replace('"', '')),
                build_installing_modules
            )) + "]"
            admin_user = self.env['res.users'].sudo().search([('login', '=', res[1])], limit=1)

            db_record = template_operator.with_context(
                build_admin_user_id=admin_user.id,
                build_partner_id=admin_user.partner_id.id,
                build_installing_modules=build_installing_modules,
                build_max_users_limit=build_max_users_limit,
                subscription_period=subscription_period
            ).with_user(SUPERUSER_ID).create_db(
                key_values={"installing_modules": installing_modules_var},
                db_name=database_name,
                with_delay=True
            )
        return res

    def action_reset_password(self):
        # prepare reset password signup
        create_mode = bool(self.env.context.get('create_user'))
        if not create_mode:
            return super(ResUsers, self).action_reset_password()

        db_record = self.env['saas.db'].search([('admin_user', '=', self.id)])
        if not db_record:
            return super(ResUsers, self).action_reset_password()

        return super(ResUsers, self.with_context(web_base_url=db_record.get_url())).action_reset_password()
