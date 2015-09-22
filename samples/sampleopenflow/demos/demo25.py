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
                                        PushVlanHeaderAction,
                                        PopVlanHeaderAction,
                                        SetFieldAction,
                                        OutputAction,
                                        Match)
from pybvc.common.status import STATUS
from pybvc.common.utils import load_dict_from_file
from pybvc.common.constants import (ETH_TYPE_STAG,
                                    ETH_TYPE_CTAG,
                                    ETH_TYPE_ARP,
                                    ETH_TYPE_IPv4)


def delete_flows(ofswitch, table_id, flow_ids):
    for flow_id in flow_ids:
        result = ofswitch.delete_flow(table_id, flow_id)
        status = result.get_status()
        if(status.eq(STATUS.OK)):
            print ("<<< Flow with id of '%s' successfully removed "
                   "from the Controller" % flow_id)
        else:
            print ("!!!Flow '%s' removal error, reason: %s" %
                   (flow_id, status.brief()))


def of_demo_25():
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
    print ("<<< Demo 25 Start")
    print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    ctrl = Controller(ctrlIpAddr, ctrlPortNum, ctrlUname, ctrlPswd)
    ofswitch = OFSwitch(ctrl, nodeName)

    table_id = 0
    priority = 500
    cookie = 1000
    cookie_mask = 255
    customer_port = 110
    provider_port = 111
    qinq_eth_type = ETH_TYPE_STAG   # 802.1ad (QinQ) VLAN tagged frame
    dot1q_eth_type = ETH_TYPE_CTAG  # 802.1q VLAN tagged frame
    arp_eth_type = ETH_TYPE_ARP
    ip_eth_type = ETH_TYPE_IPv4
    provider_vlan_id = 100          # Provider VLAN
    customer_vlan_id = 998          # Customer VLAN
    first_flow_id = 31

    print ("<<< 'Controller': %s, 'OpenFlow' switch: '%s'" %
           (ctrlIpAddr, nodeName))

    # ---------------------------------------------------
    # First flow entry
    # ---------------------------------------------------
    print "\n"
    print ("<<< Set OpenFlow flow on the Controller")
    print ("        Match:  Ethernet Type (%s)\n"
           "                VLAN ID (%s)\n"
           "                Input Port (%s)" %
           (hex(arp_eth_type), customer_vlan_id, customer_port))
    print ("        Action: Push VLAN (Ethernet Type %s)\n"
           "                Set Field (VLAN ID %s)\n"
           "                Push VLAN (Ethernet Type %s)\n"
           "                Set Field (VLAN ID %s)\n"
           "                Output (Physical Port number %s)" %
           (hex(qinq_eth_type), provider_vlan_id,
            hex(dot1q_eth_type), customer_vlan_id,
            provider_port))

    time.sleep(rundelay)

    flow_id = first_flow_id
    flow_entry1 = FlowEntry()
    flow_entry1.set_flow_table_id(table_id)
    fname = "[MLX1-A] Test flow (match:inport=110,arp;" + \
            "actions:push-QINQ-tag,mod_vlan=100," + \
            "push-DOT1Q-tag,mod_vlan=998,output:111)"
    flow_entry1.set_flow_name(flow_name=fname)
    flow_entry1.set_flow_id(flow_id)
    flow_entry1.set_flow_hard_timeout(hard_timeout=600)
    flow_entry1.set_flow_idle_timeout(idle_timeout=300)
    flow_entry1.set_flow_priority(priority)
    flow_entry1.set_flow_cookie(cookie)
    flow_entry1.set_flow_cookie_mask(cookie_mask)

    instruction = Instruction(instruction_order=0)

    action_order = 0
    action = PushVlanHeaderAction(action_order)
    action.set_eth_type(qinq_eth_type)
    instruction.add_apply_action(action)

    action_order += 1
    action = SetFieldAction(action_order)
    action.set_vlan_id(provider_vlan_id)
    instruction.add_apply_action(action)

    action_order += 1
    action = PushVlanHeaderAction(action_order)
    action.set_eth_type(dot1q_eth_type)
    instruction.add_apply_action(action)

    action_order += 1
    action = SetFieldAction(action_order)
    action.set_vlan_id(customer_vlan_id)
    instruction.add_apply_action(action)

    action_order += 1
    action = OutputAction(action_order, provider_port)
    instruction.add_apply_action(action)

    flow_entry1.add_instruction(instruction)

    match = Match()

    match.set_eth_type(arp_eth_type)
    match.set_vlan_id(customer_vlan_id)
    match.set_in_port(in_port=customer_port)

    flow_entry1.add_match(match)

    print ("\n")
    print ("<<< Flow to send:")
    print flow_entry1.get_payload()
    time.sleep(rundelay)
    result = ofswitch.add_modify_flow(flow_entry1)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("<<< Flow successfully added to the Controller")
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.detailed())
        delete_flows(ofswitch, table_id, range(first_flow_id, flow_id + 1))
        exit(0)

    # ---------------------------------------------------
    # Second flow entry
    # ---------------------------------------------------
    print "\n"
    print ("<<< Set OpenFlow flow on the Controller")
    print ("        Match:  Ethernet Type (%s)\n"
           "                VLAN ID (%s)\n"
           "                Input Port (%s)" %
           (hex(ip_eth_type), customer_vlan_id, customer_port))
    print ("        Action: Push VLAN (Ethernet Type %s)\n"
           "                Set Field (VLAN ID %s)\n"
           "                Push VLAN (Ethernet Type %s)\n"
           "                Set Field (VLAN ID %s)\n"
           "                Output (Physical Port number %s)" %
           (hex(qinq_eth_type), provider_vlan_id,
            hex(dot1q_eth_type), customer_vlan_id,
            provider_port))

    time.sleep(rundelay)

    flow_id += 1
    flow_entry2 = FlowEntry()
    flow_entry2.set_flow_table_id(table_id)
    fname = "[MLX1-A] Test flow (match:inport=110,ip;" + \
            "actions:push-QINQ-tag,mod_vlan=100,output:111)"
    flow_entry2.set_flow_name(flow_name=fname)
    flow_entry2.set_flow_id(flow_id)
    flow_entry2.set_flow_hard_timeout(hard_timeout=600)
    flow_entry2.set_flow_idle_timeout(idle_timeout=300)
    flow_entry2.set_flow_priority(priority)
    flow_entry2.set_flow_cookie(cookie)
    flow_entry2.set_flow_cookie_mask(cookie_mask)

    instruction = Instruction(instruction_order=0)

    action_order = 0
    action = PushVlanHeaderAction(action_order)
    action.set_eth_type(qinq_eth_type)
    instruction.add_apply_action(action)

    action_order += 1
    action = SetFieldAction(action_order)
    action.set_vlan_id(provider_vlan_id)
    instruction.add_apply_action(action)

    action_order += 1
    action = PushVlanHeaderAction(action_order)
    action.set_eth_type(dot1q_eth_type)
    instruction.add_apply_action(action)

    action_order += 1
    action = SetFieldAction(action_order)
    action.set_vlan_id(customer_vlan_id)
    instruction.add_apply_action(action)

    action_order += 1
    action = OutputAction(action_order, provider_port)
    instruction.add_apply_action(action)

    flow_entry2.add_instruction(instruction)

    match = Match()

    match.set_eth_type(ip_eth_type)
    match.set_vlan_id(customer_vlan_id)
    match.set_in_port(in_port=customer_port)

    flow_entry2.add_match(match)

    print ("\n")
    print ("<<< Flow to send:")
    print flow_entry2.get_payload()
    time.sleep(rundelay)
    result = ofswitch.add_modify_flow(flow_entry2)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("<<< Flow successfully added to the Controller")
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.detailed())
        delete_flows(ofswitch, table_id, range(first_flow_id, flow_id + 1))
        exit(0)

    # ---------------------------------------------------
    # Third flow entry
    # ---------------------------------------------------
    print "\n"
    print ("<<< Set OpenFlow flow on the Controller")
    print ("        Match:  Ethernet Type (%s)\n"
           "                VLAN ID (%s)\n"
           "                Input Port (%s)" %
           (hex(arp_eth_type), provider_vlan_id, provider_port))
    print ("        Action: Pop VLAN\n"
           "                Output (Physical Port number %s)" %
           (customer_port))

    time.sleep(rundelay)

    flow_id += 1
    flow_entry3 = FlowEntry()
    flow_entry3.set_flow_table_id(table_id)
    fname = "[MLX1-A] Test flow (match:inport=111,arp,vid=100;" + \
            "actions:pop-vlan-tag,output=110)"
    flow_entry3.set_flow_name(flow_name=fname)
    flow_entry3.set_flow_id(flow_id)
    flow_entry3.set_flow_hard_timeout(hard_timeout=600)
    flow_entry3.set_flow_idle_timeout(idle_timeout=300)
    flow_entry3.set_flow_priority(priority)
    flow_entry3.set_flow_cookie(cookie)
    flow_entry3.set_flow_cookie_mask(cookie_mask)

    instruction = Instruction(instruction_order=0)

    action_order = 0
    action = PopVlanHeaderAction(action_order)
    instruction.add_apply_action(action)

    action_order += 1
    action = OutputAction(action_order, customer_port)
    instruction.add_apply_action(action)

    flow_entry3.add_instruction(instruction)

    match = Match()
    match.set_eth_type(arp_eth_type)
    match.set_vlan_id(provider_vlan_id)
    match.set_in_port(provider_port)

    flow_entry3.add_match(match)

    print ("\n")
    print ("<<< Flow to send:")
    print flow_entry3.get_payload()
    time.sleep(rundelay)
    result = ofswitch.add_modify_flow(flow_entry3)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("<<< Flow successfully added to the Controller")
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.detailed())
        delete_flows(ofswitch, table_id, range(first_flow_id, flow_id + 1))
        exit(0)

    # ---------------------------------------------------
    # Fourth flow entry
    # ---------------------------------------------------
    print "\n"
    print ("<<< Set OpenFlow flow on the Controller")
    print ("        Match:  Ethernet Type (%s)\n"
           "                VLAN ID (%s)\n"
           "                Input Port (%s)" %
           (hex(ip_eth_type), provider_vlan_id, provider_port))
    print ("        Action: Pop VLAN\n"
           "                Output (Physical Port number %s)" %
           (customer_port))

    time.sleep(rundelay)

    flow_id += 1
    flow_entry4 = FlowEntry()
    flow_entry4.set_flow_table_id(table_id)
    flow_entry4.set_flow_id(flow_id)
    fname = "[MLX1-A] Test flow (match:inport=111,ip,vid=100;" + \
            "actions:pop-vlan-tag,output=110)"
    flow_entry4.set_flow_name(flow_name=fname)
    flow_entry4.set_flow_hard_timeout(hard_timeout=600)
    flow_entry4.set_flow_idle_timeout(idle_timeout=300)
    flow_entry4.set_flow_priority(priority)
    flow_entry4.set_flow_cookie(cookie)
    flow_entry4.set_flow_cookie_mask(cookie_mask)

    instruction = Instruction(instruction_order=0)

    action_order = 0
    action = PopVlanHeaderAction(action_order)
    instruction.add_apply_action(action)

    action_order += 1
    action = OutputAction(action_order, customer_port)
    instruction.add_apply_action(action)

    flow_entry4.add_instruction(instruction)

    match = Match()
    match.set_eth_type(ip_eth_type)
    match.set_vlan_id(provider_vlan_id)
    match.set_in_port(provider_port)

    flow_entry4.add_match(match)

    print ("\n")
    print ("<<< Flow to send:")
    print flow_entry4.get_payload()
    time.sleep(rundelay)
    result = ofswitch.add_modify_flow(flow_entry4)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("<<< Flow successfully added to the Controller")
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.detailed())
        delete_flows(ofswitch, table_id, range(first_flow_id, flow_id + 1))
        exit(0)

    print ("\n")
    print ("<<< Get configured flows from the Controller")
    time.sleep(rundelay)
    for i in range(first_flow_id, flow_id + 1):
        result = ofswitch.get_configured_flow(table_id, i)
        status = result.get_status()
        if(status.eq(STATUS.OK)):
            print ("<<< Flow '%s' successfully read from the Controller" % i)
            print ("Flow info:")
            flow = result.get_data()
            print json.dumps(flow, indent=4)
        else:
            print ("\n")
            print ("!!!Demo terminated, reason: %s" % status.detailed())
            delete_flows(ofswitch, table_id, range(first_flow_id,
                                                   flow_id + 1))
            exit(0)

    print ("\n")
    print ("<<< Delete flows from the Controller's cache "
           "and from the table '%s' on the '%s' node" % (table_id, nodeName))
    time.sleep(rundelay)
    delete_flows(ofswitch, table_id, range(first_flow_id, flow_id + 1))

    print ("\n")
    print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print (">>> Demo End")
    print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

if __name__ == "__main__":
    of_demo_25()
