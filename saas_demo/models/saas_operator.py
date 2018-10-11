# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# Some code is based on https://github.com/odoo/odoo-extra/blob/master/runbot/runbot.py

import os
import logging

from odoo import models, fields, api, service
from ..os import repos_dir, update_repo, update_addons_path

_logger = logging.getLogger(__name__)


class SAASOperator(models.Model):
    _inherit = 'saas.operator'

    demo_id = fields.Many2one('saas.demo')
    update_repos_state = fields.Selection([
        ('none', 'Not planned'),
        ('pending', 'Pending'),
        ('processing', 'Started')
    ])

    @api.multi
    def update_repos(self):
        """Fetch and checkout Repository. Clone repository on first call"""
        local_root = None
        local_updates = False
        for r in self:
            if r.type != 'local':
                continue
            local_root = local_root or repos_dir()
            for repo in r.repo_ids:
                path = os.path.join(local_root, repo.name_escaped)
                has_updates = update_repo(path, repo.url, repo.branch)
                if has_updates:
                    local_updates = True

        if not local_updates:
            return

        # update addons-path
        update_addons_path(local_root)

        # Restart server
        service.service.restart()
