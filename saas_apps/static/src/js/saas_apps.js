/* Copyright 2020 Vildan Safin <https://www.it-projects.info/team/Enigma228322>
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).*/
import { _t, translationIsReady } from "@web/core/l10n/translation";
import { rpc } from "@web/core/network/rpc";

const MONTHLY = "month";
const ANNUALLY = "year";

const state = {
    basketApps: new Set(),
    chosenPackageId: null,
    period: ANNUALLY,
};

const node = (id) => document.getElementById(id);
const nodes = (selector, root = document) => [...(root || document).querySelectorAll(selector)];

function dependsOf(el) {
    return (el.dataset.depends || "").split(",").filter(Boolean);
}

function nameOf(el) {
    return el.dataset.name;
}

function appNodes() {
    return nodes(".app");
}

function priceOf(el, period = state.period) {
    return parseFloat(el.dataset[`price${capitalize(period)}`] || 0);
}

function productIdOf(el, period = state.period) {
    return el.dataset[`productId${capitalize(period)}`];
}

function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function userQty() {
    const input = node("users");
    if (!input) {
        return 1;
    }
    const value = parseInt(input.value, 10);
    return Number.isNaN(value) || value <= 0 ? 1 : value;
}

function sanitizeUserInput() {
    const input = node("users");
    if (input) {
        input.value = userQty();
    }
}

function chosenApps() {
    return appNodes().filter((el) => state.basketApps.has(nameOf(el)));
}

function chosenPackages() {
    return nodes(".package").filter((el) => el.dataset.packageId === state.chosenPackageId);
}

function renderBillingPeriod() {
    for (const el of nodes(".switch-period")) {
        const active = el.dataset.period === state.period;
        el.classList.toggle("active", active);
        el.setAttribute("aria-current", String(active));
    }
    for (const el of nodes(".yearly-price")) {
        el.classList.toggle("hid", state.period !== ANNUALLY);
    }
    for (const el of nodes(".monthly-price")) {
        el.classList.toggle("hid", state.period !== MONTHLY);
    }
}

function renderTotalPrice() {
    renderBillingPeriod();
    const apps = chosenApps();
    const packages = chosenPackages();
    const sumApps = apps.reduce((acc, el) => acc + priceOf(el), 0);
    const sumPackages = packages.reduce((acc, el) => acc + priceOf(el), 0);
    const qty = userQty();
    const usersBlock = node("users_block");
    const sumUsers = qty * parseFloat(usersBlock ? usersBlock.dataset[`price${capitalize(state.period)}`] || 0 : 0);

    setText("price", String(sumApps + sumPackages + sumUsers));
    setText("box-period", state.period === MONTHLY ? _t("month") : _t("year"));
    setText("users-qty", String(qty));
    setText("users-cnt-cost", String(sumUsers));
    setText("apps-qty", String(apps.length + packages.length));
    setText("apps-cost", String(sumApps + sumPackages));

    const btnBlock = node("btn-block");
    if (btnBlock) {
        btnBlock.style.display = apps.length || packages.length ? "" : "none";
    }
}

function setText(id, value) {
    const el = node(id);
    if (el) {
        el.textContent = value;
    }
}

function renderApps() {
    for (const el of appNodes()) {
        el.classList.toggle("green-border", state.basketApps.has(nameOf(el)));
    }
}

function renderPackages() {
    for (const el of nodes(".package")) {
        el.classList.toggle("green-border", el.dataset.packageId === state.chosenPackageId);
    }
}

function selectApp(el) {
    const name = nameOf(el);
    state.basketApps.add(name);
    for (const depend of dependsOf(el)) {
        state.basketApps.add(depend);
    }
}

function deselectApp(name) {
    // Removing an app also removes the apps that depend on it, recursively.
    const queue = [name];
    while (queue.length) {
        const current = queue.shift();
        state.basketApps.delete(current);
        for (const el of appNodes()) {
            if (dependsOf(el).includes(current)) {
                queue.push(nameOf(el));
            }
        }
    }
}

