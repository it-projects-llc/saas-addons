==============
 Saas: Portal
==============

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Usage
=====

**Build listing**

* Open link ``/my``
* RESULT: there is section "Builds"

**Restored build approval workflow (without domain)**

* Follow **Simple backup and restore** steps from ``SaaS: Backups`` module
* Go to ``/my/builds``
* RESULT: you will see at least one build in "Temporary builds section"

* Open page of the build, that has restored recenlty
* Click on "Approve" button
* Open ``/web``
* Go to ``[[ SaaS ]] >> Builds``
* Open form that build
* RESULT: "Is temporary build approved?" value is True

* Click on "Set as main"
* Click "OK"
* RESULT: domain from origin build is mapped to this build
