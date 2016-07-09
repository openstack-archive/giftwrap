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

import os
import subprocess
import tempfile
import unittest2 as unittest

import yaml

from giftwrap import build_spec
from giftwrap.settings import Settings
from giftwrap.tests import utils


class TestBuildSpec(unittest.TestCase):

    def test_build_spec(self):
        manifest = {
            'settings': {},
        }
        with tempfile.TemporaryFile(mode='w+') as tf:
            version = '0'
            yaml.safe_dump(manifest, tf)
            tf.flush()
            tf.seek(0)
            bs = build_spec.BuildSpec(tf, version)
            self.assertTrue(isinstance(bs.settings, Settings))

    def test_build_spec_projects(self):
        manifest = {
            'settings': {},
            'projects': [
                {
                    'name': 'project1',
                },
                {
                    'name': 'project2',
                },
            ],
        }
        with tempfile.TemporaryFile(mode='w+') as tf:
            version = '99'
            yaml.safe_dump(manifest, tf)
            tf.flush()
            tf.seek(0)
            bs = build_spec.BuildSpec(tf, version)
            self.assertEqual(2, len(bs.projects))
            for project in bs.projects:
                self.assertEqual('99', project.version)

    @utils.make_test_repo("parentrepo")
    @utils.make_test_repo("childrepo")
    def test_build_spec_superrepo(self, parentrepo, childrepo):
        try:
            startdir = os.getcwd()
            os.chdir(parentrepo)
            subprocess.check_call(['git', 'submodule', 'add', childrepo])
            subprocess.check_call(['git', 'commit', '-m', 'adding childrepo'])
            parenthash = subprocess.check_output(
                ['git', 'log', 'HEAD', '--format=%H']).decode('ascii').strip()
            childhash = subprocess.check_output(
                ['git', 'submodule', 'status']).decode('ascii').split()[0]
        finally:
            os.chdir(startdir)
        manifest = {
            'settings': {},
            'superrepo': parentrepo,
        }
        with tempfile.TemporaryFile(mode='w+') as tf:
            yaml.safe_dump(manifest, tf)
            tf.flush()
            tf.seek(0)
            bs = build_spec.BuildSpec(tf, parenthash)
            self.assertEqual(1, len(bs.projects))
            self.assertEqual(childhash, bs.projects[0].gitref)
