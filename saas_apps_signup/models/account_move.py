# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models
from datetime import date, timedelta
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):

    _inherit = 'account.move'

    def _create_or_update_contract(self):
        contract_lines = self.mapped("line_ids.contract_line_id").filtered(lambda x: x.product_id.product_tmpl_id.is_saas_product and x.date_end)

        if not contract_lines:
            return

        for l in contract_lines:
            new_contract_lines = []

            contract = l.contract_id
            p = l.product_id

            if p.product_tmpl_id == self.env.ref("saas_product.product_users") and p != self.env.ref("saas_product.product_users_trial"):
                new_contract_lines.append({
                    "name": p.name,
                    "product_id": p.id,
                    "price_unit": p.lst_price,
                    "quantity": l.quantity,
                    "date_start": l.date_end + timedelta(days=1),
                    "date_end": l.date_end + p._get_expiration_timedelta(),
                })

            for x in new_contract_lines:
                x.update({
                    "uom_id": self.env.ref("uom.product_uom_unit").id,
                    "recurring_next_date": x["date_start"],
                    "recurring_rule_type": "yearly",
                    "recurring_interval": 999,
                })

            contract.write({
                "contract_line_ids": list(map(lambda line: (0, 0, line), new_contract_lines))
            })
