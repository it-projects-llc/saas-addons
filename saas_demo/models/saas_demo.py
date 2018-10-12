# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class Demo(models.Model):
    _inherit = 'saas.demo'

    name = fields.Char()
    operator_ids = fields.One2many('saas.operator', 'demo_id')
    template_ids = fields.One2many('saas.template', 'demo_id')
    repo_ids = fields.One2many('saas.demo.repo', 'demo_id')

    def repos_updating_start(self):
        # TODO: This method is called by cron once in a night
        self.search([]).mapped('operator_ids').write({
            'update_repos_state': 'pending',
        })
        self.repos_updating_next()

    def repos_updating_next(self):
        # TODO: This method is called by cron every few minutes

        # Check for operators with finished rebuilding
        rebuilding_operators = self.env['saas.operator'].search([
            ('update_repos_state', '=', 'rebuilding'),
        ])
        for op in rebuilding_operators:
            count = self.env['saas.template.operator'].search_count([
                ('to_rebuild', '=', True),
                ('operator_id', '=', op.id),
            ])
            if not count:
                op.update_repos_state = 'none'

        # Update repos in operators
        pending_operators = self.env['saas.operator'].search([
            ('demo_id', '!=', False),
            ('update_repos_state', '=', 'pending')
        ])
        if not pending_operators:
            # nothing to do
            return

        # filter out operators which demo already has processing operator
        def filter_free_operators(op):
            states = op.demo_id.operator_ids.mapped('update_repos_state')
            return all((s != 'processing' for s in states))

        operators = pending_operators.filtered(filter_free_operators)
        if not operators:
            # it's not a time to start
            return

        operators.write({
            'update_repos_state': 'processing',
        })
        # close transaction to make update_repos_state update visible
        self.env.cr.commit()

        operators.update_repos()

        # repos_updating_next() will be called via cron
        # we cannot use with_delay() because in case of local operators we restart server


class Repo(models.Model):
    _name = 'saas.demo.repo'
    _rec_name = 'url'

    demo_id = fields.Many2one('saas.operator')
    url = fields.Char('Repo URL')
    url_escaped = fields.Char('Repo URL (escaped)', compute='_compute_url_escaped')
    branch = fields.Char('Branch')
    demo_repo = fields.Boolean('Scan for demo', default=True)

    def _compute_url_escaped(self):
        for r in self:
            url = r.url
            for i in '@:/':
                url = url.replace(i, '_')
            r.url_escaped = url
