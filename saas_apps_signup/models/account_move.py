# Copyright 2020 Eugene Molotov; AGPL-3.0. Odoo 20 purchase integration.
from odoo import _, fields, models
from odoo.exceptions import ValidationError


class AccountMove(models.Model):
    _inherit = "account.move"

    saas_purchase_processed = fields.Boolean(copy=False, readonly=True)

    def _invoice_paid_hook(self):
        result = super()._invoice_paid_hook()
        monthly = self.env.ref("saas_product.product_users_monthly")
        annually = self.env.ref("saas_product.product_users_annually")
        for invoice in self.sudo().filtered(lambda move: move.payment_state == "paid" and move.move_type == "out_invoice" and not move.saas_purchase_processed):
            sale_lines = invoice.invoice_line_ids.sale_line_ids
            for order in sale_lines.order_id:
                invoice_lines = invoice.invoice_line_ids.filtered(lambda line: bool(line.sale_line_ids & order.order_line))
                user_lines = invoice_lines.filtered(lambda line: line.product_id and line.product_id in (monthly | annually))
                if not user_lines:
                    continue
                if len(user_lines.product_id) != 1:
                    raise ValidationError(
                        _("Use one billing period for each SaaS database purchase.")
                    )
                if not order.build_id or order.build_id.state != "draft":
                    raise ValidationError(
                        _("Select an unprovisioned database before paying for a SaaS subscription.")
                    )
                user_product = user_lines.product_id
                quantity = sum(user_lines.mapped("quantity"))
                if quantity < 1 or not float(quantity).is_integer():
                    raise ValidationError(
                        _("The SaaS user quantity must be a positive whole number.")
                    )
                period = "month" if user_product == monthly else "year"
                contract_lines = []
                for line in invoice_lines:
                    product = line.product_id
                    if not product.product_tmpl_id.is_saas_product:
                        continue
                    contract_lines.append((0, 0, {
                        "name": line.name,
                        "product_id": product.id,
                        "price_unit": line.price_unit,
                        "quantity": line.quantity,
                        "move_line_id": line.id,
                        "uom_id": line.product_uom_id.id,
                    }))
                self.env["contract.contract"].sudo().with_context(create_build_vals={
                    "expiration_date": fields.Datetime.now() + user_product._get_expiration_timedelta(),
                    "max_users_limit": int(quantity),
                }).create({
                    "name": _("%s's SaaS Contract", order.partner_id.name),
                    "partner_id": order.partner_id.id,
                    "contract_line_fixed_ids": contract_lines,
                    "line_recurrence": False,
                    "build_id": order.build_id.id,
                    "recurring_rule_type": period + "ly",
                    "recurring_interval": 1,
                })
                # The first paid invoice granted the initial period already.
                invoice.saas_renewal_applied = True
            invoice.saas_purchase_processed = True
        return result
