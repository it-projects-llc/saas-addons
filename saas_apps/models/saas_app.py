import logging
from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class SaasApp(models.Model):
    _name = "saas.app"
    _description = "SaaS App"
    _order = "name"
    _inherit = "saas.period.product.mixin"

    name = fields.Char("Technical Name", required=True, index=True)
    shortdesc = fields.Char("Module Name", required=True)
    dependency_ids = fields.Many2many("saas.app", "saas_apps_dependency_rel", "dep_id", "app_id", string="Dependencies")
    icon_image = fields.Binary("Icon", related="product_tmpl_id.image_1920", readonly=False)

    allow_to_sell = fields.Boolean(default=True, string="Sellable")

    # TODO: add non-storable compute field like "Are cyclic dependency detected?"

    @api.model_create_multi
    def create(self, vals_list):
        records = super(SaasApp, self).create(vals_list)
        for res, vals in zip(records, vals_list):
            if not res.product_tmpl_id:
                res.product_tmpl_id = self.env["product.template"].create({
                    "name": res.shortdesc,
                    "image_1920": res.icon_image,
                    "saas_app_id": res.id,
                    "is_saas_product": True,
                    "website_published": True,
                    "list_price": 0,
                })
            # create() inverts month_price/year_price before the product template is
            # linked, so the requested prices have to be applied again now that the
            # subscription variants exist.
            prices = {key: vals[key] for key in ("month_price", "year_price") if vals.get(key)}
            if prices:
                res.write(prices)
        return records

    def _search_or_create(self, ir_module):
        app = self.search([("name", "=", ir_module.name)])
        if not app:
            app = self.env["saas.app"].create({
                "name": ir_module.name,
                "shortdesc": ir_module.shortdesc,
                "icon_image": ir_module.icon_image
            })
        return app

    def dependencies_str(self):
        self.ensure_one()
        visited_saas_module_ids = set()

        def make_list(deps):
            result = []
            for dep in deps:
                if dep.id in visited_saas_module_ids:
                    continue

                visited_saas_module_ids.add(dep.id)
                result += [dep.name] + make_list(dep.dependency_ids)
            return result

        return ",".join(make_list(self.dependency_ids))

    @api.model
    def action_make_applist_from_local_instance(self):
        modules = self.env["ir.module.module"].sudo().search([("state", "!=", "uninstallable")])
        dependencies = {module.name: set(module.dependencies_id.mapped("name")) for module in modules}
        dependents = {}
        for name, names in dependencies.items():
            for dependency in names:
                dependents.setdefault(dependency, set()).add(name)

        reachable = set()
        pending = ["base"]
        while pending:
            name = pending.pop()
            if name not in reachable:
                reachable.add(name)
                pending.extend(dependents.get(name, ()))

        applications = modules.filtered(lambda module: module.application and module.name in reachable)
        apps = {app.name: app for app in self.search([("name", "in", applications.mapped("name"))])}
        missing = applications.filtered(lambda module: module.name not in apps)
        for app in self.create([{
            "name": module.name, "shortdesc": module.shortdesc or module.name, "icon_image": module.icon_image,
        } for module in missing]):
            apps[app.name] = app

        for module in applications:
            visited = {module.name}
            required_apps = set()
            pending = list(dependencies.get(module.name, ()))
            while pending:
                name = pending.pop()
                if name in visited:
                    continue
                visited.add(name)
                if name in apps:
                    required_apps.add(apps[name].id)
                else:
                    pending.extend(dependencies.get(name, ()))
            apps[module.name].dependency_ids = [(6, 0, sorted(required_apps))]
