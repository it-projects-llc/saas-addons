# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class Contract(models.Model):

    _inherit = 'contract.contract'

    # TODO: запретить ситуацию, где набор линии в контракте, в котором есть пустое пространство из будущего времени (хотя-бы в плане юзеров)
    build_id = fields.Many2one("saas.db", readonly=True)
    build_expiration_date_defacto = fields.Datetime("Build expiration date (defacto)", related="build_id.expiration_date")

    def write(self, vals):
        res = super(Contract, self).write(vals)
        self.mapped("contract_line_ids")._recompute_is_paid()
        return res

    @api.depends("contract_line_ids.is_paid")
    def action_update_build(self):
        for contract in self.filtered("build_id"):
            build = contract.build_id

            max_users_limit = contract.contract_line_ids.filtered(
                lambda line: line.product_id.product_tmpl_id == self.env.ref("saas_product.product_users")
                and line.is_paid
                and line.date_start <= fields.Date.context_today(line) <= line.date_end
            ).mapped("quantity")

            build_expiration_date = max(
                contract.contract_line_ids
                .filtered(lambda line: line.product_id.product_tmpl_id == self.env.ref("saas_product.product_users") and line.is_paid)
                .mapped("date_end")
            )

            build.write({
                "expiration_date": build_expiration_date,
                "max_users_limit": sum(max_users_limit) or 1,
            })

    def _action_update_all_builds(self):
        self.env["contract.contract"].search([("build_id", "!=", False)]).action_update_build()
