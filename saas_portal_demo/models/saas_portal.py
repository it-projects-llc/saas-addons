from odoo import models, api, SUPERUSER_ID, fields


class SaasPortalPlan(models.Model):
    _inherit = 'saas_portal.plan'

    demo_plan_module_ids = fields.One2many('saas_portal.demo_plan_module', 'demo_plan_id',
                                           help="The modules that should be in this demo plan", string='Modules')
    demo_plan_hidden_module_ids = fields.One2many('saas_portal.hidden_demo_plan_module', 'demo_plan_id',
                                                  help="The modules that should be in this demo plan", string='Modules')

    @api.multi
    def create_new_database(self, **kwargs):
        res = super(SaasPortalPlan, self).create_new_database(**kwargs)
        user_id = kwargs.get('user_id')
        user = user_id and user_id != SUPERUSER_ID and self.env['res.users'].browse(user_id)
        if user:
            user.action_id = self.env.ref('saas_portal_demo.action_open_my_instances').id
        return res
