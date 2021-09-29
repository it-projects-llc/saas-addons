from odoo import api, models
import os


class SaasOperator(models.Model):
    _inherit = "saas.operator"

    @api.model
    def get_test_remote_instance_url(self):
        return os.environ["SAAS_TEST_REMOTE_INSTANCE_URL"]

    @api.model
    def get_test_remote_master_pwd(self):
        return os.environ["SAAS_TEST_REMOTE_MASTER_PWD"]
