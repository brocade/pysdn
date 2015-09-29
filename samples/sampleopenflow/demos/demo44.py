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
                                        MeterFeatures)
from pybvc.common.utils import load_dict_from_file
from pybvc.common.status import STATUS


def of_demo_44():
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

    openflow_nodes = []

    print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    print ("<<< Demo 44 Start")
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
        print ("!!!Error, failed to obtain inventory info, reason: %s" %
               status.brief().lower())
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
    print "        {0:<15}  {1:<30}".format(sym * 15, sym * 30)
    for node in openflow_nodes:
        addr = node.get_ip_address()
        node_id = node.get_id()
        print "        {0:<15}  {1:<30}".format(addr, node_id)

    print "\n".strip()
    print ("<<< Get Meter Features Information")
    time.sleep(rundelay)
    for node in openflow_nodes:
        assert(isinstance(node, OpenFlowCapableNode))
        print "\n".strip()
        switch_id = node.get_id()
        print ("        Switch '%s'") % switch_id
        print "\n".strip()
        meter_features = node.get_meter_features()
        assert(isinstance(meter_features, MeterFeatures))

        s = 'Max meters'
        v = meter_features.get_max_meters()
        if v is not None:
            print "            %s    : %s" % (s, v)
        else:
            print "            %s    : %s" % (s, "n/a")
        s = "Max bands"
        v = meter_features.get_max_bands()
        if v is not None:
            print "            %s     : %s" % (s, v)
        else:
            print "            %s    : %s" % (s, "n/a")
        s = "Max colors"
        v = meter_features.get_max_colors()
        if v is not None:
            print "            %s    : %s" % (s, v)
        else:
            print "            %s    : %s" % (s, "n/a")

        q = 4  # number of list items to be in a single chunk (output string)

        s = 'Band types'
        alist = meter_features.get_band_types()
        if alist:
            chunks = [alist[x:x + q] for x in xrange(0, len(alist), q)]
            print "            %s    :" % s,
            for i in range(0, len(chunks)):
                n = 0 if i == 0 else len(s) + 18
                print "%s%s" % (" " * n, ", ".join(chunks[i]))
        else:
            print "            %s    : %s" % (s, "n/a")

        s = 'Capabilities'
        alist = meter_features.get_capabilities()
        if alist:
            chunks = [alist[x:x + q] for x in xrange(0, len(alist), q)]
            print "            %s  :" % s,
            for i in range(0, len(chunks)):
                n = 0 if i == 0 else len(s) + 16
                print "%s%s" % (" " * n, ", ".join(chunks[i]))
        else:
            print "            %s  : %s" % (s, "n/a")

    print ("\n")
    print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print (">>> Demo End")
    print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

if __name__ == "__main__":
    of_demo_44()
