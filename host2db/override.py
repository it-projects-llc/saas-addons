import configparser
import logging
import os
from time import time

from odoo import http
from odoo.tools import config


class Host2DBConfig(configparser.ConfigParser):
    SECTION = "mappings"
    _last_time_read = None

    def __init__(self, *args, **kwargs):
        super(Host2DBConfig, self).__init__(*args, **kwargs)
        self._reread_config()

    @property
    def config_filename(self):
        return os.path.join(config["data_dir"], "host2db.ini")

    def read(self, *args, **kwargs):
        self._last_time_read = time()
        self._config_mtime = os.path.getmtime(self.config_filename) if os.path.exists(self.config_filename) else None
        return super(Host2DBConfig, self).read(*args, **kwargs)

    def _reread_config(self):
        self.read(self.config_filename)
        if self.SECTION not in self:
            self[self.SECTION] = {}

    def _save_config(self):
        with open(self.config_filename, "w") as f:
            self.write(f)

    def assign_host_to_db(self, host, db):
        self.set(self.SECTION, host, db)

    def unassign_host(self, host):
        self.remove_option(self.SECTION, host)

    def remove_option(self, section, option):
        res = super(Host2DBConfig, self).remove_option(section, option)
        self._save_config()
        return res

    def set(self, section, option, value=None):
        res = super(Host2DBConfig, self).set(section, option, value)
        self._save_config()
        return res

    def get_db_by_host(self, host):
        mtime = os.path.getmtime(self.config_filename) if os.path.exists(self.config_filename) else None
        if not self._last_time_read or mtime != getattr(self, "_config_mtime", None):
            self.clear()
            self._reread_config()

        return self.get(self.SECTION, host, fallback=None)


db_filter_org = http.router.db_filter
host2db_config = Host2DBConfig()


def db_filter(dbs, host=None):
    host = host or http.request.httprequest.environ.get("HTTP_HOST", "")
    h = host.split(":")[0]
    dbname = host2db_config.get_db_by_host(h)
    if dbname:
        return [dbname] if dbname in dbs else []
    else:
        return db_filter_org(dbs, host)


if "host2db" in config.get("server_wide_modules"):
    _logger = logging.getLogger(__name__)
    _logger.info("monkey patching odoo.http.router.db_filter")
    http.router.db_filter = db_filter
    http.db_filter = db_filter
    # Odoo 20 controllers import db_filter directly. Update already-imported
    # aliases as well, so authentication and websocket routing use the mapping.
    import sys
    for module_name, module in tuple(sys.modules.items()):
        if module_name.startswith(("odoo.http", "odoo.addons.web.controllers")) and getattr(module, "db_filter", None) is db_filter_org:
            module.db_filter = db_filter
