# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
# Based on https://github.com/it-projects-llc/odoo-saas-tools/blob/11.0/saas.py
import logging
import requests

_logger = logging.getLogger(__name__)


class SessionRPC:
    """Keep the utility's execute_kw interface on Odoo 20 session RPC."""
    def __init__(self, url):
        self.url = url.rstrip("/")
        self.session = requests.Session()

    def request(self, path, params):
        response = self.session.post(self.url + path, json={
            "jsonrpc": "2.0", "params": params,
        }, timeout=1200)
        response.raise_for_status()
        payload = response.json()
        if payload.get("error"):
            error = payload["error"]
            raise RuntimeError(error.get("data", {}).get("message") or error.get("message", "RPC failed"))
        return payload.get("result")

    def execute_kw(self, db_name, uid, password, model, method, args, kwargs):
        return self.request("/web/dataset/call_kw", {
            "model": model, "method": method, "args": args, "kwargs": kwargs,
        })


def rpc_auth(url, db_name, admin_username="admin", admin_password="admin"):
    models = SessionRPC(url)
    try:
        result = models.request("/web/session/authenticate", {
            "db": db_name, "login": admin_username, "password": admin_password,
        })
        if not result or not result.get("uid"):
            raise RuntimeError("Authentication failed")
    except Exception:
        models.session.close()
        raise
    return db_name, models, result["uid"], admin_password


def rpc_execute_kw(auth, model, method, rpc_args=None, rpc_kwargs=None):
    db_name, models, admin_uid, admin_password = auth
    _logger.debug("RPC Execute: %s.%s", model, method)
    return models.execute_kw(db_name, admin_uid, admin_password, model, method, rpc_args or [], rpc_kwargs or {})


def rpc_install_modules(auth, domain):
    domain = [('state', '=', 'uninstalled')] + domain
    module_ids = rpc_execute_kw(auth, 'ir.module.module', 'search', [domain])
    rpc_execute_kw(auth, 'ir.module.module', 'button_immediate_install', [module_ids])


def rpc_code_eval(auth, code, name='RPC Code Eval'):
    # it's not really important which model to use
    domain = [('model', '=', 'res.users')]
    model_id = rpc_execute_kw(auth, 'ir.model', 'search', [domain])[0]

    vals = {
        'name': name,
        'state': 'code',
        'code': code,
        'model_id': model_id,
    }
    action_ids = rpc_execute_kw(auth, 'ir.actions.server', 'create', [vals])
    rpc_execute_kw(auth, 'ir.actions.server', 'run', [action_ids])
