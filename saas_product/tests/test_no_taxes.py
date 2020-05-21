# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License MIT (https://opensource.org/licenses/MIT).

from odoo.tests.common import HttpCase, tagged


@tagged("at_install", "post_install")
class TestNoTaxes(HttpCase):
    def test_no_taxes(self):
        product_template = self.env["product.template"].create(
            {"name": "Test SaaS product", "is_saas_product": True}
        )
        self.assertFalse(product_template.taxes_id)
        self.assertFalse(product_template.supplier_taxes_id)
