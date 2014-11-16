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
import tempfile

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

    def _install_gerrit_dependencies(self, repo, project):
        try:
            review = GerritReview(repo.head.change_id, project.git_path)
            LOG.info("Installing '%s' pip dependencies to the virtualenv",
                     project.name)
            execute(project.install_command %
                    review.build_pip_dependencies(string=True),
                    project.install_path)
        except Exception as e:
            LOG.warning("Could not install gerrit dependencies!!! "
                        "Error was: %s", e)

    def _build(self):
        spec = self._spec

        tempdir = tempfile.mkdtemp(prefix='giftwrap')
        src_dir = os.path.join(tempdir, 'src')
        LOG.debug("Temporary working directory: %s", tempdir)

        for project in spec.projects:
            LOG.info("Beginning to build '%s'", project.name)

            # if anything is in our way, see if we can get rid of it
            if os.path.exists(project.install_path):
                if spec.settings.force_overwrite:
                    LOG.info("force_overwrite is set, so removing "
                             "existing path '%s'" % project.install_path)
                    shutil.rmtree(project.install_path)
                else:
                    raise Exception("Install path '%s' already exists" %
                                    project.install_path)
            os.makedirs(project.install_path)

            # clone the project's source to a temporary directory
            project_src_path = os.path.join(src_dir, project.name)
            os.makedirs(project_src_path)

            LOG.info("Fetching source code for '%s'", project.name)
            repo = OpenstackGitRepo(project.giturl, project.gitref)
            repo.clone(project_src_path)

            # start building the virtualenv for the project
            LOG.info("Creating the virtualenv for '%s'", project.name)
            execute(project.venv_command, project.install_path)

            # install into the virtualenv
            LOG.info("Installing '%s' to the virtualenv", project.name)
            venv_python_path = os.path.join(project.install_path, 'bin/python')
            venv_pip_path = os.path.join(project.install_path, 'bin/pip')

            deps = " ".join(project.pip_dependencies)
            execute("%s install %s" % (venv_pip_path, deps))

            if spec.settings.gerrit_dependencies:
                self._install_gerrit_dependencies(repo, project)

            execute("%s setup.py install" % venv_python_path, project_src_path)
            execute("%s install pbr" % venv_pip_path)

            # now build the package
            pkg = Package(project.package_name, project.version,
                          project.install_path, spec.settings.force_overwrite,
                          project.system_dependencies)
            pkg.build()
