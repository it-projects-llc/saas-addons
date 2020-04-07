# Copyright 2020 Vildan Safin <https://github.com/Enigma228322>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
import logging
from slugify import slugify

_logger = logging.getLogger(__name__)


class SAASModule(models.Model):
    _inherit = 'saas.module'

    month_price = fields.Float('Month price', default=0.0)
    year_price = fields.Float('Year price', default=0.0)
    saas_modules = fields.Many2many('saas.line')

    @api.constrains('month_price')
    def _validate_month_price(self):
        if self.month_price < 0:
            raise ValidationError("Month price can't be negative.")

    @api.constrains('year_price')
    def _validate_year_price(self):
        if self.year_price < 0:
            raise ValidationError("Year price can't be negative.")

    @api.multi
    def write(self, vals):
        res = super(SAASModule, self).write(vals)
        if 'month_price' in vals or 'year_price' in vals:
            for line in self.saas_modules:
                line.compute_price()
        return res

    def refresh_modules(self):
        for app in map(self.browse, self._search([])):
            app.unlink()
        irmodules = self.env["ir.module.module"].search([])
        for irmodule in irmodules:
            if self.search_count([('name', '=', irmodule.name)]) == 0:
                self.create({'name': irmodule.name})


class SAASDependence(models.Model):
    _name = 'saas.line'
    _description = 'Module dependencies'

    # First dependence is root module
    name = fields.Char(default="default", string="Module technical name")
    module_name = fields.Char(default="default", string="Module name")
    icon_path = fields.Char(string="Icon path")
    allow_to_sell = fields.Boolean(default=True, string="Sellable")
    dependencies = fields.Many2many('saas.module')
    year_price = fields.Float(default=0.0, string="Price per year")
    month_price = fields.Float(default=0.0, string="Price per month")
    application = fields.Boolean(default=False, string="Application")

    def refresh_lines(self):
        apps = self.env["saas.module"]
        for line in map(self.browse, self._search([])):
            line.unlink()
        apps.refresh_modules()
        base_icon_path = '/base/static/description/icon.png'
        for app in apps.search([]):
            if self.search_count([('name', '=', app.name)]) == 0:
                ir_module_obj = self.env["ir.module.module"].get_module_info(app.name)
                if len(ir_module_obj):
                    new = self.create({
                        'name': app.name,
                        'module_name': ir_module_obj['name'],
                        'icon_path': ir_module_obj['icon']
                    })
                    if ir_module_obj['application']:
                        new.application = True
                    new.dependencies += apps.search([('name', '=', app.name)])
                    for dep_name in ir_module_obj['depends']:
                        new.dependencies += apps.search([('name', '=', dep_name)])
                else:
                    new = self.create({
                        'name': app.name,
                        'module_name': app.name,
                        'icon_path': base_icon_path
                    })

    @api.multi
    def compute_price(self):
        sum = 0
        for module in self.dependencies:
            sum += module.year_price
        self.year_price = sum
        sum = 0
        for module in self.dependencies:
            sum += module.month_price
        self.month_price = sum

    def dependencies_info(self, root):
        apps = []
        childs = []
        saas_module = self.dependencies.search([('name', '=', self.name)])
        for child in self.dependencies - saas_module:
            if self.search_count([('name', '=', child.name)]):
                childs.append(child.name)
        apps.append({
            'parent': root,
            'name': self.name,
            'year_price': saas_module.year_price,
            'month_price': saas_module.month_price,
            'childs': childs,
            'application': self.application
        })
        # Looking to the period
        for app in self.dependencies - saas_module:
            set = self.search([('name', '=', app.name)])
            if len(set) == 0:
                continue
            leafs = set.dependencies_info(self.name)
            for leaf in leafs:
                if not(leaf in apps):
                    apps.append(leaf)
        return apps

    @api.multi
    def change_allow_to_sell(self):
        this_app = self.dependencies.search([('name', '=', self.name)])
        for app in self.dependencies - this_app:
            temp_app = self.search([('name', '=', app.name)])
            if len(temp_app) > 0:
                temp_app.allow_to_sell = True

    @api.multi
    def write(self, vals):
        res = super(SAASDependence, self).write(vals)
        # If value of allow_to_sell changed, other sets allow_to_sell vars should be changed too
        if "allow_to_sell" in vals and vals['allow_to_sell']:
            self.change_allow_to_sell()
        return res


class SAASTemplateLine(models.Model):
    _inherit = 'saas.template.operator'

    @api.multi
    def random_ready_operator_check(self):
        ready_operators = self.filtered(lambda r: r.state == 'done')
        if len(ready_operators) > 0:
            return True
        return False
