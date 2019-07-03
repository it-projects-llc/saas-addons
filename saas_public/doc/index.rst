===============
 SaaS Public
===============

Installation
============

* Follow instruction of `Job Queue <https://github.com/OCA/queue/tree/12.0/queue_job>`__ module.
* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way
* Restart the odoo as required by the Job Queue module

Configuration
=============

* Open menu ``[[ SaaS ]] >> Templates``
* Open your template or create new for which you need to create a build
* Choose or create Template's deployments for which you can open public access
* Check the box ``Public Access``
* RESULT: Now you can create public builds on the template

Usage
=====

* Open menu ``[[ SaaS ]] >> Templates``
* Choose or create Template that has Template's deployment(s) with public access
* Copy link from Fast URL field
* Open that link in browser either as logged in or logged out user
* RESULT: You will be redirected to the newly created build
