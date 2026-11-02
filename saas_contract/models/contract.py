# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Contract(models.Model):

    _inherit = 'contract.contract'

    @api.depends("build_id.contract_id")
    def _compute_build(self):
        builds_with_contract_list = self.sudo().env["saas.db"].search_read([
            ("contract_id", "in", self.ids)
        ], ["contract_id", "id"])

        contract2build = {}
        for t in builds_with_contract_list:
            contract2build[t["contract_id"][0]] = t["id"]

        for contract in self:
            contract = contract
            contract.write({
                "build_id": contract2build.get(contract.id) or False,
            })

    def _inverse_build(self):
        Build = self.sudo().env["saas.db"]
        for contract in self:
            builds = Build.search([("contract_id", "=", contract.id)])
            (builds - contract.build_id).write({"contract_id": False})
            if contract.build_id:
                if contract.build_id.contract_id != contract:  # add extra check to prevent excessive write
                    contract.build_id.write({"contract_id": contract.id})

    # TODO: inverse is temporary hack. build_id must be only as computed field
    build_id = fields.Many2one("saas.db", readonly=True, compute="_compute_build", inverse="_inverse_build", store=True)
    build_expiration_date_defacto = fields.Datetime("Build expiration date (defacto)", related="build_id.expiration_date")
    build_status = fields.Selection([
        ("trial", "Trial"),
        ("active", "Active"),
        ("suspended", "Suspended"),
    ], "Build status", compute="_compute_build_status", store=False)
    trial_expiration_date = fields.Datetime("Trial expiration date", readonly=True)

    @api.depends("build_id", "build_id.expiration_date", "trial_expiration_date")
    def _compute_build_status(self):
        now = fields.Datetime.now()
        for record in self:
            if not record.build_id:
                record.build_status = False
                continue

            expiration = record.build_expiration_date_defacto
            if expiration and expiration <= now:
                record.build_status = "suspended"
            elif record.trial_expiration_date and expiration and expiration <= record.trial_expiration_date:
                record.build_status = "trial"
            else:
                record.build_status = "active"

    @api.model_create_multi
    def create(self, vals_list):
        records = super(Contract, self).create(vals_list)
        for res in records:
            if res.build_id and res.line_recurrence:
                raise ValidationError("Cannot create SaaS contract with enabled line-level recurrence")
        return records

    def write(self, vals):
        res = super(Contract, self).write(vals)
        if vals.get("line_recurrence") and self.mapped("build_id"):
            raise ValidationError("Cannot enable line-level recurrence for a SaaS contract")
        return res


class ContractLine(models.Model):

    _inherit = 'contract.line'

    build_id = fields.Many2one("saas.db", related="contract_id.build_id")
