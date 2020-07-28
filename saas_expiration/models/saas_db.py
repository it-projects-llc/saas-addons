# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime, timedelta


class SaasDb(models.Model):

    _inherit = "saas.db"

    expiration_date = fields.Datetime(
        "Expiration date", default=lambda *args: datetime.now() + timedelta(days=7)
    )

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