function goToBuild(buildParams, templateId) {
    rpc("/check_saas_template", { template_id: templateId }).then((template) => {
        if (template.state === "ready") {
            window.location.href = `/saas_public/${template.id}/create-fast-build${buildParams}`;
        } else {
            setTimeout(() => goToBuild(buildParams, templateId), 5000);
        }
    });
}

function showLoader() {
    for (const el of nodes(".loader")) {
        el.style.display = "";
    }
}

export function getInputs() {
    sanitizeUserInput();
    return {
        chosen_apps: [...state.basketApps],
        chosen_package_id: state.chosenPackageId,
        period: state.period,
        user_cnt: userQty(),
    };
}

function onAppClick(el) {
    state.chosenPackageId = null;
    const name = nameOf(el);
    if (state.basketApps.has(name)) {
        deselectApp(name);
    } else {
        selectApp(el);
    }
    renderApps();
    renderPackages();
    renderTotalPrice();
}

function onPackageClick(el) {
    state.basketApps.clear();
    const packageId = el.dataset.packageId;
    state.chosenPackageId = state.chosenPackageId === packageId ? null : packageId;
    renderApps();
    renderPackages();
    renderTotalPrice();
}

function setup() {
    if (!document.querySelector(".js_saas_apps")) {
        return;
    }

    for (const el of appNodes()) {
        el.addEventListener("click", () => onAppClick(el));
    }
    for (const el of nodes(".package")) {
        el.addEventListener("click", () => onPackageClick(el));
    }
    for (const el of nodes(".switch-period")) {
        el.addEventListener("click", (event) => {
            event.preventDefault();
            state.period = el.dataset.period;
            renderTotalPrice();
        });
    }

    const usersInput = node("users");
    if (usersInput) {
        usersInput.addEventListener("input", renderTotalPrice);
        const minus = node("minus-user");
        if (minus) {
            minus.addEventListener("click", () => {
                sanitizeUserInput();
                usersInput.value = Math.max(1, userQty() - 1);
                renderTotalPrice();
            });
        }
        const plus = node("plus-user");
        if (plus) {
            plus.addEventListener("click", () => {
                sanitizeUserInput();
                usersInput.value = userQty() + 1;
                renderTotalPrice();
            });
        }
    }

    const tryTrial = node("try-trial");
    if (tryTrial) {
        tryTrial.addEventListener("click", () => {
            if (state.basketApps.size > 0) {
                goToBuild(`?installing_modules=${JSON.stringify([...state.basketApps])}`);
                showLoader();
            } else if (state.chosenPackageId) {
                goToBuild("", parseInt(state.chosenPackageId, 10));
                showLoader();
            } else {
                window.alert(_t("Please, choose apps or package first"));
            }
        });
    }

    const buyNow = node("buy-now");
    if (buyNow) {
        buyNow.addEventListener("click", () => {
            let productIds = [];
            if (state.basketApps.size > 0) {
                productIds = [...state.basketApps].map((name) => {
                    const el = document.querySelector(`.app[data-name="${name}"]`);
                    return el ? productIdOf(el) : undefined;
                });
            } else if (state.chosenPackageId) {
                const el = document.querySelector(`.package[data-package-id="${state.chosenPackageId}"]`);
                productIds = el ? [productIdOf(el)] : [];
            } else {
                window.alert(_t("Please, choose apps or package first"));
                return;
            }

            rpc("/price/cart/update_json", {
                product_ids: productIds,
                period: state.period,
                user_cnt: userQty(),
            }).then((res) => {
                window.location.href = res.link;
            });
        });
    }

    renderTotalPrice();
}

// Website translations are initialized by the public root after assets load.
// Do not evaluate _t() during module startup, before that initialization.
function start() {
    translationIsReady.then(setup);
}

if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
} else {
    start();
}

export { MONTHLY, ANNUALLY };
