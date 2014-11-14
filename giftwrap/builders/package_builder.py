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
import shutil

from giftwrap.gerrit import GerritReview
from giftwrap.openstack_git_repo import OpenstackGitRepo
from giftwrap.package import Package
from giftwrap.util import execute

LOG = logging.getLogger(__name__)


from giftwrap.builder import Builder


class PackageBuilder(Builder):

    def __init__(self, spec):
        self._all_in_one = False
        super(PackageBuilder, self).__init__(spec)

    def _validate_settings(self):
        pass

    def _build(self):
        spec = self._spec
        for project in self._spec.projects:
            LOG.info("Beginning to build '%s'", project.name)
            if (os.path.exists(project.install_path) and
               spec.settings.force_overwrite):
                LOG.info("force_overwrite is set, so removing "
                         "existing path '%s'" % project.install_path)
                shutil.rmtree(project.install_path)
            os.makedirs(project.install_path)

            LOG.info("Fetching source code for '%s'", project.name)
            repo = OpenstackGitRepo(project.giturl, project.gitref)
            repo.clone(project.install_path)
            review = GerritReview(repo.change_id, project.git_path)

            LOG.info("Creating the virtualenv for '%s'", project.name)
            execute(project.venv_command, project.install_path)

            LOG.info("Installing '%s' pip dependencies to the virtualenv",
                     project.name)
            execute(project.install_command %
                    review.build_pip_dependencies(string=True),
                    project.install_path)

            LOG.info("Installing '%s' to the virtualenv", project.name)
            execute(".venv/bin/python setup.py install",
                    project.install_path)

            if not spec.settings.all_in_one:
                pkg = Package(project.package_name, project.version,
                              project.install_path, True,
                              spec.settings.force_overwrite)
                pkg.build()
