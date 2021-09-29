from odoo.addons.saas_domain_names.tests.test_main import TestMain as TestMainBase


class TestMain(TestMainBase):

    def get_operator(self):
        return self.env.ref("test_remote_saas.remote_operator")

    def get_domain_to_test(self):
        return "test2.remote"

    def get_operator_origin(self, operator):
        return operator.remote_instance_url
