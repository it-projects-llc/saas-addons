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
        if any([k in d for k in ("installing_modules", "max_users_limit", "period")]):
            try:
                assert d["period"] in ("annually", "monthly")
                assert int(d["max_users_limit"]) > 0
                assert d["installing_modules"]
            except KeyError as e:
                raise AssertionError("{} is not given".format(e))
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
                qcontext["error"] = "Database %s already exist" % (db_record,)
                return request.render("auth_signup.signup", qcontext)

        try:
            return super(Main, self).passwordless_signup()
        except OperatorNotAvailable as e:
            qcontext["error"] = str(e)
            return request.render("auth_signup.signup", qcontext)
