# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2014, Craig Tracey <craigtracey@gmail.com>
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations

import urlparse

from jinja2 import Environment

DEFAULT_GITREF = 'master'
DEFAULT_GITURL = {
    'openstack': 'https://git.openstack.org/openstack/',
    'stackforge': 'https://github.com/stackforge/'
}
DEFAULT_VENV_COMMAND = "virtualenv --no-wheel ."
DEFAULT_INSTALL_COMMAND = "./bin/pip install %s"  # noqa

TEMPLATE_VARS = ('name', 'version', 'gitref', 'stackforge')


class OpenstackProject(object):

    def __init__(self, settings, name, version=None, gitref=None, giturl=None,
                 gitdepth=1, venv_command=None, install_command=None,
                 install_path=None, package_name=None, stackforge=False,
                 system_dependencies=[], pip_dependencies=[]):
        self._settings = settings
        self.name = name
        self._version = version
        self._gitref = gitref
        self._giturl = giturl
        self.gitdepth = gitdepth
        self._venv_command = venv_command
        self._install_command = install_command
        self._install_path = install_path
        self._package_name = package_name
        self.stackforge = stackforge
        self._git_path = None
        self.system_dependencies = system_dependencies
        self.pip_dependencies = pip_dependencies

    @property
    def version(self):
        if not self._version:
            self._version = self._settings.version
        return self._version

    @property
    def gitref(self):
        if not self._gitref:
            self._gitref = DEFAULT_GITREF
        return self._gitref

    @property
    def giturl(self):
        if not self._giturl:
            key = 'openstack'
            if self.stackforge:
                key = 'stackforge'
            self._giturl = urlparse.urljoin(DEFAULT_GITURL[key], self.name)
        return self._giturl

    @property
    def venv_command(self):
        if not self._venv_command:
            self._venv_command = DEFAULT_VENV_COMMAND
        return self._venv_command

    @property
    def package_name(self):
        if not self._package_name:
            self._package_name = \
                self._render_from_settings('package_name_format')
        return self._package_name

    def _template_vars(self):
        template_vars = {'project': self}
        template_vars['settings'] = self._settings
        for var in TEMPLATE_VARS:
            template_vars[var] = object.__getattribute__(self, var)
        return template_vars

    @property
    def install_path(self):
        if not self._install_path:
            self._install_path = self._render_from_settings('install_path')
        return self._install_path

    @property
    def install_command(self):
        if not self._install_command:
            self._install_command = DEFAULT_INSTALL_COMMAND
        return self._install_command

    @property
    def git_path(self):
        if not self._git_path:
            gitorg = 'openstack'
            if self.stackforge:
                gitorg = 'stackforge'
            self._git_path = '%s/%s' % (gitorg, self.name)
        return self._git_path

    def _render_from_settings(self, setting_name):
        setting = getattr(self._settings, setting_name)
        env = Environment()
        env.add_extension('jinja2.ext.autoescape')
        result = setting
        while True:
            t = env.from_string(result)
            newresult = t.render(self._template_vars())
            if newresult == result:
                break
            result = newresult
        return result

    @staticmethod
    def factory(settings, project_dict, version):
        return OpenstackProject(settings, version=version, **project_dict)
