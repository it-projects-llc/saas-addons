from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class DomainName(models.Model):
    _name = "saas.domain.name"
    _description = "Web domain"

    name = fields.Char("Domain", required=True)
    operator_id = fields.Many2one("saas.operator", string="Operator", required=True)

    _sql_constraints = [
        ("saas_domain_name_uniq", "unique(name)", "Domain names must be unique"),
    ]

    @api.model
    def _run_domain_operations(self, operator_id, operations):
        operator = self.env["saas.operator"].sudo().browse(operator_id)
        for op in operations:
            if op[0] == "unmap":
                operator.unmap_domain(op[1])
            elif op[0] == "map":
                operator.map_domain(op[1], op[2])
            else:
                _logger.warning("Unknown domain operation: %s" % (op[0],))

    def unlink(self):
        for record in self:
            record.operator_id.unmap_domain(record.name)
        super(DomainName, self).unlink()
