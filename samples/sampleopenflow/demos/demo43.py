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
                                        Match,
                                        Instruction,
                                        SetQueueAction,
                                        OutputAction)
from pybvc.common.utils import load_dict_from_file
from pybvc.common.status import STATUS
from pybvc.common.constants import ETH_TYPE_IPv4


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


def of_demo_43():
    f = "cfg.yml"
    d = {}
    if(load_dict_from_file(f, d) is False):
        print("Config file '%s' read error: " % f)
        exit(0)

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
    print ("<<< Demo 43 Start")
    print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    ctrl = Controller(ctrlIpAddr, ctrlPortNum, ctrlUname, ctrlPswd)
    ofswitch = OFSwitch(ctrl, nodeName)

    print ("<<< 'Controller': %s, 'OpenFlow' switch: '%s'" %
           (ctrlIpAddr, nodeName))

    first_flow_id = 110
    # ---------------------------------------------------
    # First flow entry
    # ---------------------------------------------------
    table_id = 0
    flow_id = first_flow_id
    flow_name = "Set Queue example"
    priority = 1000
    cookie = 1400

    match_in_port = 109
    match_eth_type = ETH_TYPE_IPv4
    match_ipv4_dst_addr = "10.0.0.0/8"

    act_queue_id = 7
    act_out_port = 112

    print "\n"
    print ("<<< Set OpenFlow flow on the Controller")
    print ("        Match:  Input Port (%s)\n"
           "                Ethernet Type (%s)\n"
           "                IPv4 Destination Address (%s)" %
           (match_in_port,
            hex(match_eth_type),
            match_ipv4_dst_addr))
    print ("        Actions: Set Queue (%s)\n"
           "                 Output (%s)" %
           (act_queue_id, act_out_port))

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
    action = SetQueueAction(action_order)
    action.set_gueue_id(act_queue_id)
    instruction.add_apply_action(action)

    action_order += 1
    action = OutputAction(action_order)
    action.set_outport(act_out_port)
    instruction.add_apply_action(action)

    flow_entry1.add_instruction(instruction)

    # Match Fields for the Flow Entry
    match = Match()

    match.set_in_port(match_in_port)
    match.set_eth_type(match_eth_type)
    match.set_ipv4_dst(match_ipv4_dst_addr)

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
        delete_flows(ofswitch, table_id, range(first_flow_id, flow_id+1))
        exit(0)

    print "\n".strip()
    print ("<<< Get Queues Statistics for Port '%s'") % act_out_port
    time.sleep(rundelay)

    queues = []
    result = ofswitch.get_port_queues_stats(act_out_port, decode_obj=True)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        queues = result.get_data()
    elif(status.eq(STATUS.DATA_NOT_FOUND)):
        pass
    else:
        print ("\n")
        print ("!!!Error, failed to get queue statistics for port '%s" %
               act_out_port)
        print ("!!!Demo terminated, reason: %s" % status.detailed())
        delete_flows(ofswitch, table_id, range(first_flow_id, flow_id+1))
        exit(0)

    print "\n".strip()
    s = "Port '{} - Queues Statistics'".format(act_out_port)
    print " %s\n" % s

    if queues:
        for queue in sorted(queues, key=lambda q: q.queue_id()):
            print "   Queue '{}'".format(queue.queue_id())
            print "\n".strip()
            print "     Tx Packets : {}".format(queue.tx_pkts())
            print "     Tx Bytes   : {}".format(queue.tx_bytes())
            print "     Tx Errors  : {}".format(queue.tx_errs())
            print "     Duration   : {}s".format(queue.time_alive())
            print "\n".strip()
    else:
        print " None"

    print "\n".strip()
    print ("<<< Get Queue '%s' Statistics for Port '%s'" %
           (act_queue_id, act_out_port))
    time.sleep(rundelay)
    queue = None
    result = ofswitch.get_port_queue_stats(port_num=act_out_port,
                                           queue_id=act_queue_id,
                                           decode_obj=True)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        queue = result.get_data()
    elif(status.eq(STATUS.DATA_NOT_FOUND)):
        pass
    else:
        print ("\n")
        print ("!!!Error, failed to get port '%s' queue '%s' statistics " %
               act_out_port, act_queue_id)
        print ("!!!Demo terminated, reason: %s" % status.detailed())
        delete_flows(ofswitch, table_id, range(first_flow_id, flow_id+1))
        exit(0)

    print "\n".strip()
    s = "Port '{}' - Queue '{}' Statistics".format(act_out_port, act_queue_id)
    print " %s\n" % s

    if queue:
        print "     Tx Packets : {}".format(queue.tx_pkts())
        print "     Tx Bytes   : {}".format(queue.tx_bytes())
        print "     Tx Errors  : {}".format(queue.tx_errs())
        print "     Duration   : {}s".format(queue.time_alive())
        print "\n".strip()
    else:
        print " None"

    print ("\n")
    print ("<<< Delete flows from the Controller's cache "
           "and from the table '%s' on the '%s' node" % (table_id, nodeName))
    time.sleep(rundelay)
    delete_flows(ofswitch, table_id, range(first_flow_id, flow_id+1))

    print ("\n")
    print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print (">>> Demo End")
    print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

if __name__ == "__main__":
    of_demo_43()
