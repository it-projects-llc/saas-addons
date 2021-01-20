=================
 Saas: Contracts
=================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Usage
=====

Assuming, that you already have SaaS template ready to use.

* `Activate Developer Mode <https://odoo-development.readthedocs.io/en/latest/odoo/usage/debug-mode.html>`__
* Open menu ``[[ SaaS ]]``
* Create new build from template
  * Open menu ``Templates``
  * Choose template
  * Click ``[Create Build]``
  * Write build name and click ``[Create Build]``
* Click ``[Create SaaS contract]``
* Add line:
  - Product ``Users (Trial)``
  - Quantity: 5
  - Date Start: today
  - Date End: today + 10 days
  - Click ``[Save & Close]``
* Fill in other required fields
* Click ``[Save]``
* RESULT: build is assigned with recently created contract.

* Click ``[Creat invoices]``
* Smart button will show ``1 invoices``. Click on it
* Click on created invoice
* Click ``[Post]`` if it is not posted
* This invoice will be marked as paid, due to zero price
* Return back to contract
* Click ``[Update build]``
* RESULT: build has following changes:
  - Expiration date: today + 10 days
  - Max allowed users: 5
