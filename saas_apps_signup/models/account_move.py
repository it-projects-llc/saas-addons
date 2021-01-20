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
        sale_lines = self.mapped("line_ids.sale_line_ids")
        today = date.today()

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

            contract.contract_line_ids._recompute_is_paid()
            contract.action_update_build()

        for order in sale_lines.mapped("order_id"):
            sale_lines_in_order = sale_lines.filtered(lambda x: x.order_id == order)
            new_contract_lines = []
            partner = order.partner_id

            user_line = sale_lines_in_order.filtered(lambda l: l.product_id.product_tmpl_id == self.env.ref("saas_product.product_users"))

            for l in sale_lines_in_order:
                p = l.product_id
                if p.product_tmpl_id == self.env.ref("saas_product.product_users") and p != self.env.ref("saas_product.product_users_trial"):
                    new_contract_lines.append({
                        "name": p.name,
                        "product_id": p.id,
                        "price_unit": p.lst_price,
                        "quantity": l.qty_invoiced,
                        "date_start": today,
                        "date_end": today + p._get_expiration_timedelta(),
                        "move_line_id": l.invoice_lines[0].id,
                    })
                elif self.env["saas.app"].search([("product_tmpl_id", "=", p.product_tmpl_id.id)]):
                    new_contract_lines.append({
                        "name": p.name,
                        "product_id": p.id,
                        "price_unit": p.lst_price,
                        "quantity": l.qty_invoiced,
                        "date_start": today,
                        "move_line_id": l.invoice_lines[0].id,
                    })
                elif self.env["saas.template"].search([("product_tmpl_id", "=", p.product_tmpl_id.id)]):
                    new_contract_lines.append({
                        "name": p.name,
                        "product_id": p.id,
                        "price_unit": p.lst_price,
                        "quantity": l.qty_invoiced,
                        "date_start": today,
                        "date_end": today + user_line.product_id._get_expiration_timedelta(),
                        "move_line_id": l.invoice_lines[0].id,
                    })

                for x in new_contract_lines:
                    x.update({
                        "uom_id": self.env.ref("uom.product_uom_unit").id,
                        "recurring_next_date": x["date_start"],
                        "recurring_rule_type": "yearly",
                        "recurring_interval": 999,
                    })

            self.env["contract.contract"].with_context(create_build=True).create({
                "name": "{}'s SaaS Contract".format(partner.name),
                "partner_id": partner.id,
                "contract_line_ids": list(map(lambda line: (0, 0, line), new_contract_lines)),
                "line_recurrence": True,
                "build_id": order.build_id.id,
            })
