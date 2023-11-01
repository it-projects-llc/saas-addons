from odoo.tests.common import tagged, TransactionCase


@tagged('post_install', 'at_install')
class TestMain(TransactionCase):
    def test_action_make_applist_from_local_instance(self):
        self.env['saas.app'].action_make_applist_from_local_instance()

        website_hr_recruitment = self.env['saas.app'].search([('name', '=', 'website_hr_recruitment')])

        self.assertItemsEqual(
            website_hr_recruitment.dependencies_str().split(","),
            ["hr_recruitment", "hr", "mail", "calendar", "website"]
        )
        self.assertItemsEqual(
            website_hr_recruitment.dependency_ids.mapped("name"),
            ["hr_recruitment", "mail", "website"],
        )

    def test_paid_app(self):
        app = self.env["saas.app"].create({
            "name": "paid_app",
            "shortdesc": "Paid app short desc",
            "month_price": 1,
            "year_price": 2,
        })

        self.assertEqual(app.month_product_id.lst_price, 1)
        self.assertEqual(app.year_product_id.lst_price, 2)
