# Copyright 2020 Vildan Safin <https://www.it-projects.info/team/Enigma228322>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html).

{
    "name": """SaaS Apps""",
    "summary": """Choose your apps""",
    "category": "Marketing",
    # "live_test_url": "http://apps.it-projects.info/shop/product/DEMO-URL?version=14.0",
    "images": ["/images/attention.jpg"],
    "version": "15.0.1.0.1",
    "application": False,
    "author": "IT-Projects LLC, Vildan Safin",
    "support": "apps@it-projects.info",
    "website": "https://apps.odoo.com/apps/modules/14.0/saas_apps/",
    "license": "AGPL-3",
    "depends": ["saas_product", "saas_public", "website_sale"],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "data/product_data.xml",
        "data/saas_template_data.xml",
        "security/ir.model.access.csv",
        "views/calculator.xml",
        "views/saas_app_views.xml",
        "views/saas_template_views.xml",
        "views/res_config_settings_views.xml",
    ],
    "demo": [],
    "assets": {
        "web.assets_frontend": [
            "saas_apps/static/src/css/calculator.css",
            "saas_apps/static/src/js/saas_apps.js",
        ],
        "web.assets_backend": [
            "saas_apps/static/src/js/refresh_button.js",
            "saas_apps/static/src/xml/base.xml"
            ],
    },
    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,
    "auto_install": False,
    "installable": False,
}
