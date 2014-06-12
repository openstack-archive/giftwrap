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

import os
import sys

from giftwrap.gerrit import GerritReview
from giftwrap.openstack_git_repo import OpenstackGitRepo
from giftwrap.shell import LOG


class Builder(object):
    def __init__(self, spec):
        self._spec = spec

    def build(self):
        """ this is where all the magic happens """

        try:
            spec = self._spec
            base_path = spec.settings.base_path
            # version = spec.settings.version

            os.makedirs(base_path)
            for project in self._spec.projects:
                project_git_path = os.path.join(base_path, project.name)
                repo = OpenstackGitRepo(project.giturl, project.ref)
                repo.clone(project_git_path)

                review = GerritReview(repo.change_id, project.project_path)
                print "Cloned %s with change_id of: %s" % (project.name, repo.change_id)
                print "...with pip dependencies of:"
                print review.build_pip_dependencies(string=True)

                # execute('python tools/install_venv.py', cwd=project_git_path)
                # deps_string = " -d ".join(deps)
                # execute("fpm -s dir -t deb -n foobar -d %s /tmp/openstack" % deps_string)
        except Exception as e:
            LOG.exception("Oops. Something went wrong. Error was:\n%s", e)
            sys.exit(-1)
