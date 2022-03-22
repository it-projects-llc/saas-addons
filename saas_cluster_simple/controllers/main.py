# pylint: disable=translation-required
import functools
import logging

from odoo.exceptions import AccessError
from odoo.http import route, Controller
from odoo import tools

from .. import main as cluster


_logger = logging.getLogger(__name__)


def check_master_pwd(f):
    @functools.wraps(f)
    def wrap(*args, **kw):
        master_pwd = kw.pop("master_pwd", None)
        if not master_pwd:
            raise AccessError("Master password (master_pwd) not given")
        if not tools.config["admin_passwd"]:
            raise AccessError("Master password not set")
        if not tools.config.verify_admin_password(master_pwd):
            raise AccessError("Incorrect master password")
        return f(*args, **kw)

    return wrap


class OperatorController(Controller):
    @route("/saas_operator/<string:method_name>", type="json", auth="none")
    @check_master_pwd
    def run_cluster_method(self, method_name, **kw):
        method = getattr(cluster, method_name)
        return method(**kw)
