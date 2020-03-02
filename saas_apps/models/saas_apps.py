# Copyright 2020 Vildan Safin <https://github.com/Enigma228322>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

# class SAASBasket(models.Model):
#     _name = 'saas.basket'
#     _description = 'Module for selecting applications'

#     users = fields.Integer(default=0)
#     name = fields.Char(default="Basket", string="Basket Name")
#     modules_in_basket = fields.One2many('saas.lines', 'basket', ondelete="cascade", delegate=True)
#     final_basket_price = fields.Float(default=0.0, compute='_compute_price', string="Price of the set")

#     def _compute_price(self):
#         if len(self.modules_in_basket) > 0:
#             for module in self.modules_in_basket:
#                 self.final_basket_price += module.final_set_price


class SAASLine(models.Model):
    _name = 'saas.lines'
    _description = 'Model line'

    module_name = fields.Char(default="default", string="Module Name")
    price = fields.Float(default=0.0, string="Price")
    allow_to_sell = fields.Boolean(string="Sellable")
    icon_path = fields.Char(compute='_compute_path', string="icon path")
    dependencies = fields.One2many('saas.set', 'saas_modules', ondelete='cascade', delegate=True)
    final_set_price = fields.Float(default=0.0, compute='_compute_price', string="Price of the set")
    # basket = fields.Many2one('saas.basket', string='Modules in basket')
    
    def _compute_path(self): 
        self.icon_path = "/saas_apps/static/src/img/%s.png" % self.module_name
        
    def _compute_price(self):
        self.final_set_price = self.price
        for module in self.dependencies:
            self.final_set_price += module.saas_modules.price
    
    @api.constrains('price')
    def _validate_price(self):
        if self.price < 0:
            self.price = 0
            raise "Price can't be negative."

    def add_new_module(self, name):
        self.create({
            'module_name': name
        })
        return True
    
    def refresh(self):
        irmodules = self.env["ir.module.module"].search([])
        if len(irmodules) > len(self.search([])):
            for irmodule in irmodules:
                if len(self.search([('module_name', '=', irmodule.name)])) == 0:
                    self.create({'module_name': irmodule.name})
    
    def dependencies_info(self):
        apps = []
        for app in self.dependencies:
            apps.append(app.saas_modules.module_name)
        return apps


class SAASDependence(models.Model):
    _name = 'saas.set'
    _description = 'Module dependencies'

    saas_modules = fields.Many2one('saas.lines', string="Module dependencies")
    # module = fields.One2many()
