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


class Settings(object):

    DEFAULT_BASE_PATH = '/opt/openstack'

    def __init__(self, version, base_path):
        self._validate_settings(version, base_path)
        self.version = version
        self.base_path = base_path

    def _validate_settings(self, version, base_path):
        if not version:
            raise Exception("You must provide a version")

    @staticmethod
    def factory(settings_dict):
        version = settings_dict.get('version', None)
        base_path = settings_dict.get('base_path', Settings.DEFAULT_BASE_PATH)
        return Settings(version, base_path)
