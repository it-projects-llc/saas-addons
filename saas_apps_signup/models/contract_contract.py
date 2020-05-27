# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class Contract(models.Model):

    _inherit = 'contract.contract'

    build_id = fields.Many2one("saas.db")

    @api.depends(
        "contract_line_ids.recurring_next_date",
        "contract_line_ids.is_canceled",
        "build_id",
    )
    def _compute_recurring_next_date(self):
        res = super(Contract, self)._compute_recurring_next_date()
        if self.build_id and not isinstance(self.id, models.NewId):
            for contract in self.filtered("recurring_next_date"):
                contract.build_id.write({"expiration_date": contract.recurring_next_date})
                contract.build_id.flush()
        return res
