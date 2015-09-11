#!/usr/bin/env python

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

@authors: Sergei Garbuzov
@status: Development
@version: 1.1.0

oftool.py: OpenFlow tool command line utility (sample application)


"""

import json
import yaml
import argparse

from collections import OrderedDict
from pybvc.controller.controller import Controller
from pybvc.common.status import STATUS
from pybvc.common.utils import dbg_print
from pybvc.openflowdev.ofswitch import (OFSwitch,
                                        FlowEntry,
                                        GroupEntry)
from pybvc.controller.topology import Topology, Node
from pybvc.controller.inventory import (Inventory,
                                        OpenFlowCapableNode,
                                        OpenFlowPort,
                                        GroupFeatures,
                                        GroupDescription,
                                        GroupStatistics)


class CtrlCfg():
    """ Attributes necessary for communication with Controller """

    def __init__(self, addr, port, name, pswd):
        self.ip_addr = addr
        self.tcp_port = port
        self.admin_name = name
        self.admin_pswd = pswd

    def to_string(self):
        return "%s:%s" % (self.ip_addr, self.tcp_port)


class ConcatJSONObjects(json.JSONDecoder):
    """ Custom JSON decoder subclass used for retrieving multiple JSON objects
        from a text file. Capable to parse JSON files and strings annotated
        with single and multi-line comments
    """

    MULTILINE_COMMENT_START = "/*"
    MULTILINE_COMMENT_END = "*/"
    SINGLELINE_COMMENT = "//"

    def _strip_comments(self, s):
        json_string = ""
        multiline_comment = False
        lines = s.split('\n')
        for l in lines:
            l = l.strip()
            if l.startswith(self.MULTILINE_COMMENT_START):
                multiline_comment = True

            if multiline_comment:
                if l.endswith(self.MULTILINE_COMMENT_END):
                    multiline_comment = False
                continue

            if l.startswith(self.SINGLELINE_COMMENT):
                continue

            # check for the internal single-line comment
            # (current algorithm assumes that if single-line comment
            # substring is found at the highest index in the JSON string
            # and number of double-quotation marks before its position is
            # even than it is really a comment, not a substring located
            # within JSON string value)
            idx = l.rfind(self.SINGLELINE_COMMENT)
            if idx >= 0:
                cnt = l.count('"', 0, idx)
                if cnt % 2 == 0:  # single-line comment substring is outside
                    l = l[:idx]   # of the JSON body, ignore comment part

            # remove whitespaces preceding stripped comments (if any)
            l = l.rstrip()
            json_string += l

        return json_string

    def decode(self, s):
        objs = []
        json_string = self._strip_comments(s)
        try:
            idx = 0
            js_len = len(json_string)
            while idx < js_len:
                obj, idx = self.raw_decode(json_string, idx)
                objs.append(obj)
        except(Exception) as e:
            print "\n!!! JSON decode failed\n"
            print "Decode string:\n%s\n" % json_string
            print "Failure Reason: %s\n" % e

        return objs


class TopologyInfo():
    """ Class containing methods for retrieving and showing
        network topology information
    """

    def __init__(self, ctrl, topo_id):
        assert(isinstance(ctrl, Controller))
        self.ctrl = ctrl
        self.topo_id = topo_id

    def show_common(self, verbose=False):
        ctrl = self.ctrl
        result = ctrl.build_inventory_object()
        status = result.get_status()
        if(status.eq(STATUS.OK)):
            inventory = result.get_data()
            assert(isinstance(inventory, Inventory))
        elif(status.eq(STATUS.DATA_NOT_FOUND)):
            print "\n".strip()
            print " Requested data not found"
            print "\n".strip()
            exit(0)
        else:
            print ("\n")
            print ("!!!Error, failed to obtain inventory info, reason: %s" %
                   status.brief().lower())
            exit(1)

        result = ctrl.build_topology_object(self.topo_id)
        status = result.get_status()
        if(status.eq(STATUS.OK)):
            topo = result.get_data()
            assert(isinstance(topo, Topology))
        else:
            print ("\n")
            print ("!!!Error, failed to parse '%s' topology info, "
                   "reason: %s" % (self.topo_id, status.brief().lower()))
            exit(1)

        print "\n".strip()
        print (" Network topology '%s'") % self.topo_id
        print "\n".strip()

        flows_cnt = 0
        sids = topo.get_switch_ids()
        for sid in sids:
            flows_cnt += inventory.get_openflow_node_flows_cnt(sid)

        print ("   Number of switches           : %s" %
               topo.get_switches_cnt())
        print ("   Number of inter-switch links : %s" %
               topo.get_inter_switch_links_cnt())
        print ("   Number of hosts              : %s" %
               topo.get_hosts_cnt())
        print ("   Number of flows              : %s" %
               flows_cnt)

        if (verbose):
            print "\n".strip()
            print ("   Switches in topology")
            s1 = 'IP Address'
            s2 = 'OpenFlow Id'
            s3 = 'Flows Cnt'
            sym = '-'
            print "\n".strip()
            print "     {0:<15}  {1:<30}  {2:<10}".format(s1, s2, s3)
            print "     {0:<15}  {1:<30}  {2:<10}".format(sym*15,
                                                          sym*30,
                                                          sym*10)
            switch_ids = topo.get_switch_ids()
            for switch_id in switch_ids:
                inv_node = inventory.get_openflow_node(switch_id)
                addr = inv_node.get_ip_address()
                fcnt = inventory.get_openflow_node_flows_cnt(switch_id)
                print "     {0:<15}  {1:<30}  {2:<10}".format(addr,
                                                              switch_id,
                                                              fcnt)

            print "\n".strip()
            print ("   Hosts in topology")
            s4 = 'IP Address'
            s5 = 'MAC Address'
            print "\n".strip()
            print "     {0:<15}  {1:<17}".format(s4, s5)
            print "     {0:<15}  {1:<17}".format(sym*15, sym*17)
            host_ids = topo.get_host_ids()
            for host_id in host_ids:
                topo_node = topo.get_node_by_id(host_id)
                mac = topo_node.get_mac_address()
                ipaddr = topo_node.get_ip_address_for_mac(mac)
                print "     {0:<15}  {1:<17}".format(ipaddr, mac)

        print"\n"

    def show_switch(self, switch_id, verbose=False):
        ctrl = self.ctrl
        switch_inv = None
        switch_topo = None

        result = ctrl.build_openflow_node_inventory_object(switch_id)
        status = result.get_status()
        if(status.eq(STATUS.OK)):
            switch_inv = result.get_data()
            assert(isinstance(switch_inv, OpenFlowCapableNode))
        elif(status.eq(STATUS.DATA_NOT_FOUND)):
            print "\n".strip()
            print " Requested data not found"
            print "\n".strip()
            exit(0)
        else:
            print ("\n")
            print ("!!!Error, failed to get inventory info for '%s' switch, "
                   "reason: %s" % (switch_id, status.brief().lower()))
            exit(1)

        topo_id = "flow:1"
        result = ctrl.build_topology_object(topo_id)
        status = result.get_status()
        if(status.eq(STATUS.OK)):
            topo = result.get_data()
            assert(isinstance(topo, Topology))
            switch_topo = topo.get_switch(switch_id)
            assert(isinstance(switch_topo, Node))
            assert(switch_topo.is_switch())
        elif(status.eq(STATUS.DATA_NOT_FOUND)):
            print "\n".strip()
            print " Requested data not found"
            print "\n".strip()
            exit(0)
        else:
            print ("\n")
            print ("!!!Error, failed to parse '%s' topology info, "
                   "reason: %s" % (topo_id, status.brief().lower()))
            exit(1)

        print "\n".strip()
        print " Switch '%s'" % switch_id
        print "\n".strip()
        print "   IP Address      : %s" % switch_inv.get_ip_address()
        print "   Max tables      : %s" % switch_inv.get_max_tables_info()
        print "   Number of flows : %s" % switch_inv.get_flows_cnt()
        clist = switch_inv.get_capabilities()
        g = 2
        chunks = [clist[x:x+g] for x in xrange(0, len(clist), g)]
        s = 'Capabilities'
        print "   %s    :" % s,
        for i in range(0, len(chunks)):
            n = 0 if i == 0 else len(s) + 9
            print "%s%s" % (" "*n, ", ".join(chunks[i]))

        print "\n".strip()

        s1 = "Port "
        s2 = "OpenFlow Id"
        sym = '-'
        print "   {0:<10}  {1:<30}".format(s1, s2)
        print "   {0:<10}  {1:<30}".format(sym*10, sym*30)
        pids = switch_inv.get_port_ids()
        for pid in pids:
            pnum = switch_inv.get_port_number(pid)
            print "   {0:<10}  {1:<30}".format(pnum, pid)

        print "\n".strip()

        if (verbose):
            pnums = switch_topo.get_port_numbers()
            for pnum in pnums:
                if pnum == 'LOCAL':
                    continue
                print "   Port '%s' connected devices" % pnum
                print "\n".strip()
                peer_list = topo.get_peer_list_for_node_port_(switch_topo,
                                                              pnum)
                if len(peer_list):
                    for item in peer_list:
                        assert(isinstance(item, Node))
                        if(item.is_switch()):
                            print ("     Device Type : %s" % "switch")
                            print ("     OpenFlow Id : %s" %
                                   item.get_openflow_id())
                        elif (item.is_host()):
                            print ("     Device Type : %s" % "host")
                            mac_addr = item.get_mac_address()
                            print ("     MAC Address : %s" % mac_addr)
                            ip_addr = item.get_ip_address_for_mac(mac_addr)
                            print ("     IP Address  : %s" % ip_addr)
                else:
                    print "     None"

                print "\n".strip()


class InventoryInfo():
    """ Methods to retrieve and display nodes inventory information """

    def __init__(self, ctrl):
        self.ctrl = ctrl

    def show_common(self, verbose=False):
        ctrl = self.ctrl

        inv_obj = None
        result = ctrl.build_inventory_object()
        status = result.get_status()
        if(status.eq(STATUS.OK)):
            inv_obj = result.get_data()
            assert(isinstance(inv_obj, Inventory))
        elif(status.eq(STATUS.DATA_NOT_FOUND)):
            print "\n".strip()
            print " Requested data not found"
            print "\n".strip()
            exit(0)
        else:
            print ("\n")
            print ("!!!Error, failed to obtain inventory info, reason: %s" %
                   status.brief().lower())
            exit(0)

        openflow_node_ids = inv_obj.get_openflow_node_ids()
        openflow_nodes = []
        flows_cnt = 0
        for node_id in openflow_node_ids:
            node = inv_obj.get_openflow_node(node_id)
            assert(isinstance(node, OpenFlowCapableNode))
            openflow_nodes.append(node)
            flows_cnt += inv_obj.get_openflow_node_flows_cnt(node_id)

        print "\n".strip()
        print (" OpenFlow Inventory Information")
        print "\n".strip()

        print ("   Number of switches : %s" % len(openflow_node_ids))
        print ("   Number of flows    : %s" % flows_cnt)

        if (verbose):
            for node in openflow_nodes:
                assert(isinstance(node, OpenFlowCapableNode))
                print "\n".strip()
                print ("   Switch '%s'\n" %
                       node.get_id())
                print ("     IP Address      : %s" %
                       node.get_ip_address())
                print ("     Number of flows : %s" %
                       node.get_flows_cnt())
                print ("     Max tables      : %s" %
                       node.get_max_tables_info())
                print ("     Max buffers     : %s" %
                       node.get_max_buffers_info())
                s = 'Capabilities'
                clist = node.get_capabilities()
                if len(clist) > 0:
                    g = 2
                    chunks = [clist[x:x+g] for x in xrange(0, len(clist), g)]
                    print "     %s    :" % s,
                    for i in range(0, len(chunks)):
                        n = 0 if i == 0 else len(s) + 11
                        print "%s%s" % (" "*n, ", ".join(chunks[i]))
                else:
                    print "     %s : %s" % (s, None)

                s1 = 'Table Id'
                s2 = 'Flows Cnt'
                print "\n".strip()
                print "     {0:<8}  {1:<10}".format(s1, s2)
                sym = '-'
                print "     {0:<8}  {1:<10}".format(sym*len(s1), sym*len(s2))
                flow_tables_cnt = node.get_flow_tables_cnt()
                for table_id in range(0, flow_tables_cnt+1):
                    cnt = node.get_flows_in_table_cnt(table_id)
                    if (cnt != 0):
                        print "     {0:<8}  {1:<10}".format(table_id, cnt)

                s1 = 'Port'
                s2 = 'OpenFlow Id'
                print "\n".strip()
                print "     {0:<8}  {1:<16}".format(s1, s2)
                print "     {0:<8}  {1:<30}".format(sym*8, sym*30)
                port_ids = node.get_port_ids()
                for port_id in port_ids:
                    port_obj = node.get_port_obj(port_id)
                    assert(isinstance(port_obj, OpenFlowPort))
                    pnum = port_obj.get_port_number()
                    print "     {0:<8}  {1:<30}".format(pnum, port_id)
        else:
            print "\n".strip()
            print ("   Switches")
            s1 = 'IP Address'
            s2 = 'OpenFlow Id'
            s3 = 'Flows Cnt'
            sym = '-'
            print "\n".strip()
            print "     {0:<15}  {1:<30}  {2:<10}".format(s1, s2, s3)
            print "     {0:<15}  {1:<30}  {2:<10}".format(sym*15,
                                                          sym*30,
                                                          sym*10)
            for node in openflow_nodes:
                assert(isinstance(node, OpenFlowCapableNode))
                addr = node.get_ip_address()
                node_id = node.get_id()
                flows_cnt = node.get_flows_cnt()
                print "     {0:<15}  {1:<30}  {2:<10}".format(addr,
                                                              node_id,
                                                              flows_cnt)

        print "\n"

    def show_switch(self, switch_id, verbose=False):
        ctrl = self.ctrl
        switch_inv = None

        result = ctrl.build_openflow_node_inventory_object(switch_id)
        status = result.get_status()
        if(status.eq(STATUS.OK)):
            switch_inv = result.get_data()
            assert(isinstance(switch_inv, OpenFlowCapableNode))
        elif(status.eq(STATUS.DATA_NOT_FOUND)):
            print "\n".strip()
            print " Requested data not found"
            print "\n".strip()
            exit(0)
        else:
            print ("\n")
            print ("!!!Error, failed to get inventory info for '%s' switch, "
                   "reason: %s" % (switch_id, status.brief().lower()))
            exit(1)

        if (verbose):
            print "\n".strip()
            print (" Switch '%s'\n" % switch_inv.get_id())
            print ("   Manufacturer    : %s" %
                   switch_inv.get_manufacturer_info())
            print ("   Software        : %s" %
                   switch_inv.get_software_info())
            print ("   Hardware        : %s" %
                   switch_inv.get_hardware_info())
            print ("   Serial number   : %s" %
                   switch_inv.get_serial_number())
            print ("   Description     : %s" %
                   switch_inv.get_description())
            print "\n".strip()
            print ("   OpenFlow Id     : %s" %
                   switch_inv.get_id())
            print ("   IP Address      : %s" %
                   switch_inv.get_ip_address())
            print ("   Number of flows : %s" %
                   switch_inv.get_flows_cnt())
            print ("   Max tables      : %s" %
                   switch_inv.get_max_tables_info())
            print ("   Max buffers     : %s" %
                   switch_inv.get_max_buffers_info())
            clist = switch_inv.get_capabilities()
            g = 2
            chunks = [clist[x:x+g] for x in xrange(0, len(clist), g)]
            s = 'Capabilities'
            print "   %s    :" % s,
            for i in range(0, len(chunks)):
                n = 0 if i == 0 else len(s) + 9
                print "%s%s" % (" "*n, ", ".join(chunks[i]))

            port_ids = switch_inv.get_port_ids()
            for port_id in port_ids:
                port_inv = switch_inv.get_port_obj(port_id)
                assert(isinstance(port_inv, OpenFlowPort))
                pnum = port_inv.get_port_number()
                pname = port_inv.get_port_name()
                pid = port_inv.get_port_id()
                mac = port_inv.get_mac_address()
                link_state = port_inv.get_link_state()
                fwd_state = port_inv.get_forwarding_state()
                pkts_rx = port_inv.get_packets_received()
                pkts_tx = port_inv.get_packets_transmitted()
                bytes_rx = port_inv.get_bytes_received()
                bytes_tx = port_inv.get_bytes_transmitted()
                current_speed = port_inv.get_current_speed()
                print "\n".strip()
                print "   Port '{}'".format(pnum)
                print "\n".strip()
                print "     OpenFlow Id      : {}".format(pid)
                print "     Name             : {}".format(pname)
                print "     MAC address      : {}".format(mac)
                print "     Link state       : {}".format(link_state)
                print "     Oper state       : {}".format(fwd_state)
                print "     Pkts RX          : {}".format(pkts_rx)
                print "     Pkts TX          : {}".format(pkts_tx)
                print "     Bytes RX         : {}".format(bytes_rx)
                print "     Bytes TX         : {}".format(bytes_tx)
                print "     Current speed    : {}".format(current_speed)
                s = 'Current features'
                cflist = port_inv.get_current_features()
                if len(cflist) > 0:
                    g = 2
                    chunks = [cflist[x:x+g] for x in xrange(0, len(cflist), g)]
                    print "     %s :" % s,
                    for i in range(0, len(chunks)):
                        n = 0 if i == 0 else len(s) + 8
                        print "%s%s" % (" "*n, ", ".join(chunks[i]))
                else:
                    print "     %s : %s" % (s, None)
        else:
            print "\n".strip()
            print (" Switch '%s'" % switch_id)
            print "\n".strip()
            print ("   IP Address      : %s" %
                   switch_inv.get_ip_address())
            print ("   Number of flows : %s" %
                   switch_inv.get_flows_cnt())
            print ("   Max tables      : %s" %
                   switch_inv.get_max_tables_info())
            print ("   Max buffers     : %s" %
                   switch_inv.get_max_buffers_info())
            clist = switch_inv.get_capabilities()
            g = 2
            chunks = [clist[x:x+g] for x in xrange(0, len(clist), g)]
            s = 'Capabilities'
            print "   %s    :" % s,
            for i in range(0, len(chunks)):
                n = 0 if i == 0 else len(s) + 9
                print "%s%s" % (" "*n, ", ".join(chunks[i]))

            s1 = 'Table Id'
            s2 = 'Flows Cnt'
            print "\n".strip()
            print "     {0:<8}  {1:<10}".format(s1, s2)
            sym = '-'
            print "     {0:<8}  {1:<10}".format(sym*len(s1), sym*len(s2))
            flow_tables_cnt = switch_inv.get_flow_tables_cnt()
            for table_id in range(0, flow_tables_cnt+1):
                cnt = switch_inv.get_flows_in_table_cnt(table_id)
                if (cnt != 0):
                    print "     {0:<8}  {1:<10}".format(table_id, cnt)

            s1 = 'Port'
            s2 = 'OpenFlow Id'
            print "\n".strip()
            print "     {0:<8}  {1:<16}".format(s1, s2)
            print "     {0:<8}  {1:<30}".format(sym*8, sym*30)
            port_ids = switch_inv.get_port_ids()
            for port_id in port_ids:
                port_obj = switch_inv.get_port_obj(port_id)
                assert(isinstance(port_obj, OpenFlowPort))
                pnum = port_obj.get_port_number()
                print "     {0:<8}  {1:<30}".format(pnum, port_id)

        print "\n"


class FlowInfo():
    """ Methods to retrieve and display OpenFlow flows information """

    def __init__(self, ctrl, switch_id):
        self.ctrl = ctrl
        self.switchid = switch_id

    def show_table(self, table_id, oper, ofp):
        flow_entries = []
        ofswitch = OFSwitch(self.ctrl, self.switchid)
        if oper:
            result = ofswitch.get_operational_FlowEntries(table_id)
        else:
            result = ofswitch.get_configured_FlowEntries(table_id)
        status = result.get_status()
        if(status.eq(STATUS.OK)):
            data = result.get_data()
            flow_entries = sorted(data, key=lambda fe: fe.get_flow_priority())
        elif(status.eq(STATUS.DATA_NOT_FOUND)):
            print "\n".strip()
            print " Requested data not found"
            print "\n".strip()
            exit(0)
        else:
            print ("\n")
            print ("!!!Error, reason: %s" % status.brief().lower())
            exit(0)

        print "\n".strip()
        s = "Device Operational" if oper else "Controller Cached"
        print (" Switch '%s' - %s Flows" % (self.switchid, s))
        print "\n".strip()

        if len(flow_entries) > 0:
            for flow_entry in flow_entries:
                assert(isinstance(flow_entry, FlowEntry))
                if(ofp):
                    print (" -- Flow id '%s'" % flow_entry.get_flow_id())
                    print (" %s" % flow_entry.to_ofp_oxm_syntax())
                else:
                    lines = flow_entry.to_yang_json(strip=True).split('\n')
                    for line in lines:
                        print " %s" % line
        else:
            print "   No flows found"

        print "\n".strip()

    def show_flow(self, table_id, flow_id, oper, ofp):
        ofswitch = OFSwitch(self.ctrl, self.switchid)
        flow_entry = None
        if oper:
            result = ofswitch.get_operational_FlowEntry(table_id, flow_id)
        else:
            result = ofswitch.get_configured_FlowEntry(table_id, flow_id)
        status = result.get_status()
        if(status.eq(STATUS.OK)):
            flow_entry = result.get_data()
            assert(isinstance(flow_entry, FlowEntry))
        elif(status.eq(STATUS.DATA_NOT_FOUND)):
            print "\n".strip()
            print " Requested data not found"
            print "\n".strip()
            exit(0)
        else:
            print ("\n")
            print ("!!!Error, reason: %s" % status.brief().lower())
            exit(0)

        print "\n".strip()
        s = "Device Operational" if oper else "Controller Cached"
        print " Switch '%s' - %s Flows" % (self.switchid, s)
        print "\n".strip()

        if(flow_entry is not None):
            if(ofp):
                print (" -- Flow id '%s'" % flow_entry.get_flow_id())
                print (" %s" % flow_entry.to_ofp_oxm_syntax())
            else:
                lines = flow_entry.to_yang_json(strip=True).split('\n')
                for line in lines:
                    print " %s" % line
        else:
            print "   Not found"

        print "\n".strip()


class GroupInfo():
    """ Methods to retrieve and display OpenFlow groups information """

    def __init__(self, ctrl, switch_id):
        self.ctrl = ctrl
        self.switchid = switch_id

    def show_table(self, config, description, stats, ofp):
        groups = []
        ofswitch = OFSwitch(self.ctrl, self.switchid)
        s = ""
        if description:
            s = 'Device Operational Groups'
            result = ofswitch.get_groups_description(decode_object=True)
        elif stats:
            s = 'Group Statistics'
            result = ofswitch.get_groups_statistics(decode_object=True)
        elif config:
            s = 'Controller Cached Groups'
            result = ofswitch.get_configured_groups(decode_object=True)
        else:
            assert(False)

        status = result.get_status()
        if(status.eq(STATUS.OK)):
            data = result.get_data()
            groups = sorted(data, key=lambda ge: ge.get_group_id())
        elif(status.eq(STATUS.DATA_NOT_FOUND)):
            print "\n".strip()
            print " Requested data not found"
            print "\n".strip()
            exit(0)
        else:
            print ("\n")
            print ("!!!Error, reason: %s" % status.brief().lower())
            exit(0)

        print "\n".strip()
        print " Switch '%s' - %s" % (self.switchid, s)
        print "\n".strip()

        if len(groups) > 0:
            for group in groups:
                assert(isinstance(group, GroupEntry) or
                       isinstance(group, GroupDescription) or
                       isinstance(group, GroupStatistics))
                if(ofp):
                    print (" -- Group id '%s'" % group.get_group_id())
                    print (" %s" % group.to_ofp_oxm_syntax())
                else:
                    lines = group.to_yang_json(strip=True).split('\n')
                    for line in lines:
                        print " %s" % line
        else:
            print "   No groups found"

        print "\n".strip()

    def show_group(self, group_id, config, description, stats, ofp):
        ofswitch = OFSwitch(self.ctrl, self.switchid)
        group_entry = None
        s = ""
        if description:
            s = 'Description'
            result = ofswitch.get_group_description(group_id,
                                                    decode_object=True)
        elif stats:
            s = 'Statistics'
            result = ofswitch.get_group_statistics(group_id,
                                                   decode_object=True)
        elif config:
            s = 'Config'
            result = ofswitch.get_configured_group(group_id,
                                                   decode_object=True)
        else:
            assert(False)

        status = result.get_status()
        if(status.eq(STATUS.OK)):
            group_entry = result.get_data()
            assert(isinstance(group_entry, GroupEntry) or
                   isinstance(group_entry, GroupDescription) or
                   isinstance(group_entry, GroupStatistics))
        elif(status.eq(STATUS.DATA_NOT_FOUND)):
            print "\n".strip()
            print " Requested data not found"
            print "\n".strip()
            exit(0)
        else:
            print ("\n")
            print ("!!!Error, reason: %s" % status.brief().lower())
            exit(0)

        print "\n".strip()
        print " Group %s - Switch '%s'" % (s, self.switchid)
        print "\n".strip()

        if(group_entry is not None):
            if(ofp):
                print "[GroupInfo] show_group - TBD"
#                print " -- Flow id '%s'" % flow_entry.get_flow_id()
#                print " %s" % flow_entry.to_ofp_oxm_syntax()
            else:
                lines = group_entry.to_yang_json(strip=True).split('\n')
                for line in lines:
                    print " %s" % line
        else:
            print "   Not found"

        print "\n".strip()

    def show_features(self):
        ofswitch = OFSwitch(self.ctrl, self.switchid)
        result = ofswitch.get_group_features(decode_object=True)
        status = result.get_status()
        if(status.eq(STATUS.OK)):
            print "\n".strip()
            print (" Group Features - Switch '%s'") % self.switchid
            print "\n".strip()
            group_features = result.get_data()
            assert(isinstance(group_features, GroupFeatures))

            s = 'Max groups'
            alist = group_features.get_max_groups()
            if alist:
                q = 1   # number of list items per output string
                chunks = [alist[x:x+q] for x in xrange(0, len(alist), q)]
                print "  %s     :" % s,
                for i in range(0, len(chunks)):
                    n = 0 if i == 0 else len(s) + 9
                    print "%s%s" % (" "*n, ", ".join(map(str, chunks[i])))
            else:
                print "  %s     : %s" % (s, "n/a")

            s = 'Group types'
            alist = group_features.get_types()
            if alist:
                q = 1   # number of list items per output string
                chunks = [alist[x:x+q] for x in xrange(0, len(alist), q)]
                print "  %s    :" % s,
                for i in range(0, len(chunks)):
                    n = 0 if i == 0 else len(s) + 8
                    print "%s%s" % (" "*n, ", ".join(chunks[i]))
            else:
                print "  %s    : %s" % (s, "n/a")

            s = 'Capabilities'
            alist = group_features.get_capabilities()
            if alist:
                q = 1   # number of list items per output string
                chunks = [alist[x:x+q] for x in xrange(0, len(alist), q)]
                print "  %s   :" % s,
                for i in range(0, len(chunks)):
                    n = 0 if i == 0 else len(s) + 7
                    print "%s%s" % (" "*n, ", ".join(chunks[i]))
            else:
                print "  %s   : %s" % (s, "n/a")

            s = 'Actions'
            actions = group_features.get_actions()
            if actions:
                q = 4   # number of list items per output string
                print "  %s        :" % s,
                for i, alist in enumerate(actions):
                    n = 0 if i == 0 else len(s) + 12
                    chunks = [alist[x:x+q] for x in xrange(0, len(alist), q)]
                    for j in range(0, len(chunks)):
                        n = 0 if i == 0 and j == 0 else len(s) + 12
                        print "%s%s" % (" "*n, ", ".join(chunks[j]))
                    print "\n".strip()
            else:
                print "  %s     : %s" % (s, "n/a")

            print "\n".strip()

        elif(status.eq(STATUS.DATA_NOT_FOUND)):
            print "\n".strip()
            print " Requested data not found"
            print "\n".strip()
            exit(0)
        else:
            print ("\n")
            print ("!!!Error, reason: %s" % status.brief().lower())
            exit(0)

    def show_statistics(self):
        print "[GroupInfo] show_statistics - TBD"

    def show_description(self):
        print "[GroupInfo] show_description - TBD"


class OFToolParser(object):
    """ CLI parser and commands executer """

    def __init__(self):
        self.prog = 'oftool'
        parser = argparse.ArgumentParser(
            prog=self.prog,
            description=("Command line tool for interaction with "
                         "OpenFlow Controller"),
            usage=("%(prog)s [-h] [-C <path>] <command> [<args>]\n"
                   "(type '%(prog)s -h' for details)\n"
                   "\nAvailable commands are:\n"
                   "\n   show-topo       Show network topology information"
                   "\n   show-inv        Show inventory nodes information"
                   "\n   show-flow       Show OpenFlow flows information"
                   "\n   clear-flow      Delete OpenFlow flows"
                   "\n   add-flow        Add OpenFlow flows"
                   "\n   show-group      Show OpenFlow groups information"
                   "\n   clear-group     Delete OpenFlow groups"
                   "\n   add-group       Add OpenFlow groups"
                   "\n"
                   "\n  '%(prog)s help <command>' provides details "
                   "for a specific command"))
        parser.add_argument('-C', metavar="<path>",
                            dest='ctrl_cfg_file',
                            help="path to the controller's configuration file "
                                 "(default is './ctrl.yml')",
                            default="./ctrl.yml")
        parser.add_argument('command', help='command to be executed')
        args, remaining_args = parser.parse_known_args()

        # Get Controller's attributes from configuration file
        self.ctrl_cfg = self.get_ctrl_cfg(args.ctrl_cfg_file)
        if(self.ctrl_cfg is None):
            print "\n".strip()
            print ("Cannot find controller configuration file")
            print "\n".strip()
            exit(1)

        # Invoke method that is matching the name of sub-command argument
        cmd_orig = args.command
        cmd = cmd_orig.replace('-', '_')
        if hasattr(self, cmd):
            getattr(self, cmd)(remaining_args)
        else:
            print "\n".strip()
            print ("Error, unrecognized command '%s'" % cmd_orig)
            print "\n".strip()
            parser.print_help()
            exit(1)

    def show_topo(self, options):
        parser = argparse.ArgumentParser(
            prog=self.prog,
            # description='Show network topology information',
            usage="%(prog)s show-topo [-s=SWITCHID|--switch=SWITCHID]"
                  " [-v|--verbose]"
                  "\n\n"
                  "Show OpenFlow network topology information in the"
                  " operational inventory store\n\n"
                  "Options:\n"
                  "  -s, --switch    switch identifier\n"
                  "  -v, --verbose   detailed output\n")
        parser.add_argument("-v", '--verbose', action="store_true",
                            help="output details level")
        parser.add_argument('-s', '--switch', metavar="SWITCHID")
        parser.add_argument('-U', action="store_true", dest="usage",
                            help=argparse.SUPPRESS)
        args = parser.parse_args(options)
        if(args.usage):
            parser.print_usage()
            print "\n".strip()
            return

        print "\n".strip()
        print " [Controller '%s']" % self.ctrl_cfg.to_string()
        ctrl = Controller(self.ctrl_cfg.ip_addr, self.ctrl_cfg.tcp_port,
                          self.ctrl_cfg.admin_name, self.ctrl_cfg.admin_pswd)
        topo_id = 'flow:1'  # OpenFlow topology
        topo = TopologyInfo(ctrl, topo_id)
        if(args.switch):
            topo.show_switch(args.switch, args.verbose)
        else:
            topo.show_common(args.verbose)

    def show_inv(self, options):
        parser = argparse.ArgumentParser(
            prog=self.prog,
            # description=("Show OpenFlow nodes information "
            #              "in the controller's inventory store"),
            usage="%(prog)s show-inv [-s=SWITCHID|--switch=SWITCHID]"
                  " [-v|--verbose]"
                  "\n\n"
                  "Show OpenFlow nodes information in the"
                  " operational inventory store\n\n"
                  "Options:\n"
                  "  -s, --switch    switch identifier\n"
                  "  -v, --verbose   detailed output\n")
        parser.add_argument("-v", '--verbose', action="store_true",
                            help="output details level")
        parser.add_argument('-s', '--switch', metavar="SWITCHID")
        parser.add_argument('-U', action="store_true", dest="usage",
                            help=argparse.SUPPRESS)
        args = parser.parse_args(options)
        if(args.usage):
            parser.print_usage()
            print "\n".strip()
            return

        print "\n".strip()
        print " [Controller '%s']" % self.ctrl_cfg.to_string()
        ctrl = Controller(self.ctrl_cfg.ip_addr, self.ctrl_cfg.tcp_port,
                          self.ctrl_cfg.admin_name, self.ctrl_cfg.admin_pswd)
        inv = InventoryInfo(ctrl)
        if(args.switch):
            inv.show_switch(args.switch, args.verbose)
        else:
            inv.show_common(args.verbose)

    def show_flow(self, options):
        parser = argparse.ArgumentParser(
            prog=self.prog,
            # description='Show OpenFlow flows information',
            usage=("%(prog)s show-flow -s=SWITCHID|--switch=SWITCHID\n"
                   "                        -t=TABLEID|--table=TABLEID\n"
                   "                         [-f=FLOWID|--flow=FLOWID]\n"
                   "                         [--config|--operational]\n"
                   "                         [--json|--ofp]"
                   "\n\n"
                   "Show OpenFlow flows information\n\n"
                   "\n\n"
                   "Options:\n"
                   "  -s, --switch    switch identifier\n"
                   "  -t, --table     flow table id\n"
                   "  -f, --flow      flow entry id\n"
                   "  --config        controller cached flows (default)\n"
                   "  --operational   device operational flows\n"
                   "  --json          display data in JSON format (default)\n"
                   "  --ofp           display data in OpenFlow protocol "
                   "format\n"))
        parser.add_argument('-s', '--switch', metavar="SWITCHID")
        parser.add_argument('-t', '--table', metavar="TABLEID",
                            type=self.positive_int)
        parser.add_argument('-f', '--flow', metavar="FLOWID")
        group1 = parser.add_mutually_exclusive_group()
        group1.add_argument('--config', action='store_true', default=True)
        group1.add_argument('--oper', action='store_true')
        group2 = parser.add_mutually_exclusive_group()
        group2.add_argument('--json', action='store_true', default=True)
        group2.add_argument('--ofp', action='store_true')
        parser.add_argument('-U', action="store_true", dest="usage",
                            help=argparse.SUPPRESS)
        args = parser.parse_args(options)
        if(args.usage):
            parser.print_usage()
            print "\n".strip()
            return

        if (args.switch is None):
            msg = "option -s (or --switch) is required"
            parser.error(msg)

        if (args.table is None):
            msg = "option -t (or --table) is required"
            parser.error(msg)

        print "\n".strip()
        print " [Controller '%s']" % self.ctrl_cfg.to_string()
        ctrl = Controller(self.ctrl_cfg.ip_addr, self.ctrl_cfg.tcp_port,
                          self.ctrl_cfg.admin_name, self.ctrl_cfg.admin_pswd)
        flow = FlowInfo(ctrl, args.switch)
        if (args.flow is not None):
            flow.show_flow(args.table, args.flow, args.oper, args.ofp)
        else:
            flow.show_table(args.table, args.oper, args.ofp)

    def clear_flow(self, options):
        parser = argparse.ArgumentParser(
            prog=self.prog,
            description='Clear OpenFlow flows',
            usage="%(prog)s clear-flow -s=SWITCHID|--switch=SWICTHID\n"
                  "                         -t=TABLEID|--table=TABLEID\n"
                  "                          [-f=FLOWID|--flow=FLOWID]\n"
                  "\n\n"
                  "Remove one or set of flows from the Controller\n\n"
                  "\n\n"
                  "Options:\n"
                  "  -s, --switch   switch identifier\n"
                  "  -t, --table    flow table id\n"
                  "  -f, --flow     flow id\n")
        parser.add_argument('-s', '--switch', metavar="SWITCHID")
        parser.add_argument('-t', '--table', metavar="TABLEID",
                            type=self.positive_int)
        parser.add_argument('-f', '--flow', metavar="FLOWID")
        parser.add_argument('-U', action="store_true", dest="usage",
                            help=argparse.SUPPRESS)
        args = parser.parse_args(options)
        if(args.usage):
            parser.print_usage()
            print "\n".strip()
            return

        if (args.switch is None):
            msg = "option -s (or --switch) is required"
            parser.error(msg)

        if (args.table is None):
            msg = "option -t (or --table) is required"
            parser.error(msg)

        print "\n".strip()
        print " [Controller '%s']" % self.ctrl_cfg.to_string()
        ctrl = Controller(self.ctrl_cfg.ip_addr, self.ctrl_cfg.tcp_port,
                          self.ctrl_cfg.admin_name, self.ctrl_cfg.admin_pswd)
        ofswitch = OFSwitch(ctrl, args.switch)
        if(args.flow is not None):
            result = ofswitch.delete_flow(args.table, args.flow)
        else:
            result = ofswitch.delete_flows(args.table)

        status = result.get_status()
        print "\n".strip()
        print "%s" % status.detailed()
        print "\n".strip()

    def add_flow(self, options):
        parser = argparse.ArgumentParser(
            prog=self.prog,
            description="Add flow entries to the Controller's cache",
            usage="%(prog)s add-flow -s=SWITCHID|--switch=SWICTHID\n"
                  "                       -f <path>|--file <path>\n"
                  "                        [--dry-run]\n"
                  "\n\n"
                  "Add flow entries to the Controller's cache\n\n"
                  "\n\n"
                  "Options:\n"
                  "  -s, --switch   switch identifier\n"
                  "  -f, --file     path to the file containing flow entries\n"
                  "                 (default is './flow.json')\n"
                  "  -dry-run       show content of flow(s) to be created"
            )
        parser.add_argument('-s', '--switch', metavar="SWITCHID")
        parser.add_argument('-f', '--file', metavar="<path>",
                            dest='flow_file',
                            help="path to the file containing flow entries "
                                 "(default is './flow.json')",
                            default="./flow.json")
        parser.add_argument('-U', action="store_true", dest="usage",
                            help=argparse.SUPPRESS)
        parser.add_argument('--dry-run', action="store_true",
                            dest='dry_run', default=False)
        args = parser.parse_args(options)

        if(args.usage):
            parser.print_usage()
            print "\n".strip()
            return

        if(args.dry_run):
            flows = self.read_data(args.flow_file)
            if flows:
                for flow in flows:
                    print json.dumps(flow, indent=4)

            return

        if (args.switch is None):
            msg = "option -s (or --switch) is required"
            parser.error(msg)

        flows = self.read_data(args.flow_file)
        if not flows:
            print "Failed to execute command, exit"
            exit(1)

        print "\n".strip()
        print " [Controller '%s']" % self.ctrl_cfg.to_string()
        print "\n".strip()
        ctrl = Controller(self.ctrl_cfg.ip_addr, self.ctrl_cfg.tcp_port,
                          self.ctrl_cfg.admin_name, self.ctrl_cfg.admin_pswd)
        ofswitch = OFSwitch(ctrl, args.switch)

        try:
            for flow in flows:
                fid = flow['id']
                tid = flow['table_id']
                js = json.dumps(flow, default=lambda o: o.__dict__)
                result = ofswitch.add_modify_flow_json(table_id=tid,
                                                       flow_id=fid,
                                                       flow_json=js)
                status = result.get_status()
                if(status.eq(STATUS.OK)):
                    print "Flow id '%s', success" % fid
                else:
                    print ("Flow id '%s', failure, reason: %s" %
                           (fid, status.detailed()))
            print "\n".strip()
        except(Exception) as e:
            msg = "Error: %s" % repr(e)
            dbg_print(msg)

    def show_group(self, options):
        usage_txt = (
            "%(prog)s show-group -s=SWITCHID|--switch=SWITCHID\n"
            "                         [--features]\n"
            "                         [-g=GROUPID|--group=GROUPID]\n"
            #  "                         [--config|--operational]\n"
            "                         [--config|--operational|--statistics]\n"
            "                         [--json|--ofp]"
            "\n\n"
            "Show OpenFlow groups information\n\n"
            "\n\n"
            "Options:\n"
            "  -s, --switch    switch identifier\n"
            "  --features      capabilities of groups on the switch\n"
            "  -g, --group     group identifier (integer)\n"
            "  --config        controller cached groups (default)\n"
            # "  --operational   device operational groups\n"
            # "  --description   set of groups on the switch\n"
            # "  --description   operational groups on the switch\n"
            "  --operational   operational groups on the switch\n"
            # "  --statistics    statistics for one or more groups\n"
            "  --statistics    statistics for groups on the switch\n"
            "  --json          display data in JSON format (default)\n"
            "  --ofp           display data in OpenFlow protocol format\n"
        )

        parser = argparse.ArgumentParser(
            prog=self.prog,
            # description='Show OpenFlow groups information',
            usage=usage_txt)
        parser.add_argument('-s', '--switch', metavar="SWITCHID")
        parser.add_argument('-g', '--group', metavar="GROUPID")
        group1 = parser.add_mutually_exclusive_group()
        group1.add_argument('--features', action='store_true')
        group1.add_argument('--config', action='store_true', default=True)
        group1.add_argument('--oper', action='store_true', dest="description")
#        group1.add_argument('--description', action='store_true')
        group1.add_argument('--statistics', action='store_true')
        group2 = parser.add_mutually_exclusive_group()
        group2.add_argument('--json', action='store_true', default=True)
        group2.add_argument('--ofp', action='store_true')
        parser.add_argument('-U', action="store_true", dest="usage",
                            help=argparse.SUPPRESS)
        args = parser.parse_args(options)
        if(args.usage):
            parser.print_usage()
            print "\n".strip()
            return

        if (args.switch is None):
            msg = "option -s (or --switch) is required"
            parser.error(msg)

        print "\n".strip()
        print " [Controller '%s']" % self.ctrl_cfg.to_string()
        ctrl = Controller(self.ctrl_cfg.ip_addr, self.ctrl_cfg.tcp_port,
                          self.ctrl_cfg.admin_name, self.ctrl_cfg.admin_pswd)

        group = GroupInfo(ctrl, args.switch)
        if(args.features):
            group.show_features()
        elif (args.group is not None):
            group.show_group(args.group,
                             args.config, args.description,
                             args.statistics, args.ofp)
        else:
            group.show_table(args.config, args.description,
                             args.statistics, args.ofp)

    def clear_group(self, options):
        parser = argparse.ArgumentParser(
            prog=self.prog,
            # description="Clear OpenFlow groups",
            usage="%(prog)s clear-group -s=SWITCHID|--switch=SWICTHID\n"
                  "                          [-g=GROUPID|--group=GROUPID]\n"
                  "\n\n"
                  "Remove one or all groups from the Controller\n\n"
                  "\n\n"
                  "Options:\n"
                  "  -s, --switch   switch identifier\n"
                  "  -g, --group    group identifier (integer)\n"
            )
        parser.add_argument('-s', '--switch', metavar="SWITCHID")
        parser.add_argument('-g', '--group', metavar="GROUPID",
                            type=self.positive_int)
        parser.add_argument('-U', action="store_true", dest="usage",
                            help=argparse.SUPPRESS)
        args = parser.parse_args(options)
        if(args.usage):
            parser.print_usage()
            print "\n".strip()
            return

        if (args.switch is None):
            msg = "option -s (or --switch) is required"
            parser.error(msg)

        print "\n".strip()
        print " [Controller '%s']" % self.ctrl_cfg.to_string()
        ctrl = Controller(self.ctrl_cfg.ip_addr, self.ctrl_cfg.tcp_port,
                          self.ctrl_cfg.admin_name, self.ctrl_cfg.admin_pswd)
        ofswitch = OFSwitch(ctrl, args.switch)
        if(args.group is not None):
            result = ofswitch.delete_group(args.group)
            status = result.get_status()
            print "\n".strip()
            if(status.eq(STATUS.OK)):
                print (" Group '%s' successfully removed" % args.group)
            elif(status.eq(STATUS.DATA_NOT_FOUND)):
                print " Requested data not found"
            else:
                print (" Failed to remove group '%s', reason '%s'" %
                       (args.group, status.detailed()))
            print "\n".strip()
        else:
            result = ofswitch.get_group_ids(operational=False)
            status = result.get_status()
            print "\n".strip()
            if(status.eq(STATUS.OK)):
                group_ids = result.get_data()
                for group in group_ids:
                    result = ofswitch.delete_group(group)
                    status = result.get_status()
                    if(status.eq(STATUS.OK)):
                        print (" Group '%s' successfully removed" % group)
                    else:
                        print (" Failed to remove group '%s', reason '%s'" %
                               (group, status.detailed()))
            else:
                msg = " Failed to get list of groups to be deleted"
                print ("%s, reason '%s'") % (msg, status.detailed())
            print "\n".strip()

    def add_group(self, options):
        usage_txt = (
            "%(prog)s add-flow -s=SWITCHID|--switch=SWICTHID\n"
            "                       -f <path>|--file <path>\n"
            "                        [--dry-run]\n"
            "\n\n"
            "Add group table entries to the Controller's cache\n\n"
            "\n\n"
            "Options:\n"
            "  -s, --switch   switch identifier\n"
            "  -f, --file     path to the file containing group entries\n"
            "                 (default is './group.json')\n"
            "  -dry-run       show content of group(s) to be created"
        )
        parser = argparse.ArgumentParser(
            prog=self.prog,
            description="Add flow entries to the Controller's cache",
            usage=usage_txt)
        parser.add_argument('-s', '--switch', metavar="SWITCHID")
        parser.add_argument('-f', '--file', metavar="<path>",
                            dest='group_file',
                            help="path to the file containing group entries "
                                 "(default is './group.json')",
                            default="./group.json")
        parser.add_argument('-U', action="store_true", dest="usage",
                            help=argparse.SUPPRESS)
        parser.add_argument('--dry-run', action="store_true",
                            dest='dry_run', default=False)
        args = parser.parse_args(options)

        if(args.usage):
            parser.print_usage()
            print "\n".strip()
            return

        if(args.dry_run):
            groups = self.read_data(args.group_file)
            if groups:
                for group in groups:
                    print json.dumps(group, indent=4)

            return

        if (args.switch is None):
            msg = "option -s (or --switch) is required"
            parser.error(msg)

        groups = self.read_data(args.group_file)
        if not groups:
            print "Failed to execute command, exit"
            exit(1)

        print "\n".strip()
        print " [Controller '%s']" % self.ctrl_cfg.to_string()
        print "\n".strip()
        ctrl = Controller(self.ctrl_cfg.ip_addr, self.ctrl_cfg.tcp_port,
                          self.ctrl_cfg.admin_name, self.ctrl_cfg.admin_pswd)
        ofswitch = OFSwitch(ctrl, args.switch)

        try:
            for group in groups:
                gid = group['group-id']
                js = json.dumps(group, default=lambda o: o.__dict__)
                result = ofswitch.add_modify_group_json(gid, js)
                status = result.get_status()
                if(status.eq(STATUS.OK)):
                    print "Group id '%s', success" % gid
                else:
                    print ("Group id '%s', failure, reason: %s" %
                           (gid, status.detailed()))
            print "\n".strip()
        except(Exception) as e:
            msg = "Error: %s" % repr(e)
            dbg_print(msg)

    def help(self, options):
        parser = argparse.ArgumentParser(add_help=False,
                                         usage="oftool help <command>")
        parser.add_argument('command')
        args = parser.parse_args(options)
        cmd = args.command.replace('-', '_')
        if not hasattr(self, cmd):
            print 'Unrecognized command %s' % cmd
            return

        getattr(self, cmd)(['-U'])

    def get_ctrl_cfg(self, path):
        try:
            with open(path, 'r') as f:
                obj = yaml.load(f)
            d = {}
            for k, v in obj.iteritems():
                d[k] = v

            addr = d['ipaddr']
            port = d['port']
            name = d['name']
            pswd = d['pswd']
            cfg = CtrlCfg(addr, port, name, pswd)

            return cfg
        except (IOError, KeyError) as e:
            if isinstance(e, IOError):
                print("Error: failed to read file '%s'" % path)
            elif isinstance(e, KeyError):
                print ("Error: unknown attribute %s in file '%s'" % (e, path))

            return None

    def read_data(self, path):
        try:
            with open(path, 'r') as f:
                objs = json.load(f, cls=ConcatJSONObjects,
                                 object_pairs_hook=OrderedDict)
                if not objs:
                    raise ValueError('no data')
                return objs
        except (Exception) as e:
            if isinstance(e, IOError):
                print("Error: failed to read file '%s'" % path)
            elif isinstance(e, ValueError):
                print ("Error: failed to parse data in file '%s' [%s]" %
                       (path, e))
            else:
                print "!!!Error: %s" % e
            return None

    def positive_int(self, value):
        msg = "is not a valid positive integer"
        try:
            if (int(value) < 0):
                raise argparse.ArgumentTypeError("'%s' %s" % (value, msg))
        except:
            raise argparse.ArgumentTypeError("'%s' %s" % (value, msg))

        return value

if __name__ == '__main__':
    OFToolParser()
