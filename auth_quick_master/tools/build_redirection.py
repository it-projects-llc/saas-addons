# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import jinja2
import os


def build_redirection(build_url):
    path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'views'))
    loader = jinja2.FileSystemLoader(path)
    env = jinja2.Environment(loader=loader, autoescape=True)

    return env.get_template('auth_quick_master_redirect.html').render({'build_url': build_url})
