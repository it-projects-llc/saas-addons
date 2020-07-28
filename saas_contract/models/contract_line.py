# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ContractLine(models.Model):

    _inherit = 'contract.line'

    def _compute_is_paid(self):
        for line in self:
            if line.price_unit == 0:
                line.is_paid = True
            else:
                line.is_paid = self.env["account.move.line"].sudo().search([
                    ("contract_line_id", "=", line.id),
                ], limit=1).mapped("move_id").invoice_payment_state == "paid"

    is_paid = fields.Boolean("Is line payed?", compute=_compute_is_paid, store=True)

    def write(self, vals):
        res = super(ContractLine, self).write(vals)
        self._recompute_is_paid()
        return res

    def _recompute_is_paid(self):
        if not self:
            return  # nothing to recompute
        self.env.add_to_compute(self._fields['is_paid'], self)
        self.recompute()

    @api.model
    def get_paid_user_product_lines(self):
        return self.filtered(lambda line: line.product_id.product_tmpl_id == self.env.ref("saas_product.product_users") and line.is_paid)
