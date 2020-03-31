# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class SaasOperator(models.Model):

    _inherit = "saas.operator"

    def get_mandatory_modules(self):
        return super(SaasOperator, self).get_mandatory_modules() + [
            "database_expiration", "web_responsive"
        ]
