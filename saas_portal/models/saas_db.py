# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class SaasDb(models.Model):

    _inherit = ["saas.db", "portal.mixin"]
    _name = "saas.db"

    def _compute_access_url(self):
        super(SaasDb, self)._compute_access_url()
        for record in self.filtered(lambda record: record.type == "build"):
            record.access_url = '/my/build/%s' % (record.id)
