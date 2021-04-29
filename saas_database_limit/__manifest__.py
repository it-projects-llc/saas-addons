# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": """SaaS: Database size limit""",
    "summary": """This module allows to sets build's database size limit""",
    "category": "Hidden",
    # "live_test_url": "http://apps.it-projects.info/shop/product/DEMO-URL?version=14.0",
    "images": [],
    "version": "14.0.1.0.0",
    "application": False,
    "author": "IT-Projects LLC, Eugene Molotov",
    "support": "apps@it-projects.info",
    "website": "https://apps.odoo.com/apps/modules/14.0/saas_database_limit/",
    "license": "Other OSI approved licence",  # MIT
    # "price": 9.00,
    # "currency": "EUR",
    "depends": ["saas"],
    "external_dependencies": {"python": [], "bin": []},
    "data": ["views/saas_db.xml"],
    "demo": [],
    "qweb": [],
    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,
    "auto_install": False,
    "installable": True,
    # "demo_title": "SaaS: Database limit",
    # "demo_addons": [
    # ],
    # "demo_addons_hidden": [
    # ],
    # "demo_url": "DEMO-URL",
    # "demo_summary": "SHORT INTRO",
    # "demo_images": [
    #    "images/MAIN_IMAGE",
    # ]
}
