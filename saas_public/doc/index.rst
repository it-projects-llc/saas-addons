===============
 SaaS Public
===============

Installation
============

* Follow the insallation instruction of `SaaS Base <https://github.com/it-projects-llc/saas-addons/blob/14.0/saas/doc/index.rst>`__ module
* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Configuration
=============

* Open menu ``[[ SaaS ]] >> Templates``
* Open your template or create new for which you need to create a build
* Set **[x] Public Access**
* RESULT: Now you can create public builds on the template

Usage
=====

* Open menu ``[[ SaaS ]] >> Templates``
* Choose or create Template that has Template's deployment(s) with public access
* Open link `yourdomain.example/saas_public/*template_id*/create-fast-build` in browser either as logged in or logged out user. Instead of *template_id*, insert template id with public access
* RESULT: You will be redirected to the newly created build
