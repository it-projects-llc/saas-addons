# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaasDb(models.Model):

    _inherit = "saas.db"

    contract_id = fields.Many2one("contract.contract")

    def action_show_contract(self):
        self.ensure_one()
        assert self.contract_id, "This build is not associated with any contract"
        return {
            "type": "ir.actions.act_window",
            "name": "Contract",
            "res_model": "contract.contract",
            "res_id": self.contract_id.id,
            "view_mode": "form",
        }

    def action_create_contract(self):
        self.ensure_one()
        assert not self.contract_id, "This build is already associated with contract"
        return {
            "type": "ir.actions.act_window",
            "name": "Contract",
            "res_model": "contract.contract",
            "view_mode": "form",
            "context": {
                "default_name": self.name + "'s SaaS contract",
                "default_contract_type": "sale",
                "default_build_id": self.id,
                "default_line_recurrence": True,
            }
        }
