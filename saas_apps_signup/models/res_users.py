# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


class ResUsers(models.Model):

    _inherit = 'res.users'

    @api.model
    def signup(self, values, *args, **kwargs):
        self = self.with_user(SUPERUSER_ID)

        if values.get("country_code"):
            values["country_id"] = self.env["res.country"].search([("code", "=", values["country_code"])]).id
            del values["country_code"]

        if values.get('lang') and values["lang"] not in self.env['res.lang'].sudo().search([]).mapped('code'):
            self.env['base.language.install'].sudo().create({
                'lang': values["lang"],
                "overwrite": False,
            }).lang_install()
            self = self.with_context(lang=values.pop("lang"))

        elif not self.env.context.get("create_user"):
            return super(ResUsers, self).signup(values, *args, **kwargs)

        elif "sale_order_id" in values:
            return self.signup_to_buy(values, *args, **kwargs)

        elif "period" in values:
            return self.signup_to_try(values, *args, **kwargs)

        else:
            return super(ResUsers, self).signup(values, *args, **kwargs)

    def signup_to_try(self, values, *args, **kwargs):
        # popping out values before creating user
        database_name = values.pop("database_name", None)
        installing_modules = values.pop("installing_modules", "").split(",")
        saas_template_id = values.pop("saas_template_id", "")
        max_users_limit = int(values.pop("max_users_limit", 1))
        subscription_period = values.pop("period", "")

        res = super(ResUsers, self).signup(values, *args, **kwargs)

        if database_name:
            admin_user = self.env['res.users'].sudo().search([('login', '=', res[1])], limit=1)

            build = self.env["saas.db"].create({
                "name": database_name,
                "operator_id": self.env.ref("saas.local_operator").id,
                "admin_user": admin_user.id,
            })

            self.env["contract.contract"]._create_saas_contract_for_trial(
                build, max_users_limit, subscription_period,
                installing_modules=installing_modules,
                saas_template_id=saas_template_id,
            )
        return res

    def signup_to_buy(self, values, *args, **kwargs):
        sale_order = self.env["sale.order"].browse(int(values.pop("sale_order_id")))

        '''
        # detecting period by "Users" product
        products = sale_order.order_line.mapped("product_id")
        user_product = products.filtered(lambda p: p.product_tmpl_id == env.ref("saas_product.product_users"))
        user_product_attribute_value = user_product.product_template_attribute_value_ids.product_attribute_value_id
        if user_product_attribute_value == self.env.ref("saas_product.product_users_attribute_subscription_value_annually"):
            subscription_period = "annually"
        elif user_product_attribute_value == self.env.ref("saas_product.product_users_attribute_subscription_value_monthly"):
            subscription_period = "monthly"
        else:
            raise NotImplementedError("Could not detect period")
        '''

        database_name = values.pop("database_name", None)

        res = super(ResUsers, self).signup(values, *args, **kwargs)
        admin_user = self.env['res.users'].sudo().search([('login', '=', res[1])], limit=1)
        sale_order.partner_id = admin_user.partner_id

        self.env["saas.db"].create({
            "name": database_name,
            "operator_id": self.env.ref("saas.local_operator").id,
            "admin_user": admin_user.id,
        })

        return res
