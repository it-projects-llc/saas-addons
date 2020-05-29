# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models
from datetime import date, timedelta


class AccountMove(models.Model):

    _inherit = 'account.move'

    def _create_or_update_contract(self):
        for record in self:
            # TODO: в контракте надо еще указывать build
            partner = record.partner_id
            contract_line_ids = record.invoice_line_ids.mapped(lambda line: (0, 0, {
                "name": line.product_id.name,
                "product_id": line.product_id.id,
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "quantity": line.quantity,
                "recurring_interval": 1,
                "recurring_rule_type": "yearly",  # TODO: это надо как-то исправить
                "recurring_invoicing_type": "post-paid",
                "recurring_next_date": date.today() + timedelta(days=365),  # TODO: timedelta надо заранее готовить
                "date_start": date.today(),
                "date_end": date.today() + timedelta(days=365),
            }))
            if not record.contract_id:
                record.contract_id = self.env["contract.contract"].create({
                    "name": "{}'s SaaS Contract".format(partner.name),
                    "partner_id": partner.id,
                    "contract_template_id": self.env.ref("saas_contract.contract_template_annually").id,  # TODO: тут вообще говоря тоже надо исправить
                    "contract_line_ids": contract_line_ids,
                })
            else:
                record.contract_id.write({
                    "contract_line_ids": contract_line_ids
                })
