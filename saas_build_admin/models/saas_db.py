# Copyright 2020-2023 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models, api, _
import string
import random
import logging

_logger = logging.getLogger(__name__)

LETTERS_FOR_PASSWORD = string.ascii_lowercase + string.digits + "_-"


class SaasDb(models.Model):
    _inherit = "saas.db"

    admin_user = fields.Many2one("res.users", "Admin user")
    is_admin_user_updated_on_build = fields.Boolean(default=False)

    def write(self, vals):
        if "admin_user" in vals:
            vals["is_admin_user_updated_on_build"] = False
        return super().write(vals)

    def write_values_to_build(self):
        super().write_values_to_build()

        if self.is_admin_user_updated_on_build or not self.admin_user:
            return

        try:
            # 1. Créer d'abord le nouvel utilisateur admin
            password = ''.join(random.choice(LETTERS_FOR_PASSWORD) for i in range(8))
            vals = {
                'name': self.admin_user.name,
                'login': self.admin_user.login,
                'password': password,
                'active': True,
                'groups_id': [(6, 0, [])]  # On ajoutera les groupes après
            }

            if self.admin_user.country_id:
                country_id = self.execute_kw(
                    "res.country",
                    "search",
                    [[["code", "=", self.admin_user.country_id.code]]],
                    {'limit': 1}
                )
                if country_id:
                    vals['country_id'] = country_id[0]

            new_admin_id = self.execute_kw(
                "res.users",
                "create",
                [vals],
                {}
            )

            # 2. Copier les groupes de l'admin original (ID 2)
            admin_groups = self.execute_kw(
                "res.users",
                "read",
                [2],
                {'fields': ['groups_id']}
            )
            if admin_groups and admin_groups[0].get('groups_id'):
                self.execute_kw(
                    "res.users",
                    "write",
                    [[new_admin_id], {'groups_id': [(6, 0, admin_groups[0]['groups_id'])]}],
                    {}
                )

            # 3. Désactiver l'ancien admin (ID 2)
            self.execute_kw(
                "res.users",
                "write",
                [[2], {'active': False}],
                {}
            )

            # 4. Envoyer les informations par email
            template = self.env.ref("saas_build_admin.template_build_admin_is_set", raise_if_not_found=False)
            if template:
                template.with_context(
                    build=self,
                    build_admin_password=password
                ).send_mail(self.admin_user.id, force_send=True)

            self.is_admin_user_updated_on_build = True

        except Exception as e:
            _logger.error("Failed to replace admin user in build %s: %s", self.name, str(e))
            raise