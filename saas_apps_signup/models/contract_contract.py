# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models, SUPERUSER_ID
import logging
from ..exceptions import OperatorNotAvailable
from datetime import date, timedelta

_logger = logging.getLogger(__name__)


class Contract(models.Model):

    _inherit = 'contract.contract'

    @api.model
    def create(self, vals):
        record = super(Contract, self).create(vals)

        if self.env.context.get("create_build"):
            record.with_user(SUPERUSER_ID).with_delay()._create_build()

        return record

    @api.model
    def _create_saas_contract_for_trial(self, build, max_users_limit, subscription_period, installing_modules=None, saas_template_id=None):
        partner = build.admin_user.partner_id
        contract_lines = []
        today = date.today()
        subscription_period_suffix = ""
        if subscription_period == "month":
            subscription_period_suffix = "monthly"
        elif subscription_period == "year":
            subscription_period_suffix = "annually"
        else:
            raise AssertionError("Incorrect value of subscription_period: {}".format(subscription_period))

        expiration_date = self.env["saas.db"]._fields["expiration_date"].default(build)
        product_users = self.env.ref("saas_product.product_users_{}".format(subscription_period_suffix))

        contract_lines += self.env.ref("saas_product.product_users_trial").mapped(lambda p: {
            "name": p.name,
            "product_id": p.id,
            "price_unit": p.lst_price,
            "quantity": max_users_limit,
            "date_start": today,
            "date_end": expiration_date,
        })

        contract_lines += product_users.mapped(lambda p: {
            "name": p.name,
            "product_id": p.id,
            "price_unit": p.lst_price,
            "quantity": max_users_limit,
            "date_start": expiration_date + timedelta(days=1),
            "date_end": today + product_users._get_expiration_timedelta()
        })

        if installing_modules:
            contract_lines += self.env['saas.app']\
                                  .search([("name", "in", installing_modules)])\
                                  .mapped("{}_product_id".format(subscription_period))\
                                  .mapped(lambda p: {
                                      "name": p.name,
                                      "product_id": p.id,
                                      "price_unit": p.lst_price,
                                      "quantity": 1,
                                      "date_start": today,
                                  })

        if saas_template_id:
            saas_template_id = int(saas_template_id)
            contract_lines += self.env["saas.template"]\
                                  .browse(saas_template_id)\
                                  .mapped("{}_product_id".format(subscription_period))\
                                  .mapped(lambda p: {
                                      "name": p.name,
                                      "product_id": p.id,
                                      "price_unit": p.lst_price,
                                      "quantity": 1,
                                      "date_start": expiration_date + timedelta(days=1),
                                      "date_end": today + product_users._get_expiration_timedelta()
                                  })

        for x in contract_lines:
            x.update({
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "recurring_next_date": x["date_start"],
            })
            if x.get("date_end"):
                x.update({
                    "recurring_rule_type": "yearly",
                    "recurring_interval": 999,
                })

        contract = self.env["contract.contract"].with_context(create_build=True).create({
            "name": "{}'s SaaS Contract".format(partner.name),
            "build_id": build.id,
            "partner_id": partner.id,
            "line_recurrence": True,
            "contract_line_ids": list(map(lambda line: (0, 0, line), contract_lines))
        })

        invoice = contract._recurring_create_invoice()
        invoice.action_post()

        return contract

    def _create_build(self):
        for contract in self:
            partner = self.partner_id
            build = self.build_id
            if build:
                assert build.state == "draft"
                assert build.admin_user & partner.user_ids
            else:
                # TODO: избавиться от этой фигни
                build = self.env["saas.db"].search([
                    ("type", "=", "build"),
                    ("state", "=", "draft"),
                    ("admin_user", "in", partner.user_ids.ids),
                ], order='id DESC', limit=1)

            if not build:
                _logger.warning("No draft build found for making contract")
                return

            contract_products = contract.contract_line_ids.mapped('product_id')
            contract_product_templates = contract_products.mapped('product_tmpl_id')

            # fmt: off
            build_installing_modules = self.env['saas.app'].sudo().search([
                ("product_tmpl_id", "in", contract_product_templates.ids)
            ]).mapped("name")
            # fmt: on

            # TODO: оператор должен определяет по билду!
            template = self.env["saas.template"].search([
                ("is_package", "=", True),
                ("product_tmpl_id", "in", contract_product_templates.ids),
            ])
            if not template:
                template = self.env.ref("saas_apps.base_template")
            elif len(template) > 1:
                _logger.warning("Expected only one template. Using first one from {} (given using {})".format(
                    repr(template),
                    repr(template.mapped("product_tmpl_id")),
                ))
                template = template[0]
            template_operators = template.operator_ids
            if not template_operators:
                raise OperatorNotAvailable("No template operators in base template. Contact administrator")

            template_operator = template_operators.random_ready_operator()
            if not template_operator:
                raise OperatorNotAvailable("No template operators are ready. Try again later")

            installing_modules_var = "[" + ",".join(map(
                lambda item: '"{}"'.format(item.strip().replace('"', '')),
                build_installing_modules
            )) + "]"

            build = template_operator.create_db(
                key_values={"installing_modules": installing_modules_var},
                with_delay=False,
                draft_build_id=build.id
            )

            # TODO: это тоже не забудь убрать
            if not contract.build_id:
                contract.build_id = build

            contract.action_update_build()

    @api.model
    def _finalize_and_create_invoices(self, invoices_values):
        invoices = super(Contract, self)._finalize_and_create_invoices(invoices_values)
        for invoice in invoices:
            contract = invoice.contract_id
            build = contract.build_id

            contract.invalidate_cache()
            if build and build.state == "done":
                invoice.action_post()

        return invoices


class ContractLine(models.Model):

    _inherit = 'contract.line'

    @api.model
    def create(self, vals):
        move_line_id = vals.pop("move_line_id", None)
        res = super(ContractLine, self).create(vals)
        if move_line_id:
            self.env["account.move.line"].sudo().browse(move_line_id).write({
                "contract_line_id": res.id,
            })
            res._recompute_is_paid()
        return res
