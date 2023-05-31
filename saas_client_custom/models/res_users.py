from odoo import models


class ResUsers(models.Model):

    _inherit = 'res.users'

    def _update_admin_groups(self):
        assert self == self.env.ref("base.user_admin")
        group_ids_to_take_out = [
            self.env.ref("base.group_system").id,
            self.env.ref("base.group_erp_manager").id,
        ]

        while True:
            implied_groups = self.env['res.groups'].search([
                ('implied_ids', 'in', group_ids_to_take_out),
                ('id', 'not in', group_ids_to_take_out),
            ])
            if not implied_groups:
                break

            group_ids_to_take_out += implied_groups.mapped('id')

        self.write({
            "groups_id": list(map(
                lambda group_id: (3, group_id),
                group_ids_to_take_out
            ))
        })
