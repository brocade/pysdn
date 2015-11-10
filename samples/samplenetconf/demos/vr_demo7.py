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
from pysdn.netconfdev.vrouter.vrouter5600 import VRouter5600
from pysdn.netconfdev.vrouter.firewall import Firewall, Rule
from pysdn.common.status import STATUS
from pysdn.common.utils import load_dict_from_file


def vr_demo_7():

    f = "cfg4.yml"
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
        ifName = d['interfaceName']
        rundelay = d['rundelay']
    except:
        print ("Failed to get Controller device attributes")
        exit(0)

    print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    print ("<<< Demo Start")
    print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    print ("\n")

    ctrl = Controller(ctrlIpAddr, ctrlPortNum, ctrlUname, ctrlPswd)
    vrouter = VRouter5600(ctrl, nodeName, nodeIpAddr, nodePortNum,
                          nodeUname, nodePswd)
    print ("<<< 'Controller': %s, '%s': %s"
           % (ctrlIpAddr, nodeName, nodeIpAddr))

    print ("\n")
    time.sleep(rundelay)
    node_configured = False
    result = ctrl.check_node_config_status(nodeName)
    status = result.get_status()
    if(status.eq(STATUS.NODE_CONFIGURED)):
        node_configured = True
        print ("<<< '%s' is configured on the Controller" % nodeName)
    elif(status.eq(STATUS.DATA_NOT_FOUND)):
        node_configured = False
    else:
        print ("\n")
        print "Failed to get configuration status for the '%s'" % nodeName
        print ("!!!Demo terminated, reason: %s" % status.detailed())
        exit(0)

    if node_configured is False:
        result = ctrl.add_netconf_node(vrouter)
        status = result.get_status()
        if(status.eq(STATUS.OK)):
            print ("<<< '%s' added to the Controller" % nodeName)
        else:
            print ("\n")
            print ("!!!Demo terminated, reason: %s" % status.detailed())
            exit(0)

    print ("\n")
    time.sleep(rundelay)
    result = ctrl.check_node_conn_status(nodeName)
    status = result.get_status()
    if(status.eq(STATUS.NODE_CONNECTED)):
        print ("<<< '%s' is connected to the Controller" % nodeName)
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief().lower())
        exit(0)

    print("\n")
    print ("<<< Show firewalls configuration on the '%s'" % nodeName)
    time.sleep(rundelay)
    result = vrouter.get_firewalls_cfg()
    status = result.get_status()
    if (status.eq(STATUS.OK)):
        print ("'%s' firewalls config:" % nodeName)
        cfg = result.get_data()
        data = json.loads(cfg)
        print json.dumps(data, indent=4)
    elif (status.eq(STATUS.DATA_NOT_FOUND)):
        print ("No firewalls configuration found")
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief().lower())
        ctrl.delete_netconf_node(vrouter)
        exit(0)

    print "\n"
    fwName1 = "ACCEPT-SRC-IPADDR"
    print (">>> Create new firewall instance '%s' on '%s'"
           % (fwName1, nodeName))
    firewall1 = Firewall(fwName1)
    # Add a rule to the firewall instance
    rulenum = 30
    rule = Rule(rulenum)
    rule.add_action("accept")
    rule.add_source_address("172.22.17.108")
    firewall1.add_rule(rule)
    print firewall1.get_payload()
    time.sleep(rundelay)
    result = vrouter.add_modify_firewall_instance(firewall1)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("Firewall instance '%s' was successfully created" % fwName1)
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.detailed())
        exit(0)

    print "\n"
    fwName2 = "DROP-ICMP"
    print (">>> Create new firewall instance '%s' on '%s'"
           % (fwName2, nodeName))
    firewall2 = Firewall(fwName2)
    # Add a rule to the firewall instance
    rulenum = 40
    rule = Rule(rulenum)
    rule.add_action("drop")
    rule.add_icmp_typename("ping")
    firewall2.add_rule(rule)
    print firewall2.get_payload()
    time.sleep(rundelay)
    result = vrouter.add_modify_firewall_instance(firewall2)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("Firewall instance '%s' was successfully created" % fwName2)
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief().lower())
        print status.detailed()
        exit(0)

    print("\n")
    print ("<<< Show firewalls configuration on the '%s'" % nodeName)
    time.sleep(rundelay)
    result = vrouter.get_firewalls_cfg()
    status = result.get_status()
    if (status.eq(STATUS.OK)):
        print ("'%s' firewalls config:" % nodeName)
        cfg = result.get_data()
        data = json.loads(cfg)
        print json.dumps(data, indent=4)
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief().lower())
        exit(0)

    print("\n")
    print ("<<< Apply firewall '%s' to inbound traffic "
           "and '%s' to outbound traffic on the '%s' "
           "dataplane interface" % (fwName1, fwName2, ifName))
    time.sleep(rundelay)
    result = vrouter.set_dataplane_interface_firewall(ifName, fwName1, fwName2)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("Firewall instances were successfully applied "
               "to the '%s' dataplane interface" % (ifName))
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief().lower())
        exit(0)

    print("\n")
    print ("<<< Show '%s' dataplane interface configuration on the '%s'"
           % (ifName, nodeName))
    time.sleep(rundelay)
    result = vrouter.get_dataplane_interface_cfg(ifName)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("Interfaces '%s' config:" % ifName)
        cfg = result.get_data()
        data = json.loads(cfg)
        print json.dumps(data, indent=4)
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief().lower())
        exit(0)

    print("\n")
    print ("<<< Remove firewall settings from the '%s' dataplane interface"
           % (ifName))
    time.sleep(rundelay)
    result = vrouter.delete_dataplane_interface_firewall(ifName)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("Firewall settings successfully removed "
               "from '%s' dataplane interface" % ifName)
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief().lower())
        exit(0)

    print("\n")
    print ("<<< Show '%s' dataplane interface configuration on the '%s'"
           % (ifName, nodeName))
    time.sleep(rundelay)
    result = vrouter.get_dataplane_interface_cfg(ifName)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("Interfaces '%s' config:" % ifName)
        cfg = result.get_data()
        data = json.loads(cfg)
        print json.dumps(data, indent=4)
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief().lower())
        exit(0)

    print "\n"
    print (">>> Remove firewall instance '%s' from '%s'"
           % (fwName1, nodeName))
    time.sleep(rundelay)
    result = vrouter.delete_firewall_instance(firewall1)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("Firewall instance '%s' was successfully deleted" % fwName1)
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief().lower())
        exit(0)

    print "\n"
    print (">>> Remove firewall instance '%s' from '%s'"
           % (fwName2, nodeName))
    time.sleep(rundelay)
    result = vrouter.delete_firewall_instance(firewall2)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("Firewall instance '%s' was successfully deleted" % fwName2)
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief().lower())
        exit(0)

    print("\n")
    print ("<<< Show firewalls configuration on the '%s'" % nodeName)
    time.sleep(rundelay)
    result = vrouter.get_firewalls_cfg()
    status = result.get_status()
    if (status.eq(STATUS.OK)):
        print ("'%s' firewalls config:" % nodeName)
        cfg = result.get_data()
        data = json.loads(cfg)
        print json.dumps(data, indent=4)
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief().lower())
        exit(0)

    print "\n"
    print (">>> Remove '%s' NETCONF node from the Controller" % nodeName)
    time.sleep(rundelay)
    result = ctrl.delete_netconf_node(vrouter)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("'%s' NETCONF node was successfully removed "
               "from the Controller" % nodeName)
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief())
        exit(0)

    print ("\n")
    print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print (">>> Demo End")
    print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

if __name__ == "__main__":
    vr_demo_7()
