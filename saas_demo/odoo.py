# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def is_test(self):
    return self.env['ir.module.module'].search([('name', '=', 'saas_demo_test'),
                                                ('state', 'in', ['to install', 'installed'])])
