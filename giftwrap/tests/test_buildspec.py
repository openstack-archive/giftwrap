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
import shutil
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

    def _add_setup_py(self, repo):
        with open(os.path.join(repo.working_tree_dir,
                               'setup.py'), 'w') as setup:
            setup.write("#!/usr/bin/python\n")
        repo.index.add(['setup.py'])
        repo.index.commit('adding setup.py')

    def _populate_reqrepo(self, reqrepo, childname):
        constraints_path = os.path.join(reqrepo, 'upper-constraints.txt')
        with open(constraints_path, 'w') as cf:
            cf.write("foo==1.0\n{}==11.0\n".format(childname))
        reqrepo = git.Repo(reqrepo)
        reqrepo.index.add(['upper-constraints.txt'])
        reqrepo.index.commit('adding upper constraints')

    @utils.make_test_repo("parentrepo")
    @utils.make_test_repo("childrepo2")
    @utils.make_test_repo("childrepo")
    @utils.make_test_repo("reqrepo")
    def test_build_spec_superrepo(self,
                                  parentrepo,
                                  childrepo2,
                                  childrepo,
                                  reqrepo):
        parentrepo = git.Repo(parentrepo)
        childname = os.path.basename(childrepo)
        childrepo = git.Repo(childrepo)
        self._add_setup_py(childrepo)

        child2name = os.path.basename(childrepo2)
        childrepo2 = git.Repo(childrepo2)
        self._add_setup_py(childrepo2)

        # tag child repo to test describe behavior
        cw = childrepo2.config_writer()
        cw.set_value("user", "email", "nobody@noexist.test")
        cw.set_value("user", "name", "Nobody McNoperson")
        cw.release()
        childrepo2.create_tag('test-tag-1', message='Annotated ftw')
        parentrepo.create_submodule(childname, childname,
                                    url=childrepo.working_tree_dir)
        parentrepo.create_submodule(child2name, child2name,
                                    url=childrepo2.working_tree_dir)
        parentrepo.index.commit('adding child repos')
        self._populate_reqrepo(reqrepo, childname)
        parentrepo.create_submodule('requirements', 'requirements',
                                    url=reqrepo)
        version = parentrepo.head.commit.hexsha
        self._test_build_spec(version,
                              parentrepo.working_tree_dir,
                              childrepo2,
                              childrepo)

    @utils.make_test_repo("parentrepo")
    @utils.make_test_repo("childrepo2")
    @utils.make_test_repo("childrepo")
    @utils.make_test_repo("reqrepo")
    def test_build_spec_superrepo_filters(self,
                                          parentrepo,
                                          childrepo2,
                                          childrepo,
                                          reqrepo):
        parentrepo = git.Repo(parentrepo)
        childname = os.path.basename(childrepo)
        childrepo = git.Repo(childrepo)
        self._add_setup_py(childrepo)

        child2name = os.path.basename(childrepo2)
        childrepo2 = git.Repo(childrepo2)
        self._add_setup_py(childrepo2)

        # tag child repo to test describe behavior
        cw = childrepo2.config_writer()
        cw.set_value("user", "email", "nobody@noexist.test")
        cw.set_value("user", "name", "Nobody McNoperson")
        cw.release()
        childrepo2.create_tag('test-tag-1', message='Annotated ftw')
        parentrepo.create_submodule(childname, childname,
                                    url=childrepo.working_tree_dir)
        parentrepo.create_submodule(child2name, child2name,
                                    url=childrepo2.working_tree_dir)
        parentrepo.index.commit('adding child repos')
        self._populate_reqrepo(reqrepo, childname)
        parentrepo.create_submodule('requirements', 'requirements',
                                    url=reqrepo)
        version = parentrepo.head.commit.hexsha
        self._test_build_spec(version,
                              parentrepo.working_tree_dir,
                              childrepo2,
                              childrepo,
                              [child2name])

    @utils.make_test_repo("childrepo2")
    @utils.make_test_repo("childrepo")
    @utils.make_test_repo("reqrepo")
    def test_build_spec_superrepo_no_submodules(self,
                                                childrepo2,
                                                childrepo,
                                                reqrepo):
        parentdir = None
        try:
            parentdir = tempfile.mkdtemp()
            childname = os.path.basename(childrepo)
            child2name = os.path.basename(childrepo2)
            newchildrepo = os.path.join(parentdir, childname)
            newchildrepo2 = os.path.join(parentdir, child2name)
            newreqrepo = os.path.join(parentdir, 'requirements')
            os.rename(childrepo, newchildrepo)
            os.rename(childrepo2, newchildrepo2)
            os.rename(reqrepo, newreqrepo)
            newchildrepo = git.Repo(newchildrepo)
            self._add_setup_py(newchildrepo)
            newchildrepo2 = git.Repo(newchildrepo2)
            self._add_setup_py(newchildrepo2)
            self._populate_reqrepo(newreqrepo, childname)
            self._test_build_spec('9999', parentdir, newchildrepo2,
                                  newchildrepo)
        finally:
            if parentdir:
                shutil.rmtree(parentdir)

    def _test_build_spec(self,
                         version,
                         working_tree,
                         childrepo2,
                         childrepo,
                         filter=None):
        childname = os.path.basename(childrepo.working_tree_dir)
        child2name = os.path.basename(childrepo2.working_tree_dir)
        childhash = childrepo.head.commit.hexsha
        child2hash = childrepo2.head.commit.hexsha
        child2describe = childrepo2.git.describe(always=True)
        manifest = {
            'settings': {},
            'superrepo': working_tree,
        }
        with tempfile.TemporaryFile(mode='w+') as tf:
            yaml.safe_dump(manifest, tf)
            tf.flush()
            tf.seek(0)
            bs = build_spec.BuildSpec(tf, version, project_filter=filter)

        if not filter:
            self.assertEqual(2, len(bs.projects))
        else:
            self.assertEqual(1, len(bs.projects))

        results = {
            childname: {
                'gitref': childhash,
                'version': childhash[:7],
            },
            child2name: {
                'gitref': child2hash,
                'version': child2describe,
            }
        }
        for project in bs.projects:
            child_path = os.path.join(
                working_tree, project.name)
            self.assertEqual(child_path, project.giturl)
            self.assertEqual(results[project.name]['gitref'], project.gitref)
            self.assertEqual(results[project.name]['version'], project.version)
        constraints_added = os.path.join(working_tree,
                                         'requirements',
                                         'upper-constraints.txt')
        self.assertIn(constraints_added, bs.settings.constraints)
