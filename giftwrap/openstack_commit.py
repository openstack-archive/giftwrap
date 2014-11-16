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

import logging
import os
import re
import yaml

from giftwrap.gerrit import GerritReview

LOG = logging.getLogger(__name__)


class OpenstackCommit(object):

    def __init__(self, commit, project, branch, meta_cache_dir=None):
        self.commit = commit
        self.project = project
        self.branch = branch
        self._change_id = None
        self._editable_dependencies = None
        self._pip_dependencies = None
        self._is_merge = None
        self._parent = None
        self._gerrit_review = None
        self._meta_cache_dir = meta_cache_dir

    @property
    def hexsha(self):
        return self.commit.hexsha

    @property
    def change_id(self):
        if not self._change_id:
            self._change_id = str(self._get_change_id())
        return self._change_id

    @property
    def is_merge(self):
        if self._is_merge is None:
            self._is_merge = (len(self.commit.parents) == 2)
        return self._is_merge

    @property
    def parent(self):
        if self.is_merge:
            self._parent = OpenstackCommit(self.commit.parents[1],
                                           self.project, self.branch)
        return self._parent

    @property
    def gerrit_review(self):
        if not self._gerrit_review:
            self._gerrit_review = GerritReview(self.change_id,
                                               self.project, self.branch)
        return self._gerrit_review

    def _gather_dependencies(self):
        try:
            deps = self.gerrit_review.build_pip_dependencies()
            self._editable_dependencies = []
            self._pip_dependencies = {}
            for dep in deps:
                if '-e' in dep:
                    self._editable_dependencies.append(dep)
                else:
                    parts = dep.split('==')
                    self._pip_dependencies[parts[0]] = parts[1]
        except Exception as e:
            LOG.debug("Couldn't find dependencies for %s: %s", self.hexsha, e)

    @property
    def pip_dependencies(self):
        if not self._pip_dependencies:
            self._gather_dependencies()
        return self._pip_dependencies

    @property
    def editable_dependencies(self):
        if not self._editable_dependencies:
            self._gather_dependencies()
        return self._editable_dependencies

    def _get_change_id(self):
        commit = self.commit
        if self.is_merge:
            commit = self.parent.commit
        match = re.search('Change-Id:\s*(I\w+)', commit.message)
        if match:
            return match.group(1)

    def is_cached(self):
        return os.path.isfile(self.cache_file)

    @property
    def cache_file(self):
        return os.path.join(self._meta_cache_dir, self.hexsha)

    def _get_from_cache(self, key):
        if self.is_cached():
            with open(self.cache_file, 'r') as fh:
                cached_data = yaml.load(fh)
                if key in cached_data:
                    return cached_data[key]
        return None

    def is_cacheable(self):
        if self.pip_dependencies or self.editable_dependencies:
            return True
        return False

    def __dict__(self):
        data = {}
        data['pip_dependencies'] = self.pip_dependencies
        data['editable_dependencies'] = self.editable_dependencies
        data['change_id'] = self.change_id
        return data

    def persist_to_cache(self):
        if not self.is_cacheable():
            LOG.debug("Not caching %s as there is no point", self.hexsha)
            return
        dirname = os.path.dirname(self.cache_file)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(self.cache_file, 'w') as fh:
            fh.write(yaml.dump(self.__dict__()))
