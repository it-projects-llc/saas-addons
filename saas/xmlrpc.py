# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
# Based on https://github.com/it-projects-llc/odoo-saas-tools/blob/11.0/saas.py
import logging
import xmlrpc.client

_logger = logging.getLogger(__name__)


def rpc_auth(url, db_name, admin_username='admin', admin_password='admin'):
    # Authenticate
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    admin_uid = common.authenticate(db_name, admin_username, admin_password, {})
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    if not admin_uid:
        _logger.debug('Authentication failed %s', ((url, db_name, admin_username, admin_password),))
        raise Exception('Authentication to %s is failed' % url)
    return db_name, models, admin_uid, admin_password


def rpc_execute_kw(auth, model, method, rpc_args=None, rpc_kwargs=None):
    rpc_args = rpc_args or []
    rpc_kwargs = rpc_kwargs or {}
    db_name, models, admin_uid, admin_password = auth
    _logger.debug('RPC Execute: env["%s"].%s(*%s, **%s)', model, method, rpc_args, rpc_kwargs)
    return models.execute_kw(db_name, admin_uid, admin_password,
                             model, method, rpc_args, rpc_kwargs)


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
