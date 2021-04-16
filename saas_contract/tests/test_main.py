# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import base64
import unittest

from odoo.tests.common import TransactionCase, tagged


@tagged("at_install", "post_install")
class TestMain(TransactionCase):
    def test_deny_to_add_contract_lines_with_empty_gap(self):
        build = self.env["saas.db"].create({
            "name": "test_db",
            "operator_id": self.env.ref("saas.local_operator"),
        })

        saas_product_tmpl = self.env["product.template"].create({
            "name": "test saas product",
            "is_saas_product": True,
            "price": 100,
        })

        saas_product = saas_product_tmpl.product_variant_id

        self.env["contract.contract"].create({
            "name": "test_db contract",
            "build_id": build.id,
            "contract_line_ids": [(0, 0, ({
                "name": saas_product.name,
                "product_id": saas_product.id,
                "quantity": 1,
                "price": saas_product.lst_price,
            })
        })
