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
                self.content = '{"node":[{"id":"controller-config","netconf-node-inventory:connected":true,"netconf-node-inventory:initial-capability":["(urn:opendaylight:neutron-ports?revision=2015-07-12)neutron-ports","(urn:opendaylight:params:xml:ns:yang:bgp-rib?revision=2013-09-25)bgp-rib","(urn:ietf:params:xml:ns:yang:iana-afn-safi?revision=2013-07-04)iana-afn-safi","(urn:opendaylight:params:xml:ns:yang:topology-manager:impl?revision=2015-05-30)topology-manager-impl","(urn:opendaylight:params:xml:ns:yang:controller:md:sal:core:spi:entity-ownership-service?revision=2015-08-10)opendaylight-entity-ownership-service","(urn:opendaylight:params:xml:ns:yang:overlay?revision=2015-01-05)overlay","(urn:TBD:params:xml:ns:yang:network:ted?revision=2013-07-12)ted","(urn:opendaylight:params:xml:ns:yang:controller:md:sal:clustering:entity-owners?revision=2015-08-04)entity-owners","(urn:opendaylight:params:xml:ns:yang:controller:pcep:auto:bandwidth?revision=2016-01-09)odl-pcep-auto-bandwidth","(http://openconfig.net/yang/openconfig-types?revision=2015-10-09)openconfig-types","(urn:opendaylight:params:xml:ns:yang:inventory-manager:impl?revision=2015-05-30)inventory-manager-impl","(urn:com.brocade.apps.bsc.etree?revision=2016-05-01)brocade-bsc-etree","(urn:opendaylight:params:xml:ns:yang:controller:config:netconf:northbound:impl?revision=2015-01-12)netconf-northbound-impl","(urn:opendaylight:port:service?revision=2013-11-07)sal-port","(urn:ietf:params:xml:ns:yang:ietf-inet-types?revision=2010-09-24)ietf-inet-types","(urn:opendaylight:params:xml:ns:yang:openflowplugin:sm:control?revision=2015-08-12)statistics-manager-control","(urn:opendaylight:params:xml:ns:yang:controller:netconf:northbound:notification:impl?revision=2015-08-07)netconf-northbound-notification-impl","(urn:opendaylight:role:service?revision=2015-07-27)sal-role","(urn:opendaylight:params:xml:ns:yang:controller:config:netconf:auth?revision=2015-07-15)netconf-auth","(urn:opendaylight:action:types?revision=2013-11-12)opendaylight-action-types","(instance:identifier:patch:module?revision=2015-11-21)instance-identifier-patch-module","(urn:opendaylight:host-tracker?revision=2014-06-24)host-tracker-service","(urn:opendaylight:packet:service?revision=2013-07-09)packet-processing","(urn:opendaylight:params:xml:ns:yang:controller:config:netconf:client:dispatcher?revision=2014-04-08)odl-netconfig-client-cfg","(urn:opendaylight:table:types?revision=2013-10-26)opendaylight-table-types","(urn:opendaylight:params:xml:ns:yang:controller:md:sal:connector:netconf?revision=2015-08-03)odl-sal-netconf-connector-cfg","(urn:opendaylight:neutron-provider?revision=2015-07-12)neutron-provider","(urn:opendaylight:netconf-node-topology?revision=2015-01-14)netconf-node-topology","(urn:ietf:params:xml:ns:netmod:notification?revision=2008-07-14)nc-notifications","(urn:opendaylight:l2switch:host-tracker-impl?revision=2014-05-28)host-tracker-impl","(urn:com.brocade.apps.bsc.path.provider.sr?revision=2016-05-02)brocade-bsc-path-sr","(urn:opendaylight:flow:types:queue?revision=2013-09-25)opendaylight-queue-types","(urn:opendaylight:params:xml:ns:yang:bgp-types?revision=2013-09-19)bgp-types","(urn:opendaylight:params:xml:ns:yang:bgp-inet?revision=2015-03-05)bgp-inet","(urn:opendaylight:params:xml:ns:yang:netvirt:impl?revision=2015-05-13)netvirt-impl","(urn:opendaylight:params:xml:ns:yang:bmp-monitor?revision=2015-05-12)bmp-monitor","(urn:opendaylight:params:xml:ns:yang:controller:bgp:rib:spi?revision=2013-11-15)odl-bgp-rib-spi-cfg","(urn:opendaylight:openflow:augments?revision=2015-02-25)openflow-augments","(urn:opendaylight:model:match:types?revision=2013-10-26)opendaylight-match-types","(urn:opendaylight:params:xml:ns:yang:netvirt?revision=2015-12-27)netvirt","(urn:opendaylight:params:xml:ns:yang:controller:netconf:topology:shared:schema:repository?revision=2015-07-27)shared-schema-repository","(urn:opendaylight:params:xml:ns:yang:controller:config:netconf?revision=2014-04-08)odl-netconf-cfg","(urn:opendaylight:openflow:common:types?revision=2013-07-31)openflow-types","(urn:opendaylight:params:xml:ns:yang:topology:programming?revision=2013-11-02)network-topology-programming","(urn:opendaylight:params:xml:ns:yang:controller:netty:eventexecutor?revision=2013-11-12)netty-event-executor","(urn:opendaylight:openflowplugin:experimenter:types?revision=2015-10-20)openflowplugin-experimenter-types","(urn:com.brocade.apps.bsc.path?revision=2016-05-01)brocade-bsc-path","(urn:com.brocade.apps.bsc.eline?revision=2016-05-01)brocade-bsc-eline","(urn:opendaylight:params:xml:ns:yang:controller:md:sal:dom:pingpong?revision=2014-11-07)opendaylight-pingpong-broker","(urn:opendaylight:params:xml:ns:yang:openflow:common:config:impl?revision=2014-03-26)openflow-provider-impl","(urn:opendaylight:params:xml:ns:yang:controller:config:openflowplugin:nx:config?revision=2014-07-11)nicira-extension","(urn:opendaylight:neutron-networks?revision=2015-07-12)neutron-networks","(urn:opendaylight:params:xml:ns:yang:controller:md:sal:remote?revision=2014-01-14)sal-remote","(urn:opendaylight:params:xml:ns:yang:bgp-labeled-unicast?revision=2015-05-25)bgp-labeled-unicast","(urn:opendaylight:params:xml:ns:yang:controller:md:sal:dom:impl?revision=2013-10-28)opendaylight-sal-dom-broker-impl","(urn:opendaylight:params:xml:ns:yang:controller:md:sal:common?revision=2013-10-28)opendaylight-md-sal-common","(urn:opendaylight:queue:service?revision=2015-03-05)sal-queue","(urn:opendaylight:params:xml:ns:yang:controller:netconf:northbound:notification?revision=2015-08-06)netconf-northbound-notification","(urn:opendaylight:params:xml:ns:yang:controller:config:actor-system-provider:service?revision=2015-10-05)actor-system-provider-service","(urn:opendaylight:port:statistics?revision=2013-12-14)opendaylight-port-statistics","(urn:opendaylight:group:types?revision=2013-10-18)opendaylight-group-types","(urn:opendaylight:neutron-binding?revision=2015-07-12)neutron-binding","(urn:opendaylight:openflow:common:action?revision=2015-02-03)openflow-action","(urn:opendaylight:params:xml:ns:yang:pcep:message?revision=2013-10-07)pcep-message","(urn:opendaylight:params:xml:ns:yang:topology:tunnel:programming?revision=2013-09-30)topology-tunnel-programming","(urn:opendaylight:neutron-bgpvpns?revision=2015-09-03)neutron-bgpvpns","(urn:opendaylight:params:xml:ns:yang:topology:tunnel:pcep:programming?revision=2013-10-30)topology-tunnel-pcep-programming","(urn:opendaylight:params:xml:ns:yang:controller:config:concurrent-data-broker?revision=2014-11-24)odl-concurrent-data-broker-cfg","(urn:opendaylight:params:xml:ns:yang:controller:pcep:sync:optimizations?revision=2015-07-14)odl-pcep-sync-optimizations","(urn:opendaylight:model:topology:general?revision=2013-10-30)opendaylight-topology","(urn:opendaylight:packet:basepacket?revision=2014-05-28)base-packet","(urn:opendaylight:params:xml:ns:yang:controller:bgp:rib:cfg?revision=2013-07-01)odl-bgp-rib-cfg","(urn:ietf:params:xml:ns:yang:ietf-inet-types?revision=2013-07-15)ietf-inet-types","(urn:opendaylight:params:xml:ns:yang:controller:md:sal:core:general-entity?revision=2015-08-20)general-entity","(urn:opendaylight:params:xml:ns:yang:controller:pcep:spi?revision=2013-11-15)odl-pcep-spi-cfg","(urn:opendaylight:neutron-vpnaas?revision=2015-07-12)neutron-vpnaas","(urn:opendaylight:params:xml:ns:yang:bgp-epe?revision=2015-06-22)bgp-epe","(urn:opendaylight:params:xml:ns:yang:pcep:ietf:stateful?revision=2013-12-22)odl-pcep-ietf-stateful07","(urn:opendaylight:model:statistics:types?revision=2013-09-25)opendaylight-statistics-types","(http://openconfig.net/yang/bgp-policy?revision=2015-10-09)openconfig-bgp-policy","(urn:opendaylight:queue:statistics?revision=2013-12-16)opendaylight-queue-statistics","(urn:sal:restconf:event:subscription?revision=2014-07-08)sal-remote-augment","(urn:opendaylight:params:xml:ns:yang:openflowplugin:app:statistics-manager?revision=2014-09-25)statistics-manager","(urn:opendaylight:flow:topology:discovery?revision=2013-08-19)flow-topology-discovery","(urn:opendaylight:params:xml:ns:yang:southbound:impl?revision=2014-12-10)southbound-impl","(urn:opendaylight:params:xml:ns:yang:controller:shutdown?revision=2013-12-18)shutdown","(urn:opendaylight:meter:statistics?revision=2013-11-11)opendaylight-meter-statistics","(urn:ietf:params:xml:ns:netconf:base:1.0?revision=2011-06-01)ietf-netconf","(urn:ietf:params:xml:ns:yang:ietf-netconf-notifications?revision=2012-02-06)ietf-netconf-notifications","(urn:ietf:params:xml:ns:yang:ospf-topology?revision=2013-07-12)ospf-topology","(urn:ietf:params:xml:ns:yang:rpc-context?revision=2013-06-17)rpc-context","(urn:opendaylight:node:error:service?revision=2014-04-10)node-error","(urn:opendaylight:neutron-secgroups?revision=2015-07-12)neutron-secgroups","(urn:opendaylight:params:xml:ns:yang:controller:md:sal:rest:connector?revision=2014-07-24)opendaylight-rest-connector","(http://openconfig.net/yang/bgp-multiprotocol?revision=2015-10-09)openconfig-bgp-multiprotocol","(urn:opendaylight:params:xml:ns:yang:controller:bgp:flowspec?revision=2015-04-23)odl-bgp-flowspec-cfg","(urn:opendaylight:packet:ipv6?revision=2014-05-28)ipv6-packet","(urn:opendaylight:flow:service?revision=2013-08-19)sal-flow","(urn:opendaylight:params:xml:ns:yang:controller:pcep:auto:bandwidth:cfg?revision=2016-01-09)odl-pcep-auto-bandwidth-cfg","(urn:opendaylight:neutron-l2gateways?revision=2015-07-12)neutron-l2gateways","(urn:opendaylight:params:xml:ns:yang:controller:programming:impl?revision=2015-07-20)odl-programming-impl-cfg","(urn:opendaylight:group:service?revision=2013-09-18)sal-group","(urn:ietf:params:xml:ns:yang:iana-if-type?revision=2014-05-08)iana-if-type","(urn:opendaylight:params:xml:ns:yang:openflow:applications:of-switch-config-pusher?revision=2014-10-15)of-switch-config-pusher","(urn:opendaylight:neutron-constants?revision=2015-07-12)neutron-constants","(urn:opendaylight:l2:types?revision=2013-08-27)opendaylight-l2-types","(urn:ietf:params:xml:ns:yang:ietf-network?revision=2015-06-08)ietf-network","(urn:opendaylight:params:xml:ns:yang:ieee754?revision=2013-08-19)ieee754","(urn:opendaylight:neutron-metering?revision=2015-07-12)neutron-metering","(config:aaa:authn:h2:store?revision=2015-11-28)aaa-h2-store","(urn:TBD:params:xml:ns:yang:ospf-topology?revision=2013-10-21)ospf-topology","(urn:opendaylight:params:xml:ns:yang:controller:config:netconf:northbound?revision=2015-01-14)netconf-northbound","(urn:opendaylight:packet:arp-handler-impl?revision=2014-05-28)arp-handler-impl","(urn:opendaylight:params:xml:ns:yang:library:impl?revision=2014-12-10)library","(urn:opendaylight:params:xml:ns:yang:controller:tcpmd5:netty:cfg?revision=2014-04-27)odl-tcpmd5-netty-cfg","(urn:opendaylight:params:xml:ns:yang:controller:sal:restconf:service?revision=2015-07-08)sal-restconf-service","(urn:opendaylight:params:xml:ns:yang:controller:md:sal:core:spi:config-dom-store?revision=2014-06-17)opendaylight-config-dom-datastore","(urn:opendaylight:params:xml:ns:yang:openflowplugin:ofjava:nx:api:config?revision=2014-07-11)openflowjava-nx-api-config","(urn:opendaylight:params:xml:ns:yang:controller:threadpool?revision=2013-04-09)threadpool","(urn:com.brocade.apps.bsc.topology.cost?revision=2016-05-01)brocade-bsc-cost","(urn:opendaylight:l2switch:loopremover?revision=2014-07-14)stp-status-aware-node-connector","(urn:com.brocade.apps.bsc.path.provider.mpls?revision=2016-05-02)brocade-bsc-path-mpls","(urn:opendaylight:params:xml:ns:yang:neutron:transcriber:impl?revision=2014-12-10)neutron-transcriber-impl","(urn:opendaylight:params:xml:ns:yang:controller:md:sal:binding:impl?revision=2013-10-28)opendaylight-sal-binding-broker-impl","(urn:opendaylight:netconf-node-inventory?revision=2014-01-08)netconf-node-inventory","(urn:opendaylight:params:xml:ns:yang:topology:tunnel?revision=2013-08-19)topology-tunnel","(urn:opendaylight:params:xml:ns:yang:controller:topology?revision=2013-11-15)odl-topology-api-cfg","(http://openconfig.net/yang/policy-types?revision=2015-10-09)openconfig-policy-types","(urn:opendaylight:params:xml:ns:yang:pcep:crabbe:initiated?revision=2013-11-26)odl-pcep-ietf-initiated00","(urn:opendaylight:params:xml:ns:yang:controller:config:path-provider:impl?revision=2014-05-23)path-provider-impl","(urn:TBD:params:xml:ns:yang:network:isis-topology?revision=2013-07-12)isis-topology","(urn:opendaylight:params:xml:ns:yang:controller:config?revision=2013-04-05)config","(urn:opendaylight:params:xml:ns:yang:controller:pcep:impl?revision=2013-06-27)odl-pcep-impl-cfg","(urn:opendaylight:table:service?revision=2013-10-26)sal-table","(urn:opendaylight:params:xml:ns:yang:controller:bgp:topology:provider?revision=2013-11-15)odl-bgp-topology-provider-cfg","(http://openconfig.net/yang/bgp-operational?revision=2015-10-09)openconfig-bgp-operational","(urn:opendaylight:params:xml:ns:yang:controller:pcep?revision=2013-04-09)odl-pcep-api-cfg","(urn:opendaylight:params:xml:ns:yang:controller:programming:spi?revision=2013-11-15)odl-programming-spi-cfg","(urn:opendaylight:params:xml:ns:yang:controller:config:actor-system-provider:impl?revision=2015-10-05)actor-system-provider-impl","(urn:opendaylight:params:xml:ns:yang:topology:tunnel:pcep?revision=2013-08-20)topology-tunnel-pcep","(urn:opendaylight:openflowplugin:extension:general?revision=2014-07-14)openflowplugin-extension-general","(urn:opendaylight:neutron-lbaasv2?revision=2015-07-12)neutron-lbaasv2","(urn:opendaylight:openflowjava:nx:match?revision=2014-04-21)nicira-match","(urn:opendaylight:meter:types?revision=2013-09-18)opendaylight-meter-types","(urn:opendaylight:params:xml:ns:yang:controller:pcep:tunnel:provider?revision=2013-11-15)odl-pcep-tunnel-provider-cfg","(urn:opendaylight:params:xml:ns:yang:network:concepts?revision=2013-11-25)network-concepts","(urn:ietf:params:xml:ns:yang:ietf-restconf?revision=2013-10-19)ietf-restconf","(urn:opendaylight:neutron?revision=2015-07-12)neutron","(urn:opendaylight:params:xml:ns:yang:controller:netty?revision=2013-11-19)netty","(urn:TBD:params:xml:ns:yang:network:isis-topology?revision=2013-10-21)isis-topology","(urn:opendaylight:params:xml:ns:yang:aaa:credential-store?revision=2015-02-26)credential-store","(urn:opendaylight:params:xml:ns:yang:openflow:switch:connection:provider?revision=2014-03-28)openflow-switch-connection-provider","(urn:opendaylight:flow:table:statistics?revision=2013-12-15)opendaylight-flow-table-statistics","(urn:opendaylight:params:xml:ns:yang:bgp:openconfig-extensions?revision=2015-09-30)bgp-openconfig-extensions","(urn:opendaylight:params:xml:ns:yang:controller:bgp:labeled:unicast?revision=2015-05-25)odl-bgp-labeled-unicast-cfg","(urn:opendaylight:params:xml:ns:yang:controller:bgp:rib:impl?revision=2013-04-09)odl-bgp-rib-impl-cfg","(urn:opendaylight:params:xml:ns:yang:controller:bgp-openconfig-spi?revision=2015-09-25)odl-bgp-openconfig-spi-cfg","(urn:opendaylight:params:xml:ns:yang:controller:bgp:parser:spi?revision=2013-11-15)odl-bgp-parser-spi-cfg","(urn:opendaylight:params:xml:ns:yang:controller:config:distributed-entity-ownership-service?revision=2015-08-10)distributed-entity-ownership-service","(urn:opendaylight:params:xml:ns:yang:openflow:api?revision=2015-03-31)openflow-provider","(urn:opendaylight:openflowjava:nx:action?revision=2014-04-21)nicira-action","(urn:opendaylight:model:topology:inventory?revision=2013-10-30)opendaylight-topology-inventory","(urn:opendaylight:params:xml:ns:yang:controller:config:cluster-admin-provider?revision=2015-10-13)cluster-admin-provider","(urn:opendaylight:params:xml:ns:yang:controller:inmemory-datastore-provider?revision=2014-06-17)opendaylight-inmemory-datastore-provider","(urn:opendaylight:params:xml:ns:yang:controller:tcpmd5:cfg?revision=2014-04-27)odl-tcpmd5-cfg","(urn:opendaylight:openflow:config?revision=2014-06-30)openflow-configuration","(urn:opendaylight:params:xml:ns:yang:controller:pcep:stateful07:cfg?revision=2015-07-14)odl-pcep-ietf-stateful07-cfg","(urn:opendaylight:packet:arp?revision=2014-05-28)arp-packet","(urn:opendaylight:params:xml:ns:yang:controller:shutdown:impl?revision=2013-12-18)shutdown-impl","(urn:opendaylight:module:config?revision=2014-10-15)node-config","(urn:opendaylight:params:xml:ns:yang:controller:threadpool:impl:flexible?revision=2013-12-01)threadpool-impl-flexible","(urn:ietf:params:xml:ns:yang:ietf-yang-types?revision=2013-07-15)ietf-yang-types","(urn:opendaylight:params:xml:ns:yang:controller:tcpmd5:jni:cfg?revision=2014-04-27)odl-tcpmd5-jni-cfg","(urn:TBD:params:xml:ns:yang:network-topology?revision=2013-10-21)network-topology","(urn:opendaylight:params:xml:ns:yang:openflow:switch:connection:provider:impl?revision=2014-03-28)openflow-switch-connection-provider-impl","(urn:opendaylight:params:xml:ns:yang:controller:rsvp:impl?revision=2015-08-26)odl-rsvp-parser-impl-cfg","(config:aaa:authn:netconf:plugin?revision=2015-07-15)aaa-authn-netconf-plugin","(urn:opendaylight:params:xml:ns:yang:controller:threadpool:impl:fixed?revision=2013-12-01)threadpool-impl-fixed","(urn:com.brocade.apps.bsc.eline.provider.mpls?revision=2016-05-02)brocade-bsc-eline-mpls","(urn:opendaylight:params:xml:ns:yang:rsvp?revision=2015-08-20)rsvp","(urn:opendaylight:params:xml:ns:yang:controller:pcep:sr:cfg?revision=2014-06-09)odl-pcep-segment-routing-cfg","(urn:ietf:params:xml:ns:yang:ietf-interfaces?revision=2014-05-08)ietf-interfaces","(urn:opendaylight:params:xml:ns:yang:openflow:common:config?revision=2014-03-26)openflow-provider","(urn:opendaylight:address-tracker?revision=2014-06-17)address-tracker","(urn:opendaylight:flow:statistics?revision=2013-08-19)opendaylight-flow-statistics","(urn:opendaylight:params:xml:ns:yang:controller:netconf:north:mapper?revision=2015-01-14)netconf-northbound-mapper","(urn:opendaylight:params:xml:ns:yang:controller:bgp:reachability:ipv4?revision=2013-11-15)odl-bgp-treachability-ipv4-cfg","(urn:com.brocade.apps.bsc.path.provider.nodetonode?revision=2016-05-02)brocade-bsc-path-nodetonode","(urn:opendaylight:params:xml:ns:yang:controller:bgp:reachability:ipv6?revision=2013-11-15)odl-bgp-treachability-ipv6-cfg","(urn:opendaylight:params:xml:ns:yang:controller:protocol:framework?revision=2014-03-13)protocol-framework","(urn:opendaylight:packet:ipv4?revision=2014-05-28)ipv4-packet","(urn:opendaylight:neutron-subnets?revision=2015-07-12)neutron-subnets","(urn:opendaylight:params:xml:ns:yang:bmp-message?revision=2015-05-12)bmp-message","(urn:opendaylight:params:xml:ns:yang:controller:netconf:northbound:tcp?revision=2015-04-23)netconf-northbound-tcp","(urn:opendaylight:neutron-fwaas?revision=2015-07-12)neutron-fwaas","(urn:opendaylight:flow:types:port?revision=2013-09-25)opendaylight-port-types","(urn:opendaylight:openflowplugin:extension:nicira:action?revision=2014-07-14)openflowplugin-extension-nicira-action","(urn:opendaylight:params:xml:ns:yang:controller:bgp:openconfig?revision=2015-07-18)odl-openconfig-bgp-cfg","(urn:opendaylight:params:xml:ns:yang:iana?revision=2013-08-16)iana","(urn:opendaylight:openflow:common:instruction?revision=2013-07-31)openflow-instruction","(urn:opendaylight:params:xml:ns:yang:netvirt:providers:impl?revision=2015-05-13)netvirt-providers-impl","(urn:opendaylight:params:xml:ns:yang:pcep:segment:routing?revision=2015-01-12)odl-pcep-segment-routing","(urn:opendaylight:params:xml:ns:yang:controller:threadpool:impl?revision=2013-04-05)threadpool-impl","(urn:opendaylight:params:xml:ns:yang:pcep:types?revision=2013-10-05)pcep-types","(urn:opendaylight:packet:packet-handler-impl?revision=2014-05-28)packet-handler-impl","(urn:opendaylight:params:xml:ns:yang:controller:config:remote-rpc-connector?revision=2014-07-07)remote-rpc-connector","(urn:opendaylight:packet:address-tracker-impl?revision=2014-05-28)address-tracker-impl","(urn:opendaylight:params:xml:ns:yang:controller:clustered:netconf:topology?revision=2015-11-04)clustered-netconf-topology","(urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring?revision=2010-10-04)ietf-netconf-monitoring","(urn:opendaylight:openflowplugin:extension:nicira:match?revision=2014-07-14)openflowplugin-extension-nicira-match","(urn:opendaylight:arbitrary:bitmask:fields?revision=2016-01-30)opendaylight-arbitrary-bitmask-fields","(urn:opendaylight:params:xml:ns:yang:controller:md:sal:binding?revision=2013-10-28)opendaylight-md-sal-binding","(urn:opendaylight:neutron-L3-ext?revision=2015-07-12)neutron-L3-ext","(urn:opendaylight:params:xml:ns:yang:ovsdb?revision=2015-01-05)ovsdb","(urn:opendaylight:params:xml:ns:yang:controller:config:distributed-datastore-provider?revision=2014-06-12)distributed-datastore-provider","(http://openconfig.net/yang/bgp-types?revision=2015-10-09)openconfig-bgp-types","(urn:opendaylight:params:xml:ns:yang:controller:threadpool:impl:scheduled?revision=2013-12-01)threadpool-impl-scheduled","(urn:ietf:params:xml:ns:yang:ietf-yang-types?revision=2010-09-24)ietf-yang-types","(urn:opendaylight:params:xml:ns:yang:bgp-linkstate?revision=2015-02-10)bgp-linkstate","(urn:opendaylight:params:xml:ns:yang:controller:pcep:topology:provider?revision=2013-11-15)odl-pcep-topology-provider-cfg","(urn:opendaylight:yang:extension:yang-ext?revision=2013-07-09)yang-ext","(urn:com.brocade.apps.bsc.segment.routing?revision=2016-05-01)brocade-bsc-sr","(urn:TBD:params:xml:ns:yang:network:ted?revision=2013-10-21)ted","(urn:opendaylight:experimenter-mp-message:service?revision=2015-10-20)sal-experimenter-mp-message","(urn:opendaylight:flow:transaction?revision=2015-03-04)flow-capable-transaction","(http://openconfig.net/yang/bgp?revision=2015-10-09)openconfig-bgp","(urn:opendaylight:params:xml:ns:yang:bgp-segment-routing-ext?revision=2015-10-14)bgp-segment-routing","(urn:opendaylight:params:xml:ns:yang:controller:pcep:stats?revision=2014-10-06)pcep-session-stats","(urn:opendaylight:params:xml:ns:yang:openflowplugin:ofjava:nx:config?revision=2014-07-11)openflowjava-nx-config","(urn:opendaylight:params:xml:ns:yang:controller:md:sal:core:spi:operational-dom-store?revision=2014-06-17)opendaylight-operational-dom-datastore","(urn:opendaylight:flow:inventory?revision=2013-08-19)flow-node-inventory","(urn:TBD:params:xml:ns:yang:network-topology?revision=2013-07-12)network-topology","(urn:opendaylight:model:topology:view?revision=2013-10-30)opendaylight-topology-view","(urn:opendaylight:params:xml:ns:yang:controller:md:sal:dom?revision=2013-10-28)opendaylight-md-sal-dom","(urn:opendaylight:params:xml:ns:yang:bgp-multiprotocol?revision=2013-09-19)bgp-multiprotocol","(urn:ietf:params:xml:ns:yang:ietf-netconf-monitoring-extension?revision=2013-12-10)ietf-netconf-monitoring-extension","(urn:opendaylight:params:xml:ns:yang:topology:tunnel:p2p?revision=2013-08-19)topology-tunnel-p2p","(urn:opendaylight:params:xml:ns:yang:controller:netconf:topology?revision=2015-07-27)netconf-topology","(urn:ietf:params:xml:ns:netconf:notification:1.0?revision=2008-07-14)notifications","(urn:opendaylight:openflow:oxm?revision=2015-02-25)openflow-extensible-match","(urn:opendaylight:params:xml:ns:yang:programming?revision=2015-07-20)programming","(urn:opendaylight:params:xml:ns:yang:controller:netty:threadgroup?revision=2013-11-07)threadgroup","(urn:opendaylight:flow:types?revision=2013-10-26)opendaylight-flow-types","(urn:opendaylight:params:xml:ns:yang:controller:netconf:northbound:ssh?revision=2015-01-14)netconf-northbound-ssh","(urn:opendaylight:params:xml:ns:yang:controller:md:sal:cluster:admin?revision=2015-10-13)cluster-admin","(urn:opendaylight:openflow:system?revision=2013-09-27)system-notifications","(urn:opendaylight:neutron-provider-ext?revision=2015-07-12)neutron-provider-ext","(urn:opendaylight:neutron-L3?revision=2015-07-12)neutron-L3","(urn:opendaylight:neutron-attrs?revision=2015-07-12)neutron-attrs","(urn:opendaylight:params:xml:ns:yang:controller:rsvp:spi?revision=2015-08-26)odl-rsvp-parser-spi-cfg","(urn:opendaylight:inventory?revision=2013-08-19)opendaylight-inventory","(urn:opendaylight:group:statistics?revision=2013-11-11)opendaylight-group-statistics","(urn:opendaylight:params:xml:ns:yang:openflow:applications:lldp-speaker?revision=2014-10-23)lldp-speaker","(urn:opendaylight:params:xml:ns:yang:topology:pcep:programming?revision=2013-11-06)network-topology-pcep-programming","(urn:TBD:params:xml:ns:yang:nt:l3-unicast-igp-topology?revision=2013-07-12)l3-unicast-igp-topology","(urn:opendaylight:params:xml:ns:yang:openflowplugin:app:forwardingrules-manager?revision=2014-09-25)forwardingrules-manager","(urn:opendaylight:neutron-portsecurity?revision=2015-07-12)neutron-portsecurity","(urn:opendaylight:params:xml:ns:yang:openflowplugin:extension:api?revision=2015-04-25)openflowplugin-extension-registry","(urn:opendaylight:experimenter-message:service?revision=2015-10-20)sal-experimenter-message","(urn:ietf:params:xml:ns:yang:ietf-network-topology?revision=2015-06-08)ietf-network-topology","(urn:com.brocade.apps.bsc.common.types?revision=2016-05-01)brocade-bsc-common-types","(urn:opendaylight:flow:errors?revision=2013-11-16)flow-errors","(urn:opendaylight:packet:loop-remover-impl?revision=2014-05-28)loop-remover-impl","(urn:opendaylight:packet:ethernet?revision=2014-05-28)ethernet-packet","(urn:opendaylight:params:xml:ns:yang:openflowplugin:nx:config:impl?revision=2014-07-11)nicira-extension-impl","(urn:TBD:params:xml:ns:yang:nt:l3-unicast-igp-topology?revision=2013-10-21)l3-unicast-igp-topology","(urn:opendaylight:openflow:protocol?revision=2013-07-31)openflow-protocol","(urn:opendaylight:params:xml:ns:yang:bgp-flowspec?revision=2015-08-07)bgp-flowspec","(config:aaa:authn:idmlight?revision=2015-12-04)aaa-idmlight","(urn:opendaylight:params:xml:ns:yang:topology:pcep?revision=2013-10-24)network-topology-pcep","(urn:opendaylight:params:xml:ns:yang:bgp-message?revision=2013-09-19)bgp-message","(urn:opendaylight:params:xml:ns:yang:netvirt:providers:config?revision=2016-01-09)netvirt-providers-config","(urn:opendaylight:params:xml:ns:yang:controller:netty:timer?revision=2013-11-19)netty-timer","(urn:opendaylight:echo:service?revision=2015-03-05)sal-echo","(urn:opendaylight:params:xml:ns:yang:controller:bgp:linkstate?revision=2015-08-26)odl-bgp-linkstate-cfg","(http://openconfig.net/yang/routing-policy?revision=2015-10-09)openconfig-routing-policy","(http://openconfig.net/yang/openconfig-ext?revision=2015-10-09)openconfig-extensions","(urn:opendaylight:params:xml:ns:yang:network:topology?revision=2014-01-13)odl-network-topology","(urn:opendaylight:params:xml:ns:yang:topology-lldp-discovery:impl?revision=2015-05-30)topology-lldp-discovery-impl","(urn:opendaylight:meter:service?revision=2013-09-18)sal-meter"]}]}'

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
