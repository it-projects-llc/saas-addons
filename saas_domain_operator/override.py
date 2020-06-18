# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License MIT (https://opensource.org/licenses/MIT).

import configparser
import logging
import os

from odoo import http
from odoo.tools import config

SECTION = "mappings"

db_filter_org = http.db_filter
host2db_config = configparser.ConfigParser()
host2db_filename = os.path.join(config["data_dir"], "host2db.ini")


def db_filter(dbs, httprequest=None):
    httprequest = httprequest or http.request.httprequest
    h = httprequest.environ.get("HTTP_HOST", "").split(":")[0]
    dbname = host2db_config.get(SECTION, h, fallback=None)
    if dbname:
        return [dbname]
    else:
        return db_filter_org(dbs, httprequest)


if "saas_domain_operator" in config.get("server_wide_modules"):
    _logger = logging.getLogger(__name__)

    host2db_config.read(host2db_filename)
    if SECTION not in host2db_config:
        host2db_config[SECTION] = {}

    _logger.info("monkey patching http.db_filter")
    http.db_filter = db_filter
