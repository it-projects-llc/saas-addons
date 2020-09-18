# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
from odoo.addons.queue_job.exception import FailedJobError
import requests
import json


def jsonrpc(url, params, timeout=1200):
    data = {
        'jsonrpc': 2.0,
        'params': params
    }
    req = requests.post(url, json=data, timeout=timeout)
    req.raise_for_status()
    try:
        response = req.json()
    except ValueError:
        raise FailedJobError(req.text)

    error = response.get("error")
    if error:
        traceback = error.get("data", {}).get("debug")
        if type(traceback) is str:
            message = "\n".join((
                "=" * 10,
                "REMOTE INSTANCE TRACEBACK",
                "=" * 10,
                traceback
            ))
        else:
            message = json.dumps(error, indent=4, sort_keys=True)
        raise FailedJobError(message)

    return response


class SaasOperator(models.Model):

    _inherit = "saas.operator"

    type = fields.Selection(
        selection_add=[("remote", "Remote Instance")]
    )
    master_pwd = fields.Char("Master Password")

    def _create_db(self, template_db, db_name, demo, lang="en_US"):
        remote_ops = self.filtered(lambda op: op.type == "remote")
        for op in remote_ops:
            jsonrpc(op.global_url + "/saas_operator/create_db", {
                "master_pwd": op.master_pwd,
                "template_db": template_db,
                "db_name": db_name,
                "demo": demo,
                "lang": lang,
            })

        super(SaasOperator, self - remote_ops)._create_db(template_db, db_name, demo, lang)

    def _drop_db(self, db_name):
        remote_ops = self.filtered(lambda op: op.type == "remote")
        for op in remote_ops:
            jsonrpc(op.global_url + "/saas_operator/drop_db", {
                "master_pwd": op.master_pwd,
                "db_name": db_name,
            })

        super(SaasOperator, self - remote_ops)._drop_db(db_name)

    def _install_modules(self, db_name, modules):
        if self.type != "remote":
            return super(SaasOperator, self)._install_modules(db_name, modules)

        jsonrpc(self.global_url + "/saas_operator/install_modules", {
            "master_pwd": self.master_pwd,
            "db_name": db_name,
            "modules": modules,
        })

    def _post_init(self, db_name, template_post_init):
        if self.type != "remote":
            return super(SaasOperator, self)._post_init(db_name, template_post_init)

        jsonrpc(self.global_url + "/saas_operator/post_init", {
            "master_pwd": self.master_pwd,
            "db_name": db_name,
            "template_post_init": template_post_init,
        })

    def _build_execute_kw(self, db_name, model, method, args, kwargs):
        if self.type != "remote":
            return super(SaasOperator, self)._build_execute_kw(db_name, model, method, args, kwargs)

        response = jsonrpc(self.global_url + "/saas_operator/execute_kw", {
            "master_pwd": self.master_pwd,
            "db_name": db_name,
            "model": model,
            "method": method,
            "args": args,
            "kwargs": kwargs,
        })
        return response.get("result")
