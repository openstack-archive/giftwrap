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

import yaml

from giftwrap.openstack_project import OpenstackProject
from giftwrap.settings import Settings


class BuildSpec(object):

    def __init__(self, manifest, version, build_type=None, parallel=True,
                 limit_projects=None, fpm_options=None):
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
        self.fpm_options = fpm_options
        manifest_settings['parallel_build'] = parallel
        self.settings = Settings.factory(manifest_settings)
        self.projects = self._render_projects(limit_projects)

    def _render_projects(self, limit_projects):
        projects = []
        if 'projects' in self._manifest:
            for project in self._manifest['projects']:
                if limit_projects is None or project['name'] in limit_projects:
                    projects.append(OpenstackProject.factory(self.settings,
                                                             project,
                                                             self.version))
        return projects
