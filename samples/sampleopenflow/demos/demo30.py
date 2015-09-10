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

from websocket import create_connection
from pybvc.common.status import STATUS
from pybvc.common.utils import load_dict_from_file
from pybvc.controller.controller import Controller
from pybvc.controller.notification import InventoryChangeNotification


def of_demo_30():

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

    description = (
        "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n"
        " This demo illustrates how to use Controller's notification\n"
        " subscription service for tracing dynamic changes in the\n"
        " the Controller's inventory data store.\n"
        "\n"
        " It is implied that core network services (OpenFlow, NETCONF)\n"
        " are functioning on the Controller.\n"
        "\n"
        " This script creates an event listener on the Controller and\n"
        " establishes permanent connection to the events notification\n"
        " stream. Once a data change event in the inventory data store\n"
        " (such as add/remove node or flow entry) is detected\n"
        " it will be reported to the screen.\n"
        "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<\n"
        )

    print "\n".strip()
    print description
    print "\n".strip()
    time.sleep(rundelay)

    print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    print ("<<< Demo 30 Start")
    print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    ctrl = Controller(ctrlIpAddr, ctrlPortNum, ctrlUname, ctrlPswd)
    print "\n".strip()
    print ("<<< 'Controller': %s" % (ctrlIpAddr))
    time.sleep(rundelay)

    # Data store for the changes
    # Can be one of:
    # - CONFIGURATION: Logical data store representing configuration
    #                  state of the system and it's components.
    # - OPERATIONAL:   Logical data store representing operational
    #                  state of the system and it's components
    datastore = "OPERATIONAL"

    # Scope of the data changes
    # Can be one of:
    # - BASE:    Represents only a direct change of the node, such as
    #            replacement, addition or deletion of the node.
    # - ONE:     Represent a change (addition, replacement, deletion)
    #            of the node or one of its direct children.
    #            This scope is a superset of BASE.
    # - SUBTREE: Represents a change of the node or any of its child
    #            nodes, direct and nested.
    #            This scope is superset of ONE and BASE.
    scope = "SUBTREE"

    # Path to the inventory data store in the YANG data tree
    path = ctrl.get_inventory_nodes_yang_schema_path()

    # Create listener on the Controller (if it does already exist Controller
    # just returns the stream name to subscribe to)
    result = ctrl.create_data_change_event_subscription(datastore, scope, path)
    status = result.get_status()
    if not status.eq(STATUS.OK):
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.detailed())
        exit(1)

    stream_name = result.get_data()

    # Subscribe to the stream
    result = ctrl.subscribe_to_stream(stream_name)
    status = result.get_status()
    if not status.eq(STATUS.OK):
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.detailed())
        exit(1)

    print "\n".strip()
    print " Successfully subscribed for data change notifications"
    print " Stream location:"
    stream_location = result.get_data()
    print "    %s" % stream_location
    print "\n".strip()
    print " Listening ... (CTRL-C to exit)"
    print "\n".strip()

    # Connect to the notification stream on the Controller
    # and start listening for the data change notifications
    # (report only events that we are really interested in)
    websock = create_connection(stream_location)
    try:
        while True:
            notification = websock.recv()
            icn = InventoryChangeNotification(notification)

            timestamp = icn.get_time()

            l = icn.nodes_added()
            if l and len(l):
                for i in l:
                    print " [%s] added node: %s" % (timestamp, i)

            l = icn.nodes_removed()
            if l and len(l):
                for i in l:
                    print " [%s] removed node: %s" % (timestamp, i)

            l = icn.flows_added()
            if l and len(l):
                for i in l:
                    print " [%s] added flow entry: %s" % (timestamp,
                                                          i.to_string())

            l = icn.flows_removed()
            if l and len(l):
                for i in l:
                    print " [%s] removed flow entry: %s" % (timestamp,
                                                            i.to_string())
    except(KeyboardInterrupt):
        print "Interrupted from keyboard, exit\n"

    websock.close()

    print ("\n")
    print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print (">>> Demo End")
    print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

if __name__ == "__main__":
    of_demo_30()
