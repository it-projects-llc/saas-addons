======================
 Saas: Database Limit
======================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Usage
=====

* Open menu ``[[ SaaS ]] >> Builds``
* Click on any build with state `Ready`
* Click ``[Edit]``
* Set field ``Limit database size`` to some value
* RESULT: if sum of build's database and filestore sizes will be greater than given value above, build's UI will be blocked
