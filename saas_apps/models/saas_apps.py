# Copyright 2020 Vildan Safin <https://github.com/Enigma228322>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)


class SAASModule(models.Model):
    _name = 'saas.module'
    _description = 'Model line'

    name = fields.Char(default="default", string="Module Name")
    month_price = fields.Float(default=0.0, string="Month price")
    year_price = fields.Float(default=0.0, string="Year price")
    icon_path = fields.Char(compute='_compute_path', string="icon path")
    saas_modules = fields.Many2one('saas.line', string="Module dependencies")
    
    def _compute_path(self): 
        self.icon_path = "/saas_apps/static/src/img/%s.png" % self.name
    
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
        if len(irmodules) > len(self.search([])):
            for irmodule in irmodules:
                if len(self.search([('name', '=', irmodule.name)])) == 0:
                    self.create({'name': irmodule.name})


class SAASDependence(models.Model):
    _name = 'saas.line'
    _description = 'Module dependencies'

    # First dependence is root module
    name = fields.Char(default="default", string="Module Name")
    allow_to_sell = fields.Boolean(string="Sellable")
    dependencies = fields.One2many('saas.module', 'saas_modules', ondelete='cascade', delegate=True)
    year_price = fields.Float(default=0.0, compute='_compute_year_price', string="Price per year")
    month_price = fields.Float(default=0.0, compute='_compute_month_price', string="Price per month")

    def refresh(self):
        apps = self.env["saas.module"]
        apps.refresh()
        apps = apps.search([])
        if len(apps) > len(self.search([])):
            for app in apps:
                if len(self.search([('name', '=', app.name)])) == 0:
                    new = self.create({'name': app.name})
                    new.dependencies += app

    def _compute_year_price(self):
        for module in self.dependencies:
            self.year_price += module.year_price

    def _compute_month_price(self):
        for module in self.dependencies:
            self.month_price += module.month_price

    def dependencies_info(self):
        apps = []
        for app in self.dependencies:
            apps.append(app.name)
        return apps

    @api.multi
    def write(self, vals):
        last_value = self.allow_to_sell
        res = super(SAASDependence, self).write(vals)
        if vals['allow_to_sell'] != last_value and not last_value:
            for app in self.dependencies:
                self.search([('name', '=', app.name)]).allow_to_sell = True
        return res
