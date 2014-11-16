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

import re

import requests

from pygerrit.rest import GerritRestAPI

DEFAULT_GERRIT_URL = 'https://review.openstack.org'


class GerritReview(object):

    def __init__(self, changeid, project, gerrit_url=DEFAULT_GERRIT_URL):
        self.changeid = changeid
        self.project = project
        self._gerrit_url = gerrit_url
        self._restclient = None

    def build_pip_dependencies(self, py26=False, py27=True, string=False):
        url = self._get_gate_build_log_url(py26, py27)
        response = requests.get(url)

        if response.status_code != 200:
            raise Exception("Unable to get console log at %s. Error: %d" %
                            (url, response.status_code))

        log = response.text.encode('utf-8')

        freeze_found = False
        dependencies = []
        for line in log.split('\n'):
            line = re.sub('.*\|\s*', '', line)
            if not freeze_found:
                if line.endswith("pip freeze"):
                    freeze_found = True
                continue
            elif re.match('[\w\-]+==.+', line) and not line.startswith('-e'):
                dependencies.append(line)

        if string:
            return (' ').join(dependencies)
        return dependencies

    def _get_rest_client(self):
        if not self._restclient:
            self._restclient = GerritRestAPI(url=self._gerrit_url)
        return self._restclient

    def _get_review_detail(self):
        """ get review details for a given change ID """
        restclient = self._get_rest_client()
        url = "/changes/?q=%s" % self.changeid
        changes = restclient.get(url)

        change = None
        for c in changes:
            if c['project'] == self.project:
                change = c
                break

        if not change:
            raise Exception("could not find change with ID: %s" %
                            self.changeid)

        detail = restclient.get("/changes/%s/detail" % change['id'])
        return detail

    def _get_reveiew_messages(self):
        details = self._get_review_detail()
        return details['messages']

    def _get_gate_build_log_url(self, py26, py27):
        messages = self._get_reveiew_messages()
        messages.reverse()

        mergemsg = None
        for message in messages:
            msgtext = message['message']
            if re.search('Patch Set \d+: Verified', msgtext):
                mergemsg = msgtext
                break

        gate_info = self._parse_merge_message(mergemsg)
        url = None
        for gate in gate_info:
            if py26 and re.match('gate\-.+\-python26', gate['name']):
                url = gate['url']
            if py27 and re.match('gate\-.+\-python27', gate['name']):
                url = gate['url']

        # check if it is console.html or console.html.gz
        resp = requests.get(url)
        if resp.status_code != 200:
            raise Exception("Unable to find the build's console log for %s" %
                            url)

        build_log = None
        if 'console.html.gz' in resp.text:
            build_log = 'console.html.gz'
        elif 'console.html' in resp.text:
            build_log = 'console.html'
        else:
            raise Exception("Didn't find a build log. Does one exist?")

        if url:
            return "%s/%s" % (url, build_log)
        return url

    def _parse_merge_message(self, msg):
        """ a function that parses a successful gate gerrit message """
        gate_info = []
        for line in msg.split('\n'):
            parts = re.split('\s+', line)
            if parts[0] == '-':
                gate = {}
                gate['name'] = parts[1]
                gate['url'] = parts[2]
                gate['result'] = parts[4]
                gate_info.append(gate)
        return gate_info
