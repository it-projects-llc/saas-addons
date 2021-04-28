.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License: MIT

===============
 SaaS: Product
===============

This technical module helps to create saas-related products.

As example this module has product "Users" with variants "Anually" and "Monthly" with different prices.
Other saas-related products can define `product.template` record and make variants by assigning
"Subscribtion: Annually" and "Subscribtion: Monthly" attribute values.

In python it looks like this:

.. code-block:: python

    template = env["product.template"].create({"name": "Test SaaS Product"})

    template_attribute_line = env["product.template.attribute.line"].create({
        "product_tmpl_id": template.id,
        "attribute_id": env.ref("saas_product.product_attribute_subscription").id,
        "value_ids": [(6, 0, [
            env.ref("saas_product.product_attribute_value_subscription_anually").id,
            env.ref("saas_product.product_attribute_value_subscription_monthly").id,
        ])]
    })

    annually_value_id = template_attribute_line.product_template_value_ids[0]
    monthly_value_id = template_attribute_line.product_template_value_ids[1]

    product_annually = template._get_variant_for_combination(annually_value_id)
    product_monthly = template._get_variant_for_combination(monthly_value_id)


Credits
=======

Contributors
------------
* `Eugene Molotov <https://it-projects.info/team/em230418>`__:

Sponsors
--------
* `IT-Projects LLC <https://it-projects.info>`__

Maintainers
-----------
* `IT-Projects LLC <https://it-projects.info>`__

      To get a guaranteed support
      you are kindly requested to purchase the module
      at `odoo apps store <https://apps.odoo.com/apps/modules/14.0/saas_product/>`__.

      Thank you for understanding!

      `IT-Projects Team <https://www.it-projects.info/team>`__

Further information
===================

Demo: http://runbot.it-projects.info/demo/saas-addons/14.0

HTML Description: https://apps.odoo.com/apps/modules/14.0/saas_product/

Usage instructions: `<doc/index.rst>`_

Changelog: `<doc/changelog.rst>`_

Notifications on updates: `via Atom <https://github.com/it-projects-llc/saas-addons/commits/14.0/saas_product.atom>`_, `by Email <https://blogtrottr.com/?subscribe=https://github.com/it-projects-llc/saas-addons/commits/14.0/saas_product.atom>`_

Tested on Odoo 14.0 9e68ec931d254ba563b4a16afa38b6003336a7cf
