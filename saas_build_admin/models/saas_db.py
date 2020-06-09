# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
import string
import random

LETTERS_FOR_PASSWORD = string.ascii_lowercase + string.digits + "_-"


class SaasDb(models.Model):

    _inherit = "saas.db"

    admin_user = fields.Many2one("res.users", "Admin user")
    is_admin_user_updated_on_build = fields.Boolean(default=False)

    def write(self, vals):
        if "admin_user" in vals:
            vals["is_admin_user_updated_on_build"] = False
        return super(SaasDb, self).write(vals)

    def write_values_to_build(self):
        super(SaasDb, self).write_values_to_build()

        if self.is_admin_user_updated_on_build or not self.admin_user:
            return

        is_admin_language_installed = bool(self.admin_user.lang) and bool(
            self.execute_kw(
                "res.lang",
                "search_read",
                [("code", "=", self.admin_user.lang)],
                ["code"],
            )
        )
        if not is_admin_language_installed:
            lang_install_id = self.execute_kw(
                "base.language.install", "create", {"lang": self.admin_user.lang, "overwrite": False}
            )
            self.execute_kw("base.language.install", "lang_install", lang_install_id)

        vals = {}

        if self.admin_user.lang:
            vals["lang"] = self.admin_user.lang
        else:
            vals["lang"] = "en_US"

        if self.admin_user.country_id:
            res = self.execute_kw(
                "res.country", "search_read", [("code", "=", self.admin_user.country_id.code)], ["id"]
            )
            if res:
                vals["country_id"] = res[0]["id"]
        else:
            vals["country_id"] = None

        password = ''.join(random.choice(LETTERS_FOR_PASSWORD) for i in range(8))
        vals["login"] = self.admin_user.login
        vals["name"] = self.admin_user.name
        vals["password"] = password

        _, model, res_id = self.xmlid_lookup("base.user_admin")

        self.execute_kw(model, "write", res_id, vals)

        template = self.env.ref("saas_build_admin.template_build_admin_is_set")
        template.with_context(build=self, build_admin_password=password).send_mail(self.admin_user.id, force_send=True, raise_exception=True)

        self.is_admin_user_updated_on_build = True
