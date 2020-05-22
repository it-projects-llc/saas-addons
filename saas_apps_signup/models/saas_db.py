# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class SaasDb(models.Model):

    _inherit = 'saas.db'

    def create(self, vals):
        partner_id = self.env.context.get("build_partner_id")
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            self.env["contract.contract"].create({
                "name": "{}'s SaaS Contract".format(partner.name),
                "partner_id": partner.id,
                "contract_template_id": self.env.ref("saas_contract.contract_template_annually").id,
                "contract_line_ids": [

                ],
            })

        res = super(SaasDb, self).create(vals)
        return res
