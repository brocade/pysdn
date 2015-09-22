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
from pybvc.netconfdev.vrouter.vrouter5600 import VRouter5600
from pybvc.netconfdev.vrouter.vpn import Vpn
from pybvc.common.status import STATUS
from pybvc.common.utils import load_dict_from_file


def vr_demo_12():

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
    print ("<<< Show VPN configuration on the '%s'" % nodeName)
    result = vrouter.get_vpn_cfg()
    time.sleep(rundelay)
    status = result.get_status()
    if (status.eq(STATUS.OK)):
        print ("'%s' VPN configuration:" % nodeName)
        cfg = result.get_data()
        data = json.loads(cfg)
        print json.dumps(data, indent=4, sort_keys=True)
    elif (status.eq(STATUS.DATA_NOT_FOUND)):
        print ("No VPN configuration found")
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.detailed())
        ctrl.delete_netconf_node(vrouter)
        exit(0)

    print "\n"
    print (">>> Create new VPN configuration on the '%s'" % (nodeName))

    ca_cert_file = '/config/auth/ca.crt'
    srv_cert_file = '/config/auth/r1.crt'
    srv_key_file = '/config/auth/r1.key'
    crl_file = '/config/auth/r1.crl'
    print (" NOTE: For this demo to succeed the following files "
           "must exist on the '%s'\n"
           "       (empty files can be created for the sake of the demo):\n"
           "         %s\n"
           "         %s\n"
           "         %s\n"
           "         %s"
           % (nodeName, ca_cert_file, srv_cert_file, crl_file, srv_key_file))

    time.sleep(rundelay)

    # -------------------------------------------------------------------------
    # Encode VPN configuration options by using 'Vpn' object
    # -------------------------------------------------------------------------
    vpn = Vpn()

    # -------------------------------------------------------------------------
    # Create and configure Internet Key Exchange (IKE) group
    # -------------------------------------------------------------------------
    ike_grp_name = "IKE-1W"
    proposal_num = 1

    # Set the encryption cipher for proposal 1
    # (enumeration: 'aes128', 'aes256', '3des')
    encryption_cipher = 'aes256'
    vpn.set_ipsec_ike_group_proposal_encryption(ike_grp_name, proposal_num,
                                                encryption_cipher)

    # Set the hash algorithm for proposal 1
    # (enumeration: 'md5', 'sha1')
    hash_algorithm = 'sha1'
    vpn.set_ipsec_ike_group_proposal_hash(ike_grp_name, proposal_num,
                                          hash_algorithm)

    # Set the encryption cipher for proposal 2
    # (enumeration: 'aes128', 'aes256', '3des')
    proposal_num = 2
    encryption_cipher = 'aes128'
    vpn.set_ipsec_ike_group_proposal_encryption(ike_grp_name, proposal_num,
                                                encryption_cipher)

    # Set the hash algorithm for proposal 2
    # (enumeration: 'md5', 'sha1')
    hash_algorithm = 'sha1'
    vpn.set_ipsec_ike_group_proposal_hash(ike_grp_name, proposal_num,
                                          hash_algorithm)

    # Set the lifetime for the whole IKE group
    lifetime = 3600
    vpn.set_ipsec_ike_group_lifetime(ike_grp_name, lifetime)

    # -------------------------------------------------------------------------
    # Create and configure Encapsulating Security Payload (ESP) group
    # -------------------------------------------------------------------------
    esp_grp_name = "ESP-1W"

    # Set the encryption cipher for proposal 1
    # (enumeration: 'aes128', 'aes256', '3des')
    proposal_num = 1
    encryption_cipher = 'aes256'
    vpn.set_ipsec_esp_group_proposal_encryption(esp_grp_name, proposal_num,
                                                encryption_cipher)

    # Set the hash algorithm for proposal 1
    # (enumeration: 'md5', 'sha1')
    hash_algorithm = 'sha1'
    vpn.set_ipsec_esp_group_proposal_hash(esp_grp_name, proposal_num,
                                          hash_algorithm)

    # Set the encryption cipher for proposal 2
    # (enumeration: 'aes128', 'aes256', '3des')
    proposal_num = 2
    encryption_cipher = '3des'
    vpn.set_ipsec_esp_group_proposal_encryption(esp_grp_name, proposal_num,
                                                encryption_cipher)

    # Set the hash algorithm for proposal 2
    # (enumeration: 'md5', 'sha1')
    hash_algorithm = 'md5'
    vpn.set_ipsec_esp_group_proposal_hash(esp_grp_name, proposal_num,
                                          hash_algorithm)

    # Set the lifetime for the whole ESP group
    lifetime = 1800
    vpn.set_ipsec_esp_group_lifetime(esp_grp_name, lifetime)

    # -------------------------------------------------------------------------
    # Configure connection to a remote peer
    # -------------------------------------------------------------------------
    peer_node = "192.0.2.33"
    description = ("Site-to-Site VPN Configuration Example - "
                   "X.509 Certificate Authentication")
    vpn.set_ipsec_site_to_site_peer_description(peer_node, description)

    # Set authentication mode to 'x509'
    auth_mode = 'x509'
    vpn.set_ipsec_site_to_site_peer_auth_mode(peer_node, auth_mode)

    # Specify the 'distinguished name' of the certificate for the peer
    remote_id = "C=US, ST=CA, O=ABC Company, CN=east, E=root@abcco.com"
    vpn.set_ipsec_site_to_site_peer_auth_remote_id(peer_node, remote_id)

    # Specify the location of the CA certificate on the vRouter
    vpn.set_ipsec_site_to_site_peer_auth_ca_cert_file(peer_node, ca_cert_file)

    # Specify the location of the server certificate on the vRouter
    vpn.set_ipsec_site_to_site_peer_auth_srv_cert_file(peer_node,
                                                       srv_cert_file)

    # Specify the location of the server key file on the vRouter
    vpn.set_ipsec_site_to_site_peer_auth_srv_key_file(peer_node, srv_key_file)

    # Specify the password for the server key file
    srv_key_pswd = 'testpassword'
    vpn.set_ipsec_site_to_site_peer_auth_srv_key_pswd(peer_node, srv_key_pswd)

    # Specify the default ESP group for all tunnels
    esp_group_name = 'ESP-1W'
    vpn.set_ipsec_site_to_site_peer_default_esp_group(peer_node,
                                                      esp_group_name)

    # Specify the IKE group
    ike_group_name = 'IKE-1W'
    vpn.set_ipsec_site_to_site_peer_ike_group(peer_node, ike_group_name)

    # Identify the IP address on the vRouter to be used for this connection
    local_address = '192.0.2.1'
    vpn.set_ipsec_site_to_site_peer_local_address(peer_node, local_address)

    # Create a tunnel configuration and provide local and remote subnets
    # for this tunnel
    tunnel = 1
    local_prefix = '192.168.40.0/24'
    remote_prefix = '192.168.60.0/24'
    vpn.set_ipsec_site_to_site_peer_tunnel_local_prefix(peer_node, tunnel,
                                                        local_prefix)
    vpn.set_ipsec_site_to_site_peer_tunnel_remote_prefix(peer_node, tunnel,
                                                         remote_prefix)

    print "\n"
    print (">>> VPN configuration to be applied to the '%s'" % (nodeName))
    print vpn.get_payload()
    time.sleep(rundelay)

    result = vrouter.set_vpn_cfg(vpn)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("<<< VPN configuration was successfully created")
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief().lower())
        print status.detailed()
        ctrl.delete_netconf_node(vrouter)
        exit(0)

    print "\n"
    print ("<<< Show VPN configuration on the '%s'" % (nodeName))
    time.sleep(rundelay)
    result = vrouter.get_vpn_cfg()
    status = result.get_status()
    if (status.eq(STATUS.OK)):
        print ("'%s' VPN configuration:" % nodeName)
        cfg = result.get_data()
        data = json.loads(cfg)
        print json.dumps(data, indent=4, sort_keys=True)
        print ("<<< VPN configuration was successfully read")
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.detailed())
        ctrl.delete_netconf_node(vrouter)
        exit(0)

    time.sleep(rundelay)

    print "\n"
    print ("<<< Delete VPN configuration on the '%s'" % (nodeName))
    time.sleep(rundelay)
    result = vrouter.delete_vpn_cfg()
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("VPN configuration successfully removed from '%s'" % (nodeName))
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.brief().lower())
        print status.detailed()
        ctrl.delete_netconf_node(vrouter)
        exit(0)

    print "\n"
    print ("<<< Show VPN configuration on the '%s'" % (nodeName))
    time.sleep(rundelay)
    result = vrouter.get_vpn_cfg()
    status = result.get_status()
    if (status.eq(STATUS.OK)):
        print ("'%s' VPN configuration:" % nodeName)
        cfg = result.get_data()
        data = json.loads(cfg)
        print json.dumps(data, indent=4, sort_keys=True)
    elif (status.eq(STATUS.DATA_NOT_FOUND)):
        print ("No VPN configuration found")
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.detailed())
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
    vr_demo_12()
