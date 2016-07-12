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

import copy
import shutil
import tempfile
try:
    from unittest import mock
except:
    import mock
import unittest2 as unittest

from giftwrap.builders import Builder, BUILDER_DRIVER_NAMESPACE
from stevedore import extension

BASE_DRIVERS = set(['docker', 'package'])


class TestBuilder(unittest.TestCase):

    def test_default_drivers(self):
        drivers = set(Builder.builder_names())
        self.assertEqual(drivers, BASE_DRIVERS)

    def test_additional_drivers(self):
        em = extension.ExtensionManager(BUILDER_DRIVER_NAMESPACE)
        em.extensions.append(extension.Extension('test', None, None, None))
        drivers = set(Builder.builder_names(em))
        base_drivers = copy.copy(BASE_DRIVERS)
        base_drivers.add('test')
        self.assertEqual(drivers, base_drivers)


class FakeBuilder(Builder):

    def __del__(self):
        try:
            if self._temp_src_dir:
                shutil.rmdir(self._temp_src_dir)
        except Exception:
            pass
        try:
            if self._temp_dir:
                shutil.rmdir(self._temp_src_dir)
        except Exception:
            pass

    def _execute(self, command, cwd=None, exit=0):
        return

    def _make_temp_dir(self, prefix='giftwrap'):
        return tempfile.mkdtemp()

    def _make_dir(self, path, mode=0o777):
        return

    def _prepare_build(self):
        return

    def _prepare_project_build(self, project):
        return

    def _clone_project(self, project):
        return

    def _create_virtualenv(self, venv_command, path):
        return

    def _install_pip_dependencies(self, venv_path, dependencies,
                                  use_constraints=True):
        return

    def _copy_sample_config(self, src_clone_dir, project):
        return

    def _install_project(self, venv_path, src_clone_dir):
        return

    def _finalize_project_build(self, project):
        return

    def _finalize_build(self):
        return

    def _cleanup_build(self):
        return


class TestBuilderBuilds(unittest.TestCase):

    @mock.patch('requests.get')
    def _test_build(self, constraints, requests_mock):
        response = mock.MagicMock('response')
        response.raise_for_status = mock.MagicMock('raise_for_status')
        response.text = '# no constraints\n'
        requests_mock.return_value = response
        spec = mock.MagicMock('spec')
        spec.settings = mock.MagicMock('settings')
        spec.settings.constraints = constraints
        spec.settings.parallel_build = False
        spec.projects = []
        x = FakeBuilder(spec)
        x.build()
        return requests_mock

    def test_build(self):
        requests_mock = self._test_build(
            ['http://noexist.test/constraints.txt'])
        requests_mock.assert_called_once_with(
            'http://noexist.test/constraints.txt')

    def test_build_local_constraints(self):
        with tempfile.NamedTemporaryFile('wb') as tf:
            tf.write(b'# no local constraints\n')
            tf.flush()
            requests_mock = self._test_build([tf.name])
        requests_mock.assert_not_called()
