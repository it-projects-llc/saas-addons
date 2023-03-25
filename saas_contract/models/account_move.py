# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
import logging
_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    def _invoice_paid_hook(self):
        for record in self:
            new_pmt_state = record._get_invoice_in_payment_state()
            if new_pmt_state == "paid":
                for line in record.invoice_line_ids:
                    _logger.warning("product_users: %s", self.env.ref("saas_product.product_users"))

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
                    _logger.warning("build_id: %s", build_id)

        return super(AccountMove, self)._invoice_paid_hook()
