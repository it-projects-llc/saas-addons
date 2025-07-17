# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models, fields, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class SaasDb(models.Model):
    _inherit = "saas.db"

    max_users_limit = fields.Integer("Max Users Allowed")
    users_count = fields.Integer("Current No. Of Users", readonly=True)

    @api.constrains("max_users_limit")
    def _check_max_users_limit(self):
        for record in self:
            if record.max_users_limit < 1:
                raise ValidationError(
                    _("Number of allowed max users must be at least 1")
                )

    def write(self, vals):
        templates = self.filtered(lambda x: x.type == "template")
        if vals.get("state") != "done" or not templates:
            return super(SaasDb, self).write(vals)

        # Désactiver les utilisateurs demo et portal
        for template in templates:
            try:
                # Recherche des utilisateurs demo avec la nouvelle API
                demo_users = template.execute_kw(
                    "ir.model.data",
                    "search_read",
                    [("module", "=", "base"), ("name", "in", ["user_demo", "demo_user0"])],
                    ["model", "res_id"],
                )

                for row in demo_users:
                    if row.get("model") and row.get("res_id"):
                        template.execute_kw(
                            row["model"], "write", [row["res_id"]], {"active": False}
                        )
            except Exception as e:
                _logger.warning("Erreur lors de la désactivation des utilisateurs demo: %s", e)

        return super(SaasDb, self).write(vals)

    def write_values_to_build(self):
        super(SaasDb, self).write_values_to_build()

        if not self.max_users_limit:
            return

        try:
            # Essayons l'approche originale d'Odoo 16
            self.execute_kw(
                "base.limit.records_number",
                "set_max_records",
                "access_limit_max_users.max_users_limit",
                self.max_users_limit,
            )
        except Exception as e:
            _logger.error("Erreur lors de la définition de la limite d'utilisateurs: %s", e)

    def read_values_from_build(self):
        vals = super(SaasDb, self).read_values_from_build()

        # Lecture du nombre d'utilisateurs actuel
        try:
            vals.update(
                users_count=self.execute_kw(
                    "res.users",
                    "search_count",
                    [("is_excluded_from_limiting", "=", False)],
                )
            )
        except Exception as e:
            _logger.warning("Erreur lors de la lecture du nombre d'utilisateurs: %s", e)
            vals.update(users_count=0)

        # Lecture de la limite maximale si elle n'est pas définie
        if not self.max_users_limit:
            try:
                # Nouvelle méthode pour récupérer l'xmlid dans Odoo 17
                limit_record = self.env.ref("access_limit_max_users.max_users_limit", raise_if_not_found=False)
                if limit_record:
                    # Utilisation de l'ID directement
                    limit_data = self.execute_kw(
                        limit_record._name, "read", [limit_record.id], ["max_records"]
                    )
                    if limit_data:
                        vals.update(max_users_limit=limit_data[0]["max_records"])
                else:
                    # Fallback: recherche directe dans base.limit.records_number
                    limit_records = self.execute_kw(
                        "base.limit.records_number",
                        "search_read",
                        [("xml_id", "=", "access_limit_max_users.max_users_limit")],
                        ["max_records"]
                    )
                    if limit_records:
                        vals.update(max_users_limit=limit_records[0]["max_records"])
                    else:
                        _logger.warning("Limite d'utilisateurs non trouvée dans la base")
            except Exception as e:
                _logger.warning("Erreur lors de la lecture de la limite d'utilisateurs: %s", e)

        return vals

    def xmlid_to_res_model_res_id(self, xml_id):
        """
        Méthode de compatibilité pour remplacer l'ancienne méthode xmlid_lookup
        """
        try:
            record = self.env.ref(xml_id, raise_if_not_found=False)
            if record:
                return record._name, record.id
            return None, None
        except Exception as e:
            _logger.warning("Erreur lors de la résolution de l'xmlid %s: %s", xml_id, e)
            return None, None