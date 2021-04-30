===================
 Saas: Build Admin
===================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Configuration
=============

Before using this module, you need at least one outgoing mail (SMTP) server set in Odoo.

To add new SMTP server in Odoo, do following:

* `Log in as SUPERUSER <https://odoo-development.readthedocs.io/en/latest/odoo/usage/login-as-superuser.html>`__
* `Activate Developer Mode <https://odoo-development.readthedocs.io/en/latest/odoo/usage/debug-mode.html>`__
* Open menu ``[[ Settings ]] >> Technical >> Outgoing Mail Servers``
* Click ``[Create]``
* Fill in mandatory fields
* Click ``[Save]``
* Make sure your credentials are correct by clicking ``[Test Connection]``

Usage
=====

* Open menu ``[[ SaaS ]] >> Builds``
* Click on any build with state `Ready`
* Click ``[Edit]``
* Change field ``Admin user`` to someone else
* RESULT:

  * email with credentials is sent to that user
  * user's language from master database is also applied to user's languange in build
