# vim: tabstop=4 shiftwidth=4 softtabstop=4
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

import functools
import os
import shutil
import tempfile

import git


def make_test_repo(name='testrepo'):
    def decorator(test):
        @functools.wraps(test)
        def wrapper(*args, **kwargs):
            try:
                testrepo = tempfile.mkdtemp()
                kwargs[name] = testrepo
                repo = git.Repo.init(testrepo)
                tf_path = os.path.join(testrepo, 'testfile.txt')
                with open(tf_path, 'w') as tf:
                    tf.write('test content')
                repo.index.add([tf_path])
                repo.index.commit('test commit')
                return test(*args, **kwargs)
            finally:
                shutil.rmtree(testrepo)
        return wrapper
    return decorator
