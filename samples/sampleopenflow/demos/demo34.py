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

import json
import time

from pysdn.controller.controller import Controller
from pysdn.openflowdev.ofswitch import (OFSwitch,
                                        FlowEntry,
                                        Match,
                                        Instruction,
                                        GroupAction,
                                        GroupEntry,
                                        GroupBucket,
                                        OutputAction)
from pysdn.common.utils import load_dict_from_file
from pysdn.common.status import STATUS
from pysdn.common.constants import (OFPGT_SELECT, ETH_TYPE_IPv4)


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


def delete_groups(ofswitch, group_ids):
    for group_id in group_ids:
        result = ofswitch.delete_group(group_id)
        status = result.get_status()
        if(status.eq(STATUS.OK)):
            print ("<<< Group '%s' successfully removed from the Controller" %
                   group_id)
        else:
            print ("!!!Group '%s' removal error, reason: %s" %
                   (group_id, status.brief()))


def print_groups(lcfg, loper):
    q = 10  # number of list items to be in a single chunk (output string)
    print "\n".strip()
    s = 'Configured Groups IDs'
    if lcfg:
        chunks = [lcfg[x:x + q] for x in xrange(0, len(lcfg), q)]
        print "        %s  :" % s,
        for i in range(0, len(chunks)):
            n = 0 if i == 0 else len(s) + 18
            print "%s%s" % (" " * n, ", ".join(map(str, chunks[i])))
    else:
        print "        %s  : %s" % (s, "none")

    s = 'Operational Groups IDs'
    if loper:
        chunks = [loper[x:x + q] for x in xrange(0, len(loper), q)]
        print "        %s :" % s,
        for i in range(0, len(chunks)):
            n = 0 if i == 0 else len(s) + 18
            print "%s%s" % (" " * n, ", ".join(map(str, chunks[i])))
    else:
        print "        %s : %s" % (s, "none")


