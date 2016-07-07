# vim: tabstop=4 shiftwidth=4 softtabstop=4
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
import subprocess
import tempfile
import unittest2 as unittest

from giftwrap.openstack_git_repo import OpenstackGitRepo
from giftwrap.openstack_commit import OpenstackCommit


def _make_outdir(test):
    def wrapper(*args, **kwargs):
        try:
            outdir = tempfile.mkdtemp()
            kwargs['outdir'] = outdir
            return test(*args, **kwargs)
        finally:
            shutil.rmtree(outdir)
    return wrapper


def _make_test_repo(name='testrepo'):
    def decorator(test):
        def wrapper(*args, **kwargs):
            startdir = os.getcwd()
            try:
                testrepo = tempfile.mkdtemp()
                kwargs[name] = testrepo
                os.chdir(testrepo)
                subprocess.check_call(['git', 'init'])
                tf_path = os.path.join(testrepo, 'testfile.txt')
                with open(tf_path, 'w') as tf:
                    tf.write('test content')
                subprocess.check_call(['git', 'add', 'testfile.txt'])
                subprocess.check_call(['git', 'commit', '-m', 'test commit'])
                os.chdir(startdir)
                return test(*args, **kwargs)
            finally:
                shutil.rmtree(testrepo)
        return wrapper
    return decorator


class TestRepo(unittest.TestCase):
    def test_repo(self):
        OpenstackGitRepo(None)

    @_make_test_repo
    def test_repo_properties(self, testrepo):
        repo = OpenstackGitRepo(testrepo, project='baz')
        self.assertFalse(repo.cloned)
        self.assertIs(None, repo.head)
        self.assertEqual('baz', repo.project)
        try:
            repo.branches
        except AttributeError:
            self.assertTrue(True)

    @_make_test_repo
    @_make_outdir
    def test_repo_clone(self, outdir, testrepo):
        repo = OpenstackGitRepo(testrepo, project='bobafett')
        repo.clone(outdir)
        self.assertTrue(repo.cloned)
        self.assertTrue(isinstance(repo.head, OpenstackCommit))
        self.assertEquals(['HEAD', 'master'], repo.branches)

    @_make_test_repo('childrepo')
    @_make_test_repo('parentrepo')
    @_make_outdir
    def test_superrepo(self, outdir, parentrepo, childrepo):
        # Add child as submodule in parent
        try:
            startdir = os.getcwd()
            os.chdir(parentrepo)
            # -f is needed because git usually ignores /tmp dirs
            moduleremote = "file://{}".format(childrepo)
            subprocess.check_call(['git', 'submodule', 'add', '-f',
                                    moduleremote])
            subprocess.check_call(['git', 'commit', '-m', 'adding submodule'])
        finally:
            os.chdir(startdir)
        self.assertTrue(
            os.path.exists(
                os.path.join(parentrepo, os.path.basename(childrepo))))
        repo = OpenstackGitRepo(childrepo, superrepo=parentrepo)
        repo.clone(outdir)
        self.assertTrue(repo.cloned)
        self.assertTrue(isinstance(repo.head, OpenstackCommit))
        self.assertEquals(['HEAD', 'master'], repo.branches)
        self.assertTrue(
            os.path.exists(
                os.path.join(outdir, os.path.basename(childrepo))))
