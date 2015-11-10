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

from pysdn.controller.controller import Controller
from pysdn.openflowdev.ofswitch import (OFSwitch,
                                        FlowEntry,
                                        Instruction,
                                        OutputAction,
                                        PushMplsHeaderAction,
                                        SetFieldAction,
                                        Match)
from pysdn.common.status import STATUS
from pysdn.common.utils import load_dict_from_file
from pysdn.common.constants import (ETH_TYPE_IPv4,
                                    ETH_TYPE_MPLS_UCAST)


def of_demo_22():

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
    print ("<<< Demo 22 Start")
    print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    ctrl = Controller(ctrlIpAddr, ctrlPortNum, ctrlUname, ctrlPswd)
    ofswitch = OFSwitch(ctrl, nodeName)

    # --- Flow Match: Ethernet Type
    #                 Input Port
    #                 IPv4 Destination Address
    eth_type = ETH_TYPE_IPv4
    in_port = 13
    ipv4_dst = "10.12.5.4/32"

    # --- Flow Actions: Push MPLS
    #                   Set Field
    #                   Output
    push_ether_type = ETH_TYPE_MPLS_UCAST
    mpls_label = 27
    output_port = 14

    print ("<<< 'Controller': %s, 'OpenFlow' switch: '%s'" %
           (ctrlIpAddr, nodeName))

    print "\n"
    print ("<<< Set OpenFlow flow on the Controller")
    print ("        Match:  Ethernet Type (%s)\n"
           "                Input Port (%s)\n"
           "                IPv4 Destination Address (%s)" %
           (hex(eth_type), in_port, ipv4_dst))
    print ("        Action: Push MPLS Header (Ethernet Type %s)\n"
           "                Set Field (MPLS label %s)\n"
           "                Output (Physical Port number %s)" %
           (hex(push_ether_type), mpls_label, output_port))

    time.sleep(rundelay)

    flow_entry = FlowEntry()
    table_id = 0
    flow_id = 28
    flow_entry.set_flow_table_id(table_id)
    flow_entry.set_flow_name(flow_name="Push MPLS Label")
    flow_entry.set_flow_id(flow_id)
    flow_entry.set_flow_hard_timeout(hard_timeout=0)
    flow_entry.set_flow_idle_timeout(idle_timeout=0)
    flow_entry.set_flow_priority(flow_priority=1021)
    flow_entry.set_flow_cookie(cookie=654)
    flow_entry.set_flow_cookie_mask(cookie_mask=255)

    # --- Instruction: 'Apply-actions'
    #     Actions:     'Push MPLS Header'
    #                  'Set Field'
    #                  'Output'
    instruction = Instruction(instruction_order=0)
    action = PushMplsHeaderAction(order=0)
    action.set_eth_type(push_ether_type)
    instruction.add_apply_action(action)
    action = SetFieldAction(order=1)
    action.set_mpls_label(mpls_label)
    instruction.add_apply_action(action)
    action = OutputAction(order=2, port=output_port)
    instruction.add_apply_action(action)
    flow_entry.add_instruction(instruction)

    # --- Match Fields: Ethernet Type
    #                   Input Port
    #                   IPv4 Destination Address
    match = Match()
    match.set_eth_type(eth_type)
    match.set_in_port(in_port)
    match.set_ipv4_dst(ipv4_dst)
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
        print ("!!!Demo terminated, reason: %s" % status.detailed())
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
    of_demo_22()
