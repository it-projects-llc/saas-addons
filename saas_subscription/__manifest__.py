# License MIT (https://opensource.org/licenses/MIT).

{
    "name": """SaaS: Subscription""",
    "summary": """This module manages subscription with SaaS clients""",
    "category": "Sales",
    "images": [],
    "version": "17.0.2.5.1",
    "application": False,

    "author": "GetapPRO, ACHRAF",
    "support": "achraf@getap.pro",
    "website": "https://www.getap.pro/",
    #"license": "GPL",  # MIT

    "depends": [
        "saas_expiration", "saas_limit_max_users", "contract", "saas_product", "subscription_oca",
    ],
    "data": [
        "views/sale_subscription_view.xml",
        "views/saas_db_view.xml",
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,

    "auto_install": False,
    "installable": False,

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
