# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2015, Craig Tracey
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

from giftwrap.builders import Builder, BUILDER_DRIVER_NAMESPACE
from stevedore import extension


class TestBuilder(unittest.TestCase):

    def test_default_drivers(self):
        drivers = Builder.builder_names()
        self.assertEqual(drivers, ['docker', 'package'])

    def test_additional_drivers(self):
        em = extension.ExtensionManager(BUILDER_DRIVER_NAMESPACE)
        em.extensions.append(extension.Extension('test', None, None, None))
        drivers = Builder.builder_names(em)
        self.assertEqual(drivers, ['docker', 'package', 'test'])
