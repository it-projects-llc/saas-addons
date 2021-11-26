# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta


class SaasDb(models.Model):

    _inherit = "saas.db"

    @api.model
    def _get_number_of_days_for_trial(self):
        return int(
            self.sudo()
            .env["ir.config_parameter"]
            .get_param("saas_expiration.number_of_days_for_trial", 7)
        )

    # fmt: off
    expiration_date = fields.Datetime(
        "Expiration date",
        default=lambda self: datetime.now() + timedelta(days=self._get_number_of_days_for_trial()),
    )
    # fmt: on
    expiration_state = fields.Selection(
        selection=[
            ("expired", "Finished"),
            ("expiring_soon", "Expiring soon"),
            ("active", "Active"),
        ],
        compute="_compute_expiration_state",
    )

    def _compute_expiration_state(self):

        time_now = fields.datetime.now()

        for build in self:

            if time_now > build.expiration_date:
                build.expiration_state = "expired"

            elif time_now < build.expiration_date and time_now >= (
                build.expiration_date - timedelta(days=2)
            ):
                build.expiration_state = "expiring_soon"

            else:
                build.expiration_state = "active"

    def write_values_to_build(self):
        super(SaasDb, self).write_values_to_build()

        if not self.expiration_date:
            return

        self.execute_kw(
            "ir.config_parameter",
            "set_param",
            "database_expiration_date",
            self.expiration_date.strftime(DEFAULT_SERVER_DATETIME_FORMAT),
        )
