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

from giftwrap.gerrit import GerritReview

from abc import abstractmethod, ABCMeta

LOG = logging.getLogger(__name__)


class Builder(object):
    __metaclass__ = ABCMeta

    def __init__(self, spec):
        self._temp_dir = None
        self._temp_src_dir = None
        self._spec = spec

    def _get_venv_pip_path(self, venv_path):
        return os.path.join(venv_path, 'bin/pip')

    def _get_gerrit_dependencies(self, repo, project):
        try:
            review = GerritReview(repo.head.change_id, project.git_path)
            return review.build_pip_dependencies(string=True)
        except Exception as e:
            LOG.warning("Could not install gerrit dependencies!!! "
                        "Error was: %s", e)
            return ""

    def _build_project(self, project):
        self._prepare_project_build(project)
        self._make_dir(project.install_path)

        # clone the source
        src_clone_dir = os.path.join(self._temp_src_dir, project.name)
        repo = self._clone_project(project.giturl, project.name,
                                   project.gitref, project.gitdepth,
                                   src_clone_dir)

        # create and build the virtualenv
        self._create_virtualenv(project.venv_command, project.install_path)
        dependencies = ""
        if project.pip_dependencies:
            dependencies = " ".join(project.pip_dependencies)
        if self._spec.settings.gerrit_dependencies:
            dependencies = "%s %s" % (dependencies,
                                      self._get_gerrit_dependencies(repo,
                                                                    project))
        if len(dependencies):
            self._install_pip_dependencies(project.install_path, dependencies)

        if self._spec.settings.include_config:
            self._copy_sample_config(src_clone_dir, project)

        self._install_project(project.install_path, src_clone_dir)

        if project.postinstall_dependencies:
            self._install_postinstall_dependencies(project)

        # finish up
        self._finalize_project_build(project)

    def build(self):
        spec = self._spec

        self._prepare_build()

        # Create a temporary directory for the source code
        self._temp_dir = self._make_temp_dir()
        self._temp_src_dir = os.path.join(self._temp_dir, 'src')
        LOG.debug("Temporary working directory: %s", self._temp_dir)

        for project in spec.projects:
            self._build_project(project)

        self._finalize_build()

    def cleanup(self):
        self._cleanup_build()

    @abstractmethod
    def _execute(self, command, cwd=None, exit=0):
        return

    @abstractmethod
    def _make_temp_dir(self, prefix='giftwrap'):
        return

    @abstractmethod
    def _make_dir(self, path, mode=0777):
        return

    @abstractmethod
    def _prepare_build(self):
        return

    @abstractmethod
    def _prepare_project_build(self, project):
        return

    @abstractmethod
    def _clone_project(self, project):
        return

    @abstractmethod
    def _create_virtualenv(self, venv_command, path):
        return

    @abstractmethod
    def _install_pip_dependencies(self, venv_path, dependencies):
        return

    @abstractmethod
    def _copy_sample_config(self, src_clone_dir, project):
        return

    @abstractmethod
    def _install_project(self, venv_path, src_clone_dir):
        return

    @abstractmethod
    def _install_postinstall_dependencies(self, project):
        return

    @abstractmethod
    def _finalize_project_build(self, project):
        return

    @abstractmethod
    def _finalize_build(self):
        return

    @abstractmethod
    def _cleanup_build(self):
        return


from giftwrap.builders.package_builder import PackageBuilder  # noqa
from giftwrap.builders.docker_builder import DockerBuilder  # noqa


class BuilderFactory:

    @staticmethod
    def create_builder(builder_type, build_spec):
        targetclass = "%sBuilder" % builder_type.capitalize()
        return globals()[targetclass](build_spec)
