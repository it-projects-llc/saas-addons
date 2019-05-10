===========
 SaaS Base
===========

Installation
============

* Follow instruction of `Job Queue <https://github.com/OCA/queue/tree/12.0/queue_job>`__ module.
* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way
* Restart the odoo as required by the Job Queue module

Configuration
=============

* Use ``db-filter=^%d$`` when using Same Instance type in saas.operator model

Usage
=====

**Create template**

* Open menu ``[[ SaaS ]] >> Templates``
* Click ``[Create]``
* Fill in the required fields including **Template's deployments**

**Create build**

* Wait until at least one of **Template's deployments** is ready (refresh the page)
* Click ``[Create build]``
* Fill in required fields in a popup window
* Click ``[Create build]`` and then you will be redirected to the build form
* Wait for the creation of the build on the template (refresh the page)
* Click ``[Connect to the build]``
* RESULT: you will be redirected and logged in to the created build
