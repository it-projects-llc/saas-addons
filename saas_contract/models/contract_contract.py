# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class Contract(models.Model):

    _inherit = 'contract.contract'

    # TODO: запретить ситуацию, где набор линии в контракте, в котором есть пустое пространство из будущего времени (хотя-бы в плане юзеров)
    @api.depends("contract_line_ids", "build_id")
    def _compute_build_expiration_date(self):
        for contract in self.filtered("build_id"):
            contract.build_expiration_date = max(
                contract.contract_line_ids
                .filtered(lambda line: line.product_id.product_tmpl_id == self.env.ref("saas_product.product_users") and line.is_paid)
                .mapped("date_end")
            )

    build_id = fields.Many2one("saas.db", readonly=True)
    build_expiration_date = fields.Datetime("Computed expiration date of the build", compute=_compute_build_expiration_date)

    def write(self, vals):
        res = super(Contract, self).write(vals)
        lines = self.mapped("contract_line_ids")

        self.env.add_to_compute(lines._fields['is_paid'], lines)
        self.recompute()

        return res

    # TODO: добавить задачу в крон
    def action_update_build(self):
        for contract in self.filtered("build_id"):
            build = contract.build_id

            max_users_limit = contract.contract_line_ids.filtered(
                lambda line: line.product_id.product_tmpl_id == self.env.ref("saas_product.product_users")
                and line.is_paid
                and line.date_start <= fields.Date.context_today() <= line.date_end
            ).mapped("quantity")

            build.write({
                "expiration_date": contract.build_expiration_date,
                "max_users_limit": sum(max_users_limit) or 1,
            })
