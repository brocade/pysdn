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


from pybvc.controller.controller import Controller
from pybvc.openflowdev.ofswitch import (OFSwitch,
                                        FlowEntry,
                                        Instruction,
                                        Match,
                                        DropAction,
                                        OutputAction,
                                        PushVlanHeaderAction,
                                        SetFieldAction,
                                        PopVlanHeaderAction)
from pybvc.common.status import STATUS
from pybvc.common.utils import load_dict_from_file
from pybvc.common.constants import (ETH_TYPE_ARP,
                                    ETH_TYPE_IPv4,
                                    ETH_TYPE_QINQ,
                                    ETH_TYPE_DOT1Q)


def of_demo_26():
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
    print ("<<< Demo 26 Start")
    print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    ctrl = Controller(ctrlIpAddr, ctrlPortNum, ctrlUname, ctrlPswd)
    ofswitch = OFSwitch(ctrl, nodeName)

    print ("<<< 'Controller': %s, 'OpenFlow' switch: '%s'" %
           (ctrlIpAddr, nodeName))

    flow_table_id = 0
    flow_id_base = 12
    flow_id = flow_id_base
    flowEntries = []

    # Sample flow entry
    flow_entry = FlowEntry()
    flow_entry.set_flow_cookie(6001)
    flow_entry.set_flow_table_id(flow_table_id)
    flow_entry.set_flow_id(flow_id)
    flow_id += 1
    flow_entry.set_flow_idle_timeout(12000)
    flow_entry.set_flow_hard_timeout(12000)
    flow_entry.set_flow_priority(1000)

    instruction = Instruction(instruction_order=0)
    action = DropAction(order=0)
    instruction.add_apply_action(action)
    flow_entry.add_instruction(instruction)

    match = Match()
    match.set_eth_type(ETH_TYPE_ARP)
    match.set_eth_src("00:11:22:33:44:55")
    match.set_eth_dst("aa:bb:cc:dd:ee:ff")
    flow_entry.add_match(match)

    flowEntries.append(flow_entry)

    # Sample flow entry
    flow_entry = FlowEntry()
    flow_entry.set_flow_cookie(7001)
    flow_entry.set_flow_table_id(flow_table_id)
    flow_entry.set_flow_id(flow_id)
    flow_id += 1
    flow_entry.set_flow_idle_timeout(2400)
    flow_entry.set_flow_hard_timeout(2400)
    flow_entry.set_flow_priority(2000)

    instruction = Instruction(instruction_order=0)
    action = OutputAction(order=0, port="CONTROLLER", max_len=60)
    instruction.add_apply_action(action)
    flow_entry.add_instruction(instruction)

    match = Match()
    match.set_eth_type(ETH_TYPE_IPv4)
    match.set_ipv4_src("1.2.3.4/32")
    match.set_ipv4_dst("192.168.1.11/32")
    flow_entry.add_match(match)

    flowEntries.append(flow_entry)

    # Sample flow entry
    flow_entry = FlowEntry()
    flow_entry.set_flow_cookie(800)
    flow_entry.set_flow_table_id(flow_table_id)
    flow_entry.set_flow_id(flow_id)
    flow_id += 1
    flow_entry.set_flow_hard_timeout(1800)
    flow_entry.set_flow_idle_timeout(1800)
    flow_entry.set_flow_priority(3000)

    instruction = Instruction(instruction_order=0)
    action = OutputAction(order=0, port=5)
    instruction.add_apply_action(action)
    action = OutputAction(order=1, port=6)
    instruction.add_apply_action(action)
    action = OutputAction(order=2, port=7)
    instruction.add_apply_action(action)

    flow_entry.add_instruction(instruction)

    match = Match()
    match.set_in_port(1)

    flow_entry.add_match(match)

    flowEntries.append(flow_entry)

    # Sample flow entry
    flow_entry = FlowEntry()
    flow_entry.set_flow_cookie(1234)
    flow_entry.set_flow_table_id(flow_table_id)
    flow_entry.set_flow_id(flow_id)
    flow_id += 1
    flow_entry.set_flow_hard_timeout(0)
    flow_entry.set_flow_idle_timeout(0)
    flow_entry.set_flow_priority(4000)

    instruction = Instruction(instruction_order=0)

    action = PushVlanHeaderAction(order=0)
    action.set_eth_type(ETH_TYPE_QINQ)
    instruction.add_apply_action(action)

    action = SetFieldAction(order=1)
    action.set_vlan_id(100)
    instruction.add_apply_action(action)

    action = PushVlanHeaderAction(order=2)
    action.set_eth_type(ETH_TYPE_DOT1Q)
    instruction.add_apply_action(action)

    action = SetFieldAction(order=3)
    action.set_vlan_id(998)
    instruction.add_apply_action(action)

    action = OutputAction(order=4, port=111)
    instruction.add_apply_action(action)

    flow_entry.add_instruction(instruction)

    match = Match()
    match.set_eth_type(ETH_TYPE_ARP)
    match.set_vlan_id(998)
    match.set_in_port(in_port=110)

    flow_entry.add_match(match)

    flowEntries.append(flow_entry)

    # Sample flow entry
    flow_entry = FlowEntry()
    flow_entry.set_flow_cookie(1234)
    flow_entry.set_flow_table_id(flow_table_id)
    flow_entry.set_flow_id(flow_id)
    flow_id += 1
    flow_entry.set_flow_hard_timeout(0)
    flow_entry.set_flow_idle_timeout(0)
    flow_entry.set_flow_priority(4000)

    instruction = Instruction(instruction_order=0)

    action = PushVlanHeaderAction(order=0)
    action.set_eth_type(ETH_TYPE_QINQ)
    instruction.add_apply_action(action)

    action = SetFieldAction(order=1)
    action.set_vlan_id(100)
    instruction.add_apply_action(action)

    action = PushVlanHeaderAction(order=2)
    action.set_eth_type(ETH_TYPE_DOT1Q)
    instruction.add_apply_action(action)

    action = SetFieldAction(order=3)
    action.set_vlan_id(998)
    instruction.add_apply_action(action)

    action = OutputAction(order=4, port=111)
    instruction.add_apply_action(action)

    flow_entry.add_instruction(instruction)

    match = Match()
    match.set_eth_type(ETH_TYPE_IPv4)
    match.set_vlan_id(998)
    match.set_in_port(in_port=110)

    flow_entry.add_match(match)

    flowEntries.append(flow_entry)

    # Sample flow entry
    flow_entry = FlowEntry()
    flow_entry.set_flow_cookie(1234)
    flow_entry.set_flow_table_id(flow_table_id)
    flow_entry.set_flow_id(flow_id)
    flow_id += 1
    flow_entry.set_flow_hard_timeout(0)
    flow_entry.set_flow_idle_timeout(0)
    flow_entry.set_flow_priority(4000)

    instruction = Instruction(instruction_order=0)

    action = PopVlanHeaderAction(order=0)
    instruction.add_apply_action(action)

    action = OutputAction(order=1, port=110)
    instruction.add_apply_action(action)

    flow_entry.add_instruction(instruction)

    match = Match()
    match.set_eth_type(ETH_TYPE_ARP)
    match.set_vlan_id(100)
    match.set_in_port(111)

    flow_entry.add_match(match)

    flowEntries.append(flow_entry)

    # Sample flow entry
    flow_entry = FlowEntry()
    flow_entry.set_flow_cookie(1234)
    flow_entry.set_flow_table_id(flow_table_id)
    flow_entry.set_flow_id(flow_id)
    flow_id += 1
    flow_entry.set_flow_hard_timeout(0)
    flow_entry.set_flow_idle_timeout(0)
    flow_entry.set_flow_priority(4000)

    instruction = Instruction(instruction_order=0)

    action = PopVlanHeaderAction(order=0)
    instruction.add_apply_action(action)

    action = OutputAction(order=1, port=110)
    instruction.add_apply_action(action)

    flow_entry.add_instruction(instruction)

    match = Match()
    match.set_eth_type(ETH_TYPE_IPv4)
    match.set_vlan_id(100)
    match.set_in_port(111)

    flow_entry.add_match(match)

    flowEntries.append(flow_entry)

    print ("\n")
    print ("<<< Remove configured flows from the Controller")
    ofswitch.delete_flows(flow_table_id)

    print ("\n")
    print ("<<< Set OpenFlow flows on the Controller")

    print ("\n")
    print ("<<< Flows to be configured:")

    flowEntries = sorted(flowEntries, key=lambda fe: fe.get_flow_priority())
    for fe in flowEntries:
        print (" %s" % fe.to_ofp_oxm_syntax())

    time.sleep(rundelay)
    success = True
    for fe in flowEntries:
        result = ofswitch.add_modify_flow(fe)
        status = result.get_status()
        if(status.eq(STATUS.OK)):
            pass
        else:
            success = False
            print ("\n")
            print ("!!!Demo terminated, failed to add flow:\n '%s'" %
                   fe.to_ofp_oxm_syntax())
            print (" Failure reason: %s" % status.detailed())

    if success:
        print "\n"
        print ("<<< Flows successfully added to the Controller")
    else:
        print "\n"
        print ("<<< Removing all flows from the Controller")
        ofswitch.delete_flows(flow_table_id)
        exit(0)

    print ("\n")
    print ("<<< Get configured flows from the Controller")
    time.sleep(rundelay)

    print ("\n")
    print ("<<< Configured flows:")
    result = ofswitch.get_configured_FlowEntries(flow_table_id=0)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        data = result.get_data()
        flowEntries = sorted(data, key=lambda fe: fe.get_flow_priority())
        for fe in flowEntries:
            print " %s" % fe.to_ofp_oxm_syntax()
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief().lower())
        exit(0)

    print ("\n")
    print ("<<< Get configured flows by IDs from the Controller:")
    time.sleep(rundelay)
    for i in range(flow_id_base, flow_id):
        result = ofswitch.get_configured_FlowEntry(flow_table_id, i)
        status = result.get_status()
        if(status.eq(STATUS.OK)):
            print (" -- Flow id '%s'" % i)
            fe = result.get_data()
            print " %s" % fe.to_ofp_oxm_syntax()
        else:
            print ("\n")
            print ("!!!Demo terminated, reason: %s" % status.brief().lower())
            print ("<<< Removing all flows from the Controller")
            ofswitch.delete_flows(flow_table_id)
            exit(0)

    time.sleep(rundelay)

    print ("\n")
    print ("<<< Remove configured flows from the Controller")
    ofswitch.delete_flows(flow_table_id)

    time.sleep(rundelay)

    print ("\n")
    print ("<<< Get configured flows from the Controller")
    result = ofswitch.get_configured_FlowEntries(flow_table_id=0)
    status = result.get_status()
    if(status.eq(STATUS.DATA_NOT_FOUND)):
        print ("\n")
        print "<<< No configured flows"
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.detailed())
        exit(0)

    print ("\n")
    print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print (">>> Demo End")
    print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

if __name__ == "__main__":
    of_demo_26()
