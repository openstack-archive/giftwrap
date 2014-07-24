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

from colorama import AnsiToWin32, Fore, Style
from logging import INFO, DEBUG, WARNING, ERROR, CRITICAL, StreamHandler


class ColorStreamHandler(StreamHandler):

    log_colors = {
        INFO: Fore.GREEN,
        DEBUG: Fore.CYAN,
        WARNING: Fore.YELLOW,
        ERROR: Fore.RED,
        CRITICAL: Fore.RED,
    }

    def __init__(self, stream):
        StreamHandler.__init__(self, AnsiToWin32(stream).stream)

    @property
    def is_tty(self):
        isatty = getattr(self.stream, 'isatty', None)
        return isatty and isatty()

    def format(self, record):
        msg = StreamHandler.format(self, record)
        if self.is_tty:
            msg = self.log_colors[record.levelno] + msg + Style.RESET_ALL
        return msg
