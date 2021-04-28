# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": """SaaS Public""",
    "summary": """Module for creating public builds""",
    "category": "SaaS",
    "images": [],
    "version": "14.0.1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Denis Mudarisov",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info/team/trojikman",
    "license": "AGPL-3",
    # "price": 9.00,
    # "currency": "EUR",

    "depends": [
        "saas",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "views/saas_template_operator_views.xml",
    ],
    "demo": [
        "demo/public_saas_template_demo.xml",
    ],
    "auto_install": False,
    "installable": True,

    # "demo_title": "{MODULE_NAME}",
    # "demo_addons": [
    # ],
    # "demo_addons_hidden": [
    # ],
    # "demo_url": "DEMO-URL",
    # "demo_summary": "{SHORT_DESCRIPTION_OF_THE_MODULE}",
    # "demo_images": [
    #    "images/MAIN_IMAGE",
    # ]
}
