# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import os
import shutil
import logging

from odoo import api, models, fields
from odoo.service import db
from odoo.exceptions import ValidationError


_logger = logging.getLogger(__name__)

# TODO: do rotation maybe?


class BackupConfig(models.Model):
    _inherit = "odoo_backup_sh.config"

    @api.depends("saas_db_id")
    def _compute_database_name(self):
        for record in self.filtered("saas_db_id"):
            record.database = record.saas_db_id

    def _inverse_database_name(self):
        pass

    saas_db_id = fields.Char("saas.db", readonly=True)
    database = fields.Char(compute=_compute_database_name, inverse=_inverse_database_name)

    def write(self, vals):
        if "database" in vals and self.filtered("saas_db_id"):
            raise ValidationError("You cannot set database name, if records are assigned to saas database")
        return super(BackupConfig, self).write(vals)

    def _make_backup(self, ts, dump_stream, info_file, info_file_content, *args, **kwargs):
        res = super(BackupConfig, self)._make_backup(ts, dump_stream, info_file, info_file_content, *args, **kwargs)

        # this is for saas databases only
        if not self.saas_db_id:
            return res

        dump_stream.seek(0)
        local_copy_filename = "backup_%s_%s.zip" % (self.database, ts)
        full_path = os.path.join(self.env["ir.attachment"]._filestore(), local_copy_filename)
        with open(full_path, "wb") as f:
            shutil.copyfileobj(dump_stream, f)

        info_file_content.update({
            "local_copy_filename": local_copy_filename
        })
        dump_stream.seek(0)

        return res


class BackupInfo(models.Model):
    _inherit = "odoo_backup_sh.backup_info"

    def _compute_local_copy_filename_fullpath(self):
        for record in self:
            if record.local_copy_filename:
                record.local_copy_filename_fullpath = os.path.join(self.env["ir.attachment"]._filestore(), record.local_copy_filename)
            else:
                record.local_copy_filename = False

    local_copy_filename = fields.Char("Filename of backup local copy", readonly=True)
    local_copy_filename_fullpath = fields.Char("Filename of backup local copy (fullpath)", store=False, compute=_compute_local_copy_filename_fullpath)

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
                db.exp_drop(self.database)

        db.restore_db(self.database, self.local_copy_filename_fullpath, copy=True)
        return {}

    def _clean_local_backup_copies(self):
        records = self.search([
            ("local_copy_filename", "!=", False),
        ], order="upload_datetime DESC", offset=5)
        # TODO: надо бы дать возможность пользователю вводить offset
        for record in records:
            try:
                os.unlink(record.local_copy_filename_fullpath)
            except FileNotFoundError:
                pass
            except Exception:
                _logger.exception("Something went wrong when deleting file %s" % (record.local_copy_filename_fullpath,))
                continue
            record.local_copy_filename = False

    def unlink(self):
        files_to_remove = self.mapped("local_copy_filename_fullpath")
        super(BackupInfo, self).unlink()
        for file_to_remove in files_to_remove:
            # TODO: это почти копипаста из _clean_local_backup_copies
            try:
                os.unlink(file_to_remove)
            except FileNotFoundError:
                pass
            except Exception:
                _logger.exception("Something went wrong when deleting file %s" % (file_to_remove,))
