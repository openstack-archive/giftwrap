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
import platform
import re

from giftwrap.util import execute

SUPPORTED_DISTROS = {
    'deb': ['Ubuntu'],
    'rpm': ['Scientific Linux', 'CentOS.*']
}


class Package(object):

    def __init__(self, name, version, install_path, output_dir,
                 overwrite=False, dependencies=None):
        self.name = name
        self.version = version
        self.install_path = install_path
        self.output_dir = output_dir
        self.overwrite = overwrite
        self.dependencies = dependencies

    def _get_platform_target(self):
        current_distro = platform.linux_distribution()[0]
        for pkgtype, distros in SUPPORTED_DISTROS.iteritems():
            for distro in distros:
                if re.match(distro, current_distro):
                    return pkgtype
        raise Exception("Sorry, '%s' is an unsupported distribution" %
                        current_distro)

    def build(self):
        target = self._get_platform_target()
        overwrite = ''
        if self.overwrite:
            overwrite = '-f'

        deps = ''
        if self.dependencies:
            deps = '-d %s' % (' -d '.join(self.dependencies))

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # not wrapping in a try block - handled by caller
        execute("fpm %s -s dir -t %s -n %s -v %s %s %s" % (overwrite,
                target, self.name, self.version, deps, self.install_path),
                self.output_dir)
