# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.http import request, route, Controller
import logging
from slugify import slugify
import werkzeug

_logger = logging.getLogger(__name__)


class Main(Controller):
    @route("/saas_apps_signup/is_database_slot_available", auth="public", type="json")
    def is_available(self, database_name, **kw):
        database_name = database_name.lower().strip()
        if not database_name:
            return {"answer": "Empty database name"}

        if database_name != slugify(database_name):
            return {"answer": "Invalid database name"}

        is_free_slot = not request.env["saas.db"].sudo().search([("name", "=", database_name)])
        if is_free_slot:
            return {"domain": request.env.ref("saas.local_operator").sudo().db_url_template.format(db_name=database_name)}
        else:
            return {"answer": "Database already exists"}

    @route("/my/builds/create", auth="user", type="http", website=True)
    def portal_build_selector(self, database_name=None, redirect=None, **kw):
        qcontext = {}
        redirect = redirect or "/my/builds"

        if request.httprequest.method == "POST" and database_name:
            res = self.is_available(database_name)
            if "domain" in res:
                try:
                    request.env["saas.db"].sudo().create({
                        "name": database_name,
                        "operator_id": request.env.ref("saas.local_operator").id,
                        "admin_user": request.env.user.id,
                    })
                    return werkzeug.utils.redirect(redirect)
                except Exception as e:
                    _logger.exception("Something went wrong, when creating draft build")
                    qcontext.update({
                        "error": str(e),
                    })
            else:
                qcontext.update({
                    "error": res["answer"],
                })

        qcontext.update(
            redirect=redirect,
            database_name=database_name or "",
        )
        return request.render("saas_apps_signup.portal_create_build", qcontext)
