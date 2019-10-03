# Copyright 2018-2019 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging
import os
import os.path
from urllib.parse import urlparse

from odoo import models, fields, api

from odoo.addons.queue_job.job import job
from ..os import analysis_dir, update_repo, get_manifests
from ..odoo import is_test

_logger = logging.getLogger(__name__)


class Demo(models.Model):
    _name = 'saas.demo'
    _description = 'Repos Set for Demo'

    name = fields.Char()
    operator_ids = fields.One2many('saas.operator', 'demo_id')
    template_ids = fields.One2many('saas.template', 'demo_id')
    repo_ids = fields.One2many('saas.demo.repo', 'demo_id', copy=True)

    @api.model
    def fetch_and_generate_templates(self):
        # TODO: this method is called via git webhooks
        analysis_path = analysis_dir()
        demos_for_immediate_update = self.env[self._name]
        for demo in self:
            updated = demo.repo_ids._local_update_repo(update_commit=True)
            if not updated:
                continue
            for repo in demo.repo_ids:
                path = os.path.join(analysis_path, repo.branch, repo.url_escaped)
                demos_for_immediate_update = self.update_modules_templates(path, demo, demos_for_immediate_update, repo)
        if demos_for_immediate_update:
            self.repos_updating_start(demos_for_immediate_update)

    def update_modules_templates(self, path, demo, demos_for_immediate_update, repo):
        for module, manifest in get_manifests(path).items():
            if not manifest.get('saas_demo_title'):
                # not a demo
                continue
            if not manifest.get('installable', True):
                # not installable
                continue
            template = self.env['saas.template'].search([
                ('repo_id', '=', repo.id),
                ('demo_main_addon_id.name', '=', module),
            ])
            if not template:
                module_rec = self.env['saas.module'].search([('name', '=', module)])
                if not module_rec:
                    module_rec = self.env['saas.module'].create({
                        'name': module
                    })
                template = self.env['saas.template'].create({
                    'repo_id': repo.id,
                    'demo_main_addon_id': module_rec.id,
                    'template_demo': True,
                    'public_access': True,
                })
                for operator in self.operator_ids:
                    # we don’t need the template to start building now
                    operator.update_repos_state = 'none'
                    self.env['saas.template.operator'].create({
                        'operator_db_name': operator.generate_db_name(),
                        'template_id': template.id,
                        'operator_id': operator.id,
                    })
                demos_for_immediate_update |= demo
            modules_to_show = [module] + (manifest.get('saas_demo_addons') or [])
            modules_to_install = modules_to_show + (manifest.get('saas_demo_addons_hidden') or [])
            template.write({
                'name': manifest.get('saas_demo_title'),
                'template_module_ids': self.get_module_vals(modules_to_install),
                'demo_addon_ids': self.get_module_vals(modules_to_show),
            })
        return demos_for_immediate_update

    @api.model
    def get_module_vals(self, modules):
        module_ids = self.env['saas.module'].search([('name', 'in', modules)])
        existing_modules = module_ids.mapped('name')
        for module in modules:
            if module not in existing_modules:
                new_module = self.env['saas.module'].create({'name': module})
                module_ids |= new_module
                existing_modules.append(module)
        vals = [(4, module.id, 0) for module in module_ids]
        return vals

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
            return all((s != 'updating' for s in states))

        operators = pending_operators.filtered(filter_free_operators)
        if not operators:
            # it's not a time to start
            return

        operators.write({
            'update_repos_state': 'updating',
        })
        # There is no clean way to determine whether we are on tests or not.
        # So, assume that we are on tests if modules is installed
        if not is_test(self):
            # close transaction to make update_repos_state update visible
            self.env.cr.commit()
        operators.update_repos()

        # repos_updating_next() will be called via cron
        # we cannot use with_delay() because in case of local operators we restart server

    def action_fetch_templates(self):
        self.fetch_and_generate_templates()


class Repo(models.Model):
    _name = 'saas.demo.repo'
    _description = 'Repository for Demo'
    _rec_name = 'url'

    repo_name = fields.Char('Repo Name', compute='_compute_url_dependent_fields', store=True)
    demo_id = fields.Many2one('saas.demo')
    url = fields.Char('Repo URL', required=True)
    url_escaped = fields.Char('Repo URL (escaped)', compute='_compute_url_dependent_fields')
    vendor = fields.Char('Vendor', compute='_compute_url_dependent_fields', store=True)
    branch = fields.Char('Branch', required=True)
    demo_repo = fields.Boolean('Scan for demo', default=True)
    commit = fields.Char('Commit SHA', help='Last processed point')

    @api.depends('url')
    def _compute_url_dependent_fields(self):
        for r in self:
            url = r.url
            if not url:
                continue
            for i in '@:/':
                url_escaped = url.replace(i, '_')
            r.url_escaped = url_escaped

            parsed = urlparse(url)
            url_path = parsed.path.split('/')
            r.vendor = url_path[1]
            repo = url_path[-1]
            if repo.endswith('.git'):
                repo = repo[:-4]
            r.repo_name = repo

    def _local_update_repo(self, update_commit=True):
        analysis_root = analysis_dir()
        updated = False
        for repo in self:
            analysis_path = os.path.join(analysis_root, repo.branch, repo.url_escaped)
            commit = update_repo(analysis_path, repo.url, repo.branch)
            if commit != repo.commit:
                updated = True
                if update_commit:
                    repo.commit = commit
        return updated
