from odoo import fields, models
import logging

_logger = logging.getLogger(__name__)


class Backup(models.Model):
    _name = "saas.db.backup"
    _description = "Build backup"

    name = fields.Char(related="remote_filename", string="Name")

    origin_build_id = fields.Many2one(
        "saas.db", readonly=True, required=True,  # TODO: restrict delition of build_id
    )
    remote_filename = fields.Char(
        "Remote filename", help="Backup filename on operator", readonly=True
    )
    unfinished_job_count = fields.Integer(
        "Unfinished job count", compute="_compute_job_count", store=False
    )
    restored_build_count = fields.Integer(
        "Restored build count", compute="_compute_restored_build_count", store=False
    )

    job_ids = fields.Many2many("queue.job", readonly=True)

    def _compute_restored_build_count(self):
        for record in self:
            record.restored_build_count = self.env["saas.db"].search_count(
                [("origin_backup_id", "=", record.id)]
            )

    def _compute_job_count(self):
        for record in self:
            record.unfinished_job_count = len(
                record.job_ids.filtered(lambda x: x.state != "done")
            )

    def _create_backup(self):
        self.ensure_one()
        job = self.with_delay()._create_backup_job()
        if not job:
            return {}

        self.write({"job_ids": [(4, job.db_record().id)]})

        return {
            "type": "ir.actions.act_window",
            "name": "Create backup",
            "res_model": "queue.job",
            "view_mode": "form",
            "res_id": job.db_record().id,
        }

    def _create_backup_job(self):
        res = self.origin_build_id.operator_id._create_backup(self.origin_build_id.name)
        self.write({"remote_filename": res["name"]})

    def action_view_unfinished_jobs(self):
        # based on queue_job.action_queue_job record
        return {
            "type": "ir.actions.act_window",
            "name": "Backup jobs",
            "res_model": "queue.job",
            "context": {
                "search_default_pending": 1,
                "search_default_enqueued": 1,
                "search_default_started": 1,
                "search_default_failed": 1,
            },
            "views": [[False, "tree"], [False, "form"]],
            "search_view_id": self.env.ref("queue_job.view_queue_job_search").id,
            "domain": [["id", "in", self.job_ids.ids]],
        }

    def action_show_restored_builds(self):
        return {
            "type": "ir.actions.act_window",
            "name": "Restored builds",
            "res_model": "saas.db",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [["origin_backup_id", "in", self.ids]],
        }

    def action_restore(self):
        self.ensure_one()
        job = self.with_delay()._restore_backup_job()

        if not job:
            return {}

        self.write({"job_ids": [(4, job.db_record().id)]})

        return {
            "type": "ir.actions.act_window",
            "name": "Restore backup",
            "res_model": "queue.job",
            "view_mode": "form",
            "res_id": job.db_record().id,
        }

    def _prepare_restored_build_vals(self, deploy_backup_res):
        return {
            "name": deploy_backup_res["db_name"],
            "origin_backup_id": self.id,
        }

    def _restore_backup_job(self):
        operator = self.origin_build_id.operator_id
        _logger.info("Started restoring backup %s" % (self,))
        res = operator._deploy_backup(self.remote_filename)
        restored_build_id = self.origin_build_id.sudo().copy(
            self._prepare_restored_build_vals(res)
        )

        operator.build_post_init(restored_build_id)

        restored_build_id.write({"state": "done"})

        job_uuid = self.env.context.get("job_uuid")
        if job_uuid:
            job = self.env["queue.job"].search([("uuid", "=", job_uuid)], limit=1)
            job.write({"restored_build_id": restored_build_id.id})
            job.user_id.notify_info(
                message="Backup for database %s restored as %s"
                % (self.origin_build_id.name, restored_build_id.name),
                sticky=True,
            )
