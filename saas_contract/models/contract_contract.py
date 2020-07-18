# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Contract(models.Model):

    _inherit = 'contract.contract'

    build_id = fields.Many2one("saas.db", readonly=True)
    is_trial = fields.Boolean("Is trial build?", readonly=True, default=False)

    def _recurring_create_invoice(self):
        # deny creating second invoice for contract with trial build
        trial_contracts_with_invoices = self.filtered(lambda contract: contract.is_trial and contract.invoice_count > 0)
        return super(Contract, self - trial_contracts_with_invoices)._recurring_create_invoice(self)

    def _prepare_recurring_invoices_values(self, date_ref=False):
        trial_contracts = self.filtered("is_trial")
        invoices_values = []
        for contract in trial_contracts:
            contract_lines = contract.contract_line_ids
            invoice_vals, move_form = contract._prepare_invoice(contract.recurring_next_date)
            for line in contract_lines:
                invoice_line_vals = line._prepare_invoice_line(move_form=move_form)
                invoice_vals["invoice_line_ids"].append((0, 0, invoice_line_vals))
            invoices_values.append(invoice_vals)
        return invoices_values + super(Contract, self - trial_contracts)._prepare_recurring_invoices_values(date_ref)
