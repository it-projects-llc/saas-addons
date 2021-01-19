/* Copyright 2020 Vildan Safin <https://www.it-projects.info/team/Enigma228322>
 License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).*/
 odoo.define('saas_apps.filter_button', function (require) {
    "use strict";

    var core = require('web.core');
    var session = require('web.session');
    var ListController = require('web.ListController');

    ListController.include({
        renderButtons: function($node) {
        this._super.apply(this, arguments);
            if (this.$buttons) {
                var refresh_apps_button = this.$buttons.find('.refresh_apps_button');
                if (refresh_apps_button.length) {
                    refresh_apps_button.on("click", this.proxy('refresh_apps_button'));
                }
            }
        },
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
});
