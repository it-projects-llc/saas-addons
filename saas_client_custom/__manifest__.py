# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License MIT (https://opensource.org/licenses/MIT).

{
    "name": """SaaS: Client (Hesham Edition)""",
    "summary": """Custom client module for SaaS""",
    "category": "Hidden",
    # "live_test_url": "http://apps.it-projects.info/shop/product/DEMO-URL?version=13.0",
    "images": [],
    "version": "13.0.1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Eugene Molotov",
    "support": "apps@it-projects.info",
    "website": "https://apps.odoo.com/apps/modules/13.0/saas_client_custom/",
    "license": "Other OSI approved licence",  # MIT
    # "price": 9.00,
    # "currency": "EUR",

    "depends": [
        'access_limit_max_users', 'base_automation'
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'data/base_automation.xml',
        'data/res_users.xml',
    ],
    "demo": [
        'demo/res_users.xml',
    ],
    "qweb": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,

    "auto_install": False,
    "installable": True,

    # "demo_title": "SaaS: Client (Hesham Edition)",
    # "demo_addons": [
    # ],
    # "demo_addons_hidden": [
    # ],
    # "demo_url": "DEMO-URL",
    # "demo_summary": "Custom client module for SaaS",
    # "demo_images": [
    #    "images/MAIN_IMAGE",
    # ]
}
