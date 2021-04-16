# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import functools
import logging

from odoo import SUPERUSER_ID, _, api, http, registry, sql_db, tools
from odoo.exceptions import AccessError
from odoo.http import route
from odoo.service import db
from odoo.service.model import execute

_logger = logging.getLogger(__name__)


# TODO: add decorator for ensuring master password and returning exception
def check_master_pwd(f):
    @functools.wraps(f)
    def wrap(*args, **kw):
        master_pwd = kw.pop("master_pwd", None)
        if not master_pwd:
            raise AccessError(_("master password (master_pwd) not given"))
        if not tools.config.verify_admin_password(master_pwd):
            raise AccessError(_("Incorrect master password or master password not set"))
        return f(*args, **kw)

    return wrap


class OperatorController(http.Controller):
    @route("/saas_operator/create_db", type="json", auth="none")
    @check_master_pwd
    def create_db(self, template_db, db_name, demo, lang="en_US"):
        # to avoid installing extra modules we need this condition
        if tools.config["init"]:
            tools.config["init"] = {}

        # we don't need tests in templates and builds
        test_enable = tools.config["test_enable"]
        if test_enable:
            tools.config["test_enable"] = {}

        try:
            if template_db:
                # TODO: does drop connection works ok?
                with sql_db.db_connect(template_db).cursor() as cr:
                    db._drop_conn(cr, template_db)
                db.exp_duplicate_database(template_db, db_name)
            else:
                db.exp_create_database(db_name, demo, lang)

        finally:
            if test_enable:
                tools.config["test_enable"] = test_enable

    @route("/saas_operator/drop_db", type="json", auth="none")
    @check_master_pwd
    def drop_db(self, db_name):
        db.exp_drop(db_name)

    @route("/saas_operator/install_modules", type="json", auth="none")
    @check_master_pwd
    def install_modules(self, db_name, modules):
        db = sql_db.db_connect(db_name)
        with api.Environment.manage(), db.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})

            module_ids = env["ir.module.module"].search(
                [("state", "=", "uninstalled")] + modules
            )
            module_ids.button_immediate_install()

            # Some magic to force reloading registry in other workers
            env.registry.registry_invalidated = True
            env.registry.signal_changes()

    @route("/saas_operator/post_init", type="json", auth="none")
    @check_master_pwd
    def post_init(self, db_name, template_post_init):
        db = sql_db.db_connect(db_name)
        registry(db_name).check_signaling()
        with api.Environment.manage(), db.cursor() as cr:
            env = api.Environment(cr, SUPERUSER_ID, {})
            action = env["ir.actions.server"].create(
                {
                    "name": "Local Code Eval",
                    "state": "code",
                    "model_id": 1,
                    "code": template_post_init,
                }
            )
            action.run()

    @route("/saas_operator/execute_kw", type="json", auth="none")
    @check_master_pwd
    def execute_kw(self, db_name, model, method, args, kwargs):
        return execute(db_name, SUPERUSER_ID, model, method, *args, **kwargs)
