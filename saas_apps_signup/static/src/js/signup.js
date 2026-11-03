/* Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).*/
import { rpc } from "@web/core/network/rpc";

function node(id) {
    return document.getElementById(id);
}

function setup() {
    const form = document.querySelector(".oe_signup_form");
    if (!form) {
        return;
    }

    form.addEventListener("submit", () => {
        for (const loader of document.querySelectorAll(".loader")) {
            loader.classList.remove("hid");
        }
    });

    const preferredLanguage = node("database_lang");
    const languageOptions = [...form.querySelectorAll(".js-database-language-option")];
    const syncRequiredLanguages = () => {
        for (const option of languageOptions) {
            const checkbox = option.querySelector('input[type="checkbox"]');
            const required = checkbox.value === "en_US" || checkbox.value === preferredLanguage?.value;
            if (required) checkbox.checked = true;
            checkbox.disabled = required;
        }
    };
    preferredLanguage?.addEventListener("change", syncRequiredLanguages);
    syncRequiredLanguages();
    node("database_language_search")?.addEventListener("input", (event) => {
        const query = event.target.value.trim().toLocaleLowerCase();
        for (const option of languageOptions) {
            option.hidden = !option.textContent.toLocaleLowerCase().includes(query);
        }
    });

    const companyName = node("company_name");
    const databaseName = node("database_name");
    if (companyName && databaseName) {
        companyName.addEventListener("change", () => {
            databaseName.value = companyName.value.toLowerCase().replace(/[^a-z0-9_-]/gi, "");
            databaseName.dispatchEvent(new Event("change"));
        });
    }

    if (!databaseName) {
        return;
    }
    databaseName.addEventListener("change", () => {
        const helper = node("build-domain-helper");
        const submitBtn = document.querySelector('.oe_login_buttons > button[type="submit"]');
        if (!helper) {
            return;
        }
        const statuses = [...helper.querySelectorAll(".build-domain-helper_status")];
        const hideAll = () => statuses.forEach((el) => (el.style.display = "none"));

        hideAll();
        if (submitBtn) {
            submitBtn.disabled = true;
        }
        if (!databaseName.value) {
            return;
        }
        const loading = helper.querySelector(".build-domain-helper_status-loading");
        if (loading) {
            loading.style.display = "";
        }

        const operator = document.querySelector("[name=operator_id]");
        rpc("/saas_apps_signup/is_database_slot_available", {
            database_name: databaseName.value,
            operator_id: operator ? operator.value : undefined,
        }).then((response) => {
            hideAll();
            if (response.domain) {
                const domain = helper.querySelector("span.domain");
                if (domain) {
                    domain.textContent = response.domain;
                }
                const ok = helper.querySelector(".build-domain-helper_status-true");
                if (ok) {
                    ok.style.display = "";
                }
                if (submitBtn) {
                    submitBtn.disabled = false;
                }
            } else {
                const failed = helper.querySelector(".build-domain-helper_status-false");
                if (failed) {
                    failed.textContent = response.answer;
                    failed.style.display = "";
                }
            }
        });
    });
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", setup);
} else {
    setup();
}
