from odoo import fields, models


FAILED = "failed"
ARCHIVED = "archived"


class SaasDb(models.Model):
    _inherit = "saas.db"

    active = fields.Boolean("Active", default=True)
    origin_build_id = fields.Many2one(
        "saas.db", related="origin_backup_id.origin_build_id", readonly=True
    )
    origin_backup_id = fields.Many2one(
        "saas.db.backup", string="Origin backup", readonly=True
    )
    backup_ids = fields.One2many("saas.db.backup", "origin_build_id", readonly=True)
    backup_count = fields.Integer("Backup count", compute="_compute_backups")
    state = fields.Selection(
        selection_add=[(FAILED, "Failed"), (ARCHIVED, "Archived")],
        ondelete={FAILED: "set default", ARCHIVED: "set default"},
    )

    def _compute_backups(self):
        for record in self:
            record.backup_count = len(record.backup_ids.ids)

    def action_create_backup(self):
        self.ensure_one()
        backup = self.env["saas.db.backup"].create({"origin_build_id": self.id})
        return backup._create_backup()

    def action_view_backups(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Backups of %s" % (self.name,),
            "res_model": "saas.db.backup",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [["origin_build_id", "=", self.id]],
        }
