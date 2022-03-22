from odoo.tests import HttpCase
from odoo.addons.http_routing.models.ir_http import slugify
from odoo.addons.saas.tests.common_saas_test import Common

DB_PREFIX = "saas_domain_names_test_"
DB_TEMPLATE_NAME = DB_PREFIX + "template"
DB_NAME = slugify(DB_PREFIX + "db")


class TestMain(HttpCase, Common):
    def get_operator(self):
        return self.env.ref("saas.local_operator")

    def get_domain_to_test(self):
        return "test1.localhost"

    def get_operator_origin(self, operator):
        return operator.global_url

    def test_domain_workflow(self):
        self.drop_dbs([DB_TEMPLATE_NAME, DB_NAME])

        env = self.env(context=dict(self.env.context, test_queue_job_no_delay=True))
        operator = self.get_operator()

        # create template and template operator
        template = env["saas.template"].create(
            {"template_module_ids": [(0, 0, {"name": "test_saas_build"})]}
        )

        template_operator = env["saas.template.operator"].create(
            {
                "operator_id": operator.id,
                "template_id": template.id,
                "operator_db_name": DB_TEMPLATE_NAME,
            }
        )

        # deploy template database
        template_operator._prepare_template()

        # create build from template
        db = template_operator.create_db({}, DB_NAME)

        domain_name = self.get_domain_to_test()

        # for any case - unmap domain from operator
        # that happens after running previous test
        operator.unmap_domain(domain_name)

        # create domain record
        dn = env["saas.domain.name"].create(
            {"name": domain_name, "operator_id": operator.id}
        )

        # we need operator's origin to make requests to
        operator_origin = self.get_operator_origin(operator)

        # make sure, that before setting database it is not assigned to build
        response = self.url_open(
            "{}/test_saas_build/get_db_name".format(operator_origin),
            headers={"Host": domain_name},
        )
        self.assertEqual(response.status_code, 404)

        # assign domain name to build
        db.write({"domain_name_id": dn.id})

        # make sure, you can access to build using assigned domain name
        response = self.url_open(
            "{}/test_saas_build/get_db_name".format(operator_origin),
            headers={"Host": domain_name},
        )
        self.assertEqual(response.text, DB_NAME)

        # TODO: unassign domain name using build
        # TODO: delete dn record and check
