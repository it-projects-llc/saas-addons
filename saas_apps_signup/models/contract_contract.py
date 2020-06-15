# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, SUPERUSER_ID
import logging
from ..exceptions import OperatorNotAvailable
from odoo.addons.queue_job.job import job
from datetime import date, timedelta

_logger = logging.getLogger(__name__)


class Contract(models.Model):

    _inherit = 'contract.contract'

    build_id = fields.Many2one("saas.db", readonly=True)

    @api.model
    def create(self, vals):

        record = super(Contract, self).create(vals)

        if self.env.context.get("create_build"):
            record.with_user(SUPERUSER_ID).with_delay()._create_build()

        return record

    def write(self, vals):
        res = super(Contract, self).write(vals)

        if "build_id" in vals:
            build = self.env["saas.db"].sudo().browse(vals["build_id"])
            build.write({
                "expiration_date": self.recurring_next_date,
                "contract_id": self.id,
            })
        return res

    @api.model
    def _create_saas_contract_for_trial(self, build, installing_modules, max_users_limit, subscription_period):
        partner = build.admin_user.partner_id
        installing_products = []
        if installing_modules and max_users_limit:
            # TODO: эту часть надо будет переписывать, когда модули уже будут иметь свои продукты
            installing_products += self.env['saas.line']\
                                       .search([("name", "in", installing_modules), ('application', '=', True)])\
                                       .mapped('product_id.product_variant_id')\
                                       .mapped(lambda p: {
                                           "id": p.id,
                                           "name": p.name,
                                           "price": p.lst_price,
                                           "quantity": 1,
                                       })

            if subscription_period:
                installing_products += self.env.ref("saas_product.product_users_{}".format(subscription_period)).mapped(lambda p: {
                    "id": p.id,
                    "name": p.name,
                    "price": p.lst_price,
                    "quantity": max_users_limit,
                })

        return self.env["contract.contract"].with_context(create_build=True).create({
            "name": "{}'s SaaS Contract".format(partner.name),
            "partner_id": partner.id,
            "contract_template_id": self.env.ref("saas_contract.contract_template_{}".format(subscription_period)).id,  # TODO: Если Try: trial В этом случае по умолчанию используем шаблон с Repeat Every: Monthly

            "contract_line_ids": list(map(lambda p: (0, 0, {
                "name": p["name"],
                "product_id": p["id"],
                "uom_id": self.env.ref("uom.product_uom_unit").id,
                "quantity": p["quantity"],
                "price_unit": p["price"],
                "recurring_interval": 1,
                "recurring_rule_type": "yearly" if subscription_period == "annually" else subscription_period,
                "recurring_invoicing_type": "pre-paid",
                "recurring_next_date": build._fields["expiration_date"].default(self),
                "date_start": build._fields["expiration_date"].default(self),
                "date_end": date.today() + timedelta(days=365)
            }), installing_products))
        })

    @job
    def _create_build(self):
        for contract in self:
            partner = self.partner_id
            build = self.env["saas.db"].search([
                ("type", "=", "build"),
                ("state", "=", "draft"),
                ("admin_user", "in", partner.user_ids.ids),
            ], order='id DESC', limit=1)

            if not build:
                _logger.warning("No draft build found for making contract")
                return

            contract_line_users = contract.contract_line_ids.filtered(lambda line: line.product_id.product_tmpl_id == self.env.ref("saas_product.product_users"))

            if not contract_line_users:
                _logger.error("Not creating build. Reason: no 'Users' products in contract")
                return contract

            if len(contract_line_users) > 1:
                _logger.error("Not creating build. Reason: too many 'Users' products in contract ({})".format(len(contract_line_users)))
                return

            contract_products = contract.contract_line_ids.mapped('product_id.product_tmpl_id')

            build_installing_modules = self.env['saas.line'].sudo().search([('product_id', 'in', contract_products.ids)]).mapped('name')
            build_max_users_limit = int(contract_line_users.quantity)

            template = self.env["saas.template"].search([
                ("set_as_package", "=", True),
                ("product_id", "in", contract_products.ids),
            ])
            if not template:
                template = self.env.ref("saas_apps.base_template")
            elif len(template) > 1:
                _logger.warning("Expected only one template. Using first one from {} (given using {})".format(
                    repr(template),
                    repr(template.mapped("product_id")),
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

            build.write({
                "max_users_limit": build_max_users_limit,
            })

            contract.build_id = build.id
