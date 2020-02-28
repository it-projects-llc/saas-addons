# Copyright 2020 Vildan Safin <https://github.com/Enigma228322>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models
import logging

_logger = logging.getLogger(__name__)

class SAASBasket(models.Model):
    _name = 'saas.basket'
    _description = 'Module for selecting applications'

    users = fields.Integer(default=0)
    module_sets_in_basket = fields.One2many('saas.set', 'basket', ondelete="cascade", delegate=True)
    final_basket_price = fields.Float(default=0.0, compute='_compute_price', string="Price of the set")

    def _compute_price(self):
        for module_set in self.module_set_in_basket:
            self.final_basket_price = self.final_basket_price + module_set.price


class SAASLine(models.Model):
    _name = 'saas.lines'
    _description = 'Model line'

    module_name = fields.Char(default="default", string="Module Name")
    price = fields.Float(default=0.0, string="Price")
    allow_to_sell = fields.Boolean(string="Sellable")
    icon_path = fields.Char(compute='_compute_path', string="icon path")
    dependencies = fields.Many2one('saas.set', string="Module dependences")
    
    def _compute_path(self): 
        self.icon_path = "/saas_apps/static/src/img/%s.png" % self.module_name
    
    @api.constrains('price')
    def _validate_price(self):
        if self.price < 0:
            self.price = 0
            raise "Price can't be negative."

    def add_new_module(self, name):
        # for module in self:
        #     if(module.module_name == name)
        #         return False
        self.create({
            'module_name': name
        })
        return True
    
    def create(self, cr, user, vals, context=None):
        import wdb
        wdb.set_trace()
        new_id = super(product_test, self).create(cr, user, vals, context)
        irmodules = self.env["ir.module.module"].search([])
        if len(irmodules) > len(self.search([])):
            for irmodule in irmodules:
                if len(self.search([('module_name', '=', irmodule.name)])) == 0:
                    self.create({'module_name': irmodule.name})
        return new_id


class SAASDependence(models.Model):
    _name = 'saas.set'
    _description = 'Module with dependencies'

    basket = fields.Many2one('saas.basket', string='Modules in basket')
    modules = fields.One2many('saas.lines', 'dependencies', ondelete='cascade', delegate=True)
    final_set_price = fields.Float(default=0.0, compute='_compute_price', string="Price of the set")

    def add_dependence(self, new_module_name, new_module_price):
        try:
            self.modules.create({
                'module_name': new_module_name,
                'price': int(new_module_name_price)
            })
        except:
            _logger.error("Can't add new item in dependencies of this module")

    def _compute_price(self):
        for module in self.modules:
            self.final_set_price = self.final_set_price + module.price
