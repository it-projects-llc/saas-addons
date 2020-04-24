# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": """SaaS: Portal""",
    "summary": """Allows to customers see their Builds at Portal.""",
    "category": "Hidden",
    # "live_test_url": "http://apps.it-projects.info/shop/product/DEMO-URL?version=12.0",
    "images": [],
    "version": "12.0.1.0.0",
    "application": False,
    "author": "IT-Projects LLC, Eugene Molotov",
    "support": "apps@it-projects.info",
    "website": "https://apps.odoo.com/apps/modules/12.0/saas_portal/",
    "license": "AGPL-3",
    # "price": 9.00,
    # "currency": "EUR",
    "depends": ["saas", "portal", "saas_expiration", "saas_limit_max_users", "saas_build_admin"],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "security/ir.model.access.csv",
        "security/saas_db_security.xml",
        "views/portal_templates.xml",
    ],
    "demo": [],
    "qweb": [],
    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,
    "auto_install": False,
    "installable": True,
    # "demo_title": "SaaS: Portal",
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
