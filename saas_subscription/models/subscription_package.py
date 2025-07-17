import datetime
from dateutil.relativedelta import relativedelta
from odoo import _, api, models, fields, SUPERUSER_ID
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class SubscriptionPackage(models.Model):
    """Subscription Package Model"""
    _inherit = 'subscription.package'
    _description = 'Subscription Package'

    @api.model
    def _get_number_of_days_for_trial(self):
        return int(
            self.sudo()
            .env["ir.config_parameter"]
            .get_param("saas_expiration.number_of_days_for_trial", 7)
        )

    is_saas = fields.Boolean(string='is SaaS', compute='_compute_is_saas')
    subdomain = fields.Char(string='Subdomain', store=True)
    operator_id = fields.Many2one('saas.operator', string='Operator')
    template_operator_id = fields.Many2one(
        'saas.template.operator',
        'Template\'s Deployment', store=True,
        ondelete='cascade')
    build_count = fields.Integer(string='Sales', compute='_compute_build_count')
    expiration_date = fields.Datetime(
        "Expiration date",
        default=lambda self: datetime.now() + timedelta(days=self._get_number_of_days_for_trial()),
    )

    @api.constrains('start_date')
    def _compute_expiration_date(self):
        for sub in self.env['subscription.package'].search([]):
            if sub.start_date:
                sub.next_invoice_date = sub.start_date + relativedelta(
                    days=sub.plan_id.renewal_time)

    def _compute_is_saas(self):
        self.ensure_one()
        product_lines = self.product_line_ids
        if not product_lines:
            self.is_saas = False
        else:
            for line in product_lines:
                product = line.product_id
                is_saas_product = product.is_saas_product
                if is_saas_product:
                    self.is_saas = True
                else:
                    self.is_saas = False
        return self.is_saas

    def _find_admin_user(self):
        admin = self.env['res.users'].search([('partner_id','=', self.partner_id.id)])
        if not admin:
            raise ValidationError(_("This partner doesn't have portal user. Please Create Portal User for the Partner"))
        return admin

    def _find_number_user(self):
        product_lines = self.product_line_ids
        for line in product_lines:
            qty = line.product_qty
            return qty

    def create_db_button(self):
        self.ensure_one()
        db_name = self.subdomain
        key_value_dict = False
        build = self.template_operator_id.sudo().create_db(key_value_dict, db_name)
        admin_user = self._find_admin_user()
        number_users = self._find_number_user()
        build.update({
            'is_subscription': True,
            'subscription_id': self.id,
            'sub_reference': self.reference_code,
            'admin_user': admin_user,
            'max_users_limit': number_users,
            'expiration_date': self.expiration_date,
        })
        build.refresh_data()

    @api.depends('build_count')
    def _compute_build_count(self):
        """ Calculate build count based on subscription package """
        self.build_count = self.env['saas.db'].search_count(
            [('subscription_id', '=', self.id)])

    def button_build_count(self):
        """ It displays sale order based on subscription package """
        return {
            'name': 'Builds',
            'domain': [('subscription_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'saas.db',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'context': {
                "create": False
            }
        }
