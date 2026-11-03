/* Copyright IT-Projects LLC; AGPL-3.0. */
import { rpc } from "@web/core/network/rpc";

function setupBuildStatus() {
    const card = document.querySelector(".js_saas_build_status");
    if (!card || card.dataset.ready === "true" || card.dataset.polling) return;
    card.dataset.polling = "true";
    const accessToken = new URLSearchParams(window.location.search).get("access_token");
    let timer;
    let stopped = false;
    const setText = (selector, value) => {
        const element = card.querySelector(selector);
        if (element) element.textContent = String(value);
    };
    async function poll() {
        if (stopped || !card.isConnected) return;
        if (document.hidden) { timer = setTimeout(poll, 5000); return; }
        try {
            const status = await rpc(`/my/build/${card.dataset.buildId}/status`, { access_token: accessToken });
            if (stopped) return;
            setText("[data-build-pending]", status.pending);
            setText("[data-build-users]", status.users);
            setText("[data-build-limit]", status.limit);
            setText("[data-build-expiration]", status.expiration);
            const draft = card.querySelector("[data-build-draft]");
            if (draft) draft.hidden = status.state !== "draft";
            const link = card.querySelector("[data-build-link]");
            if (link) {
                if (status.ready) link.href = status.url;
                link.hidden = !status.ready;
            }
            card.dataset.ready = String(status.ready);
            if (status.ready) { stopped = true; return; }
        } catch {
            // Keep the current page usable and retry transient provisioning/server errors.
        }
        timer = setTimeout(poll, 2000);
    }
    timer = setTimeout(poll, 1000);
    window.addEventListener("pagehide", () => {
        stopped = true;
        clearTimeout(timer);
        delete card.dataset.polling;
    }, { once: true });
}
if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", setupBuildStatus);
else setupBuildStatus();
window.addEventListener("pageshow", (event) => { if (event.persisted) setupBuildStatus(); });
