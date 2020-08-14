import os
import shutil

from odoo import models, fields


# TODO: do rotation maybe?

class BackupConfig(models.Model):
    _inherit = "odoo_backup_sh.config"

    def _make_backup(self, ts, dump_stream, info_file, info_file_content, *args, **kwargs):
        super(BackupConfig, self)._make_backup(ts, dump_stream, info_file, info_file_content, *args, **kwargs)

        dump_stream.seek(0)
        local_copy_filename = "backup_%s_%s" % (self.database_name, ts)
        full_path = os.path.join(self.env["ir.attachment"]._filestore, local_copy_filename)
        with open(full_path, "wb") as f:
            shutil.copyfileobj(dump_stream, f)

        info_file_content.update({
            "local_copy_filename": local_copy_filename
        })
        dump_stream.seek(0)


class BackupInfo(models.Model):
    _inherit = "odoo_backup_sh.backup_info"

    local_copy_filename = fields.Char("Filename of backup local copy")
