# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License MIT (https://opensource.org/licenses/MIT).

{
    "name": """SaaS: Contracts""",
    "summary": """This module manages contracts with SaaS clients""",
    "category": "Sales",
    # "live_test_url": "http://apps.it-projects.info/shop/product/DEMO-URL?version=14.0",
    "images": [],
    "version": "14.0.1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Eugene Molotov",
    "support": "apps@it-projects.info",
    "website": "https://apps.odoo.com/apps/modules/14.0/saas_contract/",
    "license": "Other OSI approved licence",  # MIT
    # "price": 9.00,
    # "currency": "EUR",

    "depends": [
        "saas_expiration", "saas_limit_max_users", "contract", "saas_product", "l10n_generic_coa",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "data/ir_cron.xml",
        "views/contract.xml",
        "views/saas_db.xml",
    ],
    "demo": [
    ],
    "qweb": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,

    "auto_install": False,
    "installable": True,

    # "demo_title": "SaaS: Contracts",
    # "demo_addons": [
    # ],
    # "demo_addons_hidden": [
    # ],
    # "demo_url": "DEMO-URL",
    # "demo_summary": "This module manages contracts with SaaS clients",
    # "demo_images": [
    #    "images/MAIN_IMAGE",
    # ]
}
