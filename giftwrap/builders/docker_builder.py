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
import jinja2
import json
import logging
import os
import re
import tempfile

from giftwrap.builders import Builder

LOG = logging.getLogger(__name__)

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
    'python-pip',
    'build-essential'
]
DEFAULT_SRC_PATH = '/opt/openstack'


class DockerBuilder(Builder):

    def __init__(self, spec):
        self.base_image = 'ubuntu:14.04'
        self.maintainer = 'maintainer@example.com'
        self.envvars = {'DEBIAN_FRONTEND': 'noninteractive'}
        self._commands = []
        super(DockerBuilder, self).__init__(spec)

    def _execute(self, command, cwd=None, exit=0):
        if cwd:
            self._commands.append("cd %s" % (cwd))
        self._commands.append(command)
        if cwd:
            self._commands.append("cd -")

    def _make_temp_dir(self, prefix='giftwrap'):
        return "/tmp/giftwrap"
        self._commands.append("mktemp -d -t %s.XXXXXXXXXX" % prefix)

    def _make_dir(self, path, mode=0o777):
        self._commands.append("mkdir -p -m %o %s" % (mode, path))

    def _prepare_project_build(self, project):
        self.image_name = "giftwrap/openstack:%s" % (project.version)
        return

    def _clone_project(self, giturl, name, gitref, depth, path):
        cmd = "git clone %s -b %s --depth=%d %s" % (giturl, gitref,
                                                    depth, path)
        self._commands.append(cmd)

    def _create_virtualenv(self, venv_command, path):
        self._execute(venv_command, path)

    def _install_pip_dependencies(self, venv_path, dependencies):
        pip_path = self._get_venv_pip_path(venv_path)
        for dependency in dependencies:
            self._execute("%s install '%s'" % (pip_path, dependency))

    def _copy_sample_config(self, src_clone_dir, project):
        src_config = os.path.join(src_clone_dir, 'etc')
        dest_config = os.path.join(project.install_path, 'etc')

        self._commands.append("if [ -d %s ]; then cp -R %s %s; fi" % (
            src_config, src_config, dest_config))

    def _install_project(self, venv_path, src_clone_dir):
        pip_path = self._get_venv_pip_path(venv_path)
        self._execute("%s install %s" % (pip_path, src_clone_dir))

    def _finalize_project_build(self, project):
        self._commands.append("rm -rf %s" % self._temp_dir)
        for command in self._commands:
            print(command)

    def _finalize_build(self):
        template_vars = {
            'commands': self._commands
        }
        print(self._render_dockerfile(template_vars))
        self._build_image()

    def _cleanup_build(self):
        return

    def _prepare_build(self):
        self._commands.append('apt-get update && apt-get install -y %s' %
                              ' '.join(APT_REQUIRED_PACKAGES))
        self._commands.append("pip install -U pip virtualenv")

    def _set_path(self):
        path = ":".join(self._paths)
        self.envvars['PATH'] = "%s:$PATH" % path

    def _render_dockerfile(self, extra_vars):
        template_vars = self.__dict__
        template_vars.update(extra_vars)
        template_loader = jinja2.FileSystemLoader(searchpath='/')
        template_env = jinja2.Environment(loader=template_loader)
        template = template_env.get_template(DEFAULT_TEMPLATE_FILE)
        return template.render(template_vars)

    def _build_image(self):
        template_vars = {
            'commands': self._commands
        }
        dockerfile_contents = self._render_dockerfile(template_vars)

        tempdir = tempfile.mkdtemp()
        dockerfile = os.path.join(tempdir, 'Dockerfile')
        with open(dockerfile, "w") as w:
            w.write(dockerfile_contents)
        docker_client = docker.Client(base_url='unix://var/run/docker.sock',
                                      timeout=10)
        build_result = docker_client.build(path=tempdir, stream=True,
                                           tag=self.image_name)
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
