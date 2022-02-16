=======================
 Saas Operator: Remote
=======================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Remote instance configuration
=============================

On instance, where builds will be created, you need to edit odoo.conf:

* set ``server_wide_modules`` with value ``web,host2db,saas_cluster_simple``. For example:

```
[options]
(...)
server_wide_modules = web,host2db,saas_cluster_simple
(...)
```

* set ``admin_passwd``. More info in `Deploying Odoo <https://www.odoo.com/documentation/13.0/setup/deploy.html#setup-deploy-odoo>`__

* set ``dbfilter=^%d$``

* set ``limit_time_cpu`` and ``limit_time_real`` big enough, (e.g. 1800 and 3600).

If you are using nginx, make sure ``proxy_read_timeout`` is also big enough (e.g. ``720s``)

Master instance configuration
=============================

For example, ``remote.server.net:8069`` is address of remote Odoo instance.

* Open menu ``[[ SaaS ]] >> Operators``
* Click ``[Create]``
* Fill the form with following values:

  - Name: anything
  - Type: ``Remote instance``
  - DB URLs: ``http://{db_name}.remote.server.net:8069``
  - DB Names: ``fast_build_{unique_id}``
  - Master URL: url of master instance. Example ``http://master.server.net:8069``
  - Instance URL: ``http://remote.server.net:8069``
  - Master Password: value of ``admin_passwd`` from section above
