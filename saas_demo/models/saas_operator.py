# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging
import os.path

from odoo import models, fields, api, service
from ..os import repos_dir, update_addons_path, root_odoo_path, git, update_repo
from ..odoo import is_test

_logger = logging.getLogger(__name__)


class SAASOperator(models.Model):
    _inherit = 'saas.operator'

    demo_id = fields.Many2one('saas.demo')
    update_repos_state = fields.Selection([
        ('base', 'Not a demo'),
        ('none', 'Not planned'),
        ('pending', 'Pending'),
        ('updating', 'Updating Repositories'),
        ('rebuilding', 'Rebuilding Templates'),
    ], default='base')
    needs_restart = fields.Boolean(string="Server needs to be restarted", default=True)
    automatic_addons_path_update = fields.Boolean(default=True)

    def is_local(self):
        return any((r.type == 'local' for r in self))

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
            if has_updates:
                # we need to make sure that templates will only be created after restarting the odoo
                r.needs_restart = True
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

    def update_odoo(self):
        """Fetch and checkout Repository"""
        if self.is_local():
            if is_test(self):
                # no need to pull odoo folder in test mode
                return
            else:
                try:
                    git(root_odoo_path(), ['pull', 'origin'])
                except:
                    # root odoo may be not a git folder
                    pass

    def update_addons_path(self):
        if self.is_local():
            if is_test(self):
                # no need to update config in test mode
                return
            local_root = repos_dir()
            for r in self:
                if r.automatic_addons_path_update:
                    for repo in r.demo_id.repo_ids:
                        update_addons_path(os.path.join(local_root, repo.branch), False)

    def restart_odoo(self):
        if self.is_local():
            if is_test(self):
                # no need to restart odoo folder in test mode
                return
            self.write({'needs_restart': False})
            service.server.restart()

    def _update_repos(self):
        self.ensure_one()
        if self.type != 'local':
            return
        has_updates = False
        for repo in self.demo_id.repo_ids:
            updated = self._local_server_update_repo(repo.url, repo.url_escaped, repo.branch, repo.commit)
            if updated:
                has_updates = True
        return has_updates

    @staticmethod
    def _local_server_update_repo(url, url_escaped, branch, commit):
        """
        Updates git repository
        :param url: link to git repository
        :param url_escaped: used for directory name
        :param branch: repository branch to be cloned
        :param commit: commit hash
        :return bool: whether the repository was updated or not
        """
        repos_root = repos_dir()
        updated = False
        repos_path = os.path.join(repos_root, branch, url_escaped)
        if not os.path.isdir(os.path.join(repos_path)):
            updated = True
        current_commit = update_repo(repos_path, url, branch)
        if current_commit != commit:
            updated = True
        return updated
