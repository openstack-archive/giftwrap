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

DEFAULT_BUILD_TYPE = 'package'


class Settings(object):

    DEFAULTS = {
        'package_name_format': 'openstack-{{ project.name }}',
        'base_path': '/opt/openstack'
    }

    def __init__(self, build_type=DEFAULT_BUILD_TYPE,
                 package_name_format=None, version=None,
                 base_path=None, all_in_one=False, force_overwrite=False):
        if not version:
            raise Exception("'version' is a required settings")
        self.build_type = build_type
        self._package_name_format = package_name_format
        self.version = version
        self._base_path = base_path
        self.all_in_one = all_in_one
        self.force_overwrite = force_overwrite

    @property
    def package_name_format(self):
        return self._get_setting('package_name_format')

    @property
    def base_path(self):
        return self._get_setting('base_path')

    def _get_setting(self, setting_name):
        setting = object.__getattribute__(self, '_%s' % setting_name)
        if setting is None:
            setting = Settings.DEFAULTS[setting_name]
        return setting

    @staticmethod
    def factory(settings_dict):
        return Settings(**settings_dict)
