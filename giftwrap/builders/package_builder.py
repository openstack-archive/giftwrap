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

import distutils.dir_util
import logging
import os
import shutil
import tempfile

from giftwrap.builders import Builder
from giftwrap.openstack_git_repo import OpenstackGitRepo
from giftwrap.package import Package
from giftwrap.util import execute

LOG = logging.getLogger(__name__)


class PackageBuilder(Builder):

    def __init__(self, spec):
        self._temp_dir = None
        super(PackageBuilder, self).__init__(spec)

    def _execute(self, command, cwd=None, exit=0):
        return execute(command, cwd, exit)

    def _make_temp_dir(self, prefix='giftwrap'):
        return tempfile.mkdtemp(prefix)

    def _make_dir(self, path, mode=0o777):
        os.makedirs(path, mode)

    def _prepare_build(self):
        return

    def _prepare_project_build(self, project):
        install_path = project.install_path

        LOG.info("Beginning to build '%s'", project.name)
        if os.path.exists(install_path):
            if self._spec.settings.force_overwrite:
                LOG.info("force_overwrite is set, so removing "
                         "existing path '%s'" % install_path)
                shutil.rmtree(install_path)
            else:
                raise Exception("Install path '%s' already exists" %
                                install_path)

    def _clone_project(self, giturl, name, gitref, depth, path):
        LOG.info("Fetching source code for '%s'", name)
        repo = OpenstackGitRepo(giturl, name, gitref, depth=depth)
        repo.clone(path)
        return repo

    def _create_virtualenv(self, venv_command, path):
        self._execute(venv_command, path)

    def _install_pip_dependencies(self, venv_path, dependencies,
                                  use_constraints=True):
        pip_path = self._get_venv_pip_path(venv_path)
        install = "install"
        if use_constraints:
            for constraint in self._constraints:
                install = "%s -c %s" % (install, constraint)

        for dependency in dependencies:
            self._execute("%s %s %s" % (pip_path, install, dependency))

    def _copy_sample_config(self, src_clone_dir, project):
        src_config = os.path.join(src_clone_dir, 'etc')
        dest_config = os.path.join(project.install_path, 'etc')

        if not os.path.exists(src_config):
            LOG.warning("Project configuration does not seem to exist "
                        "in source repo '%s'. Skipping.", project.name)
        else:
            LOG.debug("Copying config from '%s' to '%s'", src_config,
                      dest_config)
            distutils.dir_util.copy_tree(src_config, dest_config)

    def _install_project(self, venv_path, src_clone_dir):
        pip_path = self._get_venv_pip_path(venv_path)
        install = "install"
        for constraint in self._constraints:
            install = "%s -c %s" % (install, constraint)
        self._execute("%s %s %s" % (pip_path, install, src_clone_dir))

    def _finalize_project_build(self, project):
        # build the package
        pkg = Package(project.package_name, project.version,
                      project.install_path, self._spec.settings.output_dir,
                      self._spec.settings.force_overwrite,
                      project.system_dependencies)
        pkg.build()

    def _finalize_build(self):
        return

    def _cleanup_build(self):
        shutil.rmtree(self._temp_dir)
        for project in self._spec.projects:
            install_path = project.install_path
            do_deletion = (self._spec.settings.force_overwrite and
                           os.path.exists(install_path))
            if do_deletion:
                LOG.info("force_overwrite is set, so removing "
                         "path created for build '%s'" % install_path)
                shutil.rmtree(install_path)
