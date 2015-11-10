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

from pysdn.controller.controller import Controller
from pysdn.controller.inventory import Inventory
from pysdn.controller.topology import Topology, Node

from pysdn.common.status import STATUS
from pysdn.common.utils import load_dict_from_file


def of_demo_27():

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

    print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    print ("<<< Demo 27 Start")
    print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    ctrl = Controller(ctrlIpAddr, ctrlPortNum, ctrlUname, ctrlPswd)

    print "\n"
    print ("<<< Controller '%s:%s'" % (ctrlIpAddr, ctrlPortNum))
    time.sleep(rundelay)

    print ("\n")
    print ("<<< Get OpenFlow Network Topology information")
    time.sleep(rundelay)

    topology_ids = []
    topologies = []
    inventory = None

    result = ctrl.build_inventory_object()
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        inventory = result.get_data()
        assert(isinstance(inventory, Inventory))
    else:
        print ("\n")
        print ("!!!Error, failed to obtain inventory info, reason: %s" %
               status.brief().lower())
        exit(0)

    result = ctrl.get_topology_ids()
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        topology_ids = result.get_data()
        assert(isinstance(topology_ids, list))
    else:
        print ("\n")
        print ("!!!Error, failed to obtain topology info, reason: %s" %
               status.brief().lower())
        exit(0)

    print "\n"
    print ("<<< Network topologies")
    for topo_id in topology_ids:
        print "       '%s'" % topo_id

    of_topo_id = 'flow:1'
    for topo_id in topology_ids:
        if (topo_id != of_topo_id):
            continue
        result = ctrl.build_topology_object(topo_id)
        status = result.get_status()
        if(status.eq(STATUS.OK)):
            topo = result.get_data()
            topologies.append(topo)
            assert(isinstance(topo, Topology))
        else:
            print ("\n")
            print ("!!!Error, failed to parse '%s' topology info, reason: %s" %
                   (topo_id, status.brief().lower()))
            exit(0)

    for topo in topologies:
        if topo.get_id() != of_topo_id:
            continue
        time.sleep(rundelay)
        print "\n"
        print ("<<< Information for '%s' network topology:") % topo.get_id()
        print "\n".strip()

        flows_cnt = 0
        sids = topo.get_switch_ids()
        for sid in sids:
            flows_cnt += inventory.get_openflow_node_flows_cnt(sid)

        print ("        Number of flows              : %s" %
               flows_cnt)
        print ("        Number of switches           : %s" %
               topo.get_switches_cnt())
        print ("        Number of inter-switch links : %s" %
               topo.get_inter_switch_links_cnt())
        print ("        Number of hosts              : %s" %
               topo.get_hosts_cnt())

        time.sleep(rundelay)
        print "\n"
        print ("<<< OpenFlow switches in '%s' topology") % topo.get_id()
        s1 = 'IP Address'
        s2 = 'OpenFlow Id'
        sym = '-'
        print "\n".strip()
        print "        {0:<15}  {1:<30}".format(s1, s2)
        print "        {0:<15}  {1:<30}".format(sym * 15, sym * 30)
        switch_ids = topo.get_switch_ids()
        for switch_id in switch_ids:
            inv_node = inventory.get_openflow_node(switch_id)
            addr = inv_node.get_ip_address()
            node_id = inv_node.get_id()
            print "        {0:<15}  {1:<30}".format(addr, node_id)

        switches = topo.get_switches()
        for switch in switches:
            assert(isinstance(switch, Node))
            print "\n".strip()
            time.sleep(rundelay)
            print ("<<< Neighborhood information for '%s' switch ports" %
                   switch.get_id())
            pnums = switch.get_port_numbers()
            for pnum in pnums:
                if pnum == 'LOCAL':
                    continue
                print "\n".strip()
                print "        Port '%s'" % pnum
                peer_list = topo.get_peer_list_for_node_port_(switch, pnum)
                if len(peer_list):
                    for item in peer_list:
                        assert(isinstance(item, Node))
                        if(item.is_switch()):
                            print ("            Device Type : %s" %
                                   "switch")
                            print ("            OpenFlow Id : %s" %
                                   item.get_openflow_id())
                        elif (item.is_host()):
                            print ("            Device Type : %s" %
                                   "host")
                            mac_addr = item.get_mac_address()
                            print ("            MAC Address : %s" %
                                   mac_addr)
                            ip_addr = item.get_ip_address_for_mac(mac_addr)
                            print ("            IP Address  : %s" %
                                   ip_addr)
                else:
                    print "            None"

    time.sleep(rundelay)

    print ("\n")
    print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print (">>> Demo End")
    print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

if __name__ == "__main__":
    of_demo_27()
