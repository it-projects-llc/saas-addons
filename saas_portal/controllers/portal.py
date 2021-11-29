from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError


class CustomerPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if "build_count" in counters:
            values["build_count"] = request.env["saas.db"].search_count([
                ("type", "=", "build"),
            ])
        return values

    @http.route(
        ["/my/builds", "/my/builds/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def portal_my_builds(self, page=1, sortby=None, **kw):
        values = self._prepare_portal_layout_values()
        Build = request.env["saas.db"]
        domain = [("type", "=", "build")]

        searchbar_sortings = {
            "name": {"label": _("Name"), "order": "name"},
        }
        if not sortby:
            sortby = "name"
        order = searchbar_sortings[sortby]["order"]

        # content according to pager and archive selected
        builds = Build.search(
            domain + [("is_temporary", "=", False)], order=order
        )

        values.update(
            {
                "builds": builds,
                "temporary_builds": Build.search(domain + [("is_temporary", "=", True)]),
                "page_name": "build",
                "default_url": "/my/builds",
                "searchbar_sortings": searchbar_sortings,
                "sortby": sortby,
            }
        )
        return request.render("saas_portal.portal_my_builds", values)

    @http.route(["/my/build/<int:build_id>"], type="http", auth="user", website=True)
    def portal_my_build(self, build_id=None, access_token=None, **kw):
        try:
            build_sudo = self._document_check_access("saas.db", build_id, access_token)
        except (AccessError, MissingError):
            return request.redirect("/my")

        values = {
            "page_name": "build",
            "build": build_sudo,
        }
        values = self._get_page_view_values(
            build_sudo, access_token, values, None, False, **kw
        )
        return request.render("saas_portal.portal_my_build", values)
