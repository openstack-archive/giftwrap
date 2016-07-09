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

import shutil
import tempfile
import unittest2 as unittest

from giftwrap.openstack_git_repo import OpenstackGitRepo
from giftwrap.openstack_commit import OpenstackCommit
from giftwrap.tests import utils


class TestRepo(unittest.TestCase):
    def test_repo(self):
        OpenstackGitRepo(None)

    @utils.make_test_repo()
    def test_repo_properties(self, testrepo):
        repo = OpenstackGitRepo(testrepo, project='baz')
        self.assertFalse(repo.cloned)
        self.assertIs(None, repo.head)
        self.assertEqual('baz', repo.project)
        try:
            repo.branches
        except AttributeError:
            self.assertTrue(True)

    @utils.make_test_repo()
    def test_repo_clone(self, testrepo):
        try:
            outdir = tempfile.mkdtemp()
            repo = OpenstackGitRepo(testrepo, project='bobafett')
            repo.clone(outdir)
            self.assertTrue(repo.cloned)
            self.assertTrue(isinstance(repo.head, OpenstackCommit))
            self.assertEquals(['HEAD', 'master'], repo.branches)
        finally:
            shutil.rmtree(outdir)
