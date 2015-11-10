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
from pysdn.common.status import STATUS
from pysdn.controller.netconfnode import NetconfNode
from pysdn.common.utils import load_dict_from_file


def nc_demo_10():

    f = "cfg2.yml"
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
        nodeIpAddr = d['nodeIpAddr']
        nodePortNum = d['nodePortNum']
        nodeUname = d['nodeUname']
        nodePswd = d['nodePswd']
        rundelay = d['rundelay']
    except:
        print ("Failed to get Controller or NETCONF device attributes")
        exit(0)

    print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    print ("<<< Demo Start")
    print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    print ("\n")
    print ("<<< Creating Controller instance")
    ctrl = Controller(ctrlIpAddr, ctrlPortNum, ctrlUname, ctrlPswd)
    print ("'Controller':")
    print ctrl.to_json()

    print "\n"
    print ("<<< Show NETCONF nodes configured on the Controller")
    time.sleep(rundelay)
    result = ctrl.get_netconf_nodes_in_config()
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print "Nodes configured:"
        nlist = result.get_data()
        for item in nlist:
            print "   '{}'".format(item)
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief())
        exit(0)

    node_configured = False
    result = ctrl.check_node_config_status(nodeName)
    status = result.get_status()
    if(status.eq(STATUS.NODE_CONFIGURED)):
        node_configured = True
    elif(status.eq(STATUS.DATA_NOT_FOUND)):
        node_configured = False
    else:
        print ("\n")
        print "Failed to get configuration status for the '%s'" % nodeName
        print ("!!!Demo terminated, reason: %s" % status.detailed())
        exit(0)

    if node_configured:
        print ("\n")
        print ("<<< '%s' is already configured on the Controller" % nodeName)
        print ("Unmounting '%s' from the Controller" % nodeName)
        time.sleep(rundelay)
        result = ctrl.delete_netconf_node(nodename=nodeName)
        status = result.get_status()
        if(status.eq(STATUS.OK)):
            print ("<<< '%s' NETCONF node was successfully removed "
                   "from the Controller" % nodeName)
        else:
            print ("\n")
            print ("!!!Demo terminated, reason: %s" % status.brief())
            exit(0)

    print ("\n")
    time.sleep(rundelay)
    print ("<<< Creating new '%s' NETCONF node" % nodeName)
    node = NetconfNode(ctrl, nodeName, nodeIpAddr, nodePortNum,
                       nodeUname, nodePswd)
    print ("'%s':" % nodeName)
    print node.to_json()

    print ("\n")
    print ("<<< Add '%s' NETCONF node to the Controller" % nodeName)
    time.sleep(rundelay)
    result = ctrl.add_netconf_node(node)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("'%s' NETCONF node was successfully added "
               "to the Controller" % nodeName)
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief())
        print status.detailed()
        exit(0)

    print "\n"
    print ("<<< Show NETCONF nodes configured on the Controller")
    time.sleep(rundelay)
    result = ctrl.get_netconf_nodes_in_config()
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print "Nodes configured:"
        nlist = result.get_data()
        for item in nlist:
            print "   '{}'".format(item)
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief())
        exit(0)

    print "\n"
    print ("<<< Find the '%s' NETCONF node on the Controller" % nodeName)
    time.sleep(rundelay)
    result = ctrl.check_node_config_status(nodeName)
    status = result.get_status()
    if(status.eq(STATUS.NODE_CONFIGURED)):
        print ("'%s' node is configured" % nodeName)
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief())
        exit(0)

    print "\n"
    print ("<<< Show connection status for all NETCONF nodes "
           "configured on the Controller")
    time.sleep(rundelay)
    result = ctrl.get_netconf_nodes_conn_status()
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print "Nodes connection status:"
        nlist = result.get_data()
        for item in nlist:
            status = ""
            if (item['connected'] is True):
                status = "connected"
            else:
                status = "not connected"
            print "   '{}' is {}".format(item['node'], status)
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief())
        exit(0)

    print "\n"
    print ("<<< Show connection status for the '%s' NETCONF node" % nodeName)
    time.sleep(rundelay)
    result = ctrl.check_node_conn_status(nodeName)
    status = result.get_status()
    if(status.eq(STATUS.NODE_CONNECTED)):
        print ("'%s' node is connected" % nodeName)
    elif (status.eq(STATUS.NODE_DISONNECTED)):
        print ("'%s' node is not connected" % nodeName)
    elif (status.eq(STATUS.NODE_NOT_FOUND)):
        print ("'%s' node is not found" % nodeName)
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief())
        exit(0)

    print "\n"
    print (">>> Remove '%s' NETCONF node from the Controller" % nodeName)
    time.sleep(rundelay)
    result = ctrl.delete_netconf_node(node)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("'%s' NETCONF node was successfully removed "
               "from the Controller" % nodeName)
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief())
        exit(0)

    print "\n"
    print ("<<< Show NETCONF nodes configured on the Controller")
    time.sleep(rundelay)
    result = ctrl.get_netconf_nodes_in_config()
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print "Nodes configured:"
        nlist = result.get_data()
        for item in nlist:
            print "   '{}'".format(item)
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief())
        exit(0)

    print "\n"
    print ("<<< Show connection status for the '%s' NETCONF node" % nodeName)
    time.sleep(rundelay)
    result = ctrl.check_node_conn_status(nodeName)
    status = result.get_status()
    if (status.eq(STATUS.NODE_CONNECTED)):
        print ("'%s' node is connected" % nodeName)
    elif (status.eq(STATUS.NODE_DISONNECTED)):
        print ("'%s' node is not connected" % nodeName)
    elif (status.eq(STATUS.NODE_NOT_FOUND)):
        print ("'%s' node is not found" % nodeName)
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief())
        exit(0)

    print ("\n")
    print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print (">>> Demo End")
    print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")


if __name__ == "__main__":
    nc_demo_10()
