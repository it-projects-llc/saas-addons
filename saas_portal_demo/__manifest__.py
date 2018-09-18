{
    "name": """Demo datatabases""",
    "summary": """All you need to create demos for your applications in odoo apps store""",
    "category": "SaaS",
    "images": [],
    "version": "11.0.1.0.0",

    "author": "IT-Projects LLC, Cesar Lage, Ivan Yelizariev, Nicolas JEUDY",
    "website": "https://it-projects.info",
    "license": "GPL-3",
    # "price": 9.00,
    # "currency": "EUR",

    "depends": [
        "saas_portal",
    ],
    "external_dependencies": {"python": ['requests'], "bin": []},
    "data": [
        "security/ir.model.access.csv",
        "views/saas_portal_demo.xml",
        "data/ir_cron.xml",
    ],
    "qweb": [
    ],
    "demo": [
    ],

    "post_load": None,
    "pre_init_hook": None,
    "post_init_hook": None,
    "installable": True,
    "auto_install": False,
}
