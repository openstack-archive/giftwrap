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
import signal
import sys

from giftwrap.builders import Builder, BuilderFactory
from giftwrap.build_spec import BuildSpec
from giftwrap.color import ColorStreamHandler

LOG = logging.getLogger(__name__)


def _setup_logger(level=logging.INFO):
    logger = logging.getLogger()
    logger.setLevel(level)
    log_handler = ColorStreamHandler(sys.stdout)
    fmt = logging.Formatter(fmt='%(asctime)s %(threadName)s %(name)s '
                            '%(levelname)s: %(message)s',
                            datefmt='%F %H:%M:%S')
    log_handler.setFormatter(fmt)
    logger.addHandler(log_handler)


def build(args):
    """ the entry point for all build subcommand tasks """
    builder = None
    fail = False
    try:
        manifest = None

        with open(args.manifest, 'r') as fh:
            manifest = fh.read()

        buildspec = BuildSpec(manifest, args.version, args.type, args.parallel,
                              args.projects)
        builder = BuilderFactory.create_builder(args.type, buildspec)

        def _signal_handler(*args):
            LOG.info("Process interrrupted. Cleaning up.")
            builder.cleanup()
            sys.exit()
        signal.signal(signal.SIGINT, _signal_handler)

        rc = builder.build()
    except Exception as e:
        LOG.exception("Oops something went wrong: %s", e)
        fail = True

    if builder:
        builder.cleanup()
    if fail:
        sys.exit(-1)
    sys.exit(rc)


def main():
    """ the entry point for all things giftwrap """
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Set logging level to DEBUG')

    subparsers = parser.add_subparsers(title='subcommands',
                                       description='valid subcommands',
                                       help='additional help')
    build_subcmd = subparsers.add_parser('build',
                                         description='build giftwrap packages')
    build_subcmd.add_argument('-m', '--manifest', required=True)
    build_subcmd.add_argument('-v', '--version')
    build_subcmd.add_argument('-t', '--type', choices=Builder.builder_names(),
                              required=True)
    build_subcmd.add_argument('-s', '--synchronous', dest='parallel',
                              action='store_false')

    def csvarg(arg):
        if arg is not None:
            return arg.split(',')

    build_subcmd.add_argument('-p', '--projects', type=csvarg, dest='projects')
    build_subcmd.set_defaults(func=build)

    args = parser.parse_args()

    log_level = logging.INFO
    if args.debug:
        log_level = logging.DEBUG
    _setup_logger(log_level)

    args.func(args)


if __name__ == '__main__':
    main()
