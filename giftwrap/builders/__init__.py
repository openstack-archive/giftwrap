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
import threading

import requests

from giftwrap.gerrit import GerritReview
from stevedore.driver import DriverManager
from stevedore.extension import ExtensionManager

from abc import abstractmethod, ABCMeta

BUILDER_DRIVER_NAMESPACE = 'giftwrap.builder.drivers'
LOG = logging.getLogger(__name__)


class Builder(object):
    __metaclass__ = ABCMeta

    def __init__(self, spec):
        self._temp_dir = None
        self._temp_src_dir = None
        self._spec = spec
        self._thread_exit = []
        self._constraints = []

    @staticmethod
    def builder_names(ext_mgr=None):
        if not ext_mgr:
            ext_mgr = ExtensionManager(BUILDER_DRIVER_NAMESPACE)
        return ext_mgr.names()

    def _get_venv_pip_path(self, venv_path):
        return os.path.join(venv_path, 'bin/pip')

    def _get_gerrit_dependencies(self, repo, project):
        try:
            review = GerritReview(repo.head.change_id, project.git_path)
            return review.build_pip_dependencies()
        except Exception as e:
            LOG.warning("Could not install gerrit dependencies!!! "
                        "Error was: %s", e)
            return []

    def _get_constraints(self):
        cfiles = []
        try:
            for i, cons_url in enumerate(self._spec.settings.constraints):
                if cons_url.startswith('/') or cons_url.startswith('.'):
                    with open(cons_url, 'rb') as cf:
                        constraints = cf.read()
                else:
                    response = requests.get(cons_url)

                    # Raise an error if we got a bad URL
                    response.raise_for_status()

                    constraints = response.text.encode('utf-8')
                cfilepath = os.path.join(self._temp_dir,
                                         'constraints-%s.txt' % i)

                with open(cfilepath, 'wb') as cfile:
                    cfile.write(constraints)

                cfiles.append(cfilepath)

            return cfiles

        except Exception as e:
            raise Exception("Unable to construct constraints. Error: %s" % e)

    def _build_project(self, project):
        try:
            self._prepare_project_build(project)
            self._make_dir(project.install_path)

            # clone the source
            src_clone_dir = os.path.join(self._temp_src_dir, project.name)
            repo = self._clone_project(project.giturl, project.name,
                                       project.gitref, project.gitdepth,
                                       src_clone_dir)

            # create and build the virtualenv
            self._create_virtualenv(project.venv_command, project.install_path)
            dependencies = []
            if project.pip_dependencies:
                dependencies = project.pip_dependencies
            if self._spec.settings.gerrit_dependencies:
                dependencies += self._get_gerrit_dependencies(repo, project)

            if len(dependencies):
                self._install_pip_dependencies(project.install_path,
                                               dependencies)

            if self._spec.settings.include_config:
                self._copy_sample_config(src_clone_dir, project)

            self._install_project(project.install_path, src_clone_dir, project)

            if project.postinstall_dependencies:
                dependencies = project.postinstall_dependencies
                self._install_pip_dependencies(project.install_path,
                                               dependencies, False)

            # finish up
            self._finalize_project_build(project)
        except Exception as e:
            LOG.error("Oops. Problem building %s: %s", project.name, e)
            self._thread_exit.append(-1)
        self._thread_exit.append(0)

    def build(self):
        spec = self._spec

        self._prepare_build()

        # Create a temporary directory for the source code
        self._temp_dir = self._make_temp_dir()
        self._temp_src_dir = os.path.join(self._temp_dir, 'src')
        LOG.debug("Temporary working directory: %s", self._temp_dir)

        # get constraints paths
        self._constraints = self._get_constraints()

        threads = []
        for project in spec.projects:
            if spec.settings.parallel_build:
                t = threading.Thread(target=self._build_project,
                                     name=project.name, args=(project,))
                threads.append(t)
                t.start()
            else:
                self._build_project(project)

        rc = 0
        if spec.settings.parallel_build:
            for thread in threads:
                thread.join()

            for thread_exit in self._thread_exit:
                if thread_exit != 0:
                    rc = thread_exit

        self._finalize_build()
        return rc

    def cleanup(self):
        self._cleanup_build()

    @abstractmethod
    def _execute(self, command, cwd=None, exit=0):
        return

    @abstractmethod
    def _make_temp_dir(self, prefix='giftwrap'):
        return

    @abstractmethod
    def _make_dir(self, path, mode=0o777):
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
    def _install_pip_dependencies(self, venv_path, dependencies,
                                  use_constraints=True):
        return

    @abstractmethod
    def _copy_sample_config(self, src_clone_dir, project):
        return

    @abstractmethod
    def _install_project(self, venv_path, src_clone_dir, project):
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


class PipBuilder(Builder):
    def _install_project(self, venv_path, src_clone_dir, project):
        pip_path = self._get_venv_pip_path(venv_path)
        install = "install"
        for constraint in self._constraints:
            with open(constraint, 'r') as constraint_content:
                orig = constraint_content.read()
            editted_constraint = '%s.editted' % constraint
            with open(editted_constraint, 'w') as new_constraint:
                editted = False
                for orig_line in orig.split('\n'):
                    if orig_line.startswith("%s==" % project.name):
                        editted = True
                        LOG.info('Removed project {} from '
                                 'constraints'.format(orig_line.strip()))
                        continue
                    if orig_line:
                        new_constraint.write("%s\n" % orig_line)
            if editted:
                constraint = editted_constraint
            install = "%s -c %s" % (install, constraint)
        self._execute("%s %s %s" % (pip_path, install, src_clone_dir))


from giftwrap.builders.package_builder import PackageBuilder  # noqa
from giftwrap.builders.docker_builder import DockerBuilder  # noqa


class BuilderFactory:

    @staticmethod
    def create_builder(builder_type, build_spec):
        driver_mgr = DriverManager(namespace=BUILDER_DRIVER_NAMESPACE,
                                   name=builder_type,
                                   invoke_args=(build_spec,),
                                   invoke_on_load=True)
        return driver_mgr.driver
