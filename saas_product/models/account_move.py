# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import models


class AccountInvoiceLine(models.Model):

    _inherit = "account.invoice.line"

    def _set_taxes(self):
        """
        Zero taxes for saas products
        """
        res = super(AccountInvoiceLine, self)._set_taxes()

        if self.product_id and self.product_id.product_tmpl_id.is_saas_product:
            self.invoice_line_tax_ids = self.env["account.tax"]

        return res
