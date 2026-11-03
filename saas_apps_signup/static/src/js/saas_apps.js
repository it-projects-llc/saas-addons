/* Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).*/
import { _t } from "@web/core/l10n/translation";
import { getInputs } from "@saas_apps/js/saas_apps";

function setup() {
    const btn = document.getElementById("try-trial2");
    if (!btn) {
        return;
    }
    btn.addEventListener("click", () => {
        const inputs = getInputs();
        if (!inputs.chosen_apps.length && !inputs.chosen_package_id) {
            window.alert(_t("Please chosen apps or package to install"));
            return;
        }
        if (!inputs.user_cnt) {
            window.alert(_t("Number of users are not given"));
            return;
        }

        let url =
            "/saas_apps_signup/make_database_for_trial?max_users_limit=" +
            inputs.user_cnt +
            "&period=" +
            inputs.period;

        if (inputs.chosen_package_id) {
            url += "&saas_template_id=" + inputs.chosen_package_id;
        } else {
            url += "&installing_modules=" + inputs.chosen_apps.join(",");
        }

        window.location = url;
    });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setup);
} else {
    setup();
}
