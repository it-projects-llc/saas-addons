# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaasDb(models.Model):

    _inherit = 'saas.db'

    backup_config = fields.Many2one("odoo_backup_sh.config", compute='_compute_backup_config')

    def _compute_backup_config(self):
        for record in self:
            record.backup_config = self.env["odoo_backup_sh.config"].search([("database", "=", record.name)], limit=1)
            if record.backup_config and not record.backup_config.saas_db_id != record.id:
                record.backup_config.write({"saas_db_id": record.id})

    def create_backup_config_action(self):
        self.ensure_one()
        assert not self.backup_config, "Backup config is already created for this saas database"
        assert self.operator_id == self.env.ref("saas.local_operator"), "You can only create backup config in local operator"

        self.env["odoo_backup_sh.config"].create({
            "saas_db_id": self.id,
            "storage_service": "google_drive",
            "config_cron_ids": [(0, 0, {
                "interval_type": "days",
                "interval_number": 1,
            })],
            "hourly_rotation": "disabled",
            "daily_rotation": "limited",
            "daily_limit": 15,
            "weekly_rotation": "disabled",
            "monthly_rotation": "disabled",
            "yearly_rotation": "disabled",

        })

        self.env.add_to_compute(self._fields['backup_config'], self)
        self.recompute()

        return {}
