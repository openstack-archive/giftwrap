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

import os

DEFAULT_BUILD_TYPE = 'package'


class Settings(object):

    DEFAULTS = {
        'package_name_format': 'openstack-{{ project.name }}',
        'base_path': '/opt/openstack',
        'install_path': '{{ settings.base_path }}/{{ project.name }}'
    }

    def __init__(self, build_type=DEFAULT_BUILD_TYPE,
                 package_name_format=None, version=None,
                 base_path=None, install_path=None, gerrit_dependencies=True,
                 force_overwrite=False, output_dir=None, include_config=True,
                 parallel_build=True, constraints=None):
        if not version:
            raise Exception("'version' is a required settings")
        if constraints is None:
            constraints = []
        if not isinstance(constraints, list):
            raise Exception("'constraints' is required to be a list")
        self.build_type = build_type
        self._package_name_format = package_name_format
        self.version = version
        self._base_path = base_path
        self._install_path = install_path
        self.gerrit_dependencies = gerrit_dependencies
        self.force_overwrite = force_overwrite
        self._output_dir = output_dir
        self.include_config = include_config
        self.parallel_build = parallel_build
        self.constraints = constraints

    @property
    def package_name_format(self):
        return self._get_setting('package_name_format')

    @property
    def base_path(self):
        return self._get_setting('base_path')

    @property
    def install_path(self):
        return self._get_setting('install_path')

    @property
    def output_dir(self):
        if not self._output_dir:
            self._output_dir = os.getcwd()
        return self._output_dir

    def _get_setting(self, setting_name):
        setting = object.__getattribute__(self, '_%s' % setting_name)
        if setting is None:
            setting = Settings.DEFAULTS[setting_name]
        return setting

    @staticmethod
    def factory(settings_dict):
        return Settings(**settings_dict)
