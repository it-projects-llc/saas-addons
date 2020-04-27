# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2018-2019 Denis Mudarisov <https://it-projects.info/team/mudarisov>
# Copyright 2019 Anvar Kildebekov <https://it-projects.info/team/kildebekov>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": """SaaS Base""",
    "summary": """Base module for master SaaS instance""",
    "category": "SaaS",
    # "live_test_url": "http://apps.it-projects.info/shop/product/DEMO-URL?version=13.0",
    "images": [],
    "version": "13.0.2.4.3",
    "application": False,

    "author": "IT-Projects LLC, Ivan Yelizariev",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info/team/yelizariev",
    "license": "AGPL-3",
    # "price": 9.00,
    # "currency": "EUR",

    "depends": [
        "auth_quick_master",
        "queue_job",
        "web_editor",
        "web_notify",
    ],
    "external_dependencies": {"python": ['python-slugify'], "bin": []},
    "data": [
        "security/saas_security.xml",
        "security/ir.model.access.csv",
        "views/saas_view.xml",
        "views/saas_template_views.xml",
        "views/saas_template_operator_views.xml",
        "views/saas_operator_views.xml",
        "views/saas_module_views.xml",
        "views/saas_db_views.xml",
        "wizard/saas_template_create_build_view.xml",
        "data/ir_cron_data.xml",
        "data/saas_operator_data.xml",
        "data/default_modules.xml",
        "data/db_sequence.xml",
    ],
    "demo": [
        "demo/saas_template_demo.xml",
        "demo/saas_security_demo.xml",
    ],
    "qweb": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "uninstall_hook": None,

    "auto_install": False,
    "installable": True,
}
