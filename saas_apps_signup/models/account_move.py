# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models
from datetime import date
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):

    _inherit = 'account.move'

    def action_invoice_paid(self):
        sale_lines = self.mapped("line_ids.sale_line_ids")
        today = date.today()

        for order in sale_lines.mapped("order_id"):
            sale_lines_in_order = sale_lines.filtered(lambda x: x.order_id == order)
            new_contract_lines = []
            partner = order.partner_id

            user_line = sale_lines_in_order.filtered(lambda l: l.product_id.product_tmpl_id == self.env.ref("saas_product.product_users"))
            if user_line.product_id == self.env.ref("saas_product.product_users_monthly"):
                subscription_period = "month"
            elif user_line.product_id == self.env.ref("saas_product.product_users_annually"):
                subscription_period = "year"

            build_vals = {}
            for l in sale_lines_in_order:
                p = l.product_id
                if p.product_tmpl_id == self.env.ref("saas_product.product_users") and p != self.env.ref("saas_product.product_users_trial"):
                    new_contract_lines.append({
                        "name": p.name,
                        "product_id": p.id,
                        "price_unit": p.lst_price,
                        "quantity": l.qty_invoiced,
                        "move_line_id": l.invoice_lines[0].id,
                    })
                    build_vals["expiration_date"] = today + p._get_expiration_timedelta()
                    build_vals["max_users_limit"] = l.qty_invoiced
                elif self.env["saas.app"].search([("product_tmpl_id", "=", p.product_tmpl_id.id)]):
                    new_contract_lines.append({
                        "name": p.name,
                        "product_id": p.id,
                        "price_unit": p.lst_price,
                        "quantity": l.qty_invoiced,
                        "move_line_id": l.invoice_lines[0].id,
                    })
                elif self.env["saas.template"].search([("product_tmpl_id", "=", p.product_tmpl_id.id)]):
                    new_contract_lines.append({
                        "name": p.name,
                        "product_id": p.id,
                        "price_unit": p.lst_price,
                        "quantity": l.qty_invoiced,
                        "move_line_id": l.invoice_lines[0].id,
                    })

                for x in new_contract_lines:
                    x.update({
                        "uom_id": self.env.ref("uom.product_uom_unit").id,
                    })

            self.env["contract.contract"].with_context(create_build_vals=build_vals).create({
                "name": "{}'s SaaS Contract".format(partner.name),
                "partner_id": partner.id,
                "contract_line_ids": list(map(lambda line: (0, 0, line), new_contract_lines)),
                "line_recurrence": False,
                "build_id": order.build_id.id,
                "recurring_rule_type": subscription_period + "ly",
                "recurring_interval": 1,
            })
        super(AccountMove, self).action_invoice_paid()
