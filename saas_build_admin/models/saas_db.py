# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api
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

        # Vérification de la langue admin avec la nouvelle API
        is_admin_language_installed = bool(self.admin_user.lang) and bool(
            self.execute_kw(
                "res.lang",
                "search_count",
                [("code", "=", self.admin_user.lang)],
            )
        )

        # Installation de la langue si nécessaire (code commenté mais corrigé)
        # if not is_admin_language_installed:
        #    lang_install_id = self.execute_kw(
        #        "base.language.install", "create", [{"lang": self.admin_user.lang, "overwrite": False}]
        #    )
        #    self.execute_kw("base.language.install", "lang_install", [lang_install_id])

        vals = {}

        # Configuration de la langue (code commenté mais corrigé)
        # if self.admin_user.lang:
        #    vals["lang"] = self.admin_user.lang
        # else:
        #    vals["lang"] = "en_US"

        # Configuration du pays
        if self.admin_user.country_id:
            res = self.execute_kw(
                "res.country", "search_read", [("code", "=", self.admin_user.country_id.code)], ["id"]
            )
            if res:
                vals["country_id"] = res[0]["id"]
        else:
            vals["country_id"] = False

        # Génération du mot de passe
        password = ''.join(random.choice(LETTERS_FOR_PASSWORD) for i in range(8))
        vals["login"] = self.admin_user.login
        vals["name"] = self.admin_user.name
        vals["password"] = password

        # Récupération et mise à jour de l'utilisateur admin
        try:
            # Nouvelle méthode pour récupérer l'xmlid dans Odoo 17
            admin_user_ref = self.env.ref("base.user_admin", raise_if_not_found=False)
            if admin_user_ref:
                # Utilisation de l'ID directement
                self.execute_kw("res.users", "write", [admin_user_ref.id], vals)
            else:
                # Fallback: recherche directe de l'utilisateur admin
                admin_users = self.execute_kw(
                    "res.users", "search", [("login", "=", "admin")]
                )
                if admin_users:
                    self.execute_kw("res.users", "write", admin_users, vals)
        except Exception as e:
            # Log d'erreur si nécessaire
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error("Erreur lors de la mise à jour de l'utilisateur admin: %s", e)

        # Envoi de l'email de notification
        try:
            template = self.env.ref("saas_build_admin.template_build_admin_is_set", raise_if_not_found=False)
            if template:
                template.with_context(
                    build=self,
                    build_admin_password=password
                ).send_mail(
                    self.admin_user.id,
                    force_send=True,
                    raise_exception=True
                )
        except Exception as e:
            import logging
            _logger = logging.getLogger(__name__)
            _logger.error("Erreur lors de l'envoi de l'email admin: %s", e)

        # Marquer comme mis à jour
        self.is_admin_user_updated_on_build = True