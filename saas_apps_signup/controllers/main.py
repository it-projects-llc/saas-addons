# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.http import request, route, Controller
import logging

import werkzeug
from werkzeug.urls import Href, url_encode
from odoo import SUPERUSER_ID
from odoo.addons.http_routing.models.ir_http import slugify
from odoo.addons.saas_portal.controllers.portal import CustomerPortal

_logger = logging.getLogger(__name__)


class Main(Controller):
    @route("/saas_apps_signup/is_database_slot_available", auth="public", type="json")
    def is_available(self, database_name, operator_id, **kw):
        database_name = database_name.lower().strip()
        if not database_name:
            return {"answer": "Empty database name"}

        if database_name != slugify(database_name):
            return {"answer": "Invalid database name"}

        is_free_slot = not request.env["saas.db"].sudo().search([("name", "=", database_name)])
        if is_free_slot:
            return {"domain": request.env["saas.operator"].sudo().browse(int(operator_id)).db_url_template.format(db_name=database_name)}
        else:
            return {"answer": "Database already exists"}

    @route("/my/builds/create", auth="user", type="http", website=True)
    def portal_build_selector(self, database_name=None, redirect=None, operator_id=None, **kw):
        qcontext = {}
        redirect = redirect or "/my/builds"

        if request.httprequest.method == "POST" and database_name and operator_id:
            operator_id = int(operator_id)
            qcontext.update({
                "operator_id": operator_id,
            })
            res = self.is_available(database_name, operator_id)
            if "domain" in res:
                try:
                    request.env["saas.db"].sudo().create({
                        "name": database_name,
                        "operator_id": int(operator_id),
                        "admin_user": request.env.user.id,
                    })
                    return request.redirect(redirect)
                except Exception as e:
                    _logger.exception("Something went wrong, when creating draft build")
                    qcontext.update({
                        "error": str(e),
                    })
            else:
                qcontext.update({
                    "error": res["answer"],
                })
        else:
            try:
                qcontext.update({
                    "operator_id": request.env.ref("saas_apps.base_template")._random_ready_operator_id()
                })
            except AssertionError as e:
                qcontext.update({
                    "error": str(e),
                })

        qcontext.update(
            query=url_encode({
                "redirect": redirect,
            }),
            database_name=database_name or "",
        )
        return request.render("saas_apps_signup.portal_create_build", qcontext)

    @route("/saas_apps_signup/make_database_for_trial", auth="public", type="http", website=True)
    def make_database_for_trial(self, period, max_users_limit, database_name=None, installing_modules=None, saas_template_id=None, **kw):
        params = {
            "max_users_limit": max_users_limit,
            "period": period,
            "installing_modules": installing_modules or "",
            "saas_template_id": saas_template_id or "",
        }

        assert not(saas_template_id and installing_modules), "Both saas_template_id and installing_modules given"

        if request.env.user == request.env.ref("base.public_user"):
            return werkzeug.utils.redirect(Href("/web/signup")(params))

        build = request.env["saas.db"].search([
            ("type", "=", "build"),
            ("state", "=", "draft"),
            ("admin_user", "=", request.env.user.id),
        ], order='id DESC', limit=1)
        if not build:
            return request.redirect(Href("/my/builds/create")({
                "redirect": request.httprequest.full_path
            }))

        request.env["contract.contract"].with_user(SUPERUSER_ID)._create_saas_contract_for_trial(
            build, max_users_limit, period,
            installing_modules=(installing_modules or "").split(","),
            saas_template_id=saas_template_id
        )

        return request.redirect("/my/build/{}".format(build.id))


class CustomerPortal(CustomerPortal):
    @route(["/my/build/<int:build_id>/renew_subscription"], type="http", auth="public", website=True)
    def portal_my_build_renew_subscription(self, build_id=None, access_token=None, **kw):
        # build_sudo = self._document_check_access("saas.db", build_id, access_token)  # does not work, 'cos of ir.model.access error
        build_sudo = request.env["saas.db"].sudo().browse(build_id)

        assert build_sudo.contract_id, "Following build does not have contract"

        contract = build_sudo.contract_id

        invoices = contract._get_related_invoices().filtered(lambda invoice: (invoice.state, invoice.payment_state) == ("posted", "not_paid"))
        if not invoices:
            invoice = contract.recurring_create_invoice()
            invoice.action_post()
        else:
            invoice = invoices[0]
        return request.redirect(invoice.get_portal_url())
