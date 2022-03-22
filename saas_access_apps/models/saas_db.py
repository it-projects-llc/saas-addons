# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class SaasDb(models.Model):

    _inherit = "saas.db"

    def write_values_to_build(self):
        super(SaasDb, self).write_values_to_build()

        model, res_id = self.xmlid_to_res_model_res_id("access_apps.group_allow_apps")

        # disallowing all users to install apps
        if model and res_id:
            self.execute_kw(model, "write", [res_id], {"users": [(5,)]})
        else:
            # TODO: maybe warning or something?
            pass
