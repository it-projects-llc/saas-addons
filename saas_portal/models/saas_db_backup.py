from odoo import models


class Backup(models.Model):
    _inherit = "saas.db.backup"

    def _prepare_restored_build_vals(self, deploy_backup_res):
        res = super(Backup, self)._prepare_restored_build_vals(deploy_backup_res)
        res.update({
            "is_temporary": True,
            "is_approved": False,
        })
        return res
