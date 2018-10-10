# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import models, fields, api
from odoo.service import db


class SAASOperator(models.Model):
    _name = 'saas.operator'

    # list of types can be extended via selection_add
    type = fields.Selection([
        ('local', 'Same Instance'),
    ], 'Type')
    host = fields.Char()
    port = fields.Char()
    db_url_template = fields.Char('DB URLs', help='Avaialble variables: {db_id}, {db_name}')
    db_name_template = fields.Char('DB Names', help='Avaialble variables: {db_id}')

    @api.multi
    def _create_db(self, template_db, db_name, demo, password=None, lang='en_US'):
        """Synchronous db creation"""
        for r in self:
            if r.type != 'local':
                continue

            if template_db:
                db._drop_conn(self.env.cr, template_db)
                db.exp_duplicate_database(template_db, db_name)
            else:
                db.exp_create_database(
                    db_name, demo, lang, user_password=password)

    @api.multi
    def _drop_db(self, db_name):
        for r in self:
            if r.type != 'local':
                continue

            db.exp_drop(db_name)

    def get_db_url(self, db):
        # TODO: use mako for url templating
        self.ensure_one()
        return self.db_url.format(db_id=db.id, db_name=db.name)

    def get_db_name(self, db):
        # TODO: use mako for url templating
        self.ensure_one()
        return self.db_url.format(db_id=db.id)
