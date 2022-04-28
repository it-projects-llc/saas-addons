# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_invoice_paid(self):
        for record in self:
            if record.payment_state == "paid":
                for line in record.invoice_line_ids:
                    if line.product_id.product_tmpl_id != self.env.ref("saas_product.product_users"):
                        continue

                    build_id = line.contract_line_id.build_id
                    if not build_id:
                        continue

                    now = fields.Datetime.now()
                    if not build_id.expiration_date or build_id.expiration_date <= now:
                        start = now
                    else:
                        start = build_id.expiration_date
                    build_id.expiration_date = start + line.product_id._get_expiration_timedelta()
        super(AccountMove, self).action_invoice_paid()
