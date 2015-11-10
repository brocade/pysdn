#!/usr/bin/python

# Copyright (c) 2015,  BROCADE COMMUNICATIONS SYSTEMS, INC

# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from this
# software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.

"""

@authors: Lera Nosyreva
@status: Development


"""

import unittest
import time
import json
import mock

from pysdn.controller.controller import Controller
from pysdn.common.utils import load_dict_from_file
from pysdn.common.status import STATUS


class ControllerTests(unittest.TestCase):

    def setUp(self):
        f = "cfg1.yml"
        d = {}
        if not(load_dict_from_file(f, d)):
            print("Config file '%s' read error: " % f)
            exit()
        try:
            self.ctrlIpAddr = d['ctrlIpAddr']
            self.ctrlPortNum = d['ctrlPortNum']
            self.ctrlUname = d['ctrlUname']
            self.ctrlPswd = d['ctrlPswd']
            self.rundelay = d['rundelay']
        except:
            print ("Failed to get Controller device attributes")
            exit(0)

    # This method will be used by the mock to replace requests.get
    def mocked_requests_http_error(*args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code
                self.content = '{}'
                self.reason = '_HTTP_ERROR_'

        def json(self):
            return self.json_data

        return MockResponse({}, 404)

    def mocked_requests_empty_content(*args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code
                self.content = '{}'

        def json(self):
            return self.json_data

        return MockResponse({"key2": "value2"}, 200)

    @mock.patch('requests.get', side_effect=mocked_requests_http_error)
    def test_ControllerGetSchemas_404(self, controller):

        print ("--------------------------------------------------------- ")
        print ("<< Test ControllerGetSchemas_HTTP_Error Start")
        print ("--------------------------------------------------------- ")
        print ("<< Creating Controller instance")
        time.sleep(self.rundelay)
        ctrl = Controller(self.ctrlIpAddr, self.ctrlPortNum, self.ctrlUname, self.ctrlPswd)
        print ("\n<< Getting list of YANG models supported by the Controller ")
        time.sleep(self.rundelay)
        nodeName = "controller-config"

        result = ctrl.get_schemas(nodeName)
        status = result.get_status()
        print ("<< Request Status: %s" % status.brief())

        # and verify the results: STATUS.HTTP_ERROR
        self.assertEquals(10, status.status_code)

    @mock.patch('requests.get', side_effect=mocked_requests_empty_content)
    def test_ControllerGetSchemas_no_content(self, controller):

        print ("--------------------------------------------------------- ")
        print ("<< Test ControllerGetSchemas_no_content Start")
        print ("--------------------------------------------------------- ")
        print ("<< Creating Controller instance")
        time.sleep(self.rundelay)
        ctrl = Controller(self.ctrlIpAddr, self.ctrlPortNum, self.ctrlUname, self.ctrlPswd)
        print ("<< 'Controller':")
        print ctrl.to_json()

        print ("\n<< Getting list of YANG models supported by the Controller ")
        time.sleep(self.rundelay)
        nodeName = "controller-config"

        result = ctrl.get_schemas(nodeName)
        status = result.get_status()
        print ("<< Verifying STATUS.DATA_NOT_FOUND ")

        # and verify the results: STATUS.DATA_NOT_FOUND
        self.assertEquals(2, status.status_code)

    # This method will be used by the mock to replace requests.get
    def mocked_requests_get_schemas(*args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code
                self.reason = "_NoRealReason_"
                self.content = '{"schemas":{"schema":[{"identifier":"threadpool-impl","version":"2013-04-05","format":"ietf-netconf-monitoring:yang","location":["NETCONF"],"namespace\":"urn:opendaylight:params:xml:ns:yang:controller:threadpool:impl"}]}}'

        def json(self):
            return self.json_data

        return MockResponse({"key1": "value1"}, 200)

    @mock.patch('requests.get', side_effect=mocked_requests_get_schemas)
    def test_ControllerGetSchemas(self, controller):

        print ("--------------------------------------------------------- ")
        print ("<< Test ControllerGetSchemas Start")
        print ("--------------------------------------------------------- ")
        print ("<< Creating Controller instance")
        time.sleep(self.rundelay)
        ctrl = Controller(self.ctrlIpAddr, self.ctrlPortNum, self.ctrlUname, self.ctrlPswd)
        print ("<< 'Controller':")
        print ctrl.to_json()

        print ("\n<< Getting list of YANG models supported by the Controller ")
        time.sleep(self.rundelay)
        nodeName = "controller-config"

        result = ctrl.get_schemas(nodeName)
        status = result.get_status()

        if(status.eq(STATUS.OK)):
            slist = result.get_data()
            print "\n<< YANG models list: %s" % slist
            print "\n<< JSON dumps:"
            print json.dumps(slist, default=lambda o: o.__dict__,
                             sort_keys='True', indent=4)
        else:
            print ("\n")
            print ("!!!Demo terminated, reason: %s" % status.brief())

        # and verify the results
        self.assertEquals(str(slist), "[{u'location': [u'NETCONF'], u'identifier': u'threadpool-impl', u'namespace': u'urn:opendaylight:params:xml:ns:yang:controller:threadpool:impl', u'version': u'2013-04-05', u'format': u'ietf-netconf-monitoring:yang'}]")

    # This method will be used by the mock to replace requests.get
    def mocked_requests_get_nodes_list(*args, **kwargs):
        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code
                self.reason = "_NoRealReason_"
                self.content = '{"nodes":{"node":[{"id":"vRouter"},{"id":"vRouter_110"},{"id":"vRouter_120"}]}}'

        def json(self):
            return self.json_data

        return MockResponse({"key1": "value1"}, 200)

    @mock.patch('requests.get', side_effect=mocked_requests_get_nodes_list)
    def test_ControllerGetNodeList(self, controller):

        print ("--------------------------------------------------------- ")
        print ("<< Test ControllerNodeList Start")
        print ("--------------------------------------------------------- ")
        print ("<< Getting list of all nodes registered on the Controller ")

        ctrl = Controller(self.ctrlIpAddr, self.ctrlPortNum, self.ctrlUname, self.ctrlPswd)
        result = ctrl.get_nodes_operational_list()
        status = result.get_status()

        if(status.eq(STATUS.OK)):
            print "Nodes:"
            nlist = result.get_data()
            for item in nlist:
                print "   * {} *".format(item)
        else:
            print ("\n")
            print ("!!!Failed, reason: %s" % status.brief().lower())
            exit(0)
        print "<  Number of nodes in list: %s > " % len(nlist)
        print "\n"

        # and verify the results
        self.assertEquals(3, len(nlist))


if __name__ == '__main__':
    # unittest.main()
    suite = unittest.TestLoader().loadTestsFromTestCase(ControllerTests)
    unittest.TextTestRunner(verbosity=2).run(suite)
