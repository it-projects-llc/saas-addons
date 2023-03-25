from odoo import models


class QueueJob(models.Model):
    _inherit = "queue.job"

    def write(self, vals):
        res = super(QueueJob, self).write(vals)
        # self.flush()
        self.flush_model()
        return res
