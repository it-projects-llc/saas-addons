# Copyright 2021 Bykov Victor
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": """SaaS: saas_installed_apps""",
    "summary": """This module disallows anyone to install apps on build and shows installed apps.""",
    "category": "Hidden",
    "version": "16.0.1.0.0",
    "application": False,
    "author": "IT-Projects LLC, Bykov Victor",
    "support": "apps@it-projects.info",
    "website": "https://apps.odoo.com/apps/modules/14.0/saas_access_apps/",
    "license": "AGPL-3",
    "depends": ["saas"],
    "data": ["views/saas_db.xml"],
    "auto_install": False,
    "installable": False,
}
