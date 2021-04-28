===========
 SaaS Base
===========

Installation
============

* Use ``db-filter=^%d$`` when using Same Instance type in saas.operator model
* Set ``--limit-time-cpu`` and ``--limit-time-real`` big enough (e.g. 1800 and
  3600), because with default values (60 and 120 seconds) it may be not enough
  to install modules in template database
* Set ``--workers`` more than 1 (you cannot use *threaded* mode, i.e. ``--workers`` equal to zero)
* Follow instruction of `Job Queue <https://github.com/OCA/queue/tree/14.0/queue_job>`__ module.
* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way
* Restart the odoo as required by the Job Queue module

Configuration
=============

**Create template**

* Open menu ``[[ SaaS ]] >> Templates``
* Click ``[Create]``
* Fill in the required fields including **Template's deployments**

Usage
=====

**Create build**

* Wait until at least one of **Template's deployments** is ready (refresh the page)
* Click ``[Create build]``
* Fill in required fields in a popup window
* Click ``[Create build]`` and then you will be redirected to the build form
* Wait for the creation of the build on the template (refresh the page)
* Click ``[Connect to the build]``
* RESULT: you will be redirected and logged in to the created build

**Delete created build**

* Open menu ``[[ SaaS ]] >> Builds``
* Open the ``build`` you want to delete
* Click on ``Action``, then press ``Delete``
* After confirming the action, the build will be deleted

**Delete created Template's deployment**

* Open menu ``[[ SaaS ]] >> Templates``
* Open the ``Template`` in which you want to make changes
* Click on ``Edit``
* Choose ``Template's deployment`` line you want to remove and click on the delete icon on the right

**Template Changes and rebuild Template's deployments**

The template will be rebuilt automatically during the following steps:

* Open menu ``[[ SaaS ]] >> Templates``
* Open the ``Template`` in which you want to make changes.
* Make the changes you need.
* If among the changed fields there are ``Install demo data``, ``Modules to install`` or ``Template Initialization`` then Template's deployment will be rebuilt.
