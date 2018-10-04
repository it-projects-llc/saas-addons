===============================
 Quick Authentication (Master)
===============================

Installation
============

To try this module you need to have two odoo databases: *master* (with ``auth_quick_master`` installed) and *build* (with ``auth_quick`` installed). Both have to have proper db-filter or must be the only database in the instances.

Configuration
=============

User must have ``Quick authentication for builds`` group to use this module.

Usage
=====

* Open url to your build: build-123.example.com/quick-auth/login?login=admin (change domain to a correct one)
* RESULT: you are authenticated at the build
