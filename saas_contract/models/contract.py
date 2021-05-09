# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Contract(models.Model):

    _inherit = 'contract.contract'

    # TODO: запретить ситуацию, где набор линии в контракте, в котором есть пустое пространство из будущего времени (хотя-бы в плане юзеров)
    build_id = fields.Many2one("saas.db", readonly=True)
    build_expiration_date_defacto = fields.Datetime("Build expiration date (defacto)", related="build_id.expiration_date")
    build_status = fields.Selection([
        ("trial", "Trial"),
        ("active", "Active"),
        ("suspended", "Suspended"),
    ], "Build status", readonly=True)

    @api.model
    def create(self, vals):
        build_id = vals.get("build_id") or self.env.context.get("default_build_id")
        build = None

        if build_id:
            if not vals.get("line_recurrence"):
                raise ValidationError(_("Cannot create SaaS contract with disabled line-level recurrence"))
            build = self.env["saas.db"].sudo().browse(build_id)
            if build.contract_id:
                raise ValidationError(_("Chosen build already has SaaS contract"))

        res = super(Contract, self).create(vals)

        if build:
            build.write({"contract_id": res.id})

        return res

    def write(self, vals):
        res = super(Contract, self).write(vals)
        if not vals.get("line_recurrence", True) and self.mapped("build_id"):
            raise ValidationError(_("Cannot unset line_recurrenct from SaaS contract"))
        self.mapped("contract_line_ids")._recompute_is_paid()
        return res

    @api.depends("contract_line_ids", "contract_line_ids.is_paid", "build_id")
    def action_update_build(self):
        for contract in self.filtered("build_id"):
            build = contract.build_id

            paid_user_product_lines = contract.contract_line_ids.get_paid_user_product_lines()
            paid_user_product_lines_for_this_day = paid_user_product_lines.filtered(
                lambda line: line.date_start <= fields.Date.context_today(line) <= line.date_end
            )

            max_users_limit = paid_user_product_lines_for_this_day.mapped("quantity")

            is_trial = bool(paid_user_product_lines_for_this_day.filtered(
                lambda line: line.product_id == self.env.ref("saas_product.product_users_trial")
            ))

            build_expiration_date = max(paid_user_product_lines.mapped("date_end"))

            build.write({
                "expiration_date": build_expiration_date,
                "max_users_limit": sum(max_users_limit) or 1,
                "contract_id": contract.id,
            })

            # TODO: тут не будет повторный раз у билда считаться?
            contract.write({
                "build_status": is_trial and "trial" or (fields.Date.context_today(contract) <= build_expiration_date and "active" or "suspended")
            })

    def _action_update_all_builds(self):
        self.env["contract.contract"].search([("build_id", "!=", False)]).action_update_build()


class ContractLine(models.Model):

    _inherit = 'contract.line'

    def _compute_is_paid(self):
        for line in self:
            if line.price_unit == 0:
                line.is_paid = True
            else:
                line.is_paid = self.env["account.move.line"].sudo().search([
                    ("contract_line_id", "=", line.id),
                ], limit=1).mapped("move_id").invoice_payment_state == "paid"

    is_paid = fields.Boolean("Is line payed?", compute=_compute_is_paid, store=True)
    build_id = fields.Many2one("saas.db", related="contract_id.build_id")

    def write(self, vals):
        res = super(ContractLine, self).write(vals)
        self._recompute_is_paid()
        return res

    def _recompute_is_paid(self):
        if not self:
            return  # nothing to recompute
        self.env.add_to_compute(self._fields['is_paid'], self)
        self.recompute()

    @api.model
    def get_paid_user_product_lines(self):
        return self.filtered(lambda line: line.product_id.product_tmpl_id == self.env.ref("saas_product.product_users") and line.is_paid)
