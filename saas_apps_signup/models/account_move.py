# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models
from datetime import date, timedelta
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):

    _inherit = 'account.move'

    def _create_or_update_contract(self):
        for record in self:
            today = date.today()

            # filtering invoice lines with saas products
            saas_invoice_line_ids = record.invoice_line_ids.filtered(lambda line: line.product_id.product_tmpl_id.is_saas_product)

            # detecting subscription period and other related values
            subscribtion_period = None
            recurring_rule_type = None

            user_product = saas_invoice_line_ids.mapped("product_id").filtered(lambda p: p.product_tmpl_id == self.env.ref("saas_product.product_users"))
            if not user_product:
                continue

            user_product_attribute_value = user_product.product_template_attribute_value_ids.product_attribute_value_id

            if user_product_attribute_value == self.env.ref("saas_product.product_attribute_value_subscription_annually"):
                subscribtion_period = "annually"
                recurring_rule_type = "yearly"
                recurring_next_date = today + timedelta(days=365)

            elif user_product_attribute_value == self.env.ref("saas_product.product_attribute_value_subscription_monthly"):
                subscribtion_period = "monthly"
                recurring_rule_type = "monthly"
                recurring_next_date = today + timedelta(days=30)

            else:
                continue

            partner = record.partner_id

            contract_line_ids = saas_invoice_line_ids.mapped(lambda line: (0, 0, {
                "name": line.product_id.name,
                "product_id": line.product_id.id,
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "quantity": line.quantity,
                "price_unit": line.price_unit,
                "recurring_interval": 1,
                "recurring_rule_type": recurring_rule_type,
                "recurring_invoicing_type": "post-paid",
                "recurring_next_date": recurring_next_date,
                "is_cancel_allowed": False,
                "date_start": today,
                "date_end": today + timedelta(days=365),
            }))

            if not record.contract_id:

                record.contract_id = self.env["contract.contract"].with_context(create_build=True).create({
                    "name": "{}'s SaaS Contract".format(partner.name),
                    "partner_id": partner.id,
                    "contract_template_id": self.env.ref("saas_contract.contract_template_{}".format(subscribtion_period)).id,
                    "contract_line_ids": contract_line_ids,
                })
            else:
                predecessor_contract_lines = []
                for contract_line in contract_line_ids:
                    existing_contract_line = record.contract_id.contract_line_ids.filtered(lambda line: not line.is_canceled and line.product_id.id == contract_line[2]["product_id"])
                    if existing_contract_line:
                        existing_contract_line = existing_contract_line[0]

                        contract_line[2]["date_start"] = existing_contract_line.recurring_next_date + timedelta(days=1)
                        contract_line[2]["date_end"] = existing_contract_line.recurring_next_date + timedelta(days=365)

                        if existing_contract_line.date_start > today and existing_contract_line.predecessor_contract_line_id:
                            predecessor_contract_lines.append((1, existing_contract_line.id, {"is_canceled": True}))
                            predecessor_contract_lines.append((2, existing_contract_line.id))
                            existing_contract_line = existing_contract_line.predecessor_contract_line_id

                        predecessor_contract_lines.append((1, existing_contract_line.id, {
                            "date_end": today,
                            "last_date_invoiced": False,
                            "is_canceled": True,
                        }))
                        contract_line[2]["predecessor_contract_line_id"] = existing_contract_line.id

                record.contract_id.write({
                    "contract_line_ids": predecessor_contract_lines + contract_line_ids,
                })
