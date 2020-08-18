# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaasDb(models.Model):

    _inherit = 'saas.db'

    backup_config = fields.Many2one("odoo_backup_sh.config")

    def create_backup_config_action(self):
        self.ensure_one()
        assert not self.backup_config, "Backup config is already created for this saas database"
        assert self.operator_id == self.env.ref("saas.local_operator"), "You can only create backup config in local operator"

        raise NotImplementedError("Надо бы как-то результат вернуть пользователю")

        self.backup_config = self.env["odoo_backup_sh.config"].create({
            "saas_db_id": self.id,
            "storage_service": "google_drive",
            "config_cron_ids": [(0, 0, {
                "interval_type": "days",
                "interval_number": 1,
            })]
        })
