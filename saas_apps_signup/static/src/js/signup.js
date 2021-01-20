/*  Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).*/
odoo.define('saas_apps_signup.signup', function (require) {
    "use strict";

    var session = require('web.session');

    $(document).ready(function() {
        if ($('.oe_signup_form').length > 0) {

          $('.oe_signup_form').on('submit', function (ev) {
                $(".loader").removeClass("hid");
            });

            $('#company_name').on('change', function(event) {
                var database_name = event.target.value.toLowerCase().replace(/[^[a-z0-9_-]/gi, '');
                $("#database_name").val(database_name).trigger("change");
            });

            $('#database_name').on('change', function(event) {

                var helper = $("#build-domain-helper");
                var submit_btn = $('.oe_login_buttons > button[type="submit"]');

                helper.find(".build-domain-helper_status").hide();
                submit_btn.attr("disabled", "disabled");
                if (!event.target.value) return;

                helper.find(".build-domain-helper_status-loading").show();

                session.rpc("/saas_apps_signup/is_database_slot_available", {
                    database_name: event.target.value,
                    operator_id: $("[name=operator_id]").val(),
                }).then(function(response) {
                    helper.find(".build-domain-helper_status").hide();
                    if (response.domain) {
                        helper.find("span.domain").html(response.domain);
                        helper.find(".build-domain-helper_status-true").show();
                        submit_btn.attr("disabled", null);
                    } else {
                        helper.find(".build-domain-helper_status-false").html(response.answer).show();
                    }
                });
            });
        }
    });

});
