from odoo import _, fields, models
from odoo.exceptions import UserError


class QueueJob(models.Model):
    _inherit = "queue.job"

    restored_build_id = fields.Many2one("saas.db")

    def action_open_restored_build(self):
        self.ensure_one()
        if not self.restored_build_id:
            raise UserError(_("No restored build defined"))

        action = self.related_action_open_record()
        action.update(
            {
                "res_model": self.restored_build_id._name,
                "res_id": self.restored_build_id.id,
            }
        )
        return action
