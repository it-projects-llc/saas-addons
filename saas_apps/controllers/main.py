# Copyright 2020 Vildan Safin <https://github.com/Enigma228322>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.http import route, request, Controller


class SaaSAppsController(Controller):
    @route('/price', type='http', auth='public')
    def index(self, *kw):
        return "shit"
