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

DEFAULT_PROJECT_PATH = '/opt/openstack'


class BuildSpec(object):

    def __init__(self, manifest):
        self._spec = yaml.load(manifest)
        self._project_path = None
        self._projects = None

    @property
    def project_path(self):
        if not self._project_path:
            if 'project_path' in self._spec.keys():
                self._project_path = self._spec['project_path']
            else:
                self._project_path = DEFAULT_PROJECT_PATH
        return self._project_path

    @property
    def projects(self):
        if 'projects' in self._spec.keys() and not self._projects:
            self._projects = self._spec['projects']
        return self._projects
