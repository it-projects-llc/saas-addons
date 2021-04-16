# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    def _compute_amount(self):
        res = super(AccountInvoice, self)._compute_amount()
        self.invoice_line_ids.mapped("contract_line_id")._recompute_is_paid()
        return res
