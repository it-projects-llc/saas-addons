/* Copyright 2020 Vildan Safin <https://www.it-projects.info/team/Enigma228322>
 License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).*/
 odoo.define('saas_apps.filter_button', function (require) {
    "use strict";

    var core = require('web.core');
    var session = require('web.session');
    var ListController = require('web.ListController');
    var ListView = require('web.ListView');
    var viewRegistry = require('web.view_registry');

    var ManageAppsController = ListController.extend({
        buttons_template: 'ManageApps.buttons',
        events: _.extend({}, ListController.prototype.events, {
            'click .refresh_apps_button': 'refresh_apps_button',
        }),

        refresh_apps_button: function () {
            // Loading all modules in saas.line from ir.module.module
            this._rpc({
                "model": "saas.app",
                "method": "action_make_applist_from_local_instance",
                "args": [],
            }).then(function (result) {
                window.location.reload()
            });
        }
    });

    var ManageAppsView = ListView.extend({
        config: _.extend({}, ListView.prototype.config, {
            Controller: ManageAppsController,
        }),
    });

    viewRegistry.add('saas_apps_tree', ManageAppsView);

});
