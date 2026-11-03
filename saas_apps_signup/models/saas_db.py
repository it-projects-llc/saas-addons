# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import Command, _, api, models, fields
from odoo.exceptions import UserError, ValidationError
import logging

_logger = logging.getLogger(__name__)


class SaasDb(models.Model):

    _inherit = 'saas.db'

    database_limit_size = fields.Float(default=lambda self: self.env["ir.config_parameter"].get_float("saas_apps_signup.database_limit_size_default", 0.0))
    is_admin_user_language_installed = fields.Boolean("Is admin user's language installed?")

    database_language_ids = fields.Many2many(
        "res.lang", "saas_db_language_rel", "build_id", "lang_id",
        string="Languages to install", context={"active_test": False}, copy=True,
    )

    @api.model
    def _get_signup_languages(self, codes, preferred=None):
        if isinstance(codes, str):
            codes = codes.split(",")
        if (
            not isinstance(codes, (list, tuple))
            or any(not isinstance(code, str) for code in codes)
            or (preferred and not isinstance(preferred, str))
        ):
            raise ValidationError(_("Invalid language selection."))
        requested = {code.strip() for code in codes if code.strip()}
        requested.update(["en_US", preferred or "en_US"])
        languages = self.env["res.lang"].sudo().with_context(active_test=False).search([
            ("code", "in", sorted(requested)),
        ])
        if requested != set(languages.mapped("code")):
            raise ValidationError(_("Select valid Odoo languages."))
        return languages

    def _install_database_languages(self):
        self.ensure_one()
        codes = set(self.database_language_ids.mapped("code"))
        codes.update(code for code in (self.admin_user.database_lang, self.admin_user.lang) if code)
        if not codes:
            return
        languages = self.execute_kw(
            "res.lang", "search_read", [("code", "in", sorted(codes))],
            ["id", "code", "active"], context={"active_test": False},
        )
        missing = codes - {lang["code"] for lang in languages}
        if missing:
            raise UserError(_(
                "The instance does not support these languages: %s", ", ".join(sorted(missing))
            ))
        pending = [lang["id"] for lang in languages if not lang["active"]]
        if pending:
            wizard = self.execute_kw("base.language.install", "create", {
                "lang_ids": [Command.set(pending)], "overwrite": False,
            })
            self.execute_kw("base.language.install", "lang_install", wizard)

    def _get_pending_job_targets(self):
        targets = super()._get_pending_job_targets()
        if self.contract_id:
            targets["contract.contract"] = self.contract_id.id
        return targets

    @api.model_create_multi
    def create(self, vals_list):

        if not self.env.user.has_group("saas.group_manager"):
            if self.env['saas.db']._search([
                ("state", "=", "draft"),
                ("admin_user", "=", self.env.user.id),
            ], limit=1):
                raise Exception(_("You cannot create more than one draft database"))

        return super(SaasDb, self).create(vals_list)

    def read_values_from_build(self):
        vals = super(SaasDb, self).read_values_from_build()

        if not self.is_admin_user_language_installed and self.admin_user.database_lang:
            installed_langs = [code for code, _ in self.execute_kw("res.lang", "get_installed")]

            if self.admin_user.database_lang in installed_langs:
                # language is installed
                vals.update(is_admin_user_language_installed=True)

        return vals

    def write_values_to_build(self):
        self._install_database_languages()
        super(SaasDb, self).write_values_to_build()

        if self.admin_user.database_lang:
            model, res_id = self.xmlid_lookup("base.user_admin")
            admin = self.execute_kw(model, "read", [res_id], ["lang"])[0]
            if admin["lang"] != self.admin_user.database_lang:
                self.execute_kw(model, "write", [res_id], {"lang": self.admin_user.database_lang})
            self.with_context(writing_from_refresh_data=True).is_admin_user_language_installed = True

        web_base_url = self.env["ir.config_parameter"].sudo().get_str("web.base.url")
        if not web_base_url:
            return

        self.execute_kw(
            "ir.config_parameter",
            "set_str",
            "database_expiration_details_link",
            web_base_url + self.access_url + "/renew_subscription",
        )

        self.execute_kw(
            "ir.config_parameter",
            "set_str",
            "database_expiration_details_link_label",
            "Renew subscribtion",
        )

        Config = self.env["ir.config_parameter"].sudo()

        database_expiration_warning_delay = Config.get_str("saas_apps_signup.database_expiration_warning_delay")
        if database_expiration_warning_delay:
            self.execute_kw(
                "ir.config_parameter",
                "set_str",
                "database_expiration_warning_delay",
                database_expiration_warning_delay
            )

    def _prepare_predecessor_build_vals(self, successor_build):
        res = super(SaasDb, self)._prepare_predecessor_build_vals(successor_build)
        res.update(
            contract_id=False,
        )
        return res

    def _prepare_successor_build_vals(self, predecessor_build):
        res = super(SaasDb, self)._prepare_successor_build_vals(predecessor_build)
        res.update(
            contract_id=predecessor_build.contract_id,
            database_language_ids=[Command.set(predecessor_build.database_language_ids.ids)],
        )
        return res
