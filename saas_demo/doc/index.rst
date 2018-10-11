======================
 Quick Demo Databases
======================

Installation
============

TODO

Configuration
=============

Manifests
---------

Add following attributes to manifest of your modules

::

    "demo_title": "Super-Duper Reminders",
    "demo_addons": ["reminder_phonecall", "reminder_task_deadline", "reminder_hr_recruitment"],
    "demo_addons_hidden": ["website"],
    "demo_url": "reminders-and-agenda",

* ``demo_title`` -- human-readable description of demonstrated modules
* ``demo_addons`` -- list of additional modules to demostrate
* ``demo_addons_hidden`` -- additional modules to install
* ``demo_url`` -- is used as part of url to get demo instance

apps.odoo.com
-------------

To activate ``[Live Preview]`` button at apps-store, add following attrubute to module manifest::

    "live_test_url": "http://demo.example.com/new/reminders-and-agenda",
    
SaaS Backend
------------

* Open menu ``[[ SaaS ]] >> Operators``
* Create or update an Operator:

  * **Repositories**
    * **Branch**
    * **Scan for demo** -- if not, it's used only as dependency

Usage
=====
TODO: how to scan?

* Open url: http://demo.example.com/new/reminders-and-agenda?version=BRANCH
* RESULT: you are authenticated in new demo instance
