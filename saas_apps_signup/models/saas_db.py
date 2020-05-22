# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from datetime import date, timedelta


class SaasDb(models.Model):

    _inherit = 'saas.db'

    contract_id = fields.Many2one("contract.contract")

    def create(self, vals):

        max_users_limit = self.env.context.get("build_max_users_limit")
        if max_users_limit:
            vals["max_users_limit"] = max_users_limit

        installing_modules = self.env.context.get("build_installing_modules")
        installing_products = None
        if installing_modules:
            # TODO: эту часть надо будет переписывать, когда модули уже будут иметь свои продукты
            installing_products = self.env['saas.line'].search([("name", "in", installing_modules), ('application', '=', True)]).mapped('product_id.product_variant_id')

        """
        <field name="name" eval="obj(ref('saas_product.product_users_monthly')).name" model="product.product" />
        <field name="quantity">1</field>
        <field name="uom_id" ref="uom.product_uom_unit" />
        <field name="price_unit" eval="obj(ref('saas_product.product_users_monthly')).lst_price" model="product.product" />
        <field name="recurring_interval">1</field>
        <field name="recurring_rule_type">monthly</field>
        <field name="recurring_invoicing_type">pre-paid</field>
        """
        # остановился тут
        partner_id = self.env.context.get("build_partner_id")
        if partner_id and installing_products:
            partner = self.env['res.partner'].browse(partner_id)
            vals["contract_id"] = self.env["contract.contract"].create({
                "name": "{}'s SaaS Contract".format(partner.name),
                "partner_id": partner.id,
                "contract_template_id": self.env.ref("saas_contract.contract_template_annually").id,
                "contract_line_ids": installing_products.mapped(lambda p: (0, 0, {
                    "name": p.name,
                    "product_id": p.id,
                    "uom_id": self.env.ref("uom.product_uom_unit").id,
                    "quantity": 1,
                    "price_unit": p.lst_price,
                    "recurring_interval": 1,
                    "recurring_rule_type": "monthly",
                    "recurring_invoicing_type": "pre-paid",
                    "date_start": self._fields["expiration_date"].default(self),
                    "date_end": date.today() + timedelta(days=365)
                })),
            }).id

        admin_user_id = self.env.context.get("build_admin_user_id")
        if admin_user_id:
            vals["admin_user"] = admin_user_id

        return super(SaasDb, self).create(vals)
