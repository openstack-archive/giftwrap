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
import tempfile
import unittest2 as unittest

import git
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
    @utils.make_test_repo("reqrepo")
    def test_build_spec_superrepo(self, parentrepo, childrepo, reqrepo):
        parentrepo = git.Repo(parentrepo)
        childname = os.path.basename(childrepo)
        with open(os.path.join(childrepo, 'setup.py'), 'w') as setup:
            setup.write("#!/usr/bin/python\n")
        childrepo = git.Repo(childrepo)
        childrepo.index.add(['setup.py'])
        childrepo.index.commit('adding setup.py')
        parentrepo.create_submodule(childname, childname,
                                    url=childrepo.working_tree_dir)
        parentrepo.index.commit('adding child repo')
        constraints_path = os.path.join(reqrepo, 'upper-constraints.txt')
        with open(constraints_path, 'w') as cf:
            cf.write("foo==1.0\n{}==11.0\n".format(childname))
        reqrepo = git.Repo(reqrepo)
        reqrepo.index.add(['upper-constraints.txt'])
        reqrepo.index.commit('adding upper constraints')
        parentrepo.create_submodule('requirements', 'requirements',
                                    url=reqrepo.working_tree_dir)
        parenthash = parentrepo.head.commit.hexsha
        childhash = childrepo.head.commit.hexsha
        manifest = {
            'settings': {},
            'superrepo': parentrepo.working_tree_dir,
        }
        with tempfile.TemporaryFile(mode='w+') as tf:
            yaml.safe_dump(manifest, tf)
            tf.flush()
            tf.seek(0)
            bs = build_spec.BuildSpec(tf, parenthash)
            self.assertEqual(1, len(bs.projects))
            self.assertEqual(childhash, bs.projects[0].gitref)
            child_path = os.path.join(parentrepo.working_tree_dir, childname)
            self.assertEqual(child_path, bs.projects[0].giturl)
        constraints_added = os.path.join(parentrepo.working_tree_dir,
                                         'requirements',
                                         'upper-constraints.txt')
        self.assertIn(constraints_added, bs.settings.constraints)
