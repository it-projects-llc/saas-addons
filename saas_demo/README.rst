.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

======================
 Quick Demo Databases
======================

One-click demo-instances with modules from your git repositories

How it works
============

* 1 ``saas.operator`` record has 1 set of repositories (``saas.demo`` record).
* In each repository only one branch is used.
* 1 ``saas.template`` record may have many ``saas.template.operator``. The idea
  is that we can rebuild template database on one operator, while there is
  another one available to use.
* ``saas.template`` records are generated automatically from ``saas.demo`` records

Repository updating
===================

* Once in a night all ``saas.demo`` 's *Operators* are marked for updates
* One by one *Operators* from ``saas.demo`` update repositories, destroy templates and start rebuilding templates.

Credits
=======

Contributors
------------
* `Ivan Yelizariev <https://it-projects.info/team/yelizariev>`__
* `Denis Mudarisov <https://it-projects.info/team/mudarisov>`__

Sponsors
--------
* `IT-Projects LLC <https://it-projects.info>`__

Maintainers
-----------
* `IT-Projects LLC <https://it-projects.info>`__

Further information
===================

Demo: http://runbot.it-projects.info/demo/saas-addons/13.0

HTML Description: https://apps.odoo.com/apps/modules/13.0/saas_demo/

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Notifications on updates: `via Atom <https://github.com/it-projects-llc/saas-addons/commits/13.0/saas_demo.atom>`_, `by Email <https://blogtrottr.com/?subscribe=https://github.com/it-projects-llc/saas-addons/commits/13.0/saas_demo.atom>`_

Tested on Odoo 12.0 8d9e276a9fbf3b4cd8b8251e184d936ff654dd1f
