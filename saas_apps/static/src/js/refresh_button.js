/* Copyright 2020 Vildan Safin <https://it-projects.info/team/Enigma228322>
   License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).*/
import { registry } from "@web/core/registry";
import { ListController } from "@web/views/list/list_controller";
import { listView } from "@web/views/list/list_view";

export class ManageAppsController extends ListController {
    async onRefreshApps() {
        // Reload the saas.app records from ir.module.module of this instance
        await this.orm.call(this.props.resModel, "action_make_applist_from_local_instance", [], {});
        await this.model.root.load();
    }
}

registry.category("views").add("saas_apps_tree", {
    ...listView,
    Controller: ManageAppsController,
    buttonTemplate: "saas_apps.ListView.Buttons",
});
