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

import unittest2 as unittest

from giftwrap import util


class TestUtil(unittest.TestCase):

    def test_execute_returns_stdout(self):
        cmd = 'echo stdout'
        out = util.execute(cmd)
        self.assertEquals(b'stdout\n', out)

    def test_execute_raises_exception_on_error(self):
        cmd = 'echo stderr >&2 && false'
        with self.assertRaises(Exception):
            util.execute(cmd)

    def test_nonzero_exit_code(self):
        cmd = 'echo stdout && false'
        out = util.execute(cmd, exit=1)
        self.assertEquals(b'stdout\n', out)
