# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaasDb(models.Model):

    _inherit = ["saas.db", "portal.mixin"]
    _name = "saas.db"

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
