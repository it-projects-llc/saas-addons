# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License MIT (https://opensource.org/licenses/MIT).

from odoo import models


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    def _get_computed_taxes(self):
        """
        Zero taxes for saas products
        """
        self.ensure_one()

        if self.product_id and self.product_id.product_tmpl_id.is_saas_product:
            return self.env["account.tax"]

        return super(AccountMoveLine, self)._get_computed_taxes()
