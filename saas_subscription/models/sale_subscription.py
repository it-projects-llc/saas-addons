# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, models, fields, SUPERUSER_ID
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError

class SaleSubscription(models.Model):
    _inherit = "sale.subscription"
    _description = "Subscription"

    @api.model
    def _get_number_of_days_for_trial(self):
        return int(
            self.sudo()
            .env["ir.config_parameter"]
            .get_param("saas_expiration.number_of_days_for_trial", 7)
        )

    is_saas = fields.Boolean(string='is SaaS',compute='_compute_is_saas')
    subdomain = fields.Char(string='Subdomain', store=True)
    operator_id = fields.Many2one('saas.operator', string='Operator')
    template_operator_id = fields.Many2one(
        'saas.template.operator',
        'Template\'s Deployment', store=True,
        ondelete='cascade')
    build_count = fields.Integer(string='Builds', compute='_compute_build_count' )
    expiration_date = fields.Datetime(
        "Expiration date",
    )

    def _compute_is_saas(self):
        self.ensure_one()
        product_lines = self.sale_subscription_line_ids
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
        admin = self.env['res.users'].search([('partner_id', '=', self.partner_id.id)])
        if not admin:
            raise ValidationError(_("This partner doesn't have portal user. Please Create Portal User for the Partner"))
        return admin

    def _find_number_user(self):
        product_lines = self.sale_subscription_line_ids
        for line in product_lines:
            qty = line.product_uom_qty
            return qty

    def create_db_button(self):
        self.ensure_one()
        db_name = self.subdomain
        key_value_dict = False
        existing_db = [db[0] for db in self.list_databases()]
        build_name = db_name
        if build_name in existing_db:
            raise ValidationError("Une base de données avec ce nom existe déjà.")
        build = self.template_operator_id.sudo().create_db(key_value_dict, db_name)
        admin_user = self._find_admin_user()
        number_users = self._find_number_user()
        build.update({
            'is_subscription': True,
            'subscription_id': self.id,
            'admin_user': admin_user,
            'max_users_limit': number_users,
            'expiration_date': self.expiration_date,
        })
        build.refresh_data()

    def list_databases(self):
        """Liste toutes les bases de données disponibles."""
        # Remplacer 'your_postgresql_connection_string' par votre chaîne de connexion PostgreSQL
        self.env.cr.execute("SELECT datname FROM pg_catalog.pg_database")
        return self.env.cr.fetchall()

    @api.depends('build_count')
    def _compute_build_count(self):
        """ Calculate build count based on subscription package """
        self.build_count = self.env['saas.db'].search_count(
            [('subscription_id', '=', self.id)])

    def button_build_count(self):
        """ It displays builds based on subscription package """
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



