# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class ResPartner(models.Model):

    _inherit = 'res.partner'

    def _get_signup_url_for_action(self, *args, **kwargs):
        res = super(ResPartner, self)._get_signup_url_for_action(*args, **kwargs)
        partners_with_sale_orders = self.env["sale.order"].sudo().search([("partner_id", "in", self.ids)]).mapped("partner_id")
        for partner in self & partners_with_sale_orders:
            res[partner.id] += "&redirect=/shop/checkout"

        return res
