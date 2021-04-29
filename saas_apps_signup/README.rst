.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

===================
 Saas: Apps Signup
===================

This module extends ``saas_apps`` module by implemeting

* signup procedure for unregistered users
* contracts management
* choosing database name before creating it

Credits
=======

Contributors
------------
* `Eugene Molotov <https://it-projects.info/team/em230418>`__:

Sponsors
--------
* `IT-Projects LLC <https://it-projects.info>`__

Maintainers
-----------
* `IT-Projects LLC <https://it-projects.info>`__

      To get a guaranteed support
      you are kindly requested to purchase the module
      at `odoo apps store <https://apps.odoo.com/apps/modules/14.0/saas_apps_signup/>`__.

      Thank you for understanding!

      `IT-Projects Team <https://www.it-projects.info/team>`__

Roadmap
=======

* TODO: write documentation
* TODO: implement test cases
  * unregistered user chooses apps, clicks try trial, registers - new build is created with expiration
  * unregistered user chooses apps, clicks buy now, registers, logs in, checkout and pay - new build is created with payed period
  * registered user chooses apps, clicks try trial, enters database name - new build is created with expiration
  * registered user chooses apps, click buy now, enters database name, checkout and pay - new build is created with payed period
  * same as above, but use other period
  * same as above, but user chooses templates

Further information
===================

Demo: http://runbot.it-projects.info/demo/saas-addons/14.0

HTML Description: https://apps.odoo.com/apps/modules/14.0/saas_apps_signup/

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Notifications on updates: `via Atom <https://github.com/it-projects-llc/saas-addons/commits/14.0/saas_apps_signup.atom>`_, `by Email <https://blogtrottr.com/?subscribe=https://github.com/it-projects-llc/saas-addons/commits/14.0/saas_apps_signup.atom>`_

Tested on Odoo 14.0 99531f5dd8966fc4ad89d1e9c2886ad701527f3a
