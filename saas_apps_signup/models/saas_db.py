# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from datetime import date, timedelta


class SaasDb(models.Model):

    _inherit = 'saas.db'

    contract_id = fields.Many2one("contract.contract")
    expiration_date = fields.Datetime(compute="_compute_expiration_date")

    @api.depends("contract_id.recurring_next_date")
    def _compute_expiration_date(self):
        for record in self:
            if record.contract_id:
                record.expiration_date = record.contract_id.recurring_next_date
            else:
                record.expiration_date = False

    def create(self, vals):

        max_users_limit = self.env.context.get("build_max_users_limit")
        if max_users_limit:
            vals["max_users_limit"] = max_users_limit

        subscription_period = self.env.context.get("subscription_period")

        installing_modules = self.env.context.get("build_installing_modules")
        installing_products = None
        if installing_modules:
            # TODO: эту часть надо будет переписывать, когда модули уже будут иметь свои продукты
            installing_products = self.env['saas.line'].search([("name", "in", installing_modules), ('application', '=', True)]).mapped('product_id.product_variant_id')
            installing_products += self.env.ref("saas_product.product_users").product_variant_id  # TODO: implement anually or monthly

        # остановился тут
        partner_id = self.env.context.get("build_partner_id")
        contract = None
        if partner_id and installing_products and subscription_period:
            partner = self.env['res.partner'].browse(partner_id)
            contract = self.env["contract.contract"].create({
                "name": "{}'s SaaS Contract".format(partner.name),
                "partner_id": partner.id,
                "contract_template_id": self.env.ref("saas_contract.contract_template_{}".format(subscription_period)).id,
                "contract_line_ids": installing_products.mapped(lambda p: (0, 0, {
                    "name": p.name,
                    "product_id": p.id,
                    "uom_id": self.env.ref("uom.product_uom_unit").id,
                    "quantity": 1,
                    "price_unit": p.lst_price,
                    "recurring_interval": 1,
                    "recurring_rule_type": "yearly" if subscription_period == "annually" else subscription_period,
                    "recurring_invoicing_type": "pre-paid",
                    "recurring_next_date": vals.get("expiration_date", self._fields["expiration_date"].default(self)),
                    "date_start": self._fields["expiration_date"].default(self),
                    "date_end": date.today() + timedelta(days=365)
                }))
            })
            vals["contract_id"] = contract.id

        admin_user_id = self.env.context.get("build_admin_user_id")
        if admin_user_id:
            vals["admin_user"] = admin_user_id

        record = super(SaasDb, self).create(vals)
        if contract:
            contract.write({"build_id": record.id})
        return record
