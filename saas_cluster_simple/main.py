# Copyright 2018 Ivan Yelizariev <https://github.com/yelizariev>
# Copyright 2019 Denis Mudarisov <https://github.com/trojikman>
# Copyright 2020-2021 Eugene Molotov <https://github.com/em230418>
from collections.abc import Mapping
from contextlib import contextmanager
from datetime import datetime
import logging
from itertools import combinations
import os
import re
import string
import threading

from odoo import SUPERUSER_ID, api, sql_db, tools
from odoo.exceptions import UserError
from odoo.http import request_var
from odoo.models import BaseModel
from odoo.modules import db
from odoo.modules import module as odoo_module
from odoo.modules.registry import Registry
from odoo.service.model import _traverse_containers
from odoo.tools import lazy

from odoo.addons.host2db import host2db_config

_logger = logging.getLogger(__name__)
BACKUP_DIR = tools.config["data_dir"] + "/backups"
if not os.path.exists(BACKUP_DIR):
    os.mkdir(BACKUP_DIR)

# Captured at import time, before the test framework patches Registry.new.
_REAL_REGISTRY_NEW = Registry.new


def full_backup_path(backup_name):
    return BACKUP_DIR + "/" + backup_name


__all__ = [
    "create_db",
    "drop_db",
    "install_modules",
    "post_init",
    "map_domain",
    "unmap_domain",
    "execute_kw",
    "create_backup",
    "signal_changes",
]


@contextmanager
def turn_off_tests():
    """Lift Odoo 20's test guards around operations on other databases.

    While a test runs, Registry.new is patched to raise and
    ir_module._button_immediate_function refuses to work when
    odoo.modules.module.current_test is set. Neither applies to what a SaaS
    operator legitimately does here: create and provision template/build
    databases, which are separate databases and separate cursors.
    """
    test_enable = tools.config["test_enable"]
    current_test = odoo_module.current_test
    registry_new = Registry.new
    tools.config["test_enable"] = {}
    odoo_module.current_test = None
    Registry.new = _REAL_REGISTRY_NEW
    try:
        yield
    finally:
        Registry.new = registry_new
        odoo_module.current_test = current_test
        tools.config["test_enable"] = test_enable
        if test_enable:
            # Odoo's shutdown summary walks every loaded registry and expects a
            # test report on it, but the registries built above have none,
            # because they were loaded with tests off.
            from odoo.tests.result import OdooTestResult

            for registry in list(Registry.registries.values()):
                if registry._assertion_report is None:
                    registry._assertion_report = OdooTestResult()


@contextmanager
def build_cursor(db_name):
    """Cursor on a template/build database, whose registry is loaded on demand.

    The guards stay lifted while the cursor closes: committing a transaction
    that invalidated the registry rebuilds it right there.
    """
    with turn_off_tests():
        registry = Registry(db_name)
        with registry.cursor() as cr:
            yield cr


def create_db(template_db, db_name, demo, lang="en_US", admin_password="admin", **kw):
    # to avoid installing extra modules we need this condition
    if tools.config["init"]:
        tools.config["init"] = {}

    with turn_off_tests():
        if template_db:
            db.duplicate(template_db, db_name)
        else:
            db.create(
                db_name,
                demo=bool(demo),
                user_password=admin_password,
                lang=lang,
            )


def drop_db(db_name):
    # Odoo 20 replaced db.exp_drop (which ignored missing databases) by
    # db.drop, that raises.
    if db.exist(db_name):
        db.drop(db_name)


def install_modules(db_name, modules):
    conn = sql_db.db_connect(db_name)
    # The guards stay lifted while the cursor closes: committing a transaction
    # that changed the registry builds the new registry right there.
    with turn_off_tests(), conn.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})

        # Unbind the current request.
        #
        # Odoo tries to use its values in translation system, which may eventually
        # change currentThread().dbname to saas master value.
        request_token = request_var.set(None)

        # We need to have fresh module list before installing new ones
        env["ir.module.module"].update_list()

        module_ids = env["ir.module.module"].search(
            [("state", "=", "uninstalled")] + modules
        )
        module_ids.button_immediate_install()

        # Some magic to force reloading registry in other workers: the commit
        # performed when leaving this cursor signals the registry change.
        env.transaction.will_change_registry()

        # return request back
        request_var.reset(request_token)


def post_init(db_name, template_post_init):
    conn = sql_db.db_connect(db_name)
    with turn_off_tests(), conn.cursor() as cr:
        Registry(db_name)
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


def map_domain(domain, db_name):
    host2db_config.assign_host_to_db(domain, db_name)


def unmap_domain(domain):
    host2db_config.unassign_host(domain)


def execute_kw(db_name, model, method, args, kwargs):
    return execute(db_name, SUPERUSER_ID, model, method, *args, **kwargs)


def create_backup(db_name):
    backup_name = "{}_{}.zip".format(db_name, datetime.now().strftime("%Y-%m-%d_%H_%M_%S"))
    with open(full_backup_path(backup_name), "wb") as f:
        db.dump(db_name, f, backup_format="zip")
    return {
        "name": backup_name,
    }


def remove_backup(backup_name):
    os.unlink(full_backup_path(backup_name))


def _get_new_database_name(old_db_name):
    for suffix_length in (1, 2, 3):  # should be enough for one day
        for combo in combinations(string.ascii_lowercase, suffix_length):
            db_name = old_db_name + "_" + datetime.now().strftime("%Y-%m-%d") + "".join(combo)
            if not db.exist(db_name):
                return db_name


def deploy_backup(backup_name):
    original_db_name = re.match(r"([^_]+)_.*\.zip", backup_name).group(1)
    db_name = _get_new_database_name(original_db_name)
    if not db_name:
        raise Exception("Cannot calculate database name for deploying backup %s" % (backup_name,))

    db.restore(db_name, full_backup_path(backup_name), copy=True)
    return {
        "db_name": db_name,
    }


def signal_changes(db_name):
    with build_cursor(db_name) as cr:
        # Odoo 20: cursors get their Transaction only via an Environment, and
        # registry signaling moved from Registry to Transaction.
        api.Environment(cr, SUPERUSER_ID, {}).transaction.will_change_registry()


# Modified version of odoo.service.model.execute_cr
# Removes checking private methods since
# cluster requires all methods to be executed
# It is expected, that master password check will protect
# from unauthorized usage
def execute(db, uid, obj, method, *args, **kw):
    threading.current_thread().dbname = db
    with build_cursor(db) as cr:
        env = api.Environment(cr, uid, {})
        env.transaction.default_env = env
        recs = env.get(obj)
        if recs is None:
            raise UserError("Object %s doesn't exist" % obj)

        model_method = getattr(type(recs), method)
        context = kw.pop("context", None) or {}
        if getattr(model_method, "_api_model", False):
            # @api.model methods receive no ids
            targets = recs
        else:
            ids, args = args[0], args[1:]
            targets = recs.browse(ids)

        res = model_method(targets.with_context(context), *args, **kw)
        if method == "create":
            res = res.id if isinstance(args[0], Mapping) else res.ids
        elif isinstance(res, BaseModel):
            res = res.ids
        # evaluate lazy values before the cursor is closed
        for x in _traverse_containers(res, lazy):
            x._value
        if res is None:
            _logger.info('The method %s of the object %s can not return `None` !', method, obj)
        return res
