# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2014, John Dewey
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
#    under the License.

import logging
import sys

from giftwrap.color import ColorStreamHandler

NAME = 'giftwrap'
_logger = None


def get_logger():
    global _logger


    if _logger:
        return _logger

    _logger = logging.getLogger(NAME)
    log_handler = ColorStreamHandler(sys.stdout)
    fmt = logging.Formatter(fmt='%(asctime)s %(levelname)s: %(message)s',
                            datefmt='%F %H:%M:%S')
    log_handler.setFormatter(fmt)
    _logger.addHandler(log_handler)
    _logger.setLevel(logging.INFO)
    _logger.propagate = False

    return _logger


def set_level_debug():
    logger = get_logger()
    logger.setLevel(logging.DEBUG)
