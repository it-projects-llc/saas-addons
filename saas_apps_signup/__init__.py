# pylint: disable=absent-doc,js-empty-coverage
from . import controllers
from . import models


def post_init_hook(env):
    new_id = env.ref("saas_apps_signup.set_password_email").id
    env["ir.model.data"].search([("module", "=", "auth_signup"), ("name", "=", "set_password_email")]).res_id = new_id
