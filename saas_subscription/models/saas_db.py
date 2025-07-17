
from odoo import _, api, models, fields, SUPERUSER_ID



class SaaSDB(models.Model):
    """SaaS DB Model"""
    _inherit = 'saas.db'
    _description = 'Add Subscription to SaaS DB'

    is_subscription = fields.Boolean(string='Is Subscription', default=False)
    subscription_id = fields.Many2one('sale.subscription',
                                      string='Subscription')