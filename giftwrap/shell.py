# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2014, Craig Tracey <craigtracey@gmail.com>
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations

import argparse
import logging
import sys

LOG = logging.getLogger(__name__)
log_handler = logging.StreamHandler()
LOG.addHandler(log_handler)
LOG.setLevel(logging.DEBUG)

from giftwrap.build_spec import BuildSpec
from giftwrap.builder import Builder


def build(args):
    """ the entry point for all build subcommand tasks """
    try:
        manifest = None
        templatevars = None

        with open(args.manifest, 'r') as fh:
            manifest = fh.read()

        if args.templatevars:
            with open(args.templatevars, 'r') as fh:
                templatevars = fh.read()

        buildspec = BuildSpec(manifest, args.version, templatevars)
        builder = Builder(buildspec)
        builder.build()
    except Exception as e:
        LOG.exception("Unable to parse manifest. Error: %s", e)
        sys.exit(-1)


def main():
    """ the entry point for all things giftwrap """
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(title='subcommands',
                                       description='valid subcommands',
                                       help='additional help')
    build_subcmd = subparsers.add_parser('build',
                                         description='build giftwrap packages')
    build_subcmd.add_argument('-m', '--manifest', required=True)
    build_subcmd.add_argument('-a', '--allinone', action='store_true')
    build_subcmd.add_argument('-v', '--version')
    build_subcmd.add_argument('-s', '--source', action='store_true')
    build_subcmd.add_argument('-t', '--templatevars')
    build_subcmd.set_defaults(func=build)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
