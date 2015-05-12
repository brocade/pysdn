"""
Copyright (c) 2015,  BROCADE COMMUNICATIONS SYSTEMS, INC

All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
 are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this 
list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, 
this list of conditions and the following disclaimer in the documentation and/or 
other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors 
may be used to endorse or promote products derived from this software without 
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE 
GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) 
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT 
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT 
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.




vrouter5600.py: vRouter-5600 specific properties and communication methods


"""

import string
import json

from pybvc.controller.netconfnode import NetconfNode
from pybvc.common.status import OperStatus, STATUS
from pybvc.common.utils import remove_empty_from_dict


#===============================================================================
# Class 'VRouter5600'
#===============================================================================
class VRouter5600(NetconfNode):
    """Class that represents an instance of vRouter-5600 (NETCONF capable server device).

        :param ctrl: :class:`pybvc.controller.controller.Controller`
        :param string name: The name of the vrouter5600
        :param string ipAddr:  The ip address for the vrouter5600 
        :param int portNum:  The port number to communicate NETCONF to the vrouter5600
        :param string adminName:  The username to authenticate setup of the NETCONF communication 
        :param string adminPassword:  The password to authenticate setup of the NETCONF communication 
        :param boolean tcpOnly:  Use TCP only or not. 
        :return: The newly created vrouter5600 instance.
        :rtype: :class:`pybvc.netconfdev.vrouter.vrouter5600.VRouter5600`
        """
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, ctrl, name, ipAddr, portNum, adminName, adminPassword, tcpOnly=False):
        super(VRouter5600, self).__init__(ctrl, name, ipAddr, portNum, adminName, adminPassword, tcpOnly)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def to_string(self):
        """Returns string representation of this object."""
        return str(vars(self))

    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def to_json(self):
        """Returns JSON representation of this object."""
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4) 

    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_schemas(self):
        """Return a list of YANG schemas for this VRouter5600

        :return: A tuple:  Status, list of YANG schemas for the VRouter5600.
        :rtype: :class:`pybvc.common.status.OperStatus`, JSON listing information about the YANG schemas for the node

        - STATUS.CONN_ERROR:  if the controller did not respond. List is empty.
        - STATUS.CTRL_INTERNAL_ERROR:  if the controller responded but did not provide any status. List is empty.
        - STATUS.OK:  Success. List is valid.  
        - STATUS.HTTP_ERROR:  if the controller responded with an error status code. 

        """
        ctrl = self.ctrl
        myname = self.name
        return ctrl.get_schemas(myname)

    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_schema(self, schemaId, schemaVersion):
        """Return a YANG schema for the indicated schema on the VRouter5600.

        :param string schemaId: id of schema
        :param string schemaVersion: version of the schema
        :return: A tuple:  Status, YANG schema.
        :rtype: :class:`pybvc.common.status.OperStatus`, YANG schema 

        - STATUS.CONN_ERROR:  if the controller did not respond. schema is empty.
        - STATUS.CTRL_INTERNAL_ERROR:  if the controller responded but did not provide any status. schema is empty.
        - STATUS.OK:  Success. result is valid.  
        - STATUS.DATA_NOT_FOUND:  Data missing or in unexpected format.  
        - STATUS.HTTP_ERROR:  if the controller responded with an error status code. 

        """ 
        ctrl = self.ctrl
        myname = self.name
        return ctrl.get_schema(myname, schemaId, schemaVersion)

    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_cfg(self):        
        """Return configuration of the VRouter5600.

        :return: A tuple:  Status, JSON for configuration.
        :rtype: :class:`pybvc.common.status.OperStatus`, JSON 

        - STATUS.CONN_ERROR:  if the controller did not respond. schema is empty.
        - STATUS.CTRL_INTERNAL_ERROR:  if the controller responded but did not provide any status. schema is empty.
        - STATUS.OK:  Success. result is valid.  
        - STATUS.HTTP_ERROR:  if the controller responded with an error status code. 

        """ 
        status = OperStatus()
        cfg = None
        ctrl = self.ctrl
        myname = self.name
        url = ctrl.get_ext_mount_config_url(myname)

        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            cfg = resp.content
            status.set_status(STATUS.OK)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return (status, cfg)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_firewalls_cfg(self):        
        """Return firewall configuration of the VRouter5600.

        :return: A tuple:  Status, JSON for firewall configuration.
        :rtype: :class:`pybvc.common.status.OperStatus`, JSON 

        - STATUS.CONN_ERROR:  if the controller did not respond. schema is empty.
        - STATUS.CTRL_INTERNAL_ERROR:  if the controller responded but did not provide any status. schema is empty.
        - STATUS.OK:  Success. result is valid.  
        - STATUS.HTTP_ERROR:  if the controller responded with an error status code. 

        """ 
        status = OperStatus()
        cfg = None
        templateModelRef = "vyatta-security:security/vyatta-security-firewall:firewall"        
        modelref = templateModelRef       
        ctrl = self.ctrl
        myname = self.name
        url = ctrl.get_ext_mount_config_url(myname)
        url += modelref
        
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            cfg = resp.content
            status.set_status(STATUS.OK)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return (status, cfg)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_firewall_instance_cfg(self, instance):        
        """Return configuration for a specific firewall on the VRouter5600.

        :param instance: Firewall :class:`pybvc.netconfdev.vrouter.vrouter5600.Firewall` 
        :return: A tuple:  Status, JSON for firewall configuration.
        :rtype: :class:`pybvc.common.status.OperStatus`, JSON 

        - STATUS.CONN_ERROR:  if the controller did not respond. schema is empty.
        - STATUS.CTRL_INTERNAL_ERROR:  if the controller responded but did not provide any status. schema is empty.
        - STATUS.OK:  Success. result is valid.  
        - STATUS.HTTP_ERROR:  if the controller responded with an error status code. 

        """ 
        status = OperStatus()
        cfg = None
        templateModelRef = "vyatta-security:security/vyatta-security-firewall:firewall/name/{}"     
        modelref = templateModelRef.format(instance)
        ctrl = self.ctrl
        myname = self.name
        url = ctrl.get_ext_mount_config_url(myname)
        url += modelref
        
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            cfg = resp.content
            status.set_status(STATUS.OK)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return (status, cfg)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def create_firewall_instance(self, fwInstance):        
        """Create a firewall on the VRouter5600.

        :param fwInstance: Firewall :class:`pybvc.netconfdev.vrouter.vrouter5600.Firewall` 
        :return: A tuple:  Status, None.
        :rtype: :class:`pybvc.common.status.OperStatus`, JSON 

        - STATUS.CONN_ERROR:  if the controller did not respond. schema is empty.
        - STATUS.CTRL_INTERNAL_ERROR:  if the controller responded but did not provide any status. schema is empty.
        - STATUS.OK:  Success. result is valid.  
        - STATUS.HTTP_ERROR:  if the controller responded with an error status code. 

        """
        status = OperStatus()
        ctrl = self.ctrl
        myname = self.name
        url = ctrl.get_ext_mount_config_url(myname)
        headers = {'content-type': 'application/yang.data+json'}
        payload = fwInstance.get_payload()
        
        resp = ctrl.http_post_request(url, payload, headers)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200 or resp.status_code == 204):
            status.set_status(STATUS.OK)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return (status, None)
    
    #---------------------------------------------------------------------------
    # TBD
    #---------------------------------------------------------------------------
    def add_firewall_instance_rule(self, fwInstance, fwRule):
        pass
    
    #---------------------------------------------------------------------------
    # TBD
    #---------------------------------------------------------------------------
    def update_firewall_instance_rule(self, fwInstance, fwRule):
        pass
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def delete_firewall_instance(self, fwInstance):
        """Delete a firewall from the VRouter5600.

        :param fwInstance: Firewall :class:`pybvc.netconfdev.vrouter.vrouter5600.Firewall` 
        :return: A tuple:  Status, None.
        :rtype: :class:`pybvc.common.status.OperStatus`, None

        - STATUS.CONN_ERROR:  if the controller did not respond. schema is empty.
        - STATUS.CTRL_INTERNAL_ERROR:  if the controller responded but did not provide any status. schema is empty.
        - STATUS.OK:  Success. result is valid.  
        - STATUS.HTTP_ERROR:  if the controller responded with an error status code. 

        """
        status = OperStatus()
        ctrl = self.ctrl
        myname = self.name
        url = ctrl.get_ext_mount_config_url(myname)
        ext = fwInstance.get_url_extension()
        url += ext
        rules = fwInstance.get_rules()
        p1 = "/name/"
        url += p1
        for item in rules:
            name = item.get_name()
            resp = ctrl.http_delete_request(url + name, data=None, headers=None)
            if(resp == None):
                status.set_status(STATUS.CONN_ERROR)
                break
            elif(resp.content == None):
                status.set_status(STATUS.CTRL_INTERNAL_ERROR)
                break
            elif (resp.status_code == 200):
                status.set_status(STATUS.OK)
            else:
                status.set_status(STATUS.HTTP_ERROR, resp)
                break
            
        return (status, None)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_dataplane_interface_firewall(self, ifName,
                                         inboundFwName, outboundFwName):
        """Set a firewall for inbound, outbound or both for a dataplane interface on the VRouter5600.

        :param string ifName: The dataplane interface to attache a firewall. 
        :param string inboundFwName: None or name of firewall on VRouter5600 to use for traffic inbound towards router.   
        :param string outboundFwName: None or name of firewall on VRouter5600 to use for traffic outbound from router.   
        :return: A tuple:  Status, None.
        :rtype: :class:`pybvc.common.status.OperStatus`, None except when STATUS.HTTP_ERROR

        - STATUS.CONN_ERROR:  if the controller did not respond. schema is empty.
        - STATUS.CTRL_INTERNAL_ERROR:  if the controller responded but did not provide any status. schema is empty.
        - STATUS.OK:  Success. result is valid.  
        - STATUS.HTTP_ERROR:  if the controller responded with an error status code. 

        """
        status = OperStatus()
        ctrl = self.ctrl
        headers = {'content-type': 'application/yang.data+json'}
        url = ctrl.get_ext_mount_config_url(self.name)        
        obj = DataplaneInterfaceFirewall(ifName)
        
        if (inboundFwName != None):
            obj.add_in_item(inboundFwName)
        
        if (outboundFwName != None):
            obj.add_out_item(outboundFwName)
        
        payload = obj.get_payload()
        urlext = obj.get_url_extension()
        
        resp = ctrl.http_put_request(url + urlext, payload, headers)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            status.set_status(STATUS.OK)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return (status, None)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def delete_dataplane_interface_firewall(self, ifName):        
        """Delete both inbound and outbound firewalls for a dataplane interface on the VRouter5600.

        :param string ifName: The dataplane interface to attach a firewall. 
        :return: A tuple:  Status, Response from VRouter5600.
        :rtype: :class:`pybvc.common.status.OperStatus`, None except when STATUS.HTTP_ERROR

        - STATUS.CONN_ERROR:  if the controller did not respond. schema is empty.
        - STATUS.CTRL_INTERNAL_ERROR:  if the controller responded but did not provide any status. schema is empty.
        - STATUS.OK:  Success. result is valid.  
        - STATUS.HTTP_ERROR:  if the controller responded with an error status code. 

        """
        status = OperStatus()
        templateModelRef = "vyatta-interfaces:interfaces/vyatta-interfaces-dataplane:dataplane/{}/vyatta-security-firewall:firewall/"
        modelref = templateModelRef.format(ifName)
        myname = self.name
        ctrl = self.ctrl
        url = ctrl.get_ext_mount_config_url(myname)  
        
        resp = ctrl.http_delete_request(url + modelref, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            status.set_status(STATUS.OK)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return (status, None)
    
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_interfaces_list(self):
        """Get the list of interfaces on the VRouter5600.

        :return: A tuple:  Status, list of interface names.
        :rtype: :class:`pybvc.common.status.OperStatus`, list of strings

        - STATUS.CONN_ERROR:  if the controller did not respond. schema is empty.
        - STATUS.CTRL_INTERNAL_ERROR:  if the controller responded but did not provide any status. schema is empty.
        - STATUS.OK:  Success. result is valid.  
        - STATUS.HTTP_ERROR:  if the controller responded with an error status code. 

        """
        ifList = []
        
        result = self.get_interfaces_cfg()
        status = result[0]
        if(status.eq(STATUS.OK)):
            cfg = result[1]
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
        
        return (status, ifList)
    
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_interfaces_cfg(self):        
        """Return the configuration for the interfaces on the VRouter5600

        :return: A tuple:  Status, configuration of the interfaces
        :rtype: :class:`pybvc.common.status.OperStatus`, None or JSON describing configuration

        - STATUS.CONN_ERROR:  if the controller did not respond. schema is empty.
        - STATUS.CTRL_INTERNAL_ERROR:  if the controller responded but did not provide any status. schema is empty.
        - STATUS.OK:  Success. result is valid.  
        - STATUS.HTTP_ERROR:  if the controller responded with an error status code. 

        """
        status = OperStatus()
        cfg = None
        templateModelRef = "vyatta-interfaces:interfaces"        
        modelref = templateModelRef       
        ctrl = self.ctrl
        url = ctrl.get_ext_mount_config_url(self.name)
        url += modelref        
        
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            cfg = resp.content
            status.set_status(STATUS.OK)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return (status, cfg)
    
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_dataplane_interfaces_list(self):        
        """Return a list of interfaces on the VRouter5600

        :return: A tuple:  Status, list of interface names
        :rtype: :class:`pybvc.common.status.OperStatus`, None or list of strings 

        - STATUS.CONN_ERROR:  if the controller did not respond. schema is empty.
        - STATUS.CTRL_INTERNAL_ERROR:  if the controller responded but did not provide any status. schema is empty.
        - STATUS.OK:  Success. result is valid.  
        - STATUS.HTTP_ERROR:  if the controller responded with an error status code. 

        """
        dpIfList = []

        result = self.get_interfaces_cfg()
        status = result[0]
        if(status.eq(STATUS.OK)):
            cfg = result[1]
            p1 = 'interfaces'
            p2 = 'vyatta-interfaces-dataplane:dataplane'
            if(p1 in cfg and p2 in cfg):
                items = json.loads(cfg).get(p1).get(p2)
                p3 = 'tagnode'
                for item in items:
                    if p3 in item:
                        dpIfList.append(item[p3])
        
        return (status, dpIfList)
    

    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_dataplane_interfaces_cfg(self):
        """Return the configuration for the dataplane interfaces on the VRouter5600

        :return: A tuple:  Status, configuration of dataplane interfaces
        :rtype: :class:`pybvc.common.status.OperStatus`, None or JSON 

        - STATUS.CONN_ERROR:  if the controller did not respond. schema is empty.
        - STATUS.CTRL_INTERNAL_ERROR:  if the controller responded but did not provide any status. schema is empty.
        - STATUS.OK:  Success. result is valid.  
        - STATUS.HTTP_ERROR:  if the controller responded with an error status code. 

        """
        dpIfCfg = None
        
        result = self.get_interfaces_cfg()
        status = result[0]
        if(status.eq(STATUS.OK)):
            cfg = result[1]
            p1 = 'interfaces'
            p2 = 'vyatta-interfaces-dataplane:dataplane'
            if(p1 in cfg and p2 in cfg):
                dpIfCfg = json.loads(cfg).get(p1).get(p2)

        return (status, dpIfCfg)
    

    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_dataplane_interface_cfg(self, ifName): 
        """Return the configuration for a dataplane interface on the VRouter5600

        :param string ifName: The interface name of the interface for which configuration should be returned
        :return: A tuple:  Status, configuration of dataplane interface
        :rtype: :class:`pybvc.common.status.OperStatus`, None or JSON 

        - STATUS.CONN_ERROR:  if the controller did not respond. schema is empty.
        - STATUS.CTRL_INTERNAL_ERROR:  if the controller responded but did not provide any status. schema is empty.
        - STATUS.OK:  Success. result is valid.  
        - STATUS.HTTP_ERROR:  if the controller responded with an error status code. 

        """       
        status = OperStatus()
        cfg = None
        templateModelRef = "vyatta-interfaces:interfaces/vyatta-interfaces-dataplane:dataplane/{}"
        modelref = templateModelRef.format(ifName)
        ctrl = self.ctrl
        url = ctrl.get_ext_mount_config_url(self.name)
        url += modelref

        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            cfg = resp.content
            status.set_status(STATUS.OK)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return (status, cfg)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_loopback_interfaces_list(self):
        """Return a list of loopback interfaces on the VRouter5600

        :return: A tuple:  Status, list of loopback interface names
        :rtype: :class:`pybvc.common.status.OperStatus`, None or list of strings 

        - STATUS.CONN_ERROR:  if the controller did not respond. schema is empty.
        - STATUS.CTRL_INTERNAL_ERROR:  if the controller responded but did not provide any status. schema is empty.
        - STATUS.OK:  Success. result is valid.  
        - STATUS.HTTP_ERROR:  if the controller responded with an error status code. 

        """
        lbInterfaces = []
        
        result = self.get_interfaces_cfg()
        status = result[0]
        if(status.eq(STATUS.OK)):
            cfg = result[1]
            p1 = 'interfaces'
            p2 = 'vyatta-interfaces-loopback:loopback'
            if(p1 in cfg and p2 in cfg):
                items = json.loads(cfg).get(p1).get(p2)
                p3 = 'tagnode'
                for item in items:
                    if p3 in item:
                        lbInterfaces.append(item[p3])
      
        return (status, lbInterfaces)        
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_loopback_interfaces_cfg(self):
        """Return the configuration for the loopback interfaces on the VRouter5600

        :return: A tuple:  Status, configuration of loopback interfaces
        :rtype: :class:`pybvc.common.status.OperStatus`, None or JSON 

        - STATUS.CONN_ERROR:  if the controller did not respond. schema is empty.
        - STATUS.CTRL_INTERNAL_ERROR:  if the controller responded but did not provide any status. schema is empty.
        - STATUS.OK:  Success. result is valid.  
        - STATUS.HTTP_ERROR:  if the controller responded with an error status code. 

        """
        lbIfCfg = None

        result = self.get_interfaces_cfg()
        status = result[0]
        if(status.eq(STATUS.OK)):
            cfg = result[1]
            p1 = 'interfaces'
            p2 = 'vyatta-interfaces-loopback:loopback'
            if(p1 in cfg and p2 in cfg):
                lbIfCfg = json.loads(cfg).get(p1).get(p2)
        
        return (status, lbIfCfg)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_loopback_interface_cfg(self, ifName):        
        """Return the configuration for a single loopback interface on the VRouter5600

        :param string ifName: The interface name of the interface for which configuration should be returned
        :return: A tuple:  Status, configuration of dataplane interface
        :rtype: :class:`pybvc.common.status.OperStatus`, None or JSON 

        - STATUS.CONN_ERROR:  if the controller did not respond. schema is empty.
        - STATUS.CTRL_INTERNAL_ERROR:  if the controller responded but did not provide any status. schema is empty.
        - STATUS.OK:  Success. result is valid.  
        - STATUS.HTTP_ERROR:  if the controller responded with an error status code. 

        """ 
        status = OperStatus()
        templateModelRef = "vyatta-interfaces:interfaces/vyatta-interfaces-loopback:loopback/{}"
        modelref = templateModelRef.format(ifName)
        ctrl = self.ctrl
        url = ctrl.get_ext_mount_config_url(self.name)
        url += modelref

        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            status.set_status(STATUS.OK)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return (status, resp)

#===============================================================================
# Class 'Firewall'
#===============================================================================
class Firewall():
    """ A class that defines a Firewall. """
    _mn1 = "vyatta-security:security"
    _mn2 = "vyatta-security-firewall:firewall"
    def __init__(self):
        self.name = []
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def to_string(self):
        """ Return Firewall as a string """
        return str(vars(self))
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def to_json(self):
        """ Return Firewall as JSON """
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4) 
    
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_payload(self):
        s = self.to_json()
        s = string.replace(s, 'typename', 'type-name')
        d1 = json.loads(s)
        d2 = remove_empty_from_dict(d1)
        payload = {self._mn1:{self._mn2:d2}}
        return json.dumps(payload, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_url_extension(self):
        return (self._mn1 + "/" +  self._mn2)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def add_rules(self, rules):
        """Add rules to Firewall.

        :param rules: Rules to be added to Firewall.  :class:`pybvc.netconfdev.vrouter.vrouter5600.Rules`
        """ 
        self.name.append(rules)
        
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_rules(self):
        """Return the Rules of a Firewall

        :return: Rules of the Firewall 
        :rtype: :class:`pybvc.netconfdev.vrouter.vrouter5600.Rules`

        """ 
        rules = []
        for item in self.name:
            rules.append(item)
        return rules

#===============================================================================
# Class 'Rules'
#===============================================================================
class Rules():
    """The class that defines firewall Rules.

    :param string name: The name for the firewall Rule 

    """ 
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, name):
        self.tagnode = name
        self.rule = []
        
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def to_string(self):
        """ return the firewall Rules as a string """
        return str(vars(self))
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def to_json(self):
        """ Return the firewall Rules as JSON """
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def add_rule(self, rule):
        """Add a single firewall rule to Rules.

        :param rule: The rule to add to this Rules instance.  :class:`pybvc.netconfdev.vrouter.vrouter5600.Rule`
        :return: None

        """ 
        self.rule.append(rule)
        
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_name(self):
        """Return the name of the Rules instance.

        :return: The name of the Rules instance.
        :rtype:  string

        """ 
        return self.tagnode 