def of_demo_34():

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
    print ("<<< Demo 34 Start")
    print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    ctrl = Controller(ctrlIpAddr, ctrlPortNum, ctrlUname, ctrlPswd)
    ofswitch = OFSwitch(ctrl, nodeName)

    print "\n".strip()
    print ("<<< 'Controller': %s, 'OpenFlow' switch: '%s'" %
           (ctrlIpAddr, nodeName))

    grp_ids_cfg = []
    grp_ids_oper = []

    print "\n".strip()
    print ("<<< Get OpenFlow Groups Information")
    time.sleep(rundelay)

    result = ofswitch.get_configured_group_ids()
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        grp_ids_cfg = result.get_data()
    elif(status.eq(STATUS.DATA_NOT_FOUND)):
        grp_ids_cfg = []
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.detailed())
        exit(0)

    result = ofswitch.get_operational_group_ids()
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        grp_ids_oper = result.get_data()
    elif(status.eq(STATUS.DATA_NOT_FOUND)):
        grp_ids_oper = []
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.detailed())
        exit(0)

    # Show current state of the Group Table in the Controller's
    # configuration and operational data stores
    print_groups(grp_ids_cfg, grp_ids_oper)

    # Create new group
    group_id = 13
    group_type = OFPGT_SELECT
    group_name = "Example of 'load balancing' group"
    weight1 = 60
    weight2 = 30
    weight3 = 10
    out_port1 = 110
    out_port2 = 111
    out_port3 = 112
    print "\n".strip()
    print ("<<< Create Group")
    print "\n".strip()
    print ("        Group Type : %s\n"
           "        Group ID   : %s\n"
           "        Group Name : \"%s\"" %
           (group_type.strip('group-').upper(),
            group_id, group_name))
    print ("        Buckets    :")
    print ("                     [0] weight : %s" %
           weight1)
    print ("                         actions: Output (%s)" %
           out_port1)
    print ("                     [1] weight : %s" %
           weight2)
    print ("                         actions: Output (%s)" %
           out_port2)
    print ("                     [2] weight : %s" %
           weight3)
    print ("                         actions: Output (%s)" %
           out_port3)
    time.sleep(rundelay)

    # Allocate a placeholder for the group entry
    group_entry = GroupEntry(group_id, group_type)
    group_entry.set_group_name(group_name)

    # Fill in group entry with action buckets
    # ---------
    bucket_id = 0
    bucket1 = GroupBucket(bucket_id)
    bucket1.set_weight(weight1)
    action = OutputAction(order=0, port=out_port1)
    bucket1.add_action(action)
    group_entry.add_bucket(bucket1)

    # ---------
    bucket_id += 1
    bucket2 = GroupBucket(bucket_id)
    bucket2.set_weight(weight2)
    action = OutputAction(order=0, port=out_port2)
    bucket2.add_action(action)
    group_entry.add_bucket(bucket2)

    # ---------
    bucket_id += 1
    bucket3 = GroupBucket(bucket_id)
    bucket3.set_weight(weight3)
    action = OutputAction(order=0, port=out_port3)
    bucket3.add_action(action)
    group_entry.add_bucket(bucket3)

    # Request Controller to create the group
    print "\n".strip()
    print ("<<< Group to create:")
    print group_entry.get_payload()
    time.sleep(rundelay)
    result = ofswitch.add_modify_group(group_entry)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("<<< Group successfully added")
        grp_ids_oper = result.get_data()
    else:
        print ("\n").strip()
        print ("!!!Demo terminated, reason: %s" % status.detailed())
        exit(0)

    print ("\n").strip()
    print ("<<< Get group '%s' configuration status") % group_id
    time.sleep(rundelay)
    result = ofswitch.get_configured_group(group_id)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("Group configuration info:")
        group = result.get_data()
        print json.dumps(group, indent=4)
    else:
        print ("\n").strip()
        print ("!!!Demo terminated, reason: %s" % status.detailed())
        exit(0)

    print ("\n").strip()
    print ("<<< Get group '%s' operational status") % group_id
    time.sleep(rundelay)
    result = ofswitch.get_group_description(group_id)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("Group operational info:")
        group = result.get_data()
        print json.dumps(group, indent=4)
    else:
        print ("\n").strip()
        print ("!!!Error, reason: %s" % status.detailed())

    print ("\n").strip()
    print ("<<< Get group '%s' statistics information") % group_id
    time.sleep(rundelay)
    result = ofswitch.get_group_statistics(group_id)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("Group statistics info:")
        group = result.get_data()
        print json.dumps(group, indent=4)
    else:
        print ("\n").strip()
        print ("!!!Error, reason: %s" % status.detailed())

    print ("\n").strip()
    print ("<<< Get OpenFlow Groups Information")
    time.sleep(rundelay)

    result = ofswitch.get_configured_group_ids()
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        grp_ids_cfg = result.get_data()
    elif(status.eq(STATUS.DATA_NOT_FOUND)):
        grp_ids_cfg = []
    else:
        print ("\n").strip()
        print ("!!!Error, reason: %s" % status.detailed())

    result = ofswitch.get_operational_group_ids()
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        grp_ids_oper = result.get_data()
    elif(status.eq(STATUS.DATA_NOT_FOUND)):
        grp_ids_oper = []
    else:
        print ("\n").strip()
        print ("!!!Error, reason: %s" % status.detailed())

    # Show current state of the Group Table in the Controller's
    # configuration and operational data stores
    print_groups(grp_ids_cfg, grp_ids_oper)

    first_flow_id = 110
    # ---------------------------------------------------
    # First flow entry
    # ---------------------------------------------------
    table_id = 0
    flow_id = first_flow_id
    flow_name = "Group action example"
    priority = 1000
    cookie = 1400

    match_in_port = 109
    match_eth_type = ETH_TYPE_IPv4

    print "\n".strip()
    print ("<<< Set OpenFlow flow on the Controller")
    print ("        Match: Input Port (%s)\n"
           "               Ethernet Type (%s)" %
           (match_in_port, hex(match_eth_type)))
    print ("        Actions: Apply Group (%s)\n" % group_id)

    time.sleep(rundelay)

    # Allocate a placeholder for the Flow Entry
    flow_entry1 = FlowEntry()

    # Generic attributes of the Flow Entry
    flow_entry1.set_flow_table_id(table_id)
    flow_entry1.set_flow_name(flow_name)
    flow_entry1.set_flow_id(flow_id)
    flow_entry1.set_flow_cookie(cookie)
    flow_entry1.set_flow_priority(priority)
    flow_entry1.set_flow_hard_timeout(0)
    flow_entry1.set_flow_idle_timeout(0)

    # Instructions/Actions for the Flow Entry
    instruction = Instruction(instruction_order=0)

    action_order = 0
    action = GroupAction(action_order)
    action.set_group_id(group_id)
    instruction.add_apply_action(action)

    flow_entry1.add_instruction(instruction)

    # Match Fields for the Flow Entry
    match = Match()

    match.set_in_port(match_in_port)
    match.set_eth_type(match_eth_type)

    flow_entry1.add_match(match)

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
        delete_groups(ofswitch, grp_ids_cfg)
        delete_flows(ofswitch, table_id, range(first_flow_id, flow_id + 1))
        exit(0)

    print "\n".strip()
    print ("<<< Remove all flows from the Controller")
    time.sleep(rundelay)
    delete_flows(ofswitch, table_id, range(first_flow_id, flow_id + 1))

    print "\n".strip()
    print ("<<< Remove all groups from the Controller")
    time.sleep(rundelay)
    delete_groups(ofswitch, grp_ids_cfg)

    print ("\n").strip()
    print ("<<< Get OpenFlow Groups Information")
    time.sleep(rundelay)

    result = ofswitch.get_configured_group_ids()
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        grp_ids_cfg = result.get_data()
    elif(status.eq(STATUS.DATA_NOT_FOUND)):
        grp_ids_cfg = []
    else:
        print ("\n").strip()
        print ("!!!Error, reason: %s" % status.detailed())

    result = ofswitch.get_operational_group_ids()
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        grp_ids_oper = result.get_data()
    elif(status.eq(STATUS.DATA_NOT_FOUND)):
        grp_ids_oper = []
    else:
        print ("\n")
        print ("!!!Error, reason: %s" % status.detailed())

    # Show current state of the Group Table in the Controller's
    # configuration and operational data stores
    print_groups(grp_ids_cfg, grp_ids_oper)

    print ("\n").strip()
    print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print (">>> Demo End")
    print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

if __name__ == "__main__":
    of_demo_34()
