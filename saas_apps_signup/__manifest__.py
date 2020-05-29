# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": """SaaS: apps signup""",
    "summary": """SHORT DESC""",
    "category": "Hidden",
    # "live_test_url": "http://apps.it-projects.info/shop/product/DEMO-URL?version=12.0",
    "images": [],
    "version": "12.0.1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Eugene Molotov",
    "support": "apps@it-projects.info",
    "website": "https://apps.odoo.com/apps/modules/12.0/saas_apps_signup/",
    "license": "AGPL-3",
    # "price": 9.00,
    # "currency": "EUR",

    "depends": [
        "auth_signup_verify_email", "saas_apps", "saas_portal", "saas_contract", "base_automation",
    ],
    "external_dependencies": {"python": ["python-slugify"], "bin": []},
    "data": [
        'data/auth_signup_data.xml',
        'data/base_automation.xml',
        'views/auth_signup.xml',
        'views/assets.xml',
        'views/saas_db.xml',
        'views/contract.xml',
    ],
    "demo": [
    ],
    "qweb": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": "post_init_hook",
    "uninstall_hook": None,

    "auto_install": False,
    "installable": True,

    # "demo_title": "SaaS: apps signup",
    # "demo_addons": [
    # ],
    # "demo_addons_hidden": [
    # ],
    # "demo_url": "DEMO-URL",
    # "demo_summary": "SHORT DESC",
    # "demo_images": [
    #    "images/MAIN_IMAGE",
    # ]
}
