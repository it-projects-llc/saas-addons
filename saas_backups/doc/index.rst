===============
 SaaS: Backups
===============

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Usage
=====

**Simple backup and restore**

* Open menu ``[[ SaaS ]] >> Templates``
* Choose any template
* Wait until at least one of **Template's deployments** is ready (refresh the page)
* Click ``[Create build]``
* Fill in required fields in a popup window
* Click ``[Create build]`` and then you will be redirected to the build form
* Wait for the creation of the build on the template (refresh the page)
* Click ``[Connect to build]``
* In new build, make some changes to identify this build (write dummy message to ``#general`` channel)
* Return to build form
* Click ``[Create backup]``
* RESULT: you will be redirected to queue job form, where backup is created

* Wait until backup job is done (refresh the page)
* When job is done, click on ``[Related]``
* RESULT: you will be redirected to backup form

* Click ``[Restore backup]``
* Wait until restore job is done (refresh the page)
* RESULT: when job is done, ``[View restored build]`` will appear

* Click on ``[View restored build]``
* RESULT: you will be redirected to form of new build
* RESULT: in that form of new build you will see backup and build, which is this build is originated from

* Click on ``[Connect to build]``
* Make sure, that this is copy of original build
