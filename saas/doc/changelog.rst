`3.0.0`
-------

- **Improvement:** mandatory modules can be redefined in dependent modules
- **New:** added "Refresh" in build view to get data from build database
- **Fix:** random_ready_operator does not throw exceptions if no operators are ready
- **Fix:** no extra rigths required to read build's URL
- **Improvement:** Removed {db_id} variable for generating database name
- **Improvement:** Added helper methods `execute_kw` and `xmlid_lookup` on `saas.db` model

`2.4.3`
-------

- **Fix:** errors on installing some modules in templates

`2.4.2`
-------

- **Improvement:** when creating a build, if there is only one Template's deployment, then it will be selected automatically

`2.4.1`
-------

- **Fix:** change the name of the direct_url field to global_url to avoid misunderstanding

`2.4.0`
-------

- **New:** notification of the user about the process of creating the template's deployment

`2.3.1`
-------

- **Fix:** multiple build removal

`2.3.0`
-------

- **Improvement:** rebuild template database if template is changed

`2.2.0`
-------

- **Improvement:** delete odoo database after unlink correspond Template's deployment record

`2.1.0`
-------

- **Improvement:** add the ability to delete created builds

`2.0.0`
-------

- **New:** don't use RPC on preparing template database -- SaaS Operator must provide it's own way to access to the database

`1.0.3`
-------

- **Fix:** update master_url in the created builds when changing the direct_url field in the operator

`1.0.2`
-------

- **Fix:** added preparation of names for builds for links to work correctly.

`1.0.1`
-------

- **Fix:** transfer tests to module and refactor

`1.0.0`
-------

- **Init version**
