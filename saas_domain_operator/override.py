# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License MIT (https://opensource.org/licenses/MIT).

import configparser
import logging
import os
from time import time

from odoo import http
from odoo.tools import config


class Host2DBConfig(configparser.ConfigParser):
    SECTION = "mappings"
    _last_time_read = None

    def read(self, *args, **kwargs):
        self._last_time_read = time()
        return super(Host2DBConfig, self).read(*args, **kwargs)

    def _reread_config(self):
        self.read(os.path.join(config["data_dir"], "host2db.ini"))
        if self.SECTION not in self:
            self[self.SECTION] = {}

    def get_db_by_host(self, host):
        print(self._last_time_read, time())
        if not self._last_time_read or time() - self._last_time_read > 60:
            self._reread_config()

        return self.get(self.SECTION, host, fallback=None)


db_filter_org = http.db_filter
host2db_config = Host2DBConfig()


def db_filter(dbs, httprequest=None):
    httprequest = httprequest or http.request.httprequest
    h = httprequest.environ.get("HTTP_HOST", "").split(":")[0]
    dbname = host2db_config.get_db_by_host(h)
    if dbname:
        return [dbname]
    else:
        return db_filter_org(dbs, httprequest)


if "saas_domain_operator" in config.get("server_wide_modules"):
    _logger = logging.getLogger(__name__)
    _logger.info("monkey patching http.db_filter")
    http.db_filter = db_filter
