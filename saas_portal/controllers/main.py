# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError


class Main(CustomerPortal):
    def _prepare_portal_layout_values(self):
        values = super(Main, self)._prepare_portal_layout_values()
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

        # archive groups - Default Group By 'create_date'
        # archive_groups = self._get_archive_groups('project.project', domain)
        # pager

        pager = portal_pager(
            url="/my/builds",
            url_args={"sortby": sortby},
            total=values["build_count"],
            page=page,
            step=self._items_per_page,
        )

        # content according to pager and archive selected
        builds = Build.search(
            domain, order=order, limit=self._items_per_page, offset=pager["offset"]
        )

        values.update(
            {
                "builds": builds,
                "page_name": "build",
                "default_url": "/my/builds",
                "pager": pager,
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
