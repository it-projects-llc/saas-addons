# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class SAASLog(models.Model):
    _name = 'saas.log'
    _description = 'Database Event Log'

    type = fields.Selection([
        ('creation', 'DB is being created'),
        ('created', 'DB is created'),
        ('authed', 'Quick Authentication'),
        ('dropped', 'DB is dropped'),
    ], string='Log type')
    data_id = fields.Reference(string='Reference', selection=[
        ('auth_quick_master.token', 'Token'),
        ('saas.operator', 'Operator'),
    ])
    description = fields.Char('Extra data')
    db_id = fields.Many2one('saas.db')
    user_id = fields.Many2one('res.users', 'User', default=lambda s: s.env.user.id)

    def log_db_creating(self, db, template=None):
        self.create({
            'type': 'creation',
            'description': 'from template: %s' % template,
            'data_id': 'saas.operator,%s' % db.operator_id.id,
            'db_id': db.id,
        })

    def log_db_created(self, db):
        self.create({
            'type': 'created',
            'data_id': 'saas.operator,%s' % db.operator_id.id,
            'db_id': db.id,
        })

    def log_db_authed(self, token_obj):
        self.create({
            'type': 'authed',
            'data_id': 'auth_quick_master.token,%s' % token_obj.id,
            'db_id': int(token_obj.build),
            'user_id': token_obj.user_id.id,
        })

    def log_db_dropped(self, db):
        self.create({
            'type': 'dropped',
            'data_id': 'saas.operator,%s' % db.operator_id.id,
            'db_id': db.id,
        })

    def create(self, vals):
        _logger.debug('saas.log: %s', vals)
        return super(SAASLog, self).create(vals)
