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

import docker
import json
import logging
import os
import re
import tempfile

from giftwrap.builder import Builder

LOG = logging.getLogger(__name__)

import jinja2

DEFAULT_TEMPLATE_FILE = os.path.join(os.path.dirname(
                                     os.path.dirname(__file__)),
                                     'templates/Dockerfile.jinja2')
APT_REQUIRED_PACKAGES = [
    'libffi-dev',
    'libxml2-dev',
    'libxslt1-dev',
    'git',
    'wget',
    'curl',
    'libldap2-dev',
    'libsasl2-dev',
    'libssl-dev',
    'python-dev',
    'libmysqlclient-dev',
    'python-virtualenv',
    'python-pip',
    'build-essential'
]


class DockerBuilder(Builder):

    def __init__(self, spec):
        self.template = DEFAULT_TEMPLATE_FILE
        self.base_image = 'ubuntu:12.04'
        self.maintainer = 'maintainer@example.com'
        self.envvars = {'DEBIAN_FRONTEND': 'noninteractive'}
        self._paths = []
        super(DockerBuilder, self).__init__(spec)

    def _validate_settings(self):
        if not self.settings.all_in_one:
            LOG.warn("The Docker builder does not support all-in-one")

    def _get_prep_commands(self):
        commands = []
        commands.append('apt-get update && apt-get install -y %s' %
                        ' '.join(APT_REQUIRED_PACKAGES))
        return commands

    def _get_build_commands(self, src_path):

        commands = []
        commands.append('mkdir -p %s' % src_path)

        for project in self._spec.projects:
            if project.system_dependencies:
                commands.append('apt-get update && apt-get install -y %s' %
                                ' '.join(project.system_dependencies))

            project_src_path = os.path.join(src_path, project.name)
            commands.append('git clone --depth 1 %s -b %s %s' %
                            (project.giturl, project.gitref, project_src_path))
            commands.append('COMMIT=`git rev-parse HEAD` && echo "%s $COMMIT" '
                            '> %s/gitinfo' % (project.giturl,
                                              project.install_path))
            commands.append('mkdir -p %s' %
                            os.path.dirname(project.install_path))
            commands.append('virtualenv --system-site-packages %s' %
                            project.install_path)

            project_bin_path = os.path.join(project.install_path, 'bin')
            self._paths.append(project_bin_path)
            venv_python_path = os.path.join(project_bin_path, 'python')
            venv_pip_path = os.path.join(project_bin_path, 'pip')

            if project.pip_dependencies:
                commands.append("%s install %s" % (venv_pip_path,
                                ' '.join(project.pip_dependencies)))
            commands.append('cd %s && %s setup.py install && cd -' %
                            (project_src_path, venv_python_path))
            commands.append("%s install pbr" % venv_pip_path)

        return commands

    def _get_cleanup_commands(self, src_path):
        commands = []
        commands.append('rm -rf %s' % src_path)
        return commands

    def _set_path(self):
        path = ":".join(self._paths)
        self.envvars['PATH'] = "%s:$PATH" % path

    def _render_dockerfile(self, extra_vars):
        template_vars = self.__dict__
        template_vars.update(extra_vars)
        template_loader = jinja2.FileSystemLoader(searchpath='/')
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template(self.template)
        return template.render(template_vars)

    def _build(self):
        src_path = '/tmp/build'
        commands = self._get_prep_commands()
        commands += self._get_build_commands(src_path)
        commands += self._get_cleanup_commands(src_path)
        self._set_path()
        dockerfile_contents = self._render_dockerfile(locals())

        tempdir = tempfile.mkdtemp()
        dockerfile = os.path.join(tempdir, 'Dockerfile')
        with open(dockerfile, "w") as w:
            w.write(dockerfile_contents)

        docker_client = docker.Client(base_url='unix://var/run/docker.sock',
                                      version='1.10', timeout=10)

        build_result = docker_client.build(path=tempdir, stream=True,
                                           tag='openstack-9.0:bbc6')
        for line in build_result:
            LOG.info(line.strip())

    # I borrowed this from docker/stackbrew, should cull it down
    # to be more sane.
    def _parse_result(self, build_result):
        build_success_re = r'^Successfully built ([a-f0-9]+)\n$'
        if isinstance(build_result, tuple):
            img_id, logs = build_result
            return img_id, logs
        else:
            lines = [line for line in build_result]
            try:
                parsed_lines = [json.loads(e).get('stream', '') for e in lines]
            except ValueError:
                # sometimes all the data is sent on a single line ????
                #
                # ValueError: Extra data: line 1 column 87 - line 1 column
                # 33268 (char 86 - 33267)
                line = lines[0]
                # This ONLY works because every line is formatted as
                # {"stream": STRING}
                parsed_lines = [
                    json.loads(obj).get('stream', '') for obj in
                    re.findall('{\s*"stream"\s*:\s*"[^"]*"\s*}', line)
                ]

            for line in parsed_lines:
                match = re.match(build_success_re, line)
                if match:
                    return match.group(1), parsed_lines
            return None, lines
