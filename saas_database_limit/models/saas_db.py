# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaasDb(models.Model):

    _inherit = "saas.db"

    database_limit_size = fields.Float("DB size limit (Mb)")

    def write_values_to_build(self):
        super(SaasDb, self).write_values_to_build()

        self.execute_kw(
            "ir.config_parameter",
            "set_param",
            "database_limit_size",
            str(int((self.database_limit_size or 0) * 1000000)),
        )
