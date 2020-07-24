# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from datetime import timedelta


class SaasDb(models.Model):

    _inherit = "saas.db"

    contract_id = fields.Many2one("contract.contract")

    @api.model
    def remove_long_expired_unpaid_builds(self):
        long_expired_builds = self.env["saas.db"].search([
            ("expiration_date", "<", fields.Date.today() - timedelta(days=7)),
            ("type", "=", "build"),
        ])

        contracts = long_expired_builds.mapped("contract_id")

        paid_invoices = self.env["account.move"].search([
            ("invoice_payment_state", "=", "paid"),
            ("contract_id", "in", contracts.ids)
        ])

        paid_contracts = paid_invoices.mapped("contract_id")
        unpaid_contracts = contracts - paid_contracts

        long_expired_unpaid_builds = unpaid_contracts.mapped('build_id')

        unpaid_contracts.write({"active": False})
        long_expired_unpaid_builds.unlink()

    @api.model
    def remove_long_expired_paid_builds(self):
        long_expired_builds = self.env["saas.db"].search([
            ("expiration_date", "<", fields.Date.today() - timedelta(days=90)),
            ("type", "=", "build"),
        ])
        expired_contracts = long_expired_builds.mapped("contract_id")

        expired_contracts.write({"active": False})
        long_expired_builds.unlink()

    @api.model
    def remove_old_draft_builds(self):
        self.env["saas.db"].search([
            ("create_date", "<", fields.Date.today() - timedelta(days=1)),
            ("type", "=", "build"),
            ("state", "=", "draft"),
        ]).unlink()
