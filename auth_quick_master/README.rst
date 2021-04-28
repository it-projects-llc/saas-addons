.. image:: https://img.shields.io/badge/license-LGPL--3-blue.png
   :target: https://www.gnu.org/licenses/lgpl
   :alt: License: LGPL-3

=======================
 Quick Auth (Master)
=======================

Authentication provider for ``auth_quick`` module.

Allows users from group ``Quick authentication for builds`` be authenticated as any user from the build. Access levels to builds can be extented in a custom module.

How it works
============

Base idea is similar to OAuth protocol.

* User is authenticated in master odoo database (where this module is installed)
* User opens url in the build (where ``auth_quick`` module is installed): ``build-123.example.com/auth_quick/login?build_login=admin`` (authentication via ``?build_user_id=1`` is also supported). This module doesn't provider UI with such links and has to be implemented via another module depending on your needs.
* Build redirects User back to master odoo with build reference
* Master odoo creates record in model ``auth_quick_master.token`` with fields

  * ``user_id``
  * ``build``
  * ``build_login``
  * ``build_user_id``
  * ``token``

* Master odoo redirects User back to the build with new url: ``build-123.example.com/auth_quick/check-token?token=abcdf456789``
* Build validates the token by sending direct request to Master odoo and initialize session if token is valid

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

Further information
===================

Demo: http://runbot.it-projects.info/demo/saas-addons/14.0

HTML Description: https://apps.odoo.com/apps/modules/14.0/auth_quick_master/

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Notifications on updates: `via Atom <https://github.com/it-projects-llc/saas-addons/commits/14.0/auth_quick_master.atom>`_, `by Email <https://blogtrottr.com/?subscribe=https://github.com/it-projects-llc/saas-addons/commits/14.0/auth_quick_master.atom>`_

Tested on Odoo 14.0 8ca3ea063050f2ab2d19cce8a68116489872a734
