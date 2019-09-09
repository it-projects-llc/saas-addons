# Copyright 2018 Ivan Yelizariev <https://it-projects.info/team/yelizariev>
# Copyright 2019 Denis Mudarisov <https://it-projects.info/team/trojikman>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
# Some code is based on https://github.com/odoo/odoo-extra/blob/master/runbot/runbot.py
import subprocess
import os
import os.path
import logging
import errno
import io
from os.path import join as opj
import ast
try:
    import configparser as ConfigParser
except ImportError:
    import ConfigParser

from odoo import tools
from odoo.modules.module import module_manifest, README, MANIFEST_NAMES, adapt_version
from odoo.tools import pycompat
import odoo

_logger = logging.getLogger(__name__)
config_parser = ConfigParser.ConfigParser()


# SYSTEM
def run(l, env=None):
    """Run a command described by l in environment env"""
    _logger.debug("run", l)
    env = dict(os.environ, **env) if env else None
    if isinstance(l, list):
        if env:
            rc = os.spawnvpe(os.P_WAIT, l[0], l, env)
        else:
            rc = os.spawnvp(os.P_WAIT, l[0], l)
    elif isinstance(l, str):
        tmp = ['sh', '-c', l]
        if env:
            rc = os.spawnvpe(os.P_WAIT, tmp[0], tmp, env)
        else:
            rc = os.spawnvp(os.P_WAIT, tmp[0], tmp)
    _logger.debug("run", rc=rc)
    return rc


def mkdir(d):
    try:
        os.makedirs(d, 0o700)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
        assert os.access(d, os.W_OK), \
            "%s: directory is not writable" % d
    return d


# GIT
def git(path, cmd):
    cmd = ['git', '-C', path] + cmd
    _logger.debug("git: %s", ' '.join(cmd))
    return subprocess.check_output(cmd).strip().decode('utf-8')


def update_repo(path, repo_url, branch):
    if not os.path.isdir(os.path.join(path)):
        run(['git', 'clone', repo_url, path])
    git(path, ['fetch', 'origin'])
    git(path, ['checkout', 'origin/%s' % branch])
    commit = git(path, ['rev-parse', 'origin/%s' % branch])
    return commit


def analysis_dir():
    d = os.path.join(tools.config['data_dir'], 'analysis')
    return mkdir(d)


# ODOO
def repos_dir():
    d = os.path.join(tools.config['data_dir'], 'repos')
    return mkdir(d)


def root_odoo_path():
    path = os.path.abspath(os.path.expanduser(
        os.path.expandvars(os.path.dirname(odoo.__file__))))
    path = os.path.join(path, '../')
    return path


def update_addons_path(folder_of_folders, force=True):
    """
    :param list folder_of_folders: <folder_of_folders>/REPO/MODULE/__manifest__.py
    :param bool force: override existing addons
    """
    if force:
        base_addons = os.path.join(root_odoo_path(), 'odoo/addons')
        main_addons = os.path.abspath(os.path.join(root_odoo_path(), 'addons'))
        addons_path = [base_addons, main_addons]
    else:
        addons_path = odoo.conf.addons_paths

    extra = [
        os.path.join(folder_of_folders, p)
        for p in os.listdir(folder_of_folders)
    ]
    extra = [
        p
        for p in extra
        if os.path.isdir(p)
    ]
    addons_path += extra
    addons_path = list(set(addons_path))
    addons_path = ','.join(addons_path)
    _logger.info('addons_path for %s:\n%s', folder_of_folders, addons_path)
    update_config('options', 'addons_path', addons_path)


def update_config(section, key, value):
    config_parser.read(tools.config.rcfile)
    config_parser.set(section, key, value)
    with open(tools.config.rcfile, 'w') as configfile:
        config_parser.write(configfile)


def _fileopen(path, mode, basedir, pathinfo):
    name = os.path.normpath(os.path.normcase(os.path.join(basedir, path)))
    if os.path.isfile(name):
        if 'b' in mode:
            fo = open(name, mode)
        else:
            fo = io.open(name, mode, encoding='utf-8')
        if pathinfo:
            return fo, name
        return fo


def file_open(name, mode="r", pathinfo=False):
    if os.path.isabs(name):
        base, name = os.path.split(name)
        return _fileopen(name, mode=mode, basedir=base, pathinfo=pathinfo)


def load_information_from_description_file(module, mod_path):
    """
    :param module: The name of the module (sale, purchase, ...)
    :param mod_path: Physical path of module, if not providedThe name of the module (sale, purchase, ...)
    """
    manifest_file = module_manifest(mod_path)
    if manifest_file:
        # default values for descriptor
        info = {
            'application': False,
            'author': 'Odoo S.A.',
            'auto_install': False,
            'category': 'Uncategorized',
            'depends': [],
            'description': '',
            'installable': True,
            'license': 'LGPL-3',
            'post_load': None,
            'version': '1.0',
            'web': False,
            'sequence': 100,
            'summary': '',
            'website': '',
        }
        info.update(pycompat.izip(
            'depends data demo test init_xml update_xml demo_xml'.split(),
            iter(list, None)))
        f = file_open(manifest_file, mode='rb')
        try:
            info.update(ast.literal_eval(pycompat.to_native(f.read())))
        finally:
            f.close()

        if not info.get('description'):
            readme_path = [opj(mod_path, x) for x in README
                           if os.path.isfile(opj(mod_path, x))]
            if readme_path:
                readme_text = file_open(readme_path[0]).read()
                info['description'] = readme_text

        if 'active' in info:
            # 'active' has been renamed 'auto_install'
            info['auto_install'] = info['active']

        info['version'] = adapt_version(info['version'])
        return info

    _logger.debug('module %s: no manifest file found %s', module, MANIFEST_NAMES)
    return {}


def get_manifests(path):

    def is_really_module(name):
        for mname in MANIFEST_NAMES:
            if os.path.isfile(os.path.join(path, name, mname)):
                return True

    modules = [
        it
        for it in os.listdir(path)
        if is_really_module(it)
    ]
    res = {}
    for mname in modules:
        mod_path = os.path.join(path, mname)
        info = load_information_from_description_file(mname, mod_path)
        res[mname] = info
    return res
