# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.http import request, route, Controller
from odoo.service.db import exp_db_exist
import logging
from slugify import slugify

_logger = logging.getLogger(__name__)


class Main(Controller):
    @route("/saas_apps_signup/is_database_slot_available", auth="public", type="json")
    def is_available(self, database_name, **kw):
        database_name = database_name.lower().strip()
        if not database_name:
            return {"answer": "Empty database name"}

        if database_name != slugify(database_name):
            return {"answer": "Invalid database name"}

        is_free_slot = not exp_db_exist(database_name)
        if is_free_slot:
            return {"domain": request.env.ref("saas.local_operator").sudo().db_url_template.format(db_name=database_name)}
        else:
            return {"answer": "Database already exists"}
