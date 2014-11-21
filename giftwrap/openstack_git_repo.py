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

import datetime
import logging
import os
import re
import time
import urlparse

from giftwrap.openstack_commit import OpenstackCommit
from git import Repo

LOG = logging.getLogger(__name__)


class OpenstackGitRepo(object):

    def __init__(self, url, project=None, branch='master',
                 metadata_cache_dir=None):
        self.url = url
        self._project = project
        self.branch = branch
        self._repo = None
        self._metadata_cache_dir = metadata_cache_dir
        self._head_commit = None

    @property
    def cloned(self):
        return self._repo is not None

    @property
    def head(self):
        if not self._head_commit and self._repo:
            self._head_commit = OpenstackCommit(self._repo.head.commit,
                                                self.project, self.branch,
                                                self._cache_dir())
        return self._head_commit

    @property
    def project(self):
        if not self._project:
            parsed_url = urlparse.urlparse(self.url)
            project = os.path.splitext(parsed_url.path)[0]
            self._project = re.sub(r'^/', '', project)
        return self._project

    def clone(self, outdir):
        LOG.debug("Cloning '%s' to '%s'", self.url, outdir)
        self._repo = Repo.clone_from(self.url, outdir, recursive=True, depth=1)
        git = self._repo.git
        git.checkout(self.branch)
        self._invalidate_attrs()

    def checkout_branch(self, branch, update=True):
        if not self._repo:
            raise Exception("Cannot checkout on non-existent repo")
        LOG.debug("Checking out branch: %s (update: %s)", branch, update)
        self._repo.git.checkout(branch)
        self._invalidate_attrs()
        self.branch = branch
        if update:
            self._repo.git.pull('origin', branch)

    @property
    def branches(self):
        branches = []
        for ref in self._repo.remotes.origin.refs:
            branches.append(re.sub('^\w*/', '', ref.name))
        return branches

    def __iter__(self):
        if not self._repo:
            raise Exception("iterator called before clone")
        self._commit_iterator = self._repo.iter_commits()
        return self

    def next(self):
        print self._cache_dir()
        return OpenstackCommit(next(self._commit_iterator),
                               self.project, self.branch,
                               self._cache_dir())

    def _cache_dir(self):
        if self._metadata_cache_dir:
            return os.path.join(self._metadata_cache_dir,
                                self.project, self.branch)
        return None

    def _invalidate_attrs(self):
        self._head_commit = None
        self._commit_iterator = None

    def reset_to_date(self, date):
        if self._repo:
            commit_date_sha = None
            for commit in self._repo.iter_commits():
                if commit.committed_date >= date:
                    continue
                elif commit.committed_date < date:
                    commit_date_sha = commit.hexsha
                    break
            if not commit_date_sha:
                raise Exception("Unable to find commit for date %s",
                                datetime.datetime.fromtimestamp(date))
            git = self._repo.git
            LOG.debug("Reset repo '%s' to commit at '%s'", self.url,
                      time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(date)))
            git.checkout(commit_date_sha)
