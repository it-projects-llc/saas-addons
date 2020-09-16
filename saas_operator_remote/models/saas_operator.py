# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
import requests


def jsonrpc(url, params, timeout=1200):
    data = {
        'jsonrpc': 2.0,
        'params': params
    }
    req = requests.post(url, json=data, timeout=timeout)
    print(req.content)
    req.raise_for_status()
    return req.json()


class SaasOperator(models.Model):

    _inherit = "saas.operator"

    type = fields.Selection(
        selection_add=[("remote", "Remote")]
    )
    master_pwd = fields.Char("Master Password")

    def _create_db(self, template_db, db_name, demo, lang="en_US"):
        remote_ops = self.filtered(lambda op: op.type == "remote")
        for op in remote_ops:
            result = jsonrpc(op.global_url + "/saas_operator/create_db", {
                "master_pwd": op.master_pwd,
                "template_db": template_db,
                "db_name": db_name,
                "demo": demo,
                "lang": lang,
            })
            # TODO: get exceptions
            error = result.get("error")
            if error:
                print("FUCK")
                import wdb; wdb.set_trace()

        super(SaasOperator, self - remote_ops)._create_db(template_db, db_name, demo, lang)

    def _drop_db(self, db_name):
        remote_ops = self.filtered(lambda op: op.type == "remote")
        for op in remote_ops:
            result = jsonrpc(op.global_url + "/saas_operator/drop_db", {
                "master_pwd": op.master_pwd,
                "db_name": db_name,
            })
            # TODO: get exceptions
            error = result.get("error")
            if error:
                print("FUCK")
                import wdb; wdb.set_trace()

        super(SaasOperator, self - remote_ops)._drop_db(db_name)

    def _install_modules(self, db_name, modules):
        if self.type != "remote":
            return super(SaasOperator, self)._install_modules(db_name, modules)

        result = jsonrpc(self.global_url + "/saas_operator/install_modules", {
            "master_pwd": self.master_pwd,
            "db_name": db_name,
            "modules": modules,
        })
        # TODO: get exceptions
        error = result.get("error")
        if error:
            print("FUCK")
            import wdb; wdb.set_trace()

    def _post_init(self, db_name, template_post_init):
        if self.type != "remote":
            return super(SaasOperator, self)._post_init(db_name, template_post_init)

        result = jsonrpc(self.global_url + "/saas_operator/post_init", {
            "master_pwd": self.master_pwd,
            "db_name": db_name,
            "template_post_init": template_post_init,
        })
        # TODO: get exceptions
        error = result.get("error")
        if error:
            print("FUCK")
            import wdb; wdb.set_trace()
