# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaasDb(models.Model):

    _inherit = 'saas.db'

    # TODO: перенести это в saas_contact
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

        if not self.env.user.has_group("saas.group_manager"):
            if self.env['saas.db']._search([
                ("state", "=", "draft"),
                ("admin_user", "=", self.env.user.id),
            ], limit=1):
                raise Exception("You cannot create more than one draft database")

        return super(SaasDb, self).create(vals)
