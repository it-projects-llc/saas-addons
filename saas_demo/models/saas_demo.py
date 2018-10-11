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

    def start_repos_updating(self):
        self.search([]).mapped('operator_ids').write({
            'update_repos_state': 'pending',
        })
        # TODO: start update process


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
