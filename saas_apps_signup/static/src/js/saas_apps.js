/*  Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).*/
odoo.define('saas_apps_signup.saas_apps', function (require) {
    "use strict";

    require("web.dom_ready");

    var getInputs = require("saas_apps.saas_apps").getInputs;

    $("#try-trial2").on("click", function() {
        var inputs = getInputs();
        if (!inputs.chosen_apps && !inputs.chosen_package_id) {
            alert("Please chosen apps or package to install");
            return;
        }

        if (!inputs.user_cnt) {
            alert("Number of users are not given");
            return;
        }

        var url = "/saas_apps_signup/make_database_for_trial?max_users_limit=" + inputs.user_cnt + "&period=" + inputs.period;

        if (inputs.chosen_package_id) {
            url += "&saas_template_id=" + inputs.chosen_package_id;
        } else {
            url += "&installing_modules=" + inputs.chosen_apps.join(",");
        }

        window.location = url;
    });
});
