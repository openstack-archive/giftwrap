# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2014, John Dewey
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import unittest2 as unittest

from giftwrap import settings


class TestSettings(unittest.TestCase):
    def test_factory(self):
        settings_dict = {'version': 'version', 'base_path': 'basepath'}
        s = settings.Settings.factory(settings_dict)

        self.assertEquals('version', s.version)

    def test_factory_has_default_base_path(self):
        settings_dict = {'version': 'version'}
        s = settings.Settings.factory(settings_dict)

        self.assertEquals('/opt/openstack', s.base_path)

    def test_factory_raises_when_version_missing(self):
        settings_dict = {'base_path': 'basepath'}
        with self.assertRaises(Exception):
            settings.Settings.factory(settings_dict)
