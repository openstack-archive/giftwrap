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

LOG = logging.getLogger(__name__)


class Builder(object):

    def __init__(self, spec):
        self._spec = spec
        self.settings = spec.settings

    def _build(self):
        raise NotImplementedError()

    def _validate_settings(self):
        raise NotImplementedError()

    def build(self):
        self._validate_settings()
        self._build()


from giftwrap.builders.package_builder import PackageBuilder
from giftwrap.builders.docker_builder import DockerBuilder


def create_builder(spec):
    if spec.settings.build_type == 'package':
        return PackageBuilder(spec)
    elif spec.settings.build_type == 'docker':
        return DockerBuilder(spec)
    raise Exception("Unknown build_type: '%s'", spec.settings.build_type)
