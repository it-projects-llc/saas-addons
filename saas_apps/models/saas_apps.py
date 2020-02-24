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

    module_name = fields.Char(default="default")
    price = fields.Float(default=0.0)
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
        import wdb
        wdb.set_trace()
        # for module in self:
        #     if(module.module_name == name)
        #         return False
        self.create({
            'name': name
        })
        return True


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


# class IrModuleModule(models.Model):
#     _inherit = "ir.module.module"

#     allow_to_sell = fields.Boolean(default=False)
