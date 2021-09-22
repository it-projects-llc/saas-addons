====================
 SaaS: Domain names
====================

Installation
============

* `Install <https://odoo-development.readthedocs.io/en/latest/odoo/usage/install-module.html>`__ this module in a usual way

Usage
=====

Make sure, you have domain with A-record which points to some saas operator, that you are using.
As another option, you can add domain in /etc/hosts (GNU/Linux, *BSD) or (C:\Windows\system32\drivers\etc\hosts).


* Open menu ``[[ SaaS ]] >> Domains``
* Create domain name and choose operator, to which it is or going to be assigned. Let it be example.remote
* Open menu ``[[ SaaS ]] >> Builds``
* Click on any build with state ``Ready``
* Click on ``[Edit]``
* On field "Web domain" input domain example.remote and click ``[Save]``
* Open http://example.remote in new browser window
* RESULT: in new browser window you will see build, where you have just assigned domain example.remote


* Return back to ``[[ SaaS ]] >> Builds``
* Click on any other build
* Click on ``[Edit]``
* On field "Web domain" input domain example.remote
* RESULT: "Domain names must be unique" message will appear
