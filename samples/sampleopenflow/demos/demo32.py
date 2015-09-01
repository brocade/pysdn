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
from pybvc.controller.inventory import (Inventory,
                                            OpenFlowCapableNode,
                                            GroupFeatures)
from pybvc.common.utils import load_dict_from_file
from pybvc.common.status import STATUS


def of_demo_32():
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
        rundelay = d['rundelay']
    except:
        print ("Failed to get Controller device attributes")
        exit(0)

    openflow_node_ids = []
    openflow_nodes = []

    print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    print ("<<< Demo 32 Start")
    print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")



    print "\n"
    ctrl = Controller(ctrlIpAddr, ctrlPortNum, ctrlUname, ctrlPswd)
    print ("<<< Controller '%s:%s'" % (ctrlIpAddr, ctrlPortNum))
    time.sleep(rundelay)

    print "\n".strip()
    print ("<<< Get OpenFlow switches information")
    time.sleep(rundelay)

    inv_obj = None
    result = ctrl.build_inventory_object()
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        inv_obj = result.get_data()
        assert(isinstance(inv_obj, Inventory))
    else:
        print ("\n")
        print ("!!!Error, failed to obtain inventory info, reason: %s"
               % status.brief().lower())
        exit(0)

    assert(inv_obj)
    openflow_node_ids = inv_obj.get_openflow_node_ids()
    for node_id in openflow_node_ids:
        node = inv_obj.get_openflow_node(node_id)
        assert(isinstance(node, OpenFlowCapableNode))
        openflow_nodes.append(node)

    print "\n".strip()
    print ("<<< OpenFlow switches in the inventory store")
    s1 = 'IP Address'
    s2 = 'OpenFlow Id'
    sym = '-'
    print "\n".strip()
    print "        {0:<15}  {1:<30}".format(s1, s2)
    print "        {0:<15}  {1:<30}".format(sym*15, sym*30)
    for node in openflow_nodes:
        addr = node.get_ip_address()
        node_id = node.get_id()
        print "        {0:<15}  {1:<30}".format(addr, node_id)

    print "\n".strip()
    print ("<<< Get Group Table Information")
    time.sleep(rundelay)
    for node in openflow_nodes:
        assert(isinstance(node, OpenFlowCapableNode))
        print "\n".strip()
        switch_id = node.get_id()
        print ("        Switch '%s'") % switch_id
        print "\n".strip()
        group_features = node.get_group_features()
        assert(isinstance(group_features, GroupFeatures))

        q = 2  # number of list items to be in a single chunk (output string)

        s = 'Max groups'
        alist = group_features.get_max_groups()
        if alist:
            chunks = [alist[x:x+q] for x in xrange(0, len(alist), q)]
            print "            %s     :" % s,
            for i in range(0, len(chunks)):
                n = 0 if i == 0 else len(s) + 19
                print "%s%s" % (" "*n, ", ".join(map(str, chunks[i])))
        else:
            print "            %s     : %s" % (s, "n/a")

        s = 'Group types'
        alist = group_features.get_types()
        if alist:
            chunks = [alist[x:x+q] for x in xrange(0, len(alist), q)]
            print "            %s    :" % s,
            for i in range(0, len(chunks)):
                n = 0 if i == 0 else len(s) + 18
                print "%s%s" % (" "*n, ", ".join(chunks[i]))
        else:
            print "            %s    : %s" % (s, "n/a")

        s = 'Capabilities'
        alist = group_features.get_capabilities()
        if alist:
            chunks = [alist[x:x+q] for x in xrange(0, len(alist), q)]
            print "            %s   :" % s,
            for i in range(0, len(chunks)):
                n = 0 if i == 0 else len(s) + 17
                print "%s%s" % (" "*n, ", ".join(chunks[i]))
        else:
            print "            %s   : %s" % (s, "n/a")

        print "\n".strip()
        total_num = node.get_groups_total_num()
        s = 'Num of groups'
        print "            %s  : %s" % (s, total_num)

        s = 'Group IDs'
        alist = node.get_group_ids()
        if alist:
            chunks = [alist[x:x+q] for x in xrange(0, len(alist), q)]
            print "            %s      :" % s,
            for i in range(0, len(chunks)):
                n = 0 if i == 0 else len(s) + 13
                print "%s%s" % (" "*n, ", ".join(map(str, chunks[i])))
        else:
            print "            %s      : %s" % (s, "")

    print ("\n")
    print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print (">>> Demo End")
    print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

if __name__ == "__main__":
    of_demo_32()
