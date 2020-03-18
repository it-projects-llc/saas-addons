# Copyright 2020 Vildan Safin <https://github.com/Enigma228322>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, modules
import logging

_logger = logging.getLogger(__name__)


class SAASModule(models.Model):
    _inherit = 'saas.module'

    month_price = fields.Float(default=0.0, string="Month price")
    year_price = fields.Float(default=0.0, string="Year price")
    saas_modules = fields.Many2many('saas.line')
    
    @api.model
    def create(self, vals):
        rec = super(SAASModule, self).create(vals)
        if len(self.saas_modules) > 0:
            self.name = self.saas_modules.name
        return rec
    
    @api.constrains('month_price', 'year_price')
    def _validate_price(self):
        if self.month_price < 0 or self.year_price < 0:
            raise "Price can't be negative."

    def add_new_module(self, name):
        self.create({
            'name': name
        })
        return True
    
    def refresh(self):
        irmodules = self.env["ir.module.module"].search([])
        ir_module_obj = self.env["ir.module.module"]
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
    allow_to_sell = fields.Boolean(string="Sellable")
    dependencies = fields.Many2many('saas.module')
    year_price = fields.Float(default=0.0, compute='_compute_year_price', string="Price per year")
    month_price = fields.Float(default=0.0, compute='_compute_month_price', string="Price per month")

    def refresh(self):
        apps = self.env["saas.module"]
        apps.search([]).unlink()
        self.search([]).unlink()
        apps.refresh()
        for app in apps.search([]):
            try:
                if len(self.search([('name', '=', app.name)])) == 0:
                    ir_module_obj = self.env["ir.module.module"].get_module_info(app.name)
                    if len(ir_module_obj):
                        new = self.create({
                            'name': app.name,
                            'module_name': ir_module_obj['name'],
                            'icon_path': ir_module_obj['icon']
                        })
                        new.dependencies += apps.search([('name', '=', app.name)])
                        for dep_name in ir_module_obj['depends']:
                            new.dependencies += apps.search([('name', '=', dep_name)])
                    else:
                        new = self.create({ 'name': app.name })
            except:
                _logger.error("Fuck!Fuck!Fuck!Fuck!Fuck!Fuck!")

    def _compute_year_price(self):
        for module in self.dependencies:
            self.year_price += module.year_price

    def _compute_month_price(self):
        for module in self.dependencies:
            self.month_price += module.month_price

    def dependencies_info(self, root):
        apps = []
        childs = []
        saas_module = self.dependencies.search([('name', '=', self.name)])
        for child in self.dependencies - saas_module:
            childs.append(child.name)
        apps.append({
            'parent': root,
            'name': self.name,
            'year_price': saas_module.year_price,
            'month_price': saas_module.month_price,
            'childs': childs,
            'icon_path': self.icon_path
        })
        # Looking to the period
        for app in self.dependencies - saas_module:
            set = self.search([('name', '=', app.name)])
            leafs = set.dependencies_info(self.name)
            for leaf in leafs:
                if not(leaf in apps):
                    apps.append(leaf)
        return apps

    @api.multi
    def write(self, vals):
        res = super(SAASDependence, self).write(vals)
        # If value of allow_to_sell changed, other sets allow_to_sell vars should be changed too
        if "allow_to_sell" in vals:
            this_app = self.dependencies.search([('name', '=', self.name)])
            for app in self.dependencies - this_app:
                self.search([('name', '=', app.name)]).allow_to_sell = vals['allow_to_sell']
        return res
