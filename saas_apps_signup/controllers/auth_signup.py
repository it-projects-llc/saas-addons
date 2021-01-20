# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import odoo
from odoo.http import request
from odoo.addons.auth_signup_verify_email.controllers.main import SignupVerifyEmail
import logging

from ..exceptions import OperatorNotAvailable

_logger = logging.getLogger(__name__)


class Main(SignupVerifyEmail):
    def get_auth_signup_qcontext(self):
        d = super(Main, self).get_auth_signup_qcontext()
        try_now_args = ("installing_modules", "max_users_limit", "period")

        if any([k in d for k in try_now_args]):
            # "Try now" is pressed
            try:
                assert d["period"] in ("year", "month")
                assert int(d["max_users_limit"]) > 0
                assert d.get("installing_modules") or d.get("saas_template_id")
                assert not (d.get("installing_modules") and d.get("saas_template_id"))
                assert not d.get("sale_order_id")  # making sure, that sale order is not used
            except KeyError as e:
                raise AssertionError("{} is not given".format(e))

        elif "sale_order_id" in d:
            # "Buy now" is pressed
            d["sale_order_id"] = int(d["sale_order_id"])
            assert all(map(lambda k: not d.get(k), try_now_args))  # making sure, that "Try now" args are not used

        if not d.get("operator_id"):
            if d.get("saas_template_id"):
                template = request.env["saas.template"].browse(int(d.get("saas_template_id")))
            else:
                template = request.env.ref("saas_apps.base_template")
            d["operator_id"] = template._random_ready_operator_id()

        d['langs'] = odoo.service.db.exp_list_lang()
        d['countries'] = odoo.service.db.exp_list_countries()
        return d

    def passwordless_signup(self):
        values = request.params
        qcontext = self.get_auth_signup_qcontext()

        database_name = values.get("database_name")
        if database_name:
            db_record = request.env['saas.db'].sudo().search([('name', '=', database_name)], limit=1)
            if db_record:
                qcontext["error"] = "Database %s already exist" % (database_name,)
                return request.render("auth_signup.signup", qcontext)

        try:
            return super(Main, self).passwordless_signup()
        except OperatorNotAvailable as e:
            qcontext["error"] = str(e)
            return request.render("auth_signup.signup", qcontext)
