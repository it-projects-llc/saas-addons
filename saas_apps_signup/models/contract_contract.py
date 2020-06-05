# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, SUPERUSER_ID
import logging
from ..exceptions import OperatorNotAvailable
from odoo.addons.queue_job.job import job

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

    @job
    def _create_build(self):
        for contract in self:
            partner = self.partner_id
            build = self.env["saas.db"].search([
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

            database_name = build.name
            build_installing_modules = self.env['saas.line'].sudo().search([('product_id', 'in', contract_products.ids)]).mapped('name')
            build_max_users_limit = int(contract_line_users.quantity)
            build_admin_user_id = build.admin_user.id

            template_operators = self.env.ref("saas_apps.base_template").operator_ids
            if not template_operators:
                raise OperatorNotAvailable("No template operators in base template. Contact administrator")

            template_operator = template_operators.random_ready_operator()
            if not template_operator:
                raise OperatorNotAvailable("No template operators are ready. Try again later")

            installing_modules_var = "[" + ",".join(map(
                lambda item: '"{}"'.format(item.strip().replace('"', '')),
                build_installing_modules
            )) + "]"

            # removing old draft build
            build.unlink()

            new_build = template_operator.with_context(
                build_admin_user_id=build_admin_user_id,
                build_installing_modules=build_installing_modules,
                build_max_users_limit=build_max_users_limit,
            ).create_db(
                key_values={"installing_modules": installing_modules_var},
                db_name=database_name,
                with_delay=False
            )

            contract.build_id = new_build.id
