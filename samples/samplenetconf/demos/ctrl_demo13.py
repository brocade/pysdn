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
from pybvc.common.status import STATUS
from pybvc.controller.inventory import NetconfCapableNode
from pybvc.common.utils import load_dict_from_file


def nc_demo_13():

    f = "cfg1.yml"
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

    netconf_ids = []
    netconf_nodes = []

    print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    print ("<<< Demo Start")
    print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    print "\n"
    ctrl = Controller(ctrlIpAddr, ctrlPortNum, ctrlUname, ctrlPswd)
    print ("<<< Controller '%s:%s'" % (ctrlIpAddr, ctrlPortNum))
    time.sleep(rundelay)

    print "\n"
    print ("<<< Get NETCONF Inventory Information")
    time.sleep(rundelay)

    result = ctrl.get_netconf_nodes_in_config()
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        netconf_ids = result.get_data()
    else:
        print ("\n")
        print ("!!!Demo terminated, "
               "failed to get list of NETCONF devices, "
               "reason: %s" % status.brief())
        exit(0)

    print "\n"
    print ("<<< NETCONF devices")
    print "\n".strip()
    for node_id in netconf_ids:
        print "         %s" % node_id

    for node_id in netconf_ids:
        result = ctrl.build_netconf_node_inventory_object(node_id)
        status = result.get_status()
        if(status.eq(STATUS.OK)):
            node = result.get_data()
            assert(isinstance(node, NetconfCapableNode))
            netconf_nodes.append(node)
        else:
            print ("\n")
            print ("!!!Demo terminated, "
                   "failed to build object for NETCONF device '%s', "
                   "reason: %s" % (node_id, status.brief()))
            exit(0)

    for node in netconf_nodes:
        time.sleep(rundelay)
        print "\n".strip()
        print "<<< Information for '{}' device".format(node.get_id())
        print "\n".strip()
        print "         Device Name       : {}".format(node.get_id())
        print "         Connection status : {}".format(node.get_conn_status())
        print "\n".strip()
        print "         Initial Capabilities"
        print "         {}".format('-' * 60)
        clist = node.get_initial_capabilities()
        for item in clist:
            print "         {}".format(item)

    print ("\n")
    print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print (">>> Demo End")
    print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")


if __name__ == "__main__":
    nc_demo_13()
