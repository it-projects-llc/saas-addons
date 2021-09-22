from odoo import api, fields, models
from collections import defaultdict


class SaasDb(models.Model):
    _inherit = "saas.db"

    domain_name_id = fields.Many2one(
        "saas.domain.name", copy=False, domain="[('operator_id', '=', operator_id)]"
    )

    _sql_constraints = [
        (
            "domain_name_id_uniq",
            "unique(domain_name_id)",
            "Cannot assign same domain to multiple builds",
        ),
    ]

    @api.model
    def create(self, vals):
        record = super(SaasDb, self).create(vals)
        if record.domain_name_id:
            DomainName = self.env["saas.domain.name"]

            DomainName.with_delay()._run_domain_operations(
                record.operator_id.id, ["map", record.domain_name_id.name, record.name]
            )

        return record

    def write(self, vals):
        domain_name_ids_before = {}
        batch_domain_operations = defaultdict(list)

        for record in self:
            domain_name_ids_before[record.id] = record.domain_name_id

        res = super(SaasDb, self).write(vals)

        for record in self:
            if record.domain_name_id == domain_name_ids_before[record.id]:
                continue

            if domain_name_ids_before[record.id]:
                batch_domain_operations[record].append(
                    ["unmap", domain_name_ids_before[record.id].name],
                )

            if record.domain_name_id:
                batch_domain_operations[record].append(
                    ["map", record.domain_name_id.name, record.name],
                )

        DomainName = self.env["saas.domain.name"]
        for build, operations in batch_domain_operations.items():
            DomainName.with_delay()._run_domain_operations(
                build.operator_id.id, operations
            )
        return res
