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

SAMPLE_SETTINGS = {
    'package_name_format': 'my-package-name',
    'version': '1.2',
    'base_path': '/basepath',
    'constraints': ['http://example.txt'],
}


class TestSettings(unittest.TestCase):

    def test_factory(self):
        settings_dict = SAMPLE_SETTINGS
        s = settings.Settings.factory(settings_dict)

        self.assertEqual('my-package-name', s.package_name_format)
        self.assertEqual('1.2', s.version)
        self.assertEqual('/basepath', s.base_path)
        self.assertEqual('http://example.txt', s.constraints[0])

    def test_factory_has_default_base_path(self):
        settings_dict = {'version': 'version'}
        s = settings.Settings.factory(settings_dict)

        self.assertEqual('/opt/openstack', s.base_path)

    def test_factory_raises_when_version_missing(self):
        settings_dict = SAMPLE_SETTINGS
        del(settings_dict['version'])

        with self.assertRaises(Exception):
            settings.Settings.factory(settings_dict)

    def test_factory_raises_when_constraints_invalid(self):
        settings_dict = SAMPLE_SETTINGS
        settings_dict['constraints'] = 'notalist'

        with self.assertRaises(Exception):
            settings.Settings.factory(settings_dict)
