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
from pysdn.netconfdev.vrouter.interfaces import OpenVpnInterface
from pysdn.netconfdev.vrouter.protocols import StaticRoute
from pysdn.common.status import STATUS
from pysdn.common.utils import load_dict_from_file


def vr_demo_13():

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
        rundelay = d['rundelay']
    except:
        print ("Failed to get Controller device attributes")
        exit(0)

    print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    print ("<<< Demo Start")
    print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    print("\n")
    print("<<< OpenVPN configuration example: "
          "Site-to-Site Mode with Preshared Secret")
    print("\n")

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
    print ("<<< Show OpenVPN interfaces configuration on the '%s'" % nodeName)
    result = vrouter.get_openvpn_interfaces_cfg()
    time.sleep(rundelay)
    status = result.get_status()
    if (status.eq(STATUS.OK)):
        print ("'%s' OpenVPN interfaces configuration:" % nodeName)
        iflist = result.get_data()
        assert(isinstance(iflist, list))
        for item in iflist:
            print json.dumps(item, indent=4, sort_keys=True)
    elif (status.eq(STATUS.DATA_NOT_FOUND)):
        print ("No OpenVPN interfaces configuration found")
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.detailed())
        ctrl.delete_netconf_node(vrouter)
        exit(0)

    print "\n"
    ifname = 'vtun0'
    print (">>> Configure new '%s' OpenVPN tunnel interface on the '%s'"
           % (ifname, nodeName))
    time.sleep(rundelay)

    # Create OpenVPN interface
    vpnif = OpenVpnInterface(ifname)

    # Set the OpenVPN mode to 'site-to-site'
    mode = 'site-to-site'
    vpnif.set_mode(mode)

    # Specify the location of the file containing the preshared secret
    secret_file = '/config/auth/secret'
    vpnif.set_shared_secret_key_file(secret_file)

    # Set the tunnel IP address for the local endpoint
    local_address = '192.168.200.1'
    vpnif.set_local_address(local_address)

    # Set the tunnel IP address of the remote endpoint
    remote_address = '192.168.200.2'
    vpnif.set_remote_address(remote_address)

    # Specify the physical IP address of the remote host
    remote_host = '87.65.43.21'
    vpnif.set_remote_host(remote_host)

    result = vrouter.set_openvpn_interface_cfg(vpnif)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("<<< '%s' interface configuration was successfully created"
               % ifname)
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief().lower())
        print status.detailed()
        ctrl.delete_netconf_node(vrouter)
        exit(0)

    print "\n"
    print ("<<< Show '%s' interface configuration on the '%s'"
           % (ifname, nodeName))
    time.sleep(rundelay)
    result = vrouter.get_openvpn_interface_cfg(ifname)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("'%s' interface configuration:" % ifname)
        cfg = result.get_data()
        data = json.loads(cfg)
        print json.dumps(data, indent=4, sort_keys=True)
        print ("<<< '%s' interface configuration was successfully read"
               % ifname)
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief().lower())
        print status.detailed()
        ctrl.delete_netconf_node(vrouter)
        exit(0)

    print "\n"
    ip_prefix = '192.168.101.0/24'
    print ("<<< Create static route to access the remote subnet '%s' "
           "through the '%s' interface " % (ip_prefix, ifname))
    time.sleep(rundelay)
    static_route = StaticRoute()
    static_route.set_interface_route(ip_prefix)
    static_route.set_interface_route_next_hop_interface(ip_prefix, ifname)
    result = vrouter.set_protocols_static_route_cfg(static_route)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("<<< Static route was successfully created")
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief().lower())
        print status.detailed()
        ctrl.delete_netconf_node(vrouter)
        exit(0)

    print "\n"
    print ("<<< Show subnet '%s' static route configuration on the '%s'"
           % (ip_prefix, nodeName))
    time.sleep(rundelay)
    result = vrouter.get_protocols_static_interface_route_cfg(ip_prefix)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("Static route configuration:")
        cfg = result.get_data()
        data = json.loads(cfg)
        print json.dumps(data, indent=4, sort_keys=True)
        print ("<<< Static route configuration was successfully read")
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief().lower())
        print status.detailed()
        ctrl.delete_netconf_node(vrouter)
        exit(0)

    print "\n"
    print ("<<< Delete '%s' interface configuration from the '%s'"
           % (ifname, nodeName))
    time.sleep(rundelay)
    result = vrouter.delete_openvpn_interface_cfg(ifname)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("<<< '%s' interface configuration successfully "
               "removed from the '%s'" % (ifname, nodeName))
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief().lower())
        print status.detailed()
        ctrl.delete_netconf_node(vrouter)
        exit(0)

    print "\n"
    print ("<<< Show '%s' interface configuration on the '%s'"
           % (ifname, nodeName))
    time.sleep(rundelay)
    result = vrouter.get_openvpn_interface_cfg(ifname)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("\n")
        print ("!!!Demo terminated, reason: %s"
               % "Interface configuration still exists")
    elif(status.eq(STATUS.DATA_NOT_FOUND)):
        print ("No '%s' interface configuration found" % (ifname))
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief().lower())
        print status.detailed()
        ctrl.delete_netconf_node(vrouter)
        exit(0)

    print "\n"
    print ("<<< Delete '%s' subnet static route configuration from the '%s'"
           % (ip_prefix, nodeName))
    time.sleep(rundelay)
    result = vrouter.delete_protocols_static_interface_route_cfg(ip_prefix)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("<<< Static route configuration successfully removed "
               "from the '%s'" % (nodeName))
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief().lower())
        print status.detailed()
        ctrl.delete_netconf_node(vrouter)
        exit(0)

    print "\n"
    print ("<<< Show '%s' subnet static route configuration on the '%s'"
           % (ip_prefix, nodeName))
    time.sleep(rundelay)
    result = vrouter.get_protocols_static_interface_route_cfg(ip_prefix)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("\n")
        print ("!!!Demo terminated, reason: %s"
               % "Static route configuration still found")
    elif(status.eq(STATUS.DATA_NOT_FOUND)):
        print ("No static route configuration found")
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief().lower())
        print status.detailed()
        ctrl.delete_netconf_node(vrouter)
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
    vr_demo_13()
