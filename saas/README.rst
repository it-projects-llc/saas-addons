.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

===========
 SaaS Base
===========

Base module for master SaaS instance.

The module is similar to ``saas_portal`` in *odoo-saas-tools*.

Models overview
===============

* ``saas.template`` -- similar to ``saas_portal.plan`` in *odoo-saas-tools*, but covers only technical aspects (database creation) and not any sale/trial stuff. A single record can be used for multiple servers (via ``saas.template.operator``.
* ``saas.operator`` -- similar to ``saas_portal.server`` in *odoo-saas-tools*. Credentials to create-destroy, update, migrate, backup, etc. odoo instances.

  * It doesn't need special odoo instance (database, *SaaS Server* in terms of
    *odoo-saas-tool* project) in corresponding server and could work by sending
    requests, for example, to kubernetes.
  * Single *operator* is only one set of modules at some versions. If you have a
    server which is used for different versions of odoo or just module version,
    then you need you to create ``saas.operator`` per each module set. Those
    *operators* may use same credentials.
  * Different *Operators* may have same postgresql scope. It's usefull in
    staging when we apply a database for new versions of modules. On the other
    hand, it force us to have unique database names across operators

* ``saas.db`` -- similar to ``saas_portal.client`` in *odoo-saas-tools*
* ``saas.log`` -- saas history, e.g. database creation, updating, etc.

Roadmap
=======

* TODO: Create menu for SaaS Operator
    * smart button for builds list
* TODO: Create menu for SaaS Log model
    * saas.db form: add smart button for saas.log's
    * saas.operator: add smart button for saas.log's
* TODO: Add check uniqueness of database name across saas.db records with state == done. Also check that there is no records of saas.db with name equal to one that user wants to use in use in wizard, saas template operator.
* TODO: Make the saas.template form duplicable again
* TODO: Add page refresh button on saas.template form
* TODO: saas_test: add database creation rollback and extra safety:
    * setUp: prepare list of database names that will be created during the tests. Check that those databases don't exist and raise error otherwise
    * use random suffix to avoid droping database reserved for production purposes during test execution, e.g. template_database_ecusnc63asdf234
    * tearDown: drop created databases after test exectuion
* TODO: Add coverage for "Connect to the build" button:
    * get authentication on master database in requests' session (use authenticate method from odoo/tests/common.py)
    * open "connect to build url"
    * check that you are finally redirected to /web page at the build
* TODO: add computed record in saas.db model to avoid using the name of the master database. Some new db type is needed. Say, ``('other', 'Reserved DB Name')``

* TODO: saas.operator: add a button that runs a wizard which allows to make new build (saas.db) from backup; add a method in ``saas.operator`` which takes the backup as argument; implement the method for "Same Instance" operator

Credits
=======

Contributors
------------
* `Ivan Yelizariev <https://it-projects.info/team/yelizariev>`__
* `Denis Mudarisov <https://it-projects.info/team/mudarisov>`__
* `Eugene Molotov <https://it-projects.info/team/em230418>`__

Sponsors
--------
* `IT-Projects LLC <https://it-projects.info>`__

Maintainers
-----------
* `IT-Projects LLC <https://it-projects.info>`__

Further information
===================

Demo: http://runbot.it-projects.info/demo/saas-addons/14.0

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Notifications on updates: `via Atom <https://github.com/it-projects-llc/saas-addons/commits/14.0/saas.atom>`_, `by Email <https://blogtrottr.com/?subscribe=https://github.com/it-projects-llc/saas-addons/commits/14.0/saas.atom>`_

Tested on Odoo 14.0 8ca3ea063050f2ab2d19cce8a68116489872a734
