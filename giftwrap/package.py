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

import platform

from giftwrap.util import execute

SUPPORTED_DISTROS = {
    'Ubuntu': 'deb',
    'Scientific Linux': 'rpm'
}


class Package(object):

    def __init__(self, name, version, path, include_src=True):
        self.name = name
        self.version = version
        self.path = path
        self.include_src = include_src

    def build(self):
        distro = platform.linux_distribution()[0]
        if distro not in SUPPORTED_DISTROS.keys():
            raise Exception("Sorry, '%s' is an unsupported distribution" %
                            distro)
        target = SUPPORTED_DISTROS[distro]

        # not wrapping in a try block - handled by caller
        execute("fpm -s dir -t %s -n %s -v %s %s" %
                (target, self.name, self.version, self.path))
