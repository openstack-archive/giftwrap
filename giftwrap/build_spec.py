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

import git
import yaml

from giftwrap.openstack_project import OpenstackProject
from giftwrap.settings import Settings


class BuildSpec(object):

    def __init__(self, manifest, version, build_type=None, parallel=True,
                 limit_projects=None):
        self._manifest = yaml.load(manifest)
        self.version = version
        self.build_type = build_type
        manifest_settings = self._manifest['settings']
        if version:
            manifest_settings['version'] = version
        if build_type:
            manifest_settings['build_type'] = build_type
        if build_type == 'docker':
            parallel = False
        manifest_settings['parallel_build'] = parallel
        self.settings = Settings.factory(manifest_settings)
        self.projects = self._render_projects(limit_projects)

    def _render_projects(self, limit_projects):
        if 'superrepo' in self._manifest:
            if 'projects' not in self._manifest:
                self._manifest['projects'] = []
            existing_project_names = set()
            for project in self._manifest['projects']:
                existing_project_names.add(project['name'])
            # Read all dirs with a setup.py as projects
            repo = git.Repo(self._manifest['superrepo'])
            try:
                # Try it as a branch
                repo.heads[self.version].checkout()
            except IndexError:
                # Nope, detach head
                repo.head.reference = repo.commit(self.version)
            for subdir in os.listdir(repo.working_tree_dir):
                # Skip any projects explicitly in the manifest
                if subdir in existing_project_names:
                    continue
                subpath = os.path.join(repo.working_tree_dir, subdir)
                if not os.path.exists(os.path.join(subpath, 'setup.py')):
                    continue
                # skip non git repos since we won't be able to figure out a
                # version
                try:
                    subrepo = git.Repo(os.path.join(repo.working_tree_dir,
                                                    subdir))
                except git.exc.InvalidGitRepositoryError:
                    continue
                project = {}
                project['gitref'] = subrepo.head.commit.hexsha
                project['name'] = subdir
                project['giturl'] = subrepo.working_tree_dir
                self._manifest['projects'].append(project)
        projects = []
        if 'projects' in self._manifest:
            for project in self._manifest['projects']:
                if limit_projects is None or project['name'] in limit_projects:
                    projects.append(OpenstackProject.factory(self.settings,
                                                             project,
                                                             self.version))
        return projects
