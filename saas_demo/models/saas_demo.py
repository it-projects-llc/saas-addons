# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
import os
import os.path
import json

from odoo import models, fields, api

from odoo.addons.queue_job.job import job
from ..os import repos_dir, update_repo, update_addons_path, root_odoo_path, git, get_manifests

_logger = logging.getLogger(__name__)


class Demo(models.Model):
    _inherit = 'saas.demo'

    name = fields.Char()
    operator_ids = fields.One2many('saas.operator', 'demo_id')
    template_ids = fields.One2many('saas.template', 'demo_id')
    repo_ids = fields.One2many('saas.demo.repo', 'demo_id', copy=True)

    @api.model
    def fetch_and_generate_templates(self):
        # TODO: this method is called via git webhooks
        # FIXME: split into methods to avoid deep nesting
        repos_path = repos_dir()
        demos_for_immediate_update = self.env[self._name]
        for demo in self:
            updated = demo.repo_ids._local_update_repo(update_commit=True)
            if not updated:
                continue
            for repo in demo.repo_ids:
                path = os.path.join(repos_path, repo.url_escaped)
                for module, manifest in get_manifests(path).items():
                    if not manifest.get('demo_url'):
                        # not a demo
                        continue
                    if not manifest.get('installable', True):
                        # not installable
                        continue
                    template = self.env['saas.template'].search([
                        ('demo_id', '=', demo.id),
                        ('demo_module', '=', module),
                    ])
                    if not template:
                        template = self.env['saas.template'].create({
                            'demo_id': demo.id,
                            'demo_module': module,
                        })
                        demos_for_immediate_update |= demo
                    template.write({
                        'name': manifest.get('demo_title'),
                        'template_modules_domain': json.dumps([
                            ('name', 'in', manifest.get('demo_addons') + manifest.get('demo_addons_hidden'))
                        ]),
                        'demo_addons': ','.join(manifest.get('demo_addons')),
                        'demo_url': manifest.get('demo_url'),
                    })
        if demos_for_immediate_update:
            self.repos_updating_start(demos_for_immediate_update)

    @api.model
    @job
    def repos_updating_start(self, demos=None):
        # TODO: This method is called by cron once in a night or when new template is created
        if not demos:
            demos = self.search([]).mark_operators_for_updating()
        demos.mapped('operator_ids').write({
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
    commit = fields.Char('Commit SHA', help='Last processed point')

    def _compute_url_escaped(self):
        for r in self:
            url = r.url
            for i in '@:/':
                url = url.replace(i, '_')
            r.url_escaped = url

    def _local_update_repo(self, update_commit=True):
        local_root = repos_dir()
        updated = False
        for repo in self:
            path = os.path.join(local_root, repo.url_escaped)
            commit = update_repo(path, repo.url, repo.branch)
            if commit != repo.commit:
                updated = True
                if update_commit:
                    repo.commit = commit
        return updated
