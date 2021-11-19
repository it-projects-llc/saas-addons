# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import json

import requests

from odoo import fields, models


def jsonrpc(url, params, timeout=1200):
    data = {"jsonrpc": 2.0, "params": params}
    req = requests.post(url, json=data, timeout=timeout)
    req.raise_for_status()
    try:
        response = req.json()
    except ValueError:
        raise Exception(req.text)

    error = response.get("error")
    if error:
        traceback = error.get("data", {}).get("debug")
        if type(traceback) is str:
            message = "\n".join(
                ("=" * 10, "REMOTE INSTANCE TRACEBACK", "=" * 10, traceback)
            )
        else:
            message = json.dumps(error, indent=4, sort_keys=True)
        raise Exception(message)

    return response


class SaasOperator(models.Model):

    _inherit = "saas.operator"

    type = fields.Selection(selection_add=[("remote", "Remote Instance")])
    remote_instance_url = fields.Char("Instance URL")
    remote_master_pwd = fields.Char("Master Password")

    def _create_db(self, template_db, db_name, demo, lang="en_US"):
        remote_ops = self.filtered(lambda op: op.type == "remote")
        for op in remote_ops:
            jsonrpc(
                op.remote_instance_url + "/saas_operator/create_db",
                {
                    "master_pwd": op.remote_master_pwd,
                    "template_db": template_db,
                    "db_name": db_name,
                    "demo": demo,
                    "lang": lang,
                },
            )

        super(SaasOperator, self - remote_ops)._create_db(
            template_db, db_name, demo, lang
        )

    def _drop_db(self, db_name):
        remote_ops = self.filtered(lambda op: op.type == "remote")
        for op in remote_ops:
            jsonrpc(
                op.remote_instance_url + "/saas_operator/drop_db",
                {"master_pwd": op.remote_master_pwd, "db_name": db_name},
            )

        super(SaasOperator, self - remote_ops)._drop_db(db_name)

    def _install_modules(self, db_name, modules):
        if self.type != "remote":
            return super(SaasOperator, self)._install_modules(db_name, modules)

        jsonrpc(
            self.remote_instance_url + "/saas_operator/install_modules",
            {
                "master_pwd": self.remote_master_pwd,
                "db_name": db_name,
                "modules": modules,
            },
        )

    def _post_init(self, db_name, template_post_init):
        if self.type != "remote":
            return super(SaasOperator, self)._post_init(db_name, template_post_init)

        jsonrpc(
            self.remote_instance_url + "/saas_operator/post_init",
            {
                "master_pwd": self.remote_master_pwd,
                "db_name": db_name,
                "template_post_init": template_post_init,
            },
        )

    def _build_execute_kw(self, db_name, model, method, args, kwargs):
        if self.type != "remote":
            return super(SaasOperator, self)._build_execute_kw(
                db_name, model, method, args, kwargs
            )

        response = jsonrpc(
            self.remote_instance_url + "/saas_operator/execute_kw",
            {
                "master_pwd": self.remote_master_pwd,
                "db_name": db_name,
                "model": model,
                "method": method,
                "args": args,
                "kwargs": kwargs,
            },
        )
        return response.get("result")

    def _map_domain(self, domain, db_name):
        if self.type != "remote":
            return super(SaasOperator, self)._map_domain(domain, db_name)

        response = jsonrpc(
            self.remote_instance_url + "/saas_operator/map_domain",
            {
                "master_pwd": self.remote_master_pwd,
                "domain": domain,
                "db_name": db_name,
            },
        )
        return response.get("result")

    def _unmap_domain(self, domain):
        if self.type != "remote":
            return super(SaasOperator, self)._unmap_domain(domain)

        response = jsonrpc(
            self.remote_instance_url + "/saas_operator/unmap_domain",
            {"master_pwd": self.remote_master_pwd, "domain": domain},
        )
        return response.get("result")

    def _create_backup_internal(self, db_name):
        if self.type != "remote":
            return super(SaasOperator, self)._create_backup_internal(db_name)

        response = jsonrpc(
            self.remote_instance_url + "/saas_operator/create_backup",
            {"master_pwd": self.remote_master_pwd, "db_name": db_name},
        )
        return response.get("result")

    def _deploy_backup_internal(self, backup_name):
        if self.type != "remote":
            return super(SaasOperator, self)._deploy_backup_internal(backup_name)

        response = jsonrpc(
            self.remote_instance_url + "/saas_operator/deploy_backup",
            {"master_pwd": self.remote_master_pwd, "backup_name": backup_name},
        )
        return response.get("result")
