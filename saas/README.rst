.. image:: https://img.shields.io/badge/license-LGPL--3-blue.png
   :target: https://www.gnu.org/licenses/lgpl
   :alt: License: LGPL-3

===========
 SaaS Base
===========

Base module for master SaaS instance.

The module is similar to ``saas_portal`` in *odoo-saas-tools*.

Models overview
===============

* ``saas.template`` -- similar to ``saas_portal.plan`` in *odoo-saas-tools*, but covers only technical aspects (database creation) and not any sale/trial stuff. A single record can be used for multiple servers.
* ``saas.operator`` -- similar to ``saas_portal.server`` in *odoo-saas-tools*. Credentials to create-destoroy, update, migrate, backup, etc. odoo instances. It doesn't need special odoo instance (database) in corresponding server and could work by sending requests, for example, to kubernetes.
* ``saas.client`` -- similar to ``saas_portal.client`` in *odoo-saas-tools*
* ``saas.log`` -- client instance history.


Credits
=======

Contributors
------------
* `Ivan Yelizariev <https://it-projects.info/team/yelizariev>`__

Sponsors
--------
* `IT-Projects LLC <https://it-projects.info>`__

Maintainers
-----------
* `IT-Projects LLC <https://it-projects.info>`__

      To get a guaranteed support
      you are kindly requested to purchase the module
      at `odoo apps store <https://apps.odoo.com/apps/modules/12.0/saas/>`__.

      Thank you for understanding!

      `IT-Projects Team <https://www.it-projects.info/team>`__

Further information
===================

Demo: http://runbot.it-projects.info/demo/saas-addons/12.0

HTML Description: https://apps.odoo.com/apps/modules/12.0/saas/

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Notifications on updates: `via Atom <https://github.com/it-projects-llc/saas-addons/commits/12.0/saas.atom>`_, `by Email <https://blogtrottr.com/?subscribe=https://github.com/it-projects-llc/saas-addons/commits/12.0/saas.atom>`_

Tested on Odoo 12.0 032d0ed90f580f25819cd6846e21cf155ade44e7
