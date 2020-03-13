# Copyright 2020 Vildan Safin <https://github.com/Enigma228322>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models, modules
import logging

_logger = logging.getLogger(__name__)


class SAASModule(models.Model):
    _inherit = 'saas.module'

    month_price = fields.Float(default=0.0, string="Month price")
    year_price = fields.Float(default=0.0, string="Year price")
    icon_path = fields.Char(string="Icon path")
    saas_modules = fields.Many2one('saas.line', string="Module dependencies")
    
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
        if len(irmodules) > len(self.search([])):
            for irmodule in irmodules:
                if len(self.search([('name', '=', irmodule.name)])) == 0:
                    self.create({'name': irmodule.name})


class SAASDependence(models.Model):
    _name = 'saas.line'
    _description = 'Module dependencies'

    # First dependence is root module
    name = fields.Char(default="default", string="Module technical name")
    module_name = fields.Char(default="default", string="Module name")
    allow_to_sell = fields.Boolean(string="Sellable")
    dependencies = fields.One2many('saas.module', 'saas_modules', ondelete='cascade', delegate=True)
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
                    new = self.create({
                        'name': app.name,
                        'module_name': app.module_name
                    })
                    if len(ir_module_obj.get_module_info(app.name)):
                        for dep_name in ir_module_obj.get_module_info(app.name)['depends']:
                            new.dependencies += app.search([('name', '=', dep_name)])
            except:
                # import wdb
                # wdb.set_trace()
                _logger.error("Fuck!")

    def _compute_year_price(self):
        for module in self.dependencies:
            self.year_price += module.year_price

    def _compute_month_price(self):
        for module in self.dependencies:
            self.month_price += module.month_price

    def dependencies_info(self, root):
        apps = []
        childs = []
        for child in self.dependencies - self.dependencies[0]:
            childs.append(child.module_name)
        apps.append({
            'parent': root,
            'name': self.module_name,
            'year_price': self.dependencies[0].year_price,
            'month_price': self.dependencies[0].month_price,
            'childs': childs,
            'icon_path': self.dependencies[0].icon_path
        })
        # Looking to the period
        for app in self.dependencies - self.dependencies[0]:
            set = self.search([('name', '=', app.name)])
            leafs = set.dependencies_info(self.name)
            for leaf in leafs:
                if not(leaf in apps):
                    apps.append(leaf)
        return apps

    @api.multi
    def write(self, vals):
        last_value = self.allow_to_sell
        res = super(SAASDependence, self).write(vals)
        # If value of allow_to_sell changed, other sets allow_to_sell vars should be changed too
        # If it's not, then if root modules(self) allow_to_sell value is True, then other sets allow_to_sell values should be True
        if "allow_to_sell" in vals:
            if vals['allow_to_sell'] != last_value and not last_value:
                for app in self.dependencies:
                    self.search([('name', '=', app.name)]).allow_to_sell = vals['allow_to_sell']
        else:
            if last_value:
                for app in self.dependencies:
                    self.search([('name', '=', app.name)]).allow_to_sell = True
        return res
