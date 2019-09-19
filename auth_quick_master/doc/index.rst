====================
 Quick Auth (Master)
====================

Installation
============

To try this module you need to have two odoo databases: *master* (with ``auth_quick_master`` installed) and *build* (with ``auth_quick`` installed).

Configuration
=============

User must have ``Quick authentication for builds`` group to use this module.

Usage
=====

* Logout from your build
* Open url to your build: build-123.example.com/auth_quick/login?build_login=admin (change domain to a correct one)
* RESULT: you are authenticated at the build
