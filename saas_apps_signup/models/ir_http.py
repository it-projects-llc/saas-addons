# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    @classmethod
    def _get_translation_frontend_modules_name(cls):
        return super()._get_translation_frontend_modules_name() + ["saas_apps_signup"]
