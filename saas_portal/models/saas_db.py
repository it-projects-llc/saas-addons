from odoo import _, fields, models
from odoo.exceptions import UserError
from odoo.addons.saas_backups.models.saas_db import ARCHIVED
import logging

_logger = logging.getLogger(__name__)


class SaasDb(models.Model):
    _inherit = ["saas.db", "portal.mixin"]
    _name = "saas.db"

    is_temporary = fields.Boolean("Is temporary build?", readonly=True)
    is_approved = fields.Boolean("Is temporary build approved?", readonly=True, tracking=True)

    def name_get(self):
        if self.env.context.get("use_domain_name"):
            return [(record.id, record.domain_name_id.name or record.name) for record in self]
        return super(SaasDb, self).name_get()

    def _get_domain_of_queue_job_records(self):
        return [
            "&",
            ("model_name", "=", "saas.db"),
            ("record_ids", "like", [self.id]),
        ]

    def _compute_number_of_queue_jobs_to_be_done(self):
        for record in self:
            record.number_of_queue_jobs_to_be_done = self.env["queue.job"].search_count([
                ("state", "in", ["started", "pending", "enqueued"]),
            ] + record._get_domain_of_queue_job_records())

    number_of_queue_jobs_to_be_done = fields.Integer(compute=_compute_number_of_queue_jobs_to_be_done, store=False)

    def _compute_access_url(self):
        super(SaasDb, self)._compute_access_url()
        for record in self.filtered(lambda record: record.type == "build"):
            record.access_url = '/my/build/%s' % (record.id)

    def _prepare_predecessor_build_vals(self, successor_build):
        return {
            "active": False,
            "state": ARCHIVED,
            "domain_name_id": False,
        }

    def _prepare_successor_build_vals(self, predecessor_build):
        return {
            "domain_name_id": predecessor_build.domain_name_id.id,
            "is_temporary": False,
        }

    def _set_as_successor(self):
        self.ensure_one()

        if not self.origin_build_id:
            raise UserError(_("Predecessor build is not set"))

        predecessor_vals = self.origin_build_id._prepare_predecessor_build_vals(self)
        successor_build_vals = self._prepare_successor_build_vals(self.origin_build_id)

        self.origin_build_id.write(predecessor_vals)
        self.write(successor_build_vals)
        return True

    def action_set_as_successor(self):
        self.ensure_one()
        if not self.is_temporary:
            raise UserError(_("This build is not marked as temporary"))

        if not self.is_approved and not self.env.context.get("ignore_is_approved"):
            confirm_dialog = self.env.ref("saas_portal.ignore_is_approved_dialog")
            return {
                "type": "ir.actions.act_window",
                "res_model": "saas.db",
                "views": [(confirm_dialog.id, "form")],
                "views_id": confirm_dialog.id,
                "res_id": self.id,
                "context": {"ignore_is_approved": True},
                "target": "new",
            }

        if self.origin_build_id.domain_name_id and not self.env.context.get("user_is_aware_of_domain_change"):
            info_dialog = self.env.ref("saas_portal.domain_change_notice_dialog")
            return {
                "type": "ir.actions.act_window",
                "res_model": "saas.db",
                "views": [(info_dialog.id, "form")],
                "views_id": info_dialog.id,
                "res_id": self.id,
                "context": {"ignore_is_approved": True, "user_is_aware_of_domain_change": True},
                "target": "new",
            }

        return self._set_as_successor()
