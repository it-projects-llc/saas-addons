# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2018-2019 Denis Mudarisov <https://it-projects.info/team/mudarisov>
# Copyright 2019 Anvar Kildebekov <https://it-projects.info/team/kildebekov>
# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": """SaaS Base""",
    "summary": """Base module for master SaaS instance""",
    "category": "SaaS",
    # "live_test_url": "http://apps.it-projects.info/shop/product/DEMO-URL?version=14.0",
    "images": [],
    "version": "14.0.3.1.0",
    "application": False,

    "author": "IT-Projects LLC, Ivan Yelizariev",
    "support": "apps@it-projects.info",
    "website": "https://it-projects.info/team/yelizariev",
    "license": "AGPL-3",
    # "price": 9.00,
    # "currency": "EUR",

    "depends": [
        "auth_quick_master",
        "saas_cluster_simple",
        "queue_job",
        "web_editor",
        "web_notify",
        "mail",
        "http_routing",
    ],
    "external_dependencies": {"python": [], "bin": []},
    "data": [
        "security/saas_security.xml",
        "security/ir.model.access.csv",
        "views/saas_view.xml",
        "views/saas_template_views.xml",
        "views/saas_template_operator_views.xml",
        "views/saas_operator_views.xml",
        "views/saas_module_views.xml",
        "views/saas_db_views.xml",
        "views/res_config_settings_views.xml",
        "wizard/saas_template_create_build_view.xml",
        "data/ir_cron_data.xml",
        "data/saas_operator_data.xml",
        "data/default_modules.xml",
        "data/db_sequence.xml",
        "data/queue_job_data.xml",
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
