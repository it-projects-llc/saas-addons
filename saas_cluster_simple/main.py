# Copyright 2018 Ivan Yelizariev <https://github.com/yelizariev>
# Copyright 2019 Denis Mudarisov <https://github.com/trojikman>
# Copyright 2020-2021 Eugene Molotov <https://github.com/em230418>
from contextlib import contextmanager, closing
from datetime import datetime
import logging
from itertools import combinations
import os
import re
import string

from odoo import SUPERUSER_ID, api, registry, sql_db, tools
from odoo.service import db
from odoo.service.model import execute
from odoo.http import _request_stack

from odoo.addons.host2db import host2db_config

_logger = logging.getLogger(__name__)
BACKUP_DIR = tools.config["data_dir"] + "/backups"
if not os.path.exists(BACKUP_DIR):
    os.mkdir(BACKUP_DIR)


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
    "create_backup"
]


@contextmanager
def turn_off_tests():
    test_enable = tools.config["test_enable"]
    if test_enable:
        tools.config["test_enable"] = {}

    yield

    if test_enable:
        tools.config["test_enable"] = test_enable


def create_db(template_db, db_name, demo, lang="en_US", **kw):
    # to avoid installing extra modules we need this condition
    if tools.config["init"]:
        tools.config["init"] = {}

    with turn_off_tests():
        if template_db:
            with closing(sql_db.db_connect(template_db).cursor()) as cr:
                db._drop_conn(cr, template_db)
            db.exp_duplicate_database(template_db, db_name)
        else:
            db.exp_create_database(db_name, demo, lang)


def drop_db(db_name):
    db.exp_drop(db_name)


def install_modules(db_name, modules):
    conn = sql_db.db_connect(db_name)
    with api.Environment.manage(), conn.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})

        # Set odoo.http.request to None.
        #
        # Odoo tries to use its values in translation system, which may eventually
        # change currentThread().dbname to saas master value.
        _request_stack.push(None)

        # We need to have fresh module list before installing new ones
        env["ir.module.module"].update_list()

        module_ids = env["ir.module.module"].search(
            [("state", "=", "uninstalled")] + modules
        )
        with turn_off_tests():
            module_ids.button_immediate_install()

        # Some magic to force reloading registry in other workers
        env.registry.registry_invalidated = True
        env.registry.signal_changes()

        # return request back
        _request_stack.pop()


def post_init(db_name, template_post_init):
    conn = sql_db.db_connect(db_name)
    registry(db_name).check_signaling()
    with api.Environment.manage(), conn.cursor() as cr:
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
        db.dump_db(db_name, f)
    return {
        "name": backup_name,
    }


def remove_backup(backup_name):
    os.unlink(full_backup_path(backup_name))


def _get_new_database_name(old_db_name):
    for suffix_length in (1, 2, 3):  # should be enough for one day
        for combo in combinations(string.ascii_lowercase, suffix_length):
            db_name = old_db_name + "_" + datetime.now().strftime("%Y-%m-%d") + "".join(combo)
            if not db.exp_db_exist(db_name):
                return db_name


def deploy_backup(backup_name):
    original_db_name = re.match(r"([^_]+)_.*\.zip", backup_name).group(1)
    db_name = _get_new_database_name(original_db_name)
    if not db_name:
        raise Exception("Cannot calculate database name for deploying backup %s" % (backup_name,))

    db.restore_db(db_name, full_backup_path(backup_name), copy=True)
    return {
        "db_name": db_name,
    }
