# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.http import route, request, Controller


class SaasDemoController(Controller):
    @route('/demo/<string:provider>/<string:repo>/<string:branch>/<string:moodule>')
    def create_demo_build(self, provider, repo, branch, module):
        pass
