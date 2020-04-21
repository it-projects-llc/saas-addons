# Copyright 2020 Vildan Safin <https://www.it-projects.info/team/Enigma228322>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": """SaaS Apps""",
    "summary": """Choose your apps""",
    "category": "Marketing",
    # "live_test_url": "http://apps.it-projects.info/shop/product/DEMO-URL?version=12.0",
    "images": ['/images/attention.jpg'],
    "version": "12.0.1.0.0",
    "application": False,

    "author": "IT-Projects LLC, Vildan Safin",
    "support": "apps@it-projects.info",
    "website": "https://apps.odoo.com/apps/modules/12.0/saas_apps/",
    "license": "AGPL-3",
    # "price": 9.00,
    # "currency": "EUR",

    "depends": ['website', 'saas_public'],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        'security/ir.model.access.csv',
        'views/calculator.xml',
        'views/manage.xml',
        "data/saas_base_template.xml",
        'views/assets.xml'
    ],
    "demo": [
    ],
    "qweb": [
        'views/refresh.xml'
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,

    "auto_install": False,
    "installable": True,

    # "demo_title": "SaaS Apps",
    # "demo_addons": [
    # ],
    # "demo_addons_hidden": [
    # ],
    # "demo_url": "DEMO-URL",
    # "demo_summary": "short",
    # "demo_images": [
    #    "images/MAIN_IMAGE",
    # ]
}
