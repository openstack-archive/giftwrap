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
import re

from git import Repo


class OpenstackGitRepo(object):
    def __init__(self, url, ref='master'):
        self.url = url
        self.ref = ref
        self._repo = None
        self._head = None
        self._change_id = None
        self._committed_date = None

    @property
    def cloned(self):
        return self._repo is not None

    @property
    def head(self):
        if not self._head and self._repo:
            self._head = self._repo.head.commit.hexsha
        return self._head

    @property
    def change_id(self):
        if not self._change_id and self._repo:
            for commit in self._repo.iter_commits():
                match = re.search('Change-Id:\s*(I\w+)', commit.message)
                if match:
                    self._change_id = match.group(1)
                    break
        return self._change_id

    @property
    def committed_date(self):
        if not self._committed_date and self._repo:
            self._committed_date = self._repo.head.commit.committed_date
        return self._committed_date

    def _invalidate_attrs(self):
        self._head = None
        self._change_id = None
        self._committed_date = None

    def clone(self, outdir):
        self._repo = Repo.clone_from(self.url, outdir)
        git = self._repo.git
        git.checkout(self.ref)
        self._invalidate_attrs()

    def reset_to_date(self, date):
        if self._repo:
            commit_date_sha = None
            for commit in self._repo.iter_commits():
                if commit.committed_date >= date:
                    commit_date_sha = commit.hexsha
                elif commit.committed_date < date:
                    break
            if not commit_date_sha:
                raise Exception("Unable to find commit for date %s",
                                datetime.datetime.fromtimestamp(date))
            git = self._repo.git
            git.checkout(commit_date_sha)
