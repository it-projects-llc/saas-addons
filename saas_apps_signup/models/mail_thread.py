# Copyright 2020 Eugene Molotov <https://it-projects.info/team/em230418>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class MailThread(models.AbstractModel):

    _inherit = "mail.thread"

    def _message_auto_subscribe_followers(self, updated_values, default_subtype_ids):
        """
        Если создается счет на наши контракты, то не высылаем письмо о привязке
        """
        res = super(MailThread, self)._message_auto_subscribe_followers(updated_values, default_subtype_ids)
        if self._name == "account.move" and self.line_ids.mapped("contract_line_id.contract_id.build_id"):
            return list(filter(
                lambda item: item[2] != "mail.message_user_assigned",
                res
            ))
        return res
