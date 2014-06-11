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


OPENSTACK_PROJECTS = [
    {
        'name': 'keystone',
        'project_path': 'openstack/keystone',
        'giturl': 'https://github.com/openstack/keystone.git'
    }
]


class OpenstackProject(object):

    def __init__(self, name, ref=None, giturl=None):
        if not name in OpenstackProject.get_project_names():
            raise Exception("'%s' is not a supported OpenStack project name" %
                            name)
        self.name = name
        self._project = [p for p in OPENSTACK_PROJECTS if p['name'] == name][0]
        self.ref = ref if ref else 'master'
        self.project_path = self._project['project_path']
        if not giturl:
            self.giturl = OpenstackProject.get_project_giturl(name)
        else:
            self.giturl = giturl

    @staticmethod
    def factory(project_dict):
        name = project_dict.get('name', None)
        ref = project_dict.get('ref', None)
        giturl = project_dict.get('giturl', None)
        return OpenstackProject(name, ref, giturl)

    @staticmethod
    def get_project_names():
        return [n['name'] for n in OPENSTACK_PROJECTS]

    @staticmethod
    def get_project_giturl(name):
        for project in OPENSTACK_PROJECTS:
            if name == project['name']:
                return project['giturl']
        return None
