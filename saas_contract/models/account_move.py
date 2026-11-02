# Copyright 2020 Eugene Molotov; MIT. Odoo 20 paid-invoice integration.
from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    saas_renewal_applied = fields.Boolean(copy=False, readonly=True)

    def _invoice_paid_hook(self):
        result = super()._invoice_paid_hook()
        users_product = self.env.ref("saas_product.product_users")
        for invoice in self.sudo().filtered(lambda move: move.payment_state == "paid" and move.move_type == "out_invoice" and not move.saas_renewal_applied):
            applied = False
            for line in invoice.invoice_line_ids:
                if line.product_id.product_tmpl_id != users_product:
                    continue
                build = line.contract_line_id.build_id
                if not build:
                    continue
                now = fields.Datetime.now()
                start = max(now, build.expiration_date) if build.expiration_date else now
                build.expiration_date = start + line.product_id._get_expiration_timedelta()
                applied = True
            if applied:
                invoice.saas_renewal_applied = True
        return result