#===============================================================================
# Class 'Rule'
#===============================================================================
class Rule():
    """The class that defines a Rule.

    :param int number: The number for the Rule.

    """ 
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, number):
        self.tagnode = number
        self.source = Object()
        self.icmp = Object()
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def to_string(self):
        """ Return Rule as string """
        return str(vars(self))
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def to_json(self):
        """ Return Rule as JSON """
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def add_action(self, action):
        """Add an action to the Rule.

        :param string action: The action to be taken for the Rule:  accept, drop
        :return: No return value

        """ 
        self.action = action
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def add_source_address(self, srcAddr):
        """Add source address to Rule. If the packet matches this then the action is taken.

        :param string srcAddr: The IP address to match against the source IP of packet.
        :return: No return value

        """ 
        self.source.address = srcAddr

    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def add_icmp_typename(self, typeName):
        """Add typename for ICMP to Rule.  If the packet matches this then the action is taken.

        :param string typeName: The ICMP type name to test packet against.
        :return: No return value.
        """
        self.protocol = "icmp"
        self.icmp.typename = typeName


#===============================================================================
# Class 'DataplaneInterfaceFirewall'
#===============================================================================
class DataplaneInterfaceFirewall():
    mn1 = "vyatta-interfaces:interfaces"
    mn2 = "vyatta-interfaces-dataplane:dataplane"
    mn3 = "vyatta-security-firewall:firewall"

    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, ifName):
        self.tagnode = ifName
        self.firewall = Object()
        self.firewall.inlist = []
        self.firewall.outlist = []
        
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def add_in_item(self, name):
        self.firewall.inlist.append(name)

    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def add_out_item(self, name):
        self.firewall.outlist.append(name)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    def get_url_extension(self):
        return (self.mn1 + "/" + self.mn2 + "/" +  self.tagnode)

    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_name(self):
        return self.tagnode
     
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_payload(self):        
        s = self.to_json()
        s = string.replace(s, 'firewall', self.mn3)
        s = string.replace(s, 'inlist', "in")
        s = string.replace(s, 'outlist', "out")
        obj = json.loads(s)
        payload = {self.mn2:obj}
        return json.dumps(payload, default=lambda o: o.__dict__, sort_keys=True, indent=4)

#===============================================================================
# Class 'Object'
#===============================================================================
class Object():
    pass
        
