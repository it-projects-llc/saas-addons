# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaasDb(models.Model):

    _inherit = "saas.db"

    def write_values_to_build(self):
        super(SaasDb, self).write_values_to_build()

        _, model, res_id = self.xmlid_lookup("access_apps.group_allow_apps")

        # disallowing all users to install apps
        self.execute_kw(model, "write", [res_id], {"users": [(5,)]})
