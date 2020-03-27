/* Copyright 2020 Vildan Safin <https://github.com/Enigma228322>
 License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).*/
 odoo.define('whatever.filter_button', function (require) {
    "use strict";
    
    var core = require('web.core');
    var session = require('web.session');
    var ListController = require('web.ListController');
    
    ListController.include({
        renderButtons: function($node) {
        this._super.apply(this, arguments);
            if (this.$buttons) {
                var filter_button = this.$buttons.find('.oe_filter_button');
                filter_button && filter_button.click(this.proxy('filter_button')) ;
            }
        },
        filter_button: function () {
            // Loading all modules in saas.line from ir.module.module
            session.rpc('/refresh', {
            }).then(function (result) {
                window.location.reload()
            });
        }
    });
});
