
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

vrouter5600.py: vRouter-5600 specific properties and communication methods


"""

import json

from pybvc.controller.netconfnode import NetconfNode
from pybvc.common.result import Result
from pybvc.common.status import OperStatus, STATUS
from pybvc.netconfdev.vrouter.vpn import Vpn
from pybvc.netconfdev.vrouter.interfaces import OpenVpnInterface
from pybvc.netconfdev.vrouter.protocols import StaticRoute
from pybvc.netconfdev.vrouter.firewall import (Firewall,
                                               DataplaneInterfaceFirewall)


class VRouter5600(NetconfNode):
    """ Class that represents an instance of vRouter5600
        (NETCONF capable server device).
         :param ctrl: :class:`pybvc.controller.controller.Controller`
        :param string name: The name of the vrouter5600
        :param string ipAddr: The ip address for the vrouter5600
        :param int portNum: The port number to communicate NETCONF
                            to the vrouter5600
        :param string adminName:  The username to authenticate setup
                                  of the NETCONF communication
        :param string adminPassword:  The password to authenticate setup
                                      of the NETCONF communication
        :param boolean tcpOnly:  Use TCP only or not.
        :return: The newly created vrouter5600 instance.
        :rtype: :class:`pybvc.netconfdev.vrouter.vrouter5600.VRouter5600`
         """

    def __init__(self, ctrl, name, ipAddr, portNum, adminName,
                 adminPassword, tcpOnly=False):
        super(VRouter5600, self).__init__(ctrl, name, ipAddr, portNum,
                                          adminName, adminPassword, tcpOnly)

    def to_string(self):
        """ Returns string representation of this object. """
        return str(vars(self))

    def to_json(self):
        """ Returns JSON representation of this object. """
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True,
                          indent=4)

    def get_schemas(self):
        """ Return a list of YANG model schemas implemented on this VRouter5600
         :return: A tuple: Status, list of YANG model schemas for the
                  VRouter5600.
        :rtype: instance of the `Result` class (containing JSON listing
                information about the YANG schemas for the node)
         - STATUS.CONN_ERROR: If the controller did not respond. List is empty.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not
                                      provide any status. List is empty.
        - STATUS.OK: Success. List is valid.
        - STATUS.HTTP_ERROR: If the controller responded with an error
                            status code.
         """
        ctrl = self.ctrl
        myname = self.name
        return ctrl.get_schemas(myname)

    def get_schema(self, schemaId, schemaVersion):
        """Return a YANG model definition for the indicated schema
         :param string schemaId: id of schema
        :param string schemaVersion: version of the schema
        :return: A tuple: Status, YANG model schema.
        :rtype: instance of the `Result` class (containing YANG schema)
        - STATUS.CONN_ERROR: If the controller did not respond. Schema is
        .  empty.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not
        .                             provide any status. Schema is empty.
        - STATUS.OK: Success. Result is valid.
        - STATUS.DATA_NOT_FOUND: Data missing or in unexpected format.
        - STATUS.HTTP_ERROR: If the controller responded with an error
        .                    status code.
         """
        ctrl = self.ctrl
        myname = self.name
        return ctrl.get_schema(myname, schemaId, schemaVersion)

    def get_cfg(self):
        """Return configuration of the VRouter5600.
         :return: A tuple: Status, JSON for configuration.
        :rtype: instance of the `Result` class (containing configuration data)
        - STATUS.CONN_ERROR: If the controller did not respond.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not
        .                             provide any status.
        - STATUS.OK: Success. Result is valid.
        - STATUS.HTTP_ERROR: If the controller responded with an error
        .                    status code.
         """
        status = OperStatus()
        cfg = None
        ctrl = self.ctrl
        myname = self.name
        url = ctrl.get_ext_mount_config_url(myname)
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            cfg = resp.content
            status.set_status(STATUS.OK)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return Result(status, cfg)

    def get_firewalls_cfg(self):
        """Return firewall configuration of the VRouter5600.
         :return: A tuple: Status, JSON for firewall configuration.
        :rtype: instance of the `Result` class (containing configuration data)
         - STATUS.CONN_ERROR: If the controller did not respond.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did
                                      not provide any status.
        - STATUS.OK: Success. Result is valid.
        - STATUS.HTTP_ERROR: If the controller responded with an error
                             status code.
         """
        status = OperStatus()
        url_ext = "vyatta-security:security/vyatta-security-firewall:firewall"
        cfg = None

        ctrl = self.ctrl
        myname = self.name
        url = ctrl.get_ext_mount_config_url(myname)
        url += url_ext
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            cfg = resp.content
            status.set_status(STATUS.OK)
        elif (resp.status_code == 404):
            status.set_status(STATUS.DATA_NOT_FOUND, resp)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return Result(status, cfg)

    def get_firewall_instance_cfg(self, instance):
        """Return configuration for a specific firewall on the VRouter5600.
         :param instance of the 'Firewall' class
        :return: A tuple: Status, JSON for firewall configuration.
        :rtype: instance of the `Result` class (containing configuration data)
         - STATUS.CONN_ERROR: If the controller did not respond.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not
                                      provide any status.
        - STATUS.OK:  Success. Result is valid.
        - STATUS.HTTP_ERROR: If the controller responded with an error
                             status code.
        """
        status = OperStatus()
        cfg = None
        templateModelRef = "vyatta-security:" + \
            "security/vyatta-security-firewall:firewall/name/{}"
        modelref = templateModelRef.format(instance)
        ctrl = self.ctrl
        myname = self.name
        url = ctrl.get_ext_mount_config_url(myname)
        url += modelref
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            cfg = resp.content
            status.set_status(STATUS.OK)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return Result(status, cfg)

    def add_modify_firewall_instance(self, fwInstance):
        """Create a firewall on the VRouter5600.
         :param fwInstance: instance of the 'Firewall' class
        :return: A tuple:  Status, None.
        :rtype: instance of the `Result` class
         - STATUS.CONN_ERROR: If the controller did not respond.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not
                                      provide any status.
        - STATUS.OK:  Success. Result is valid.
        - STATUS.HTTP_ERROR: If the controller responded with an error
                             status code.
         """
        status = OperStatus()
        ctrl = self.ctrl
        myname = self.name
        url = ctrl.get_ext_mount_config_url(myname)
        headers = {'content-type': 'application/yang.data+json'}
        payload = fwInstance.get_payload()
        url_ext = fwInstance.get_url_extension()
        url += url_ext
        resp = ctrl.http_put_request(url, payload, headers)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200 or resp.status_code == 204):
            status.set_status(STATUS.OK)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return Result(status, None)

    # -------------------------------------------------------------------------
    # TBD
    # -------------------------------------------------------------------------
    def add_firewall_instance_rule(self, fwInstance, fwRule):
        pass

    # -------------------------------------------------------------------------
    # TBD
    # -------------------------------------------------------------------------
    def update_firewall_instance_rule(self, fwInstance, fwRule):
        pass

    def delete_firewall_instance(self, fwInstance):
        """Delete a firewall from the VRouter5600.
         :param fwInstance: Firewall :class:
        :return: A tuple: Status, None.
        :rtype: instance of the `Result` class
         - STATUS.CONN_ERROR: If the controller did not respond.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not
                                     provide any status.
        - STATUS.OK: Success. Result is valid.
        - STATUS.HTTP_ERROR:  if the controller responded with an error status
        .  code.
         """
        assert isinstance(fwInstance, Firewall)
        status = OperStatus()
        ctrl = self.ctrl
        myname = self.name
        url = ctrl.get_ext_mount_config_url(myname)
        ext = fwInstance.get_url_extension()
        url += ext
        resp = ctrl.http_delete_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            status.set_status(STATUS.OK)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return Result(status, None)

    def set_dataplane_interface_firewall(self, ifName,
                                         inboundFwName, outboundFwName):
        """ Set a firewall for inbound, outbound or both for a
            dataplane interface on the VRouter5600.
         :param string ifName: The dataplane interface to attache a firewall.
        :param string inboundFwName: None or name of firewall on VRouter5600
                                     to use for traffic inbound towards router.
        :param string outboundFwName: None or name of firewall on VRouter5600
                                     to use for traffic outbound from router.
        :return: A tuple:  Status, None.
        :rtype: instance of the `Result` class
         - STATUS.CONN_ERROR:  if the controller did not respond. schema is
           empty.
        - STATUS.CTRL_INTERNAL_ERROR:  if the controller responded but did not
           provide any status. schema is empty.
        - STATUS.OK:  Success. result is valid.
        - STATUS.HTTP_ERROR:  if the controller responded with an error status
          code.
         """
        status = OperStatus()
        ctrl = self.ctrl
        headers = {'content-type': 'application/yang.data+json'}
        url = ctrl.get_ext_mount_config_url(self.name)
        obj = DataplaneInterfaceFirewall(ifName)
        if (inboundFwName is not None):
            obj.add_in_policy(inboundFwName)
        if (outboundFwName is not None):
            obj.add_out_policy(outboundFwName)
        payload = obj.get_payload()
        url += obj.get_url_extension()
        resp = ctrl.http_put_request(url, payload, headers)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            status.set_status(STATUS.OK)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return Result(status, None)

    def delete_dataplane_interface_firewall(self, ifName):
        """ Delete both inbound and outbound firewalls for a
            dataplane interface on the VRouter5600.
         :param string ifName: The dataplane interface to attach a firewall.
        :return: A tuple:  Status, Response from VRouter5600.
        :rtype: instance of the `Result` class
         - STATUS.CONN_ERROR: If the controller did not respond.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did
                                      not provide any status.
        - STATUS.OK: Success. Result is valid.
        - STATUS.HTTP_ERROR: If the controller responded with an error
                             status code.
         """
        status = OperStatus()
        templateModelRef = "vyatta-interfaces:" + \
            "interfaces/vyatta-interfaces-dataplane:" + \
            "dataplane/{}/vyatta-security-firewall:firewall/"
        modelref = templateModelRef.format(ifName)
        myname = self.name
        ctrl = self.ctrl
        url = ctrl.get_ext_mount_config_url(myname)
        resp = ctrl.http_delete_request(url + modelref, data=None,
                                        headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            status.set_status(STATUS.OK)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return Result(status, None)

    def get_interfaces_list(self):
        """ Get the list of interfaces on the VRouter5600.
         :return: A tuple: Status, list of interface names.
        :rtype: instance of the `Result` class
         - STATUS.CONN_ERROR: If the controller did not respond.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not
                                      provide any status.
        - STATUS.OK:  Success. Result is valid.
        - STATUS.HTTP_ERROR: If the controller responded with an error
                             status code.
         """
        ifList = []
        result = self.get_interfaces_cfg()
        status = result.get_status()
        if(status.eq(STATUS.OK)):
            cfg = result.get_data()
            p1 = 'interfaces'
            if(p1 in cfg):
                d = json.loads(cfg).get(p1)
                p2 = 'tagnode'
                for k, v in d.items():
                    print k
                    print type(v)
                    if (isinstance(v, list)):
                        for item in v:
                            if p2 in item:
                                ifList.append(item[p2])
        return Result(status, ifList)

    def get_interfaces_cfg(self):
        """ Return the configuration for the interfaces on the VRouter5600
         :return: A tuple: Status, configuration of the interfaces
        :rtype: instance of the `Result` class (containing configuration data)
         - STATUS.CONN_ERROR: If the controller did not respond.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not
                                      provide any status.
        - STATUS.OK:  Success. Result is valid.
        - STATUS.HTTP_ERROR: If the controller responded with an error
                             status code.
         """
        status = OperStatus()
        cfg = None
        templateModelRef = "vyatta-interfaces:interfaces"
        modelref = templateModelRef
        ctrl = self.ctrl
        url = ctrl.get_ext_mount_config_url(self.name)
        url += modelref
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            cfg = resp.content
            status.set_status(STATUS.OK)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return Result(status, cfg)

    def get_dataplane_interfaces_list(self):
        """ Return a list of interfaces on the VRouter5600
         :return: A tuple: Status, list of interface names
        :rtype: instance of the `Result` class
         - STATUS.CONN_ERROR: If the controller did not respond.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did
                                      not provide any status.
        - STATUS.OK:  Success. Result is valid.
        - STATUS.HTTP_ERROR: If the controller responded with an error
                             status code.
         """
        dpIfList = []
        result = self.get_interfaces_cfg()
        status = result.get_status()
        if(status.eq(STATUS.OK)):
            cfg = result.get_data()
            p1 = 'interfaces'
            p2 = 'vyatta-interfaces-dataplane:dataplane'
            if(p1 in cfg and p2 in cfg):
                items = json.loads(cfg).get(p1).get(p2)
                p3 = 'tagnode'
                for item in items:
                    if p3 in item:
                        dpIfList.append(item[p3])
        return Result(status, dpIfList)

    def get_dataplane_interfaces_cfg(self):
        """ Return the configuration for the dataplane interfaces
            on the VRouter5600
         :return: A tuple: Status, configuration of dataplane interfaces
        :rtype: instance of the `Result` class (containing configuration data)
         - STATUS.CONN_ERROR: If the controller did not respond.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not
           provide
                                      any status.
        - STATUS.OK: Success. Result is valid.
        - STATUS.HTTP_ERROR: If the controller responded with an error
                             status code.
         """
        dpIfCfg = None
        result = self.get_interfaces_cfg()
        status = result.get_status()
        if(status.eq(STATUS.OK)):
            cfg = result.get_data()
            p1 = 'interfaces'
            p2 = 'vyatta-interfaces-dataplane:dataplane'
            if(p1 in cfg and p2 in cfg):
                dpIfCfg = json.loads(cfg).get(p1).get(p2)
        return Result(status, dpIfCfg)

    def get_dataplane_interface_cfg(self, ifName):
        """ Return the configuration for a dataplane interface
            on the VRouter5600
         :param string ifName: The interface name of the interface for which
                              configuration should be returned
        :return: A tuple: Status, configuration of dataplane interface
        :rtype: instance of the `Result` class (containing configuration data)
         - STATUS.CONN_ERROR: If the controller did not respond.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not
                                      provide any status.
        - STATUS.OK: Success. Result is valid.
        - STATUS.HTTP_ERROR: If the controller responded with an error
                             status code.
         """
        status = OperStatus()
        cfg = None
        templateModelRef = "vyatta-interfaces:" + \
            "interfaces/vyatta-interfaces-dataplane:" + \
            "dataplane/{}"
        modelref = templateModelRef.format(ifName)
        ctrl = self.ctrl
        url = ctrl.get_ext_mount_config_url(self.name)
        url += modelref
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            cfg = resp.content
            status.set_status(STATUS.OK)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return Result(status, cfg)

    def get_loopback_interfaces_list(self):
        """ Return a list of loopback interfaces on the VRouter5600
         :return: A tuple:  Status, list of loopback interface names
        :rtype: instance of the `Result` class
         - STATUS.CONN_ERROR: If the controller did not respond.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not
                                      provide any status.
        - STATUS.OK: Success. Result is valid.
        - STATUS.HTTP_ERROR: If the controller responded with an error
                             status code.
         """
        lbInterfaces = []
        result = self.get_interfaces_cfg()
        status = result.get_status()
        if(status.eq(STATUS.OK)):
            cfg = result.get_data()
            p1 = 'interfaces'
            p2 = 'vyatta-interfaces-loopback:loopback'
            if(p1 in cfg and p2 in cfg):
                items = json.loads(cfg).get(p1).get(p2)
                p3 = 'tagnode'
                for item in items:
                    if p3 in item:
                        lbInterfaces.append(item[p3])
        return Result(status, lbInterfaces)

    def get_loopback_interfaces_cfg(self):
        """ Return the configuration for the loopback interfaces
            on the VRouter5600
         :return: A tuple: Status, configuration of loopback interfaces
        :rtype: instance of the `Result` class (containing configuration data)
         - STATUS.CONN_ERROR: If the controller did not respond.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not
                                      provide any status.
        - STATUS.OK: Success. Result is valid.
        - STATUS.HTTP_ERROR: If the controller responded with an error
                             status code.
         """
        lbIfCfg = None
        result = self.get_interfaces_cfg()
        status = result.get_status()
        if(status.eq(STATUS.OK)):
            cfg = result.get_data()
            p1 = 'interfaces'
            p2 = 'vyatta-interfaces-loopback:loopback'
            if(p1 in cfg and p2 in cfg):
                lbIfCfg = json.loads(cfg).get(p1).get(p2)
        return Result(status, lbIfCfg)

    def get_loopback_interface_cfg(self, ifName):
        """ Return the configuration for a single loopback interface
            on the VRouter5600
         :param string ifName: The interface name of the interface for which
                              configuration should be returned
        :return: A tuple: Status, configuration of dataplane interface
        :rtype: instance of the `Result` class (containing configuration data)
         - STATUS.CONN_ERROR: If the controller did not respond.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not
                                      provide any status.
        - STATUS.OK: Success. Result is valid.
        - STATUS.HTTP_ERROR: If the controller responded with an error
                             status code.
         """
        status = OperStatus()
        templateModelRef = "vyatta-interfaces:" + \
            "interfaces/vyatta-interfaces-loopback:" + \
            "loopback/{}"
        modelref = templateModelRef.format(ifName)
        ctrl = self.ctrl
        url = ctrl.get_ext_mount_config_url(self.name)
        url += modelref
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            status.set_status(STATUS.OK)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return Result(status, resp)

    def set_vpn_cfg(self, vpn):
        """ Create/update VPN configuration
         :param vpn: instance of the 'Vpn' class
        :return: A tuple: Status, None
        :rtype: instance of the `Result` class
         - STATUS.CONN_ERROR: If the controller did not respond.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not
                                      provide any status.
        - STATUS.OK: Success. Result is valid.
        - STATUS.HTTP_ERROR: If the controller responded with an error
                             status code.
         """
        assert(isinstance(vpn, Vpn))
        status = OperStatus()
        ctrl = self.ctrl
        headers = {'content-type': 'application/yang.data+json'}
        url = ctrl.get_ext_mount_config_url(self.name)
        ext = vpn.get_url_extension()
        url += ext
        payload = vpn.get_payload()
        resp = ctrl.http_put_request(url, payload, headers)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200 or resp.status_code == 204):
            status.set_status(STATUS.OK)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return Result(status, None)

    def get_vpn_cfg(self):
        """Return VPN configuration of the VRouter5600.
         :return: A tuple: Status, JSON for VPN configuration.
        :rtype: instance of the `Result` class (containing configuration data)
         - STATUS.CONN_ERROR: If the controller did not respond.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did
                                      not provide any status.
        - STATUS.OK: Success. Result is valid.
        - STATUS.HTTP_ERROR: If the controller responded with an error
                             status code.
         """
        status = OperStatus()
        url_ext = "vyatta-security:security/vyatta-security-vpn-ipsec:vpn"
        cfg = None
        ctrl = self.ctrl
        myname = self.name
        url = ctrl.get_ext_mount_config_url(myname)
        url += url_ext
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            cfg = resp.content
            status.set_status(STATUS.OK)
        elif (resp.status_code == 404):
            status.set_status(STATUS.DATA_NOT_FOUND, resp)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return Result(status, cfg)

    def delete_vpn_cfg(self):
        """ Delete VPN configuration """
        status = OperStatus()
        url_ext = "vyatta-security:security/vyatta-security-vpn-ipsec:vpn"
        ctrl = self.ctrl
        myname = self.name
        url = ctrl.get_ext_mount_config_url(myname)
        url += url_ext
        resp = ctrl.http_delete_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            status.set_status(STATUS.OK)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return Result(status, None)

    def set_openvpn_interface_cfg(self, openvpn_interface):
        assert(isinstance(openvpn_interface, OpenVpnInterface))
        status = OperStatus()
        ctrl = self.ctrl
        headers = {'content-type': 'application/yang.data+json'}
        url = ctrl.get_ext_mount_config_url(self.name)
        obj = openvpn_interface
        payload = obj.get_payload()
        ext = openvpn_interface.get_url_extension()
        url += ext
        resp = ctrl.http_put_request(url, payload, headers)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200 or resp.status_code == 204):
            status.set_status(STATUS.OK)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return Result(status, None)

    def get_openvpn_interfaces_cfg(self):
        openVpnIfCfg = None
        result = self.get_interfaces_cfg()
        status = result.get_status()
        if(status.eq(STATUS.OK)):
            cfg = result.get_data()
            p1 = 'interfaces'
            p2 = 'vyatta-interfaces-openvpn:openvpn'
            if(p1 in cfg and p2 in cfg):
                openVpnIfCfg = json.loads(cfg).get(p1).get(p2)
            else:
                status.set_status(STATUS.DATA_NOT_FOUND)
        return Result(status, openVpnIfCfg)
        pass

    def get_openvpn_interface_cfg(self, ifName):
        status = OperStatus()
        templateModelRef = "vyatta-interfaces:" + \
            "interfaces/vyatta-interfaces-openvpn:" + \
            "openvpn/{}"
        cfg = None
        modelref = templateModelRef.format(ifName)
        ctrl = self.ctrl
        url = ctrl.get_ext_mount_config_url(self.name)
        url += modelref
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            cfg = resp.content
            status.set_status(STATUS.OK)
        elif (resp.status_code == 404):
            status.set_status(STATUS.DATA_NOT_FOUND, resp)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return Result(status, cfg)

    def delete_openvpn_interface_cfg(self, ifName):
        status = OperStatus()
        templateModelRef = "vyatta-interfaces:" + \
            "interfaces/vyatta-interfaces-openvpn:" + \
            "openvpn/{}"
        modelref = templateModelRef.format(ifName)
        ctrl = self.ctrl
        url = ctrl.get_ext_mount_config_url(self.name)
        url += modelref
        resp = ctrl.http_delete_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            status.set_status(STATUS.OK)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return Result(status, resp)

    def set_protocols_static_route_cfg(self, static_route):
        assert(isinstance(static_route, StaticRoute))
        status = OperStatus()
        ctrl = self.ctrl
        headers = {'content-type': 'application/yang.data+json'}
        url = ctrl.get_ext_mount_config_url(self.name)
        obj = static_route
        payload = obj.get_payload()
        ext = static_route.get_url_extension()
        url += ext
        resp = ctrl.http_put_request(url, payload, headers)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200 or resp.status_code == 204):
            status.set_status(STATUS.OK)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return Result(status, None)

    def get_protocols_cfg(self, model_ref=None):
        status = OperStatus()
        templateModelRef = "vyatta-protocols:protocols"
        cfg = None
        ctrl = self.ctrl
        url = ctrl.get_ext_mount_config_url(self.name)
        url += templateModelRef
        if (model_ref is not None):
            url += "/" + model_ref
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            cfg = resp.content
            status.set_status(STATUS.OK)
        elif (resp.status_code == 404):
            status.set_status(STATUS.DATA_NOT_FOUND, resp)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return Result(status, cfg)

    def delete_protocols_cfg(self, model_ref=None):
        status = OperStatus()
        url_ext = "vyatta-protocols:protocols"
        ctrl = self.ctrl
        myname = self.name
        url = ctrl.get_ext_mount_config_url(myname)
        url += url_ext
        if (model_ref is not None):
            url += "/" + model_ref
        resp = ctrl.http_delete_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            status.set_status(STATUS.OK)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return Result(status, None)

    def get_protocols_static_cfg(self):
        model_ref = "vyatta-protocols-static:static"
        return self.get_protocols_cfg(model_ref)

    def delete_protocols_static_cfg(self):
        """ Delete protocols static configuration """
        model_ref = "vyatta-protocols-static:static"
        return self.delete_protocols_cfg(model_ref)

    def get_protocols_static_interface_route_cfg(self, ip_prefix):
        templateModelRef = "vyatta-protocols-static:static/interface-route/{}"
        model_ref = templateModelRef.format(ip_prefix.replace("/", "%2F"))
        return self.get_protocols_cfg(model_ref)

    def delete_protocols_static_interface_route_cfg(self, ip_prefix):
        templateModelRef = "vyatta-protocols-static:static/interface-route/{}"
        model_ref = templateModelRef.format(ip_prefix.replace("/", "%2F"))
        return self.delete_protocols_cfg(model_ref)
