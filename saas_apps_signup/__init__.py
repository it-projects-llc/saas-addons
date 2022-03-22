# pylint: disable=absent-doc,js-empty-coverage
from . import controllers
from . import models
from . import tests

from odoo.api import Environment, SUPERUSER_ID

def post_init_hook(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    new_id = env.ref("saas_apps_signup.set_password_email").id
    env["ir.model.data"].search([("module", "=", "auth_signup"), ("name", "=", "set_password_email")]).res_id = new_id
