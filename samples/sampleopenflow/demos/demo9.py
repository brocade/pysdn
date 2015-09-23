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
import json

from pybvc.controller.controller import Controller
from pybvc.openflowdev.ofswitch import (OFSwitch,
                                        FlowEntry,
                                        Instruction,
                                        OutputAction,
                                        Match)
from pybvc.common.status import STATUS
from pybvc.common.utils import load_dict_from_file
from pybvc.common.constants import (ETH_TYPE_IPv4,
                                    IP_PROTO_TCP,
                                    IP_DSCP_AF12)


def of_demo_9():
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
        nodeName = d['nodeName']
        rundelay = d['rundelay']
    except:
        print ("Failed to get Controller device attributes")
        exit(0)

    print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    print ("<<< Demo 9 Start")
    print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    ctrl = Controller(ctrlIpAddr, ctrlPortNum, ctrlUname, ctrlPswd)
    ofswitch = OFSwitch(ctrl, nodeName)

    # --- Flow Match: Ethernet Source Address
    #                 Ethernet Destination Address
    #                 IPv4 Source Address
    #                 IPv4 Destination Address
    #                 TCP Source Port Number
    #                 TCP Destination Port Number
    #                 IP DSCP
    #                 Input Port
    #     NOTE: Ethernet type MUST be 2048 (0x800) -> IPv4 protocol
    eth_type = ETH_TYPE_IPv4
    eth_src = "00:00:00:11:23:ae"
    eth_dst = "ff:ff:29:01:19:61"
    ipv4_src = "17.1.2.3/8"
    ipv4_dst = "172.168.5.6/16"
    ip_proto = IP_PROTO_TCP
    # Assured Forwarding ('class'=1, 'drop precedence'=2)
    ip_dscp = IP_DSCP_AF12
    tcp_src_port = 25364
    tcp_dst_port = 8080
    input_port = 13

    print ("<<< 'Controller': %s, 'OpenFlow' switch: '%s'" %
           (ctrlIpAddr, nodeName))

    print "\n"
    print ("<<< Set OpenFlow flow on the Controller")
    print ("        Match:  Ethernet Type (%s)\n"
           "                Ethernet Source Address (%s)\n"
           "                Ethernet Destination Address (%s)\n"
           "                IPv4 Source Address (%s)\n"
           "                IPv4 Destination Address (%s)\n"
           "                IP Protocol Number (%s)\n"
           "                IP DSCP (%s)\n"
           "                TCP Source Port Number (%s)\n"
           "                TCP Destination Port Number (%s)\n"
           "                Input Port (%s)" %
           (hex(eth_type), eth_src,
            eth_dst, ipv4_src, ipv4_dst,
            ip_proto, ip_dscp,
            tcp_src_port, tcp_dst_port,
            input_port))
    print ("        Action: Output (NORMAL)")

    time.sleep(rundelay)

    flow_entry = FlowEntry()
    table_id = 0
    flow_entry.set_flow_table_id(table_id)
    flow_id = 16
    flow_entry.set_flow_id(flow_id)
    flow_entry.set_flow_priority(flow_priority=1007)
    flow_entry.set_flow_cookie(cookie=101)
    flow_entry.set_flow_cookie_mask(cookie_mask=255)

    # --- Instruction: 'Apply-actions'
    #     Action:      'Output' NORMAL
    instruction = Instruction(instruction_order=0)
    action = OutputAction(order=0, port="NORMAL")
    instruction.add_apply_action(action)
    flow_entry.add_instruction(instruction)

    # --- Match Fields: Ethernet Type
    #                   Ethernet Source Address
    #                   Ethernet Destination Address
    #                   IPv4 Source Address
    #                   IPv4 Destination Address
    #                   IP Protocol Number
    #                   IP DSCP
    #                   IP ECN
    #                   TCP Source Port Number
    #                   TCP Destination Port Number
    #                   Input Port
    match = Match()
    match.set_eth_type(eth_type)
    match.set_eth_src(eth_src)
    match.set_eth_dst(eth_dst)
    match.set_ipv4_src(ipv4_src)
    match.set_ipv4_dst(ipv4_dst)
    match.set_ip_proto(ip_proto)
    match.set_ip_dscp(ip_dscp)
    match.set_tcp_src(tcp_src_port)
    match.set_tcp_dst(tcp_dst_port)
    match.set_in_port(input_port)
    flow_entry.add_match(match)

    print ("\n")
    print ("<<< Flow to send:")
    print flow_entry.get_payload()
    time.sleep(rundelay)
    result = ofswitch.add_modify_flow(flow_entry)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("<<< Flow successfully added to the Controller")
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief().lower())
        exit(0)

    print ("\n")
    print ("<<< Get configured flow from the Controller")
    time.sleep(rundelay)
    result = ofswitch.get_configured_flow(table_id, flow_id)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("<<< Flow successfully read from the Controller")
        print ("Flow info:")
        flow = result.get_data()
        print json.dumps(flow, indent=4)
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief().lower())
        exit(0)

    print ("\n")
    print ("<<< Delete flow with id of '%s' from the Controller's cache "
           "and from the table '%s' on the '%s' node" %
           (flow_id, table_id, nodeName))
    time.sleep(rundelay)
    result = ofswitch.delete_flow(flow_entry.get_flow_table_id(),
                                  flow_entry.get_flow_id())
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("<<< Flow successfully removed from the Controller")
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief().lower())
        exit(0)

    print ("\n")
    print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print (">>> Demo End")
    print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

if __name__ == "__main__":
    of_demo_9()
