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

@authors: Sergei Garbuzov
@status: Development
@version: 1.1.0


"""

import time

from pybvc.common.status import STATUS
from pybvc.common.utils import load_dict_from_file
from pybvc.controller.controller import Controller
from pybvc.controller.inventory import (Inventory,
                                        OpenFlowCapableNode,
                                        OpenFlowPort)


def of_demo_28():

    f = "cfg.yml"
    d = {}
    if(load_dict_from_file(f, d) is False):
        print("Config file '%s' read error: " % f)
        exit()

    try:
        ctrlIpAddr = d['ctrlIpAddr']
        ctrlPortNum = d['ctrlPortNum']
        ctrlUname = d['ctrlUname']
        ctrlPswd = d['ctrlPswd']
        rundelay = d['rundelay']
    except:
        print ("Failed to get Controller device attributes")
        exit(0)

    openflow_nodes = []

    print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    print ("<<< Demo 28 Start")
    print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    print "\n"
    ctrl = Controller(ctrlIpAddr, ctrlPortNum, ctrlUname, ctrlPswd)
    print ("<<< Controller '%s:%s'" % (ctrlIpAddr, ctrlPortNum))
    time.sleep(rundelay)

    print "\n"
    print ("<<< Get OpenFlow Inventory Information")
    time.sleep(rundelay)

    inv_obj = None
    result = ctrl.build_inventory_object()
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        inv_obj = result.get_data()
        assert(isinstance(inv_obj, Inventory))
    else:
        print ("\n")
        print ("!!!Error, failed to obtain inventory info, reason: %s" %
               status.brief().lower())
        exit(0)

    assert(inv_obj)
    openflow_node_ids = inv_obj.get_openflow_node_ids()
    for node_id in openflow_node_ids:
        node = inv_obj.get_openflow_node(node_id)
        assert(isinstance(node, OpenFlowCapableNode))
        openflow_nodes.append(node)

    print "\n"
    print ("<<< OpenFlow switches")
    s1 = 'IP Address'
    s2 = 'OpenFlow Id'
    sym = '-'
    print "\n".strip()
    print "        {0:<15}  {1:<30}".format(s1, s2)
    print "        {0:<15}  {1:<30}".format(sym*15, sym*30)
    for node in openflow_nodes:
        addr = node.get_ip_address()
        node_id = node.get_id()
        print "        {0:<15}  {1:<30}".format(addr, node_id)

    for node in openflow_nodes:
        assert(isinstance(node, OpenFlowCapableNode))
        time.sleep(rundelay)
        print "\n".strip()
        print "<<< Information for '%s' switch\n" % node.get_id()
        print "        IP Address      : %s" % node.get_ip_address()
        print "        Max tables      : %s" % node.get_max_tables_info()
        print "        Number of flows : %s" % node.get_flows_cnt()
        clist = node.get_capabilities()
        g = 2
        chunks = [clist[x:x+g] for x in xrange(0, len(clist), g)]
        s = 'Capabilities'
        print "        %s    :" % s,
        for i in range(0, len(chunks)):
            n = 0 if i == 0 else len(s) + 14
            print "%s%s" % (" "*n, ", ".join(chunks[i]))

        s1 = 'Table Id'
        s2 = 'Flows Cnt'
        print "\n".strip()
        print "        {0:<8}  {1:<10}".format(s1, s2)
        sym = '-'
        print "        {0:<8}  {1:<10}".format(sym*len(s1), sym*len(s2))
        flow_tables_cnt = node.get_flow_tables_cnt()
        for table_id in range(0, flow_tables_cnt+1):
            cnt = node.get_flows_in_table_cnt(table_id)
            if (cnt != 0):
                print "        {0:<8}  {1:<10}".format(table_id, cnt)

        s1 = 'Port Num'
        s2 = 'OpenFlow Id'
        print "\n".strip()
        print "        {0:<8}  {1:<16}".format(s1, s2)
        print "        {0:<8}  {1:<30}".format(sym*8, sym*30)
        port_ids = node.get_port_ids()
        for port_id in port_ids:
            port_obj = node.get_port_obj(port_id)
            assert(isinstance(port_obj, OpenFlowPort))
            pnum = port_obj.get_port_number()
            print "        {0:<8}  {1:<30}".format(pnum, port_id)

    for node in openflow_nodes:
        assert(isinstance(node, OpenFlowCapableNode))
        time.sleep(rundelay)
        print "\n".strip()
        print "<<< Detailed information for '%s' switch\n" % node.get_id()
        print "        Manufacturer    : %s" % node.get_manufacturer_info()
        print "        Software        : %s" % node.get_software_info()
        print "        Hardware        : %s" % node.get_hardware_info()
        print "        Serial number   : %s" % node.get_serial_number()
        print "\n".strip()
        print "        OpenFlow Id     : %s" % node.get_id()
        print "        IP Address      : %s" % node.get_ip_address()
        print "        Description     : %s" % node.get_description()
        print "        Max buffers     : %s" % node.get_max_buffers_info()
        print "        Max tables      : %s" % node.get_max_tables_info()
        print "        Number of flows : %s" % node.get_flows_cnt()
        clist = node.get_capabilities()
        g = 2
        chunks = [clist[x:x+g] for x in xrange(0, len(clist), g)]
        s = 'Capabilities'
        print "        %s    :" % s,
        for i in range(0, len(chunks)):
            n = 0 if i == 0 else len(s) + 14
            print "%s%s" % (" "*n, ", ".join(chunks[i]))

        port_ids = node.get_port_ids()
        for port_id in port_ids:
            port_obj = node.get_port_obj(port_id)
            assert(isinstance(port_obj, OpenFlowPort))
            pnum = port_obj.get_port_number()
            pname = port_obj.get_port_name()
            pid = port_obj.get_port_id()
            mac = port_obj.get_mac_address()
            link_state = port_obj.get_link_state()
            fwd_state = port_obj.get_forwarding_state()
            pkts_rx = port_obj.get_packets_received()
            pkts_tx = port_obj.get_packets_transmitted()
            bytes_rx = port_obj.get_bytes_received()
            bytes_tx = port_obj.get_bytes_transmitted()
            print "\n".strip()
            print "        Port '{}'".format(pnum)
            print "            OpenFlow Id : {}".format(pid)
            print "            Name        : {}".format(pname)
            print "            MAC address : {}".format(mac)
            print "            Link state  : {}".format(link_state)
            print "            Oper state  : {}".format(fwd_state)
            print "            Pkts RX     : {}".format(pkts_rx)
            print "            Pkts TX     : {}".format(pkts_tx)
            print "            Bytes RX    : {}".format(bytes_rx)
            print "            Bytes TX    : {}".format(bytes_tx)

    print ("\n")
    print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print (">>> Demo End")
    print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

if __name__ == "__main__":
    of_demo_28()
