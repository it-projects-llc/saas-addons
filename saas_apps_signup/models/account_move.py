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
                recurring_next_date = date.today() + timedelta(days=365)

            elif user_product_attribute_value == self.env.ref("saas_product.product_attribute_value_subscription_monthly"):
                subscribtion_period = "monthly"
                recurring_rule_type = "monthly"
                recurring_next_date = date.today() + timedelta(days=30)

            else:
                continue

            partner = record.partner_id

            contract_line_ids = saas_invoice_line_ids.mapped(lambda line: (0, 0, {
                "name": line.product_id.name,
                "product_id": line.product_id.id,
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "quantity": line.quantity,
                "recurring_interval": 1,
                "recurring_rule_type": recurring_rule_type,
                "recurring_invoicing_type": "post-paid",
                "recurring_next_date": recurring_next_date,
                "date_start": date.today(),
                "date_end": date.today() + timedelta(days=365),
            }))

            if not record.contract_id:

                record.contract_id = self.env["contract.contract"].with_context(create_build=True).create({
                    "name": "{}'s SaaS Contract".format(partner.name),
                    "partner_id": partner.id,
                    "contract_template_id": self.env.ref("saas_contract.contract_template_{}".format(subscribtion_period)).id,
                    "contract_line_ids": contract_line_ids,
                })
            else:
                record.contract_id.write({
                    "contract_line_ids": contract_line_ids
                })
