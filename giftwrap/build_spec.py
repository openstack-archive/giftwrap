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

    def __init__(self, manifest):
        self._manifest = yaml.load(manifest)
        self.settings = Settings.factory(self._manifest['settings'])
        self.projects = self._render_projects()

    def _render_projects(self):
        projects = []
        if 'projects' in self._manifest:
            for project in self._manifest['projects']:
                projects.append(OpenstackProject.factory(self.settings,
                                                         project))
        return projects
