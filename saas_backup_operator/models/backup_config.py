import os
import shutil

from odoo import models, fields
from odoo.service import db


# TODO: do rotation maybe?

class BackupConfig(models.Model):
    _inherit = "odoo_backup_sh.config"

    def _make_backup(self, ts, dump_stream, info_file, info_file_content, *args, **kwargs):
        super(BackupConfig, self)._make_backup(ts, dump_stream, info_file, info_file_content, *args, **kwargs)

        dump_stream.seek(0)
        local_copy_filename = "backup_%s_%s.zip" % (self.database, ts)
        full_path = os.path.join(self.env["ir.attachment"]._filestore(), local_copy_filename)
        with open(full_path, "wb") as f:
            shutil.copyfileobj(dump_stream, f)

        info_file_content.update({
            "local_copy_filename": local_copy_filename
        })
        dump_stream.seek(0)


class BackupInfo(models.Model):
    _inherit = "odoo_backup_sh.backup_info"

    local_copy_filename = fields.Char("Filename of backup local copy", readonly=True)

    def restore_backup_action(self):
        self.ensure_one()
        if db.exp_db_exist(self.database):
            if not self.env.context.get("saas_remove_original_database"):
                confirm_dialog = self.env.ref("saas_backup_operator.remove_old_db_dialog")
                return {
                    "type": "ir.actions.act_window",
                    "res_model": "odoo_backup_sh.backup_info",
                    "views": [(confirm_dialog.id, "form")],
                    "views_id": confirm_dialog.id,
                    "res_id": self.id,
                    "context": {"saas_remove_original_database": True},
                    "target": "new",
                }
            else:
                print("DESTROYED")
                pass

        raise NotImplementedError(":(")
        #db.restore_db(self.database, os.path.join(self.env["ir.attachment"]._filestore(), self.local_copy_filename), copy=True)
        return {
        }
