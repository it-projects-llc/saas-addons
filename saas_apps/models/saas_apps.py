# Copyright 2020 Vildan Safin <https://github.com/Enigma228322>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
import logging
from slugify import slugify

_logger = logging.getLogger(__name__)


class SAASModule(models.Model):
    _inherit = 'saas.module'

    month_price = fields.Float(default=0.0, string="Month price")
    year_price = fields.Float(default=0.0, string="Year price")
    saas_modules = fields.Many2many('saas.line')

    @api.constrains('month_price')
    def _validate_month_price(self):
        if self.month_price < 0:
            raise ValidationError("Month price can't be negative.")

    @api.constrains('year_price')
    def _validate_year_price(self):
        if self.year_price < 0:
            raise ValidationError("Year price can't be negative.")

    def add_new_module(self, name):
        self.create({
            'name': name
        })
        return True

    def refresh_modules(self):
        for app in map(self.browse, self._search([])):
            app.unlink()
        irmodules = self.env["ir.module.module"].search([])
        for irmodule in irmodules:
            if len(self.search([('name', '=', irmodule.name)])) == 0:
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
    year_price = fields.Float(default=0.0, compute='_compute_year_price', string="Price per year")
    month_price = fields.Float(default=0.0, compute='_compute_month_price', string="Price per month")

    def refresh_lines(self):
        apps = self.env["saas.module"]
        for line in map(self.browse, self._search([])):
            line.unlink()
        apps.refresh_modules()
        base_icon_path = '/base/static/description/icon.png'
        for app in apps.search([]):
            if len(self.search([('name', '=', app.name)])) == 0:
                ir_module_obj = self.env["ir.module.module"].get_module_info(app.name)
                if len(ir_module_obj):
                    if ir_module_obj['application']:
                        new = self.create({
                            'name': app.name,
                            'module_name': ir_module_obj['name'],
                            'icon_path': ir_module_obj['icon']
                        })
                        new.dependencies += apps.search([('name', '=', app.name)])
                        for dep_name in ir_module_obj['depends']:
                            new.dependencies += apps.search([('name', '=', dep_name)])
                else:
                    new = self.create({
                        'name': app.name,
                        'module_name': app.name,
                        'icon_path': base_icon_path
                    })

    def _compute_year_price(self):
        self.year_price = 0
        for module in self.dependencies:
            self.year_price += module.year_price

    def _compute_month_price(self):
        self.month_price = 0
        for module in self.dependencies:
            self.month_price += module.month_price

    def dependencies_info(self, root):
        apps = []
        childs = []
        saas_module = self.dependencies.search([('name', '=', self.name)])
        for child in self.dependencies - saas_module:
            if len(self.search([('name', '=', child.name)])):
                childs.append(child.name)
        apps.append({
            'parent': root,
            'name': self.name,
            'year_price': saas_module.year_price,
            'month_price': saas_module.month_price,
            'childs': childs
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
    def write(self, vals):
        res = super(SAASDependence, self).write(vals)
        # If value of allow_to_sell changed, other sets allow_to_sell vars should be changed too
        if "allow_to_sell" in vals and vals['allow_to_sell']:
            this_app = self.dependencies.search([('name', '=', self.name)])
            for app in self.dependencies - this_app:
                temp_app = self.search([('name', '=', app.name)])
                if len(temp_app) > 0:
                    temp_app.allow_to_sell = vals['allow_to_sell']
        return res


class SAASTemplateLine(models.Model):
    _inherit = 'saas.template.operator'


    @api.multi
    def write(self, vals):
        if 'state' in vals:
            _logger.debug(vals['state'])
        return super(SAASTemplateLine, self).write(vals)

    @api.multi
    def random_ready_operator_check(self):
        ready_operators = self.filtered(lambda r: r.state == 'done')
        if len(ready_operators) > 0:
            return True
        return False
