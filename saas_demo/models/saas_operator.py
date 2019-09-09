# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging
import os.path

from odoo import models, fields, api, service
from ..os import repos_dir, update_addons_path, root_odoo_path, git, update_repo

_logger = logging.getLogger(__name__)


class SAASOperator(models.Model):
    _inherit = 'saas.operator'

    demo_id = fields.Many2one('saas.demo')
    update_repos_state = fields.Selection([
        ('none', 'Not planned'),
        ('pending', 'Pending'),
        ('updating', 'Updating Repositories'),
        ('rebuilding', 'Rebuilding Templates'),
    ])

    @api.multi
    def is_local(self):
        return any((r.type == 'local' for r in self))

    @api.multi
    def update_repos(self):
        """
        * Fetch and checkout Repositories. Clone repository on first call.
        * Update odoo source when there are updates in custom repositories
        * Update addons_path
        * Restart server
        """
        updated_operators = self.env['saas.operator']
        for r in self:
            has_updates = r._update_repos()
            # has_updates = r.remote_update()
            if has_updates:
                # mark to rebuild templates
                r.update_repos_state = 'rebuilding'
                updated_operators |= r
            else:
                r.update_repos_state = 'none'

        updated_operators\
            .mapped('template_operator_ids')\
            .filtered(lambda r: r.state != 'draft')\
            .write({
                'to_rebuild': True,
            })

        # update odoo source only when we have updates in other repositories.
        # Otherwise don't update it and don't rebuild templates
        updated_operators.update_odoo()
        # update addons-path
        updated_operators.update_addons_path()

        # Restart server
        updated_operators.restart_odoo()

    @api.multi
    def update_odoo(self):
        """Fetch and checkout Repository"""
        if self.is_local():
            test = self.env['ir.config_parameter'].get_param('test_saas_demo')
            if test:
                # no need to pull odoo folder in test mode
                return
            else:
                git(root_odoo_path(), ['pull', 'origin'])

    @api.multi
    def update_addons_path(self):
        if self.is_local():
            local_root = repos_dir()
            update_addons_path(local_root)

    @api.multi
    def restart_odoo(self):
        if self.is_local():
            test = self.env['ir.config_parameter'].get_param('test_saas_demo')
            if test:
                # no need to restart odoo folder in test mode
                return
            service.server.restart()

    @api.multi
    def _update_repos(self):
        self.ensure_one()
        if self.type != 'local':
            return
        has_updates = False
        for repo in self.demo_id.repo_ids:
            updated = self.local_server_update_repo(repo.url, repo.url_escaped, repo.branch, repo.commit)
            if updated:
                has_updates = True
        return has_updates

    @staticmethod
    def local_server_update_repo(url, url_escaped, branch, commit):
        repos_root = repos_dir()
        updated = False
        repos_path = os.path.join(repos_root, branch, url_escaped)
        if not os.path.isdir(os.path.join(repos_path)):
            updated = True
        current_commit = update_repo(repos_path, url, branch)
        if current_commit != commit:
            updated = True
        return updated
