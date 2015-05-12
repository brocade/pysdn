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


"""
import string
import json
#import collections
import sys

from collections import OrderedDict

from pybvc.controller.openflownode import OpenflowNode
from pybvc.common.status import OperStatus, STATUS
from pybvc.common.utils import find_key_values_in_dict
from pybvc.common.utils import replace_str_value_in_dict
from pybvc.common.utils import find_key_value_in_dict
from pybvc.common.utils import find_dict_in_list
from pybvc.common.utils import remove_empty_from_dict
#from pybvc.common.utils import remove_unset_values_from_nested_dict
from pybvc.common.utils import stripNone
    
#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class OFSwitch(OpenflowNode):
    """Class that represents an instance of 'OpenFlow Switch' (OpenFlow capable device)."""
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, ctrl=None, name=None, dpid=None):
        """Initializes this object properties."""
        super(OFSwitch, self).__init__(ctrl, name)
        self.dpid = dpid
        self.ports=[]
    
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
    def get_switch_info(self):        
        status = OperStatus()
        info = {}
        ctrl = self.ctrl
        myname = self.name
        url = ctrl.get_node_operational_url(myname)
        
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            dictionary = json.loads(resp.content)
            p1 = 'node'
            if (p1 in dictionary):
                p2 = 'flow-node-inventory:manufacturer'
                vlist = find_key_values_in_dict(dictionary, p2)
                if (len(vlist) != 0):
                    info['manufacturer'] = vlist[0]
                
                p3 = 'flow-node-inventory:serial-number'
                vlist = find_key_values_in_dict(dictionary, p3)
                if (len(vlist) != 0):
                    info['serial-number'] = vlist[0]
                
                p4 = 'flow-node-inventory:software'
                vlist = find_key_values_in_dict(dictionary, p4)
                if (len(vlist) != 0):
                    info['software'] = vlist[0]
                
                p5 = 'flow-node-inventory:hardware'
                vlist = find_key_values_in_dict(dictionary, p5)
                if (len(vlist) != 0):
                    info['hardware'] = vlist[0]
                
                p6 = 'flow-node-inventory:description'
                vlist = find_key_values_in_dict(dictionary, p6)
                if (len(vlist) != 0):
                    info['description'] = vlist[0]
                
                status.set_status(STATUS.OK)
            else:
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return (status, info)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_features_info(self):        
        status = OperStatus()
        info = {}
        ctrl = self.ctrl
        myname = self.name
        url = ctrl.get_node_operational_url(myname)
        
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            dictionary = json.loads(resp.content)
            p2 = 'flow-node-inventory:switch-features'
            vlist = find_key_values_in_dict(dictionary, p2)
            if (len(vlist) != 0 and (type(vlist[0]) is dict)):
                p3 = 'flow-node-inventory:flow-feature-capability-'
                info = replace_str_value_in_dict(vlist[0], p3, '')
                status.set_status(STATUS.OK)
            else:
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return (status, info)
    
    def get_ports_list(self):
        status = OperStatus()
        plist = []
        ctrl = self.ctrl
        myname = self.name
        url = ctrl.get_node_operational_url(myname)
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            obj = json.loads(resp.content)
            p1 = 'node'
            if(p1 in obj and isinstance(obj[p1], list)):
                vlist = obj[p1]
                p2 = 'node-connector'
                d = find_dict_in_list(vlist, p2)
                if (d != None) and isinstance(d[p2], list):
                    items = d[p2]
                    p3 = 'flow-node-inventory:port-number'
                    for item in items:
                        if(isinstance(item, dict) and item.has_key(p3)):
                            plist.append(item[p3])
                status.set_status(STATUS.OK)
            else:
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return (status, plist)
    
    def get_port_brief_info(self, portnum):
        pass
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_ports_brief_info(self):        
        status = OperStatus()
        info = []
        ctrl = self.ctrl
        myname = self.name
        url = ctrl.get_node_operational_url(myname)
        
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            dictionary = json.loads(resp.content)
            p1 = 'node-connector'
            vlist = find_key_values_in_dict(dictionary, p1)
            if (len(vlist) != 0 and (type(vlist[0]) is list)):
                try:
                    for item in vlist[0]:
                        port = {}
                        port['id'] = item['id']
                        port['number'] = item['flow-node-inventory:port-number']
                        port['name'] = item['flow-node-inventory:name']
                        port['MAC address'] = item['flow-node-inventory:hardware-address']
                        s = item['flow-node-inventory:current-feature']
                        port['current feature'] = s.upper()
                        info.append(port)
                    status.set_status(STATUS.OK)
                except () as e:
                    print "Error: " + repr(e)
                    status.set_status(STATUS.DATA_NOT_FOUND)
            else:
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return (status, info)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def add_modify_flow(self, flow_entry):
        status = OperStatus()
        templateUrlExt = "/table/{}/flow/{}"
        headers = {'content-type': 'application/yang.data+json'}
        if isinstance(flow_entry, FlowEntry):
            ctrl = self.ctrl
            url = ctrl.get_node_config_url(self.name)
            urlext = templateUrlExt.format(flow_entry.get_flow_table_id(),
                                           flow_entry.get_flow_id())
            url += urlext
#            print url
            payload = flow_entry.get_payload()
#            print payload 
            resp = ctrl.http_put_request(url, payload, headers)
#            print resp
            if(resp == None):
                status.set_status(STATUS.CONN_ERROR)
            elif(resp.content == None):
                status.set_status(STATUS.CTRL_INTERNAL_ERROR)
            elif (resp.status_code == 200):
                status.set_status(STATUS.OK)
        else:
            print "Error !!!"
            status.set_status(STATUS.MALFORM_DATA)
        return (status, None)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_port_detail_info(self, portnum):
        status = OperStatus()
        info = {}
        templateUrlExt = "/node-connector/{}:{}"
        urlext = templateUrlExt.format(self.name, portnum)
        ctrl = self.ctrl
        url = ctrl.get_node_operational_url(self.name)
        url += urlext
        
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            dictionary = json.loads(resp.content)
            try:
                vlist = dictionary['node-connector']
                if (len(vlist) != 0 and (type(vlist[0]) is dict)):
                    info = vlist[0]
                    status.set_status(STATUS.OK)
                else:
                    status.set_status(STATUS.DATA_NOT_FOUND)
            except () as e:
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return (status, info)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_flows(self, tableid, operational=True):
        status = OperStatus()
        flows = {}
        url = ""
        templateUrlExt = "/flow-node-inventory:table/{}"
        urlext = templateUrlExt.format(tableid)
        ctrl = self.ctrl
        if (operational):
            url = ctrl.get_node_operational_url(self.name)
        else:
            url = ctrl.get_node_config_url(self.name)        
        url += urlext
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            dictionary = json.loads(resp.content)
            try:
                vlist = dictionary['flow-node-inventory:table']
                if (len(vlist) != 0 and (type(vlist[0]) is dict) and ('flow' in vlist[0])):
                    flows = vlist[0]['flow']
                    status.set_status(STATUS.OK)
                else:
                    status.set_status(STATUS.DATA_NOT_FOUND)
            except () as e:
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return (status, flows)    
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_operational_flows(self, tableid):
        flows = {}
        result = self.get_flows(tableid, operational=True)
        status = result[0]
        if(status.eq(STATUS.OK) == True):
            flows = result[1]
        
        return (status, flows)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_operational_flows_ovs_syntax(self, tableid, sort=None):
        ovsflows = []
        result = self.get_operational_flows(tableid)
        status = result[0]
        if(status.eq(STATUS.OK) == True):
            flist = result[1]
            if (sort == True):
                flist.sort(key=self.__getPriorityKey)                
            for item in flist:
                f = self.odl_to_ovs_flow_syntax(item)
                ovsflows.append(f)

        return (status, ovsflows)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_configured_flows(self, tableid):
        flows = {}
        result = self.get_flows(tableid, operational=False)
        status = result[0]
        if(status.eq(STATUS.OK) == True):
            flows = result[1]
        
        return (status, flows)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_configured_flow(self, table_id, flow_id):
        status = OperStatus()
        flow = {}
        templateUrlExt = "/table/{}/flow/{}"
        ctrl = self.ctrl
        url = ctrl.get_node_config_url(self.name)
        urlext = templateUrlExt.format(table_id, flow_id)
        url += urlext
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
#            print resp.content
            flow = json.loads(resp.content)
            status.set_status(STATUS.OK)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return (status, flow)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_configured_flows_ovs_syntax(self, tableid, sort=None):
        ovsflows = []
        result = self.get_configured_flows(tableid)
        status = result[0]
        if(status.eq(STATUS.OK) == True):
            flist = result[1]
            if (sort == True):
                flist.sort(key=self.__getPriorityKey)                
            for item in flist:
                f = self.odl_to_ovs_flow_syntax(item)
                ovsflows.append(f)

        return (status, ovsflows)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def odl_to_ovs_flow_syntax(self, odlflow):
        od = OrderedDict()
#        print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
#        print (odlflow)
        
        f = odlflow
        
        v = find_key_value_in_dict(f, 'cookie')
        if (v != None):
            od['cookie'] = hex(v)

        v = find_key_value_in_dict(f, 'duration')
        if (v != None and type(v) is dict):
            if ('second' in v and 'nanosecond' in v):
                s = v['second']
                ns = v['nanosecond']
                duration = float(s*1000000000 + ns)/1000000000
                od['duration'] = "{}s".format(duration)
        
        v = find_key_value_in_dict(f, 'table_id')
        if (v != None and type(v) is int):
            od['table'] = v
        
        # Flow Statistics
        v = find_key_value_in_dict(f, 'packet-count')
        if (v != None and type(v) is int):
            od['n_packets'] = v

        v = find_key_value_in_dict(f, 'byte-count')
        if (v != None and type(v) is int):
            od['n_bytes'] = v

        v = find_key_value_in_dict(f, 'idle-timeout')
        if (v != None and type(v) is int and v != 0):
            od['idle_timeout'] = v

        v = find_key_value_in_dict(f, 'hard-timeout')
        if (v != None and type(v) is int and v != 0):
            od['hard_timeout'] = v
        
        v = find_key_value_in_dict(f, 'priority')
        if (v != None and type(v) is int):
            od['priority'] = v
            
        # Flow Match
        v = find_key_value_in_dict(f, 'match')
        if (v != None and type(v) is dict):            
            p = find_key_value_in_dict(v, 'in-port')
            if (p != None and isinstance(p, basestring)):
                od['in_port'] = string.replace(p, self.name + ":", '')
            
            vlanmatch = find_key_value_in_dict(v, 'vlan-match')
            if (vlanmatch != None and type(vlanmatch) is dict):
                if ('vlan-id' in vlanmatch and type(vlanmatch['vlan-id'] is dict)):
                    if ('vlan-id' in vlanmatch['vlan-id'] and type(vlanmatch['vlan-id']['vlan-id']) is int):
                        od['dl_vlan'] = vlanmatch['vlan-id']['vlan-id']
                
                if ('vlan-pcp' in vlanmatch and type(vlanmatch['vlan-pcp'] is int)):
                    od['dl_vlan_pcp'] = vlanmatch['vlan-pcp']
            
            ethermatch = find_key_value_in_dict(v, 'ethernet-match')
            if (ethermatch != None and type(v) is dict):
                ethertype = find_key_value_in_dict(ethermatch, 'type')
                if(ethertype != None and type(ethertype) is int):
                    od['dl_type'] = hex(ethertype)
                
                ethersrc = find_key_value_in_dict(ethermatch, 'ethernet-source')
                if(ethersrc != None and type(ethersrc) is dict):
                    addr = find_key_value_in_dict(ethersrc, 'address')
                    if(addr != None and isinstance(addr, basestring)):
                        od['dl_src'] = addr.lower()
                
                etherdst = find_key_value_in_dict(ethermatch, 'ethernet-destination')
                if(etherdst != None and type(etherdst) is dict):
                    addr = find_key_value_in_dict(etherdst, 'address')
                    if(addr != None and isinstance(addr, basestring)):
                        od['dl_dst'] = addr.lower()
            
            ipmatch = find_key_value_in_dict(v, 'ip-match')
            if (ipmatch != None and type(ipmatch) is dict):
                if('ip-protocol' in ipmatch and type(ipmatch['ip-protocol']) is int):                    
                    od['nw_proto'] = ipmatch['ip-protocol']
            
            tcpsrcport = find_key_value_in_dict(v, 'tcp-source-port')
            if (tcpsrcport != None and type(tcpsrcport) is int):
                od['tp_src'] = tcpsrcport
            
            ipv4src = find_key_value_in_dict(v, 'ipv4-source')
            if (ipv4src != None and isinstance(ipv4src, basestring)):
                od['nw_src'] = ipv4src
            
            ipv4dst = find_key_value_in_dict(v, 'ipv4-destination')
            if (ipv4dst != None and isinstance(ipv4dst, basestring)):
                od['nw_dst'] = ipv4dst
        
        # Flow Actions
        v = find_key_value_in_dict(f, 'instructions')
        if (v != None and type(v) is dict):
            v = find_key_value_in_dict(v, 'instruction')
            if (v != None and type(v) is list):
                if (len(v) != 0 and type(v[0]) is dict):
                    v = find_key_value_in_dict(v[0], 'apply-actions')
                    if (v != None and type(v) is dict):
                        v = find_key_value_in_dict(v, 'action')
                        if (v != None and type(v) is list):
                            astr = ""
                            al = self.__build_ovs_action_list(v)
                            if(al != None):
                                al.sort(key=self.__getOrderKey)
                                l = len(al)
                                i = 0
                                for a in al:
                                    astr += a.to_string()
                                    i += 1
                                    if(i < l):
                                        astr += ","

                            od['actions'] = '{}'.format(astr)
        # Following 'else' case is a hack, ODL flows do not seem to contain
        # the 'instructions' info for flows that were set with 'drop' action
        # TBD: Perhaps this hack should be removed!!!
        else:
            od['actions'] = 'drop'
                                    
#        print json.dumps(od, indent=4)
#        print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

        return od
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __build_ovs_action_list(self, alist):
        al = []
        
        for item in alist:
            if ('output-action' in item):
                a = ActionOutput()
                a.update_from_list(item)
                al.append(a)

        return al
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __getOrderKey(self, item):
        return item.order
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __getPriorityKey(self, item):
        return item['priority']

#---------------------------------------------------------------------------
# 
#---------------------------------------------------------------------------
class ActionOutput():
    ''' OpenFlow 'Output' action type '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, port=None, length=None, order=None):        
        self.type = 'output'
        self.order = order
        self.action = {'port': port, 'max-len': length}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def update(self, port=None, length=None, order=None):
        self.action = {'port': port, 'max-len': length}
        if(port != None):
            self.action['port'] = port
        if(length != None):
            self.action['max-len'] = length
        if(order != None):
            self.order = order
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def update_from_list(self, data):
        if(data != None and type(data) is dict and ('output-action' in data)):
            self.type = 'output'
            self.order = find_key_value_in_dict(data, 'order')
            self.action = {'port': None, 'max-len': None}
            self.action['port'] = find_key_value_in_dict(data, 'output-node-connector')
            self.action['max-len'] = find_key_value_in_dict(data, 'max-length')
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def to_string(self):
        s = ""
        p = self.action['port']
        l = self.action['max-len']
        if(p != None and l != None):
            if(p == 'CONTROLLER'):
                s = '{}:{}'.format(p, l)
            else:
                s = '{}:{}'.format(self.type, p)
        
        return s

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class FlowEntry(object):
    ''' Class for creating and interacting with OpenFlow flows '''
    _mn = "flow-node-inventory:flow"
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self):
        ''' Flow identifier in ODL inventory '''
        self.id = None
        
        ''' Opaque Controller-issued identifier '''
        self.cookie = None
        
        ''' Mask used to restrict the cookie bits that must match when the command is
            OFPFC_MODIFY* or OFPFC_DELETE*. A value of 0 indicates no restriction '''
        self.cookie_mask = None  
        
        ''' ID of the table to put the flow in '''
        self.table_id = 0
        
        ''' Priority level of flow entry '''
        self.priority = None
        
        ''' Idle time before discarding (seconds) '''
        self.idle_timeout = 0
        
        ''' Max time before discarding (seconds) '''
        self.hard_timeout = 0 
        
        ''' Modify/Delete entry strictly matching wildcards and priority '''
        self.strict = False
        
        ''' For OFPFC_DELETE* commands, require matching entries to include this as an
            output port. A value of OFPP_ANY indicates no restriction. '''
        self.out_port = None
        
        ''' For OFPFC_DELETE* commands, require matching entries to include this as an
            output group. A value of OFPG_ANY indicates no restriction '''
        self.out_group = None
        
        ''' Bitmap of OFPFF_* flags '''
        self.flags = None
        
        ''' This FlowEntry name in the FlowTable (internal Controller's inventory attribute) '''
        self.flow_name = None
        
        ''' This FlowEntry identifier in the FlowTable (internal Controller's inventory attribute) '''    
        self.id = None
        
        ''' ??? (internal Controller's inventory attribute) '''
        self.installHw = False
        
        ''' Boolean flag used to enforce OpenFlow switch to do ordered message processing.
            Barrier request/reply messages are used by the controller to ensure message dependencies
            have been met or to receive notifications for completed operations. When the controller
            wants to ensure message dependencies have been met or wants to receive notifications for
            completed operations, it may use an OFPT_BARRIER_REQUEST message. This message has no body.
            Upon receipt, the switch must finish processing all previously-received messages, including
            sending corresponding reply or error messages, before executing any messages beyond the
            Barrier Request. '''
        self.barrier=False
        
        ''' Buffered packet to apply to, or OFP_NO_BUFFER. Not meaningful for OFPFC_DELETE* '''
        self.buffer_id = None
        
        '''  Flow match fields '''
        self.match = None
        
        ''' Instructions to be executed when a flow matches this entry flow match fields '''
        self.instructions = None
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def to_json(self):
        """ Return FlowEntry as JSON """
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_payload(self):
        s = self.to_json()        
        s = string.replace(s, '_', '-')
        # Following are exceptions from the common ODL rules for having all
        # multi-part keywords in YANG modules being hash separated
        s = string.replace(s, 'table-id', 'table_id')
        s = string.replace(s, 'cookie-mask', 'cookie_mask')
        d1 = json.loads(s)
        d2 = stripNone(d1)
        payload = {self._mn : d2}
        return json.dumps(payload, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_flow_table_id(self, table_id):
        self.table_id = table_id
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_flow_table_id(self):
        return self.table_id
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_flow_name(self, flow_name):
        self.flow_name = flow_name
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_flow_id(self, flow_id):
        self.id = flow_id
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_flow_id(self):
        return self.id
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_flow_priority(self, flow_priority):
        self.priority = flow_priority
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_flow_hard_timeout(self, hard_timeout):
        self.hard_timeout = hard_timeout
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_flow_idle_timeout(self, idle_timeout):
        self.idle_timeout = idle_timeout
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_flow_cookie(self, cookie):
        self.cookie = cookie
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_flow_cookie_mask(self, cookie_mask):
        self.cookie_mask = cookie_mask
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def add_instruction(self, instruction):
        if(self.instructions == None):
            self.instructions = {}
        self.instructions.update({'instruction':instruction})
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def add_match(self, match):
        if(self.match == None):
            self.match = {}
        self.match.update(match.__dict__)

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class Instructions():
    ''' 'Class representing OpenFlow flow instructions set ''' 
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self):
        self.instructions = {}

    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def add_instruction(self, instruction):
        self.instructions.append(instruction)

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class Instruction():
    ''' Class representing an OpenFlow flow instruction '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, instruction_order=0):
        self.order = instruction_order
#  TBD      self.goto_table = {}
#  TBD      self.write_metadata = {}
#  TBD      self.write_actions = {}
        self.apply_actions = {'action': []}
#  TBD      self.clear_actions = {}
#  TBD      self.meter = {}
    
    '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def add_action(self, action):
        self.actions.append(action)
    '''
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def add_apply_action(self, action):
        self.apply_actions['action'].append(action)

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class Action(object):
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=None):
        self.order = order
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_order(self, order):
        self.order = order

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class OutputAction(Action):
    ''' The Output action forwards a packet to a specified OpenFlow port
        OpenFlow switches must support forwarding to physical ports, 
        switch-defined logical ports and the required reserved ports  '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, action_order=0, port=None, max_len=None):
        super(OutputAction, self).__init__(action_order)
        self.output_action = {'output-node-connector' : port, 'max-length' : max_len }
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_outport(self, port):
        self.output_action['output-node-connector'] = port
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_max_len(self, max_len):
        self.output_action['max-length'] = max_len
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_order(self, order):
        self.order = order

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class SetQueueAction(Action):
    ''' The set-queue action sets the queue id for a packet. When the packet is
        forwarded to a port using the output action, the queue id determines 
        which queue attached to this port is used for scheduling and forwarding
        the packet. Forwarding behavior is dictated by the configuration of the
        queue and is used to provide basic Quality-of-Service (QoS) support '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=None, queue=None, queue_id=None):
        super(SetQueueAction, self).__init__(order)
        self.set_queue_action = {'queue': queue, 'queue-id': queue_id}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_queue(self, queue):
        self.group_action['queue'] = queue
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_group_id(self, queue_id):
        self.group_action['queue_id'] = queue_id
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_order(self, order):
        self.order = order

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class DropAction(Action):
    ''' There is no explicit action to represent drops. Instead, packets whose
        action sets have no output actions should be dropped. This result could
        come from empty instruction sets or empty action buckets in the
        processing pipeline, or after executing a Clear-Actions instruction '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, action_order=None):
        super(DropAction, self).__init__(action_order)
        self.drop_action = {}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_order(self, order):
        self.order = order

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class GroupAction(Action):
    ''' Process the packet through the specified group.
        The exact interpretation depends on group type. '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=None, group=None, group_id=None):
        super(GroupAction, self).__init__(order)
        self.group_action = {'group': group, 'group-id': group_id}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_group(self, group):
        self.group_action['group'] = group
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_group_id(self, group_id):
        self.group_action['group_id'] = group_id

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class SetVlanIdAction(Action):
    ''' Set the 802.1q VLAN id '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=None, vid=None):
        super(SetVlanIdAction, self).__init__(order)
        self.set_vlan_id_action = {'vlan-id' : vid}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_vid(self, vid):
        self.set_vlan_id_action['vlan-id'] = vid

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class SetVlanPCPAction(Action):
    ''' Set the 802.1q priority '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=None, vlan_pcp=None):
        super(SetVlanPCPAction, self).__init__(order)
        self.set_vlan_pcp_action = {'vlan-pcp' : vlan_pcp}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_vlan_pcp(self, vlan_pcp):
        self.set_vlan_pcp_action['vlan-pcp'] = vlan_pcp

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class SetVlanCfiAction(Action):
    ''' Seems to be ODL proprietary action type ???
        CFI (1-bit field) was formerly designated Canonical Format Indicator
        with a value of 0 indicating a MAC address in canonical format. It is
        always set to zero for Ethernet. CFI was used for compatibility between
        Ethernet and Token Ring networks. If a frame received at an Ethernet
        port had a CFI set to 1, then that frame would not be bridged to an
        untagged port.
        Currently renamed as Drop eligible indicator (DEI).        
        May be used separately or in conjunction with PCP to indicate
        frames eligible to be dropped in the presence of congestion. '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=None, vlan_cfi=None):
        super(SetVlanCfiAction, self).__init__(order)
        self.set_vlan_cfi_action = {'vlan-cfi' : vlan_cfi}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_vlan_cfi(self, vlan_cfi):
        self.set_vlan_cfi_action['vlan-cfi'] = vlan_cfi

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class StripVlanAction(Action):
    ''' Strip the 802.1q header '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=None):
        super(StripVlanAction, self).__init__(order)
        self.strip_vlan_action = {}

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class SetDlSrcAction(Action):
    ''' Set Ethernet source address '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=None, mac_addr=None):
        super(SetDlSrcAction, self).__init__(order)
        self.set_dl_src_action = {'address' : mac_addr}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_dl_src(self, mac_addr):
        self.set_dl_src_action['address'] = mac_addr

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class SetDlDstAction(Action):
    ''' Set Ethernet destination address '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=None, mac_addr=None):
        super(SetDlDstAction, self).__init__(order)
        self.set_dl_dst_action = {'address' : mac_addr}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_dl_dst(self, mac_addr):
        self.set_dl_dst_action['address'] = mac_addr

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class SetNwSrcAction(Action):
    ''' Set IP source address '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=None, ip_addr=None):
        super(SetNwSrcAction, self).__init__(order)
        self.set_nw_src_action = {'address' : ip_addr}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_nw_src(self, ip_addr):
        self.set_nw_src_action['address'] = ip_addr

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class SetNwDstAction(Action):
    ''' Set IP destination address '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=None, ip_addr=None):
        super(SetNwDstAction, self).__init__(order)
        self.set_nw_dst_action = {'address' : ip_addr}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_nw_dst(self, ip_addr):
        self.set_nw_dst_action['address'] = ip_addr

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class SetTpSrcAction(Action):
    ''' Set TCP/UDP source port '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=None, port=None):
        super(SetTpSrcAction, self).__init__(order)
        self.set_tp_src_action = {'port' : port}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_tp_src_port(self, port):
        self.set_tp_src_action['port'] = port

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class SetTpDstAction(Action):
    ''' Set TCP/UDP destination port '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=None, port=None):
        super(SetTpDstAction, self).__init__(order)
        self.set_tp_dst_action = {'port' : port}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_tp_dst_port(self, port):
        self.set_tp_dst_action['port'] = port

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class PushVlanHeaderAction(Action):
    ''' Push a new VLAN header onto the packet. The 'ethernet-type' is used as
        the Ethertype for the tag. Only 'ethernet-type' 0x8100 and 0x88a8 should
        be used. '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, action_order=0, eth_type=None, tag=None, pcp=None, cfi=None, vid=None):
        super(PushVlanHeaderAction, self).__init__(action_order)
        self.push_vlan_action = {'ethernet-type': eth_type, 'tag': tag, 'pcp': pcp, 'cfi': cfi, 'vlan-id': vid }
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_eth_type(self, eth_type):
        self.push_vlan_action['ethernet-type'] = eth_type
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_tag(self, tag):
        self.output_action['tag'] = tag
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_pcp(self, pcp):
        self.output_action['pcp'] = pcp
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_cfi(self, cfi):
        self.output_action['cfi'] = cfi
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_vid(self, vid):
        self.output_action['vlan-id'] = vid
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_order(self, order):
        self.order = order

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class PopVlanHeaderAction(Action):
    ''' Pop the outer-most VLAN header from the packet '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=0):
        super(PopVlanHeaderAction, self).__init__(order)
        self.pop_vlan_action = {}

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class PushMplsHeaderAction(Action):
    ''' Push a new MPLS shim header onto the packet. The 'ethernet-type' is used
        as the Ethertype for the tag. Only Ethertype 0x8847 and 0x8848 should be
        used. '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, action_order=0, ethernet_type=None):
        super(PushMplsHeaderAction, self).__init__(action_order)
        self.push_mpls_action = {'ethernet-type': ethernet_type}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_eth_type(self, eth_type):
        self.push_mpls_action['ethernet-type'] = eth_type

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class PopMplsHeaderAction(Action):
    ''' Pop the outer-most MPLS tag or shim header from the packet.
        The 'ethernet-type' is used as the Ethertype for the resulting packet
        (Ethertype for the MPLS payload). '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, action_order=0, ethernet_type=None):
        super(PopMplsHeaderAction, self).__init__(action_order)
        self.pop_mpls_action = {'ethernet-type': ethernet_type}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_eth_type(self, eth_type):
        self.pop_mpls_action['ethernet-type'] = eth_type

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class PushPBBHeaderAction(Action):
    ''' Push a new PBB service instance header (I-TAG TCI) onto the packet.
        The Ethertype is used as the Ethertype for the tag. Only Ethertype
        0x88E7 should be used 
        PBB - Provider Backbone Bridges is an Ethernet data-plane technology
              (also known as MAC-in-MAC) that involves encapsulating an
              Ethernet datagram inside another one with new source and
              destination addresses '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=0, ethernet_type=None):
        super(PushPBBHeaderAction, self).__init__(order)
        self.push_pbb_action = {'ethernet-type': ethernet_type}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_eth_type(self, ethernet_type):
        self.push_pbb_action['ethernet-type'] = ethernet_type

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class PopPBBHeaderAction(Action):
    ''' Pop the outer-most PBB service instance header (I-TAG TCI)
        from the packet
        PBB - Provider Backbone Bridges is an Ethernet data-plane technology
              (also known as MAC-in-MAC) that involves encapsulating an
              Ethernet datagram inside another one with new source and
              destination addresses '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=0):
        super(PopPBBHeaderAction, self).__init__(order)
        self.pop_pbb_action = {}

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class SetMplsTTLAction(Action):
    ''' Replace the existing MPLS TTL. Only applies to packets with an existing
        MPLS shim header '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=0, mpls_ttl=None):
        super(SetMplsTTLAction, self).__init__(order)
        self.set_mpls_ttl_action = {'mpls-ttl': mpls_ttl}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_mpls_ttl(self, mpls_ttl):
        self.set_mpls_ttl_action['mpls-ttl'] = mpls_ttl

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class DecMplsTTLAction(Action):
    ''' Decrement the MPLS TTL. Only applies to packets with an existing MPLS
        shim header '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=0):
        super(DecMplsTTLAction, self).__init__(order)
        self.dec_mpls_ttl = {}

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class SetNwTTLAction(Action):
    ''' Replace the existing IPv4 TTL or IPv6 Hop Limit and update the IP
        checksum. Only applies to IPv4 and IPv6 packets. '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=0, ip_ttl=None):
        super(SetNwTTLAction, self).__init__(order)
        self.set_nw_ttl_action = {'nw-ttl': ip_ttl}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_ip_ttl(self, ip_ttl):
        self.set_nw_ttl_action['nw-ttl'] = ip_ttl

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class DecNwTTLAction(Action):
    ''' Decrement the IPv4 TTL or IPv6 Hop Limit field and update the IP
        checksum. Only applies to IPv4 and IPv6 packets. '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=0):
        super(DecNwTTLAction, self).__init__(order)
        self.dec_nw_ttl = {}

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class CopyTTLOutwardsAction(Action):
    ''' Copy the TTL from next-to-outermost to outermost header with TTL.
        Copy can be IP-to-IP, MPLS-to-MPLS, or IP-to-MPLS. '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=0):
        super(CopyTTLOutwardsAction, self).__init__(order)
        self.copy_ttl_out = {}

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class CopyTTLInwardsAction(Action):
    ''' Copy the TTL from outermost to next-to-outermost header with TTL.
        Copy can be IP-to-IP, MPLS-to-MPLS, or MPLS-to-IP. '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=0):
        super(CopyTTLInwardsAction, self).__init__(order)
        self.copy_ttl_in = {}

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class SetFieldAction(Action):
    ''' The Extensible set_field action reuses the OXM encoding defined for
        matches, and enables to rewrite any header field in a single action.
        This allows any new match field, including experimenter fields, to be
        available for rewrite.
        The various Set-Field actions are identified by their field type and
        modify the values of respective header fields in the packet. While 
        not strictly required, the support of rewriting various header fields
        using Set-Field actions greatly increase the usefulness of an OpenFlow
        implementation. To aid integration with existing networks, we suggest
        that VLAN modification actions be supported. Set-Field actions should
        always be applied to the outermost-possible header (e.g. a 'Set VLAN ID'
        action always sets the ID of the outermost VLAN tag), unless the field
        type specifies otherwise. '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, action_order=0):
        super(SetFieldAction, self).__init__(action_order)
        self.set_field = {'vlan-match': None, 'protocol-match-fields' :None}
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_vlan_id(self, vid):
        if(self.set_field['vlan-match'] == None):
            self.set_field['vlan-match'] = VlanMatch()
        self.set_field['vlan-match'].set_vid(vid)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_mpls_label(self, mpls_label):
        if(self.set_field['protocol-match-fields'] == None):
            self.set_field['protocol-match-fields'] = ProtocolMatchFields()
        self.set_field['protocol-match-fields'].set_mpls_lable(mpls_label)

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class FloodAction(Action):
    ''' Flood the packet along the minimum spanning tree, not including the
        incoming interface.
        The sentence 'along the minimum spanning tree' implies: flood the packet
        on all the ports that are not disabled by Spanning Tree Protocol. '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=0):
        super(FloodAction, self).__init__(order)
        self.flood_action = {}

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class FloodAllAction(Action):
    ''' Send the packet out all interfaces, not including the incoming
        interface '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=0):
        super(FloodAllAction, self).__init__(order)
        self.flood_all_action = {}

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class HwPathAction(Action):
    ''' Seems to be ODL proprietary action type ??? '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=0):
        super(HwPathAction, self).__init__(order)
        self.hw_path_action = {}

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class SwPathAction(Action):
    ''' Seems to be ODL proprietary action type ??? '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=0):
        super(SwPathAction, self).__init__(order)
        self.sw_path_action = {}

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class LoopbackAction(Action):
    ''' Seems to be ODL proprietary action type ???'''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, order=0):
        super(LoopbackAction, self).__init__(order)
        self.loopback_action = {}

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class Match(object):
    """Class that represents OpenFlow flow matching attributes """
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self):
        ''' Ingress port. Numerical representation of in-coming port, starting at 1
            (may be a physical or switch-defined logical port) '''
        self.in_port = None
        
        ''' Physical port (in 'ofp_packet_in messages', underlying physical port when
            packet received on a logical port) '''
        self.in_phy_port = None
        
        ''' Ethernet match fields: 
            - ethernet destination MAC address
            - ethernet source MAC address
            - ethernet type of the OpenFlow packet payload (after VLAN tags) '''
        self.ethernet_match = None
        
        ''' IPv4 source address (can use subnet mask) '''
        self.ipv4_source = None
        
        ''' IPv4 destination address (can use subnet mask) '''
        self.ipv4_destination = None
        
        ''' IP match fields:
            - Differentiated Service Code Point (DSCP). Part of the IPv4 ToS field or
              the IPv6 Traffic Class field.
            - ECN bits of the IP header. Part of the IPv4 ToS field or
              the IPv6 Traffic Class field 
            - IPv4 or IPv6 protocol number '''
        self.ip_match = None
        
        ''' IPv6 source address (can use subnet mask) '''
        self.ipv6_source = None
        
        ''' IPv6 destination address (can use subnet mask) '''
        self.ipv6_destination = None
        
        ''' The target address in an IPv6 Neighbor Discovery message '''
        self.ipv6_nd_target = None
        
        ''' The source link-layer address option in an IPv6 Neighbor Discovery message '''
        self.ipv6_nd_sll = None
        
        ''' The target link-layer address option in an IPv6 Neighbor Discovery message '''
        self.ipv6_nd_tll = None
        
        ''' IPv6 flow label '''
        self.ipv6_label = None
        
        ''' IPv6 Extension Header pseudo-field '''
        self.ipv6_ext_header = None
        
        ''' Protocol match fields:
           - The LABEL in the first MPLS shim header
           - The TC in the first MPLS shim header
           - The BoS bit (Bottom of Stack bit) in the first MPLS shim header
           - The I-SID in the first PBB service instance tag '''
        self.protocol_match_fields = None
        
        ''' UDP source port '''
        self.udp_source_port = None
        
        ''' UDP destination port '''
        self.udp_destination_port = None
        
        ''' TCP source port '''
        self.tcp_source_port = None
        
        ''' TCP destination port '''
        self.tcp_destination_port = None
        
        ''' SCTP source port '''
        self.sctp_source_port = None
        
        ''' SCTP destination port '''
        self.sctp_destination_port = None
        
        ''' ICMPv4 match fields:
            - ICMP type 
            - ICMP code '''
        self.icmpv4_match = None
        
        ''' ICMPv6 match fields
            - ICMPv6 type 
            - ICMPv6 code '''
        self.icmpv6_match = None
        
        ''' VLAN match fields:
            - VLAN-ID from 802.1Q header (the CFI bit indicate the presence of a valid VLAN-ID)
            - VLAN-PCP from 802.1Q header '''
        self.vlan_match = None
        
        ''' ARP opcode '''
        self.arp_op = None
        
        ''' Source IPv4 address in the ARP payload (can use subnet mask) '''
        self.arp_source_transport_address = None
        
        ''' Target IPv4 address in the ARP payload (can use subnet mask) '''
        self.arp_target_transport_address = None
        
        ''' Source Ethernet address in the ARP payload '''
        self.arp_source_hardware_address = None
        
        ''' Target Ethernet address in the ARP payload '''
        self.arp_target_hardware_address = None
        
        ''' Metadata associated with a logical port '''
        self.tunnel = None
        
        ''' Table metadata (used to pass information between tables) '''
        self.metadata = None
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_eth_type(self, eth_type):
        if(self.ethernet_match == None):
            self.ethernet_match = EthernetMatch()
        self.ethernet_match.set_type(eth_type)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_eth_src(self, eth_src):
        if(self.ethernet_match == None):
            self.ethernet_match = EthernetMatch()
        self.ethernet_match.set_src(eth_src)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_eth_dst(self, eth_dst):
        if(self.ethernet_match == None):
            self.ethernet_match = EthernetMatch()
        self.ethernet_match.set_dst(eth_dst )       
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_vlan_id(self, vlan_id):
        if(self.vlan_match == None):
            self.vlan_match = VlanMatch()
        self.vlan_match.set_vid(vlan_id)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_vlan_pcp(self, vlan_pcp):
        if(self.vlan_match == None):
            self.vlan_match = VlanMatch()
        self.vlan_match.set_pcp(vlan_pcp)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_ipv4_src(self, ipv4_src):
        self.ipv4_source = ipv4_src
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_ipv4_dst(self, ipv4_dst):
        self.ipv4_destination = ipv4_dst
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_ipv6_src(self, ipv6_src):
        self.ipv6_source = ipv6_src
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_ipv6_dst(self, ipv6_dst):
        self.ipv6_destination = ipv6_dst    
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_ipv6_flabel(self, ipv6_flabel):
        if(self.ipv6_label == None):
            self.ipv6_label = Ipv6Label()
        self.ipv6_label.set_flabel(ipv6_flabel)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_ipv6_exh_hdr(self, ipv6_exthdr):
        if(self.ipv6_ext_header == None):
            self.ipv6_ext_header = Ipv6ExtHdr()
        self.ipv6_ext_header.set_exthdr(ipv6_exthdr)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_ip_dscp(self, ip_dscp):
        if(self.ip_match == None):
            self.ip_match = IpMatch()
        self.ip_match.ip_dscp = ip_dscp
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_ip_ecn(self, ip_ecn):
        if(self.ip_match == None):
            self.ip_match = IpMatch()
        self.ip_match.ip_ecn = ip_ecn
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_ip_proto(self, ip_proto):
        if(self.ip_match == None):
            self.ip_match = IpMatch()
        self.ip_match.ip_protocol = ip_proto
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    '''        
    def ip_proto_version(self, version):
        self.ip_match.ip_proto = version    
    '''    
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_udp_src_port(self, udp_src_port):
        self.udp_source_port = udp_src_port
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_udp_dst_port(self, udp_dst_port):
        self.udp_destination_port = udp_dst_port
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_tcp_src_port(self, tcp_src_port):
        self.tcp_source_port = tcp_src_port
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_tcp_dst_port(self, tcp_dst_port):
        self.tcp_destination_port = tcp_dst_port        
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_sctp_src(self, sctp_port):
        self.sctp_source_port = sctp_port
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def sctp_dst(self, sctp_port):
        self.sctp_destination_port = sctp_port
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_icmpv4_type(self, icmpv4_type):
        if(self.icmpv4_match == None):
            self.icmpv4_match = IcmpMatch()
        self.icmpv4_match.set_type(icmpv4_type)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_icmpv4_code(self, icmpv4_code):
        if(self.icmpv4_match == None):
            self.icmpv4_match = IcmpMatch()
        self.icmpv4_match.set_code(icmpv4_code)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_icmpv6_type(self, icmpv6_type):
        if(self.icmpv6_match == None):
            self.icmpv6_match = IcmpV6Match()
        self.icmpv6_match.set_type(icmpv6_type)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_icmpv6_code(self, icmpv6_code):
        if(self.icmpv6_match == None):
            self.icmpv6_match = IcmpV6Match()
        self.icmpv6_match.set_code(icmpv6_code)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_in_port(self, in_port):
        self.in_port = in_port
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_in_phy_port(self, in_phy_port):
        self.in_phy_port = in_phy_port
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_arp_opcode(self, arp_opcode):
        self.arp_op = arp_opcode
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_arp_src_transport_address(self, arp_src_tp_addr):
        self.arp_source_transport_address = arp_src_tp_addr       
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_arp_tgt_transport_address(self, arp_tgt_tp_addr):
        self.arp_target_transport_address = arp_tgt_tp_addr
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_arp_src_hw_address(self, arp_src_hw_addr):
        if(self.arp_source_hardware_address == None):
            self.arp_source_hardware_address = {}
        self.arp_source_hardware_address['address'] = arp_src_hw_addr
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_arp_tgt_hw_address(self, arp_tgt_hw_addr):
        if(self.arp_target_hardware_address == None):
            self.arp_target_hardware_address = {}
        self.arp_target_hardware_address['address'] = arp_tgt_hw_addr    
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_mpls_lable(self, mpls_label):
        if(self.protocol_match_fields == None):
            self.protocol_match_fields = ProtocolMatchFields()
        self.protocol_match_fields.set_mpls_lable(mpls_label)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_mpls_tc(self, mpls_tc):
        if(self.protocol_match_fields == None):
            self.protocol_match_fields = ProtocolMatchFields()
        self.protocol_match_fields.set_mpls_tc(mpls_tc)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_mpls_bos(self, mpls_bos):
        if(self.protocol_match_fields == None):
            self.protocol_match_fields = ProtocolMatchFields()
        self.protocol_match_fields.set_mpls_bos(mpls_bos)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_tunnel_id(self, tunnel_id):
        if(self.tunnel == None):
            self.tunnel = Tunnel()
        self.tunnel.tunnel_id = tunnel_id
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_metadata(self, metadata):
        if(self.metadata == None):
            self.metadata = Metadata()
        self.metadata.set_metadata(metadata)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_metadata_mask(self, metadata_mask):
        if(self.metadata == None):
            self.metadata = Metadata()
        self.metadata.set_metadata_mask(metadata_mask)

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class EthernetMatch(Match):
    ''' Ethernet specific match fields '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self):
        self.ethernet_type = None
        self.ethernet_source = None
        self.ethernet_destination = None
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_type(self, ether_type):
        if(self.ethernet_type == None):
            self.ethernet_type = {}
        self.ethernet_type['type'] = ether_type
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_src(self, ether_src):
        if(self.ethernet_source == None):
            self.ethernet_source = {}
        self.ethernet_source['address'] = ether_src
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_dst(self, ether_dst):
        if(self.ethernet_destination == None):
            self.ethernet_destination = {}
        self.ethernet_destination['address'] = ether_dst

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class VlanMatch(Match):
    ''' VLAN specific match fields '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self):
        ''' VLAN-ID from 802.1Q header '''
        self.vlan_id = None
        
        ''' VLAN-PCP from 802.1Q header '''
        self.vlan_pcp = None
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_vid(self, vid):
        if(self.vlan_id == None):
            self.vlan_id = VlanId()            
        self.vlan_id.set_vid(vid)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_pcp(self, pcp):
        self.vlan_pcp = pcp

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class VlanId(VlanMatch):
    ''' Helper subclass of VlanMatch class to help in serialization
        of VLAN ID information encoded in match rules of a flow entry '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self):
        ''' VLAN-ID from 802.1Q header '''
        self.vlan_id = None
        
        ''' Flag that indicates that 'vlan_id' value is set and matching is
            only for packets with VID equal to 'vlan_id' value '''
        self.vlan_id_present = False
    
    def set_vid(self, vid):
        self.vlan_id = vid
        self.vlan_id_present = True

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class IcmpMatch(Match):
    ''' ICMPv4 specific match fields '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self):
        ''' ICMP type '''
        self.icmpv4_type = None
    
        ''' ICMP code '''
        self.icmpv4_code = None
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_type(self, icmp_type):
        self.icmpv4_type = icmp_type
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_code(self, icmp_code):
        self.icmpv4_code = icmp_code

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class IcmpV6Match(Match):
    ''' ICMPv6 specific match fields '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self):
        ''' ICMPv6 type '''
        self.icmpv6_type = None
    
        ''' ICMPv6 code '''
        self.icmpv6_code = None
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_type(self, icmpv6_type):
        self.icmpv6_type = icmpv6_type
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_code(self, icmpv6_code):
        self.icmpv6_code = icmpv6_code

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class IpMatch(Match):
    ''' IPv4 protocol specific match fields '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self):
        ''' "IP DSCP (6 bits in ToS field) '''
        self.ip_dscp = None
        
        ''' IP ECN (2 bits in ToS field) '''
        self.ip_ecn = None
        
        ''' IP protocol (IPv4 or IPv6 Protocol Number)'''
        self.ip_proto = None

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class Ipv6Label(Match):
    ''' IPv6 Flow Label '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, flabel=None, flabel_mask=None):
        self.ipv6_flabel = flabel
        self.flabel_mask = flabel_mask
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_flabel(self, flabel, flabel_mask=None):
        self.ipv6_flabel = flabel
        self.flabel_mask = flabel_mask
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_flabel_mask(self, flabel_mask):
        self.flabel_mask = flabel_mask

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class Ipv6ExtHdr(Match):
    ''' IPv6 Extension Header pseudo-field '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, exthdr=None, exthdr_mask=None):
        self.ipv6_exthdr = exthdr
        self.ipv6_exthdr_mask = exthdr_mask
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_exthdr(self, exthdr, exthdr_mask=None):
        self.ipv6_exthdr = exthdr
        self.ipv6_exthdr_mask = exthdr_mask
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_exthdr_mask(self, exthdr_mask):
        self.ipv6_exthdr_mask = exthdr_mask

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class ProtocolMatchFields(Match):
    ''' Protocol match fields '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self):
        ''' The LABEL in the first MPLS shim header '''
        self.mpls_label = None
        
        ''' The TC in the first MPLS shim header '''
        self.mpls_tc = None
        
        ''' The BoS bit (Bottom of Stack bit) in the first MPLS shim header '''
        self.mpls_bos = None
        
        ''' The I-SID in the first PBB service instance tag '''
        self.pbb = None
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_mpls_lable(self, mpls_lable):
        self.mpls_label = mpls_lable
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_mpls_tc(self, mpls_tc):
        self.mpls_tc = mpls_tc
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_mpls_bos(self, mpls_bos):
        self.mpls_bos = mpls_bos

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class Pbb(ProtocolMatchFields):
    ''' The I-SID in the first PBB service instance tag '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self):
        self.pbb_isid = None
        self.pbb_mask = None
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_pbb_isid(self, pbb_isid):
        self.pbb_isid = pbb_isid
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_pbb_mask(self, pbb_mask):
        self.pbb_mask = pbb_mask

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class ArpSrcHwAddrMatch(Match):
    ''' ARP source hardware address '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self):
        self.address = None

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class ArpTgtHwAddrMatch(Match):
    ''' ARP target hardware address '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self):
        self.address = None

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class Tunnel(Match):
    ''' Logical Port Metadata '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self):
        ''' Metadata associated with a logical port'''
        self.tunnel_id = None

#-------------------------------------------------------------------------------
# 
#-------------------------------------------------------------------------------
class Metadata(Match):
    ''' TBD '''
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self):
        self.metadata = None
        self.metadata_mask = None

    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_metadata(self, metadata):
        self.metadata = metadata

    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def set_metadata_mask(self, metadata_mask):
        self.metadata_mask = metadata_mask

''' Test code - START '''
if __name__ == "__main__":
    print "Start"
    
    # --- Ethernet Type and IP Dst Address
    flow = FlowEntry()
    flow.set_flow_id(flow_id = 11)
    flow.set_flow_priority(flow_priority = 1000)
    
    instruction = Instruction(instruction_order = 0)    
    action = DropAction(action_order = 0)   
    instruction.add_apply_action(action)
    flow.add_instruction(instruction)
    
    match = Match()
    match.set_eth_type(eth_type = 2048)    
    match.set_ipv4_dst(ipv4_dst = "10.11.12.13/24")
    flow.add_match(match)
    
    # --- Ethernet Type and IP Src Address
    flow = FlowEntry()
    flow.set_flow_id(flow_id = 12)
    flow.set_flow_priority(flow_priority = 1000)
    
    instruction = Instruction(instruction_order = 0)    
    action = DropAction(action_order = 0)    
    instruction.add_apply_action(action)
    flow.add_instruction(instruction)
    
    match = Match()
    match.set_eth_type(eth_type = 2048)     
    match.set_ipv4_src(ipv4_src = "10.11.12.13/24")       
    flow.add_match(match)
    
    # --- Ethernet Src Address
    flow = FlowEntry()
    flow.set_flow_id(flow_id = 13)
    flow.set_flow_priority(flow_priority = 1002)
    
    instruction = Instruction(instruction_order = 0)
    action = DropAction(action_order = 0)
    instruction.add_apply_action(action)
    flow.add_instruction(instruction)
    
    match = Match()    
    match.set_eth_src(eth_src = "00:11:22:33:44:56")    
    flow.add_match(match)
    
    # --- Ethernet Src & Dest Addresses, Ethernet Type    
    flow = FlowEntry()
    flow.set_flow_id(flow_id = 14)
    flow.set_flow_priority(flow_priority = 1000)
    
    instruction = Instruction(instruction_order = 0)    
    action = DropAction(action_order = 0)   
    instruction.add_apply_action(action)    
    flow.add_instruction(instruction)
    
    match = Match()
    match.set_eth_type(eth_type = 45)
    match.set_eth_dst(eth_dst = "ff:ff:ff:ff:ff:ff")
    match.set_eth_src(eth_src = "00:00:00:00:23:ae")    
    flow.add_match(match)
    
    #--- Ethernet Src & Dest Addresses, IPv4 Src & Dest Addresses, Input Port    
    flow = FlowEntry()
    flow.set_flow_id(flow_id = 15)
    flow.set_flow_priority(flow_priority = 1005)
    
    instruction = Instruction(instruction_order = 0)    
    action = DropAction(action_order = 0)   
    instruction.add_apply_action(action)    
    flow.add_instruction(instruction)
    
    match = Match()
    match.set_eth_type(eth_type = 34887)
    match.set_eth_dst(eth_dst = "ff:ff:ff:ff:ff:ff")
    match.set_eth_src(eth_src = "00:00:00:11:23:af")
    
    match.set_ipv4_src(ipv4_src = "44.1.2.3/24")
    match.set_ipv4_dst(ipv4_dst = "55.4.5.6/16")
    match.set_in_port(in_port = 1)
    flow.add_match(match)
    
    # --- Ethernet Src & Dest Addresses, IPv4 Src & Dest Addresses, 
    #     IP Protocol Number, IP DSCP, IP ECN, Input Port
    #     NOTE: ethernet type MUST be 2048 (0x800) 
    flow = FlowEntry()
    flow.set_flow_id(flow_id = 16)
    flow.set_flow_priority(flow_priority = 1007)
    
    instruction = Instruction(instruction_order = 0)
    action = DropAction(action_order = 0)
    instruction.add_apply_action(action)
    flow.add_instruction(instruction)
    
    match = Match()    
    match.set_eth_type(eth_type = 2048)
    match.set_eth_dst(eth_dst = "ff:ff:ff:ff:ff:aa")
    match.set_eth_src(eth_src = "00:00:00:11:23:ae")
    match.set_ipv4_src(ipv4_src = "77.77.77.77/20")
    match.set_ipv4_dst(ipv4_dst = "88.88.88.88/16")
    match.set_ip_proto(ip_proto = 56)
    match.set_ip_dscp(ip_dscp = 15)
    match.set_ip_ecn(ip_ecn = 1)    
    match.set_in_port(in_port = 1)    
    flow.add_match(match)
    
    # --- Ethernet Src & Dest Addresses, IPv4 Src & Dest Addresses,
    #     TCP Src & Dest Ports, IP DSCP, IP ECN, Input Port
    #     NOTES: ethernet type MUST be 2048 (0x800)
    #            IP Protocol Type MUST be 6
    flow = FlowEntry()
    flow.set_flow_id(flow_id = 17)
    flow.set_flow_priority(flow_priority = 1008)
    
    instruction = Instruction(instruction_order = 0)
    action = DropAction(action_order = 0)
    instruction.add_apply_action(action)
    flow.add_instruction(instruction)
    
    match = Match()    
    match.set_eth_type(eth_type = 2048)
    match.set_eth_dst(eth_dst = "ff:ff:29:01:19:61")
    match.set_eth_src(eth_src = "00:00:00:11:23:ae")
    match.set_ipv4_src(ipv4_src = "17.1.2.3/8")
    match.set_ipv4_dst(ipv4_dst = "172.168.5.6/16")
    match.set_ip_proto(ip_proto = 6)
    match.set_ip_dscp(ip_dscp = 2)
    match.set_ip_ecn(ip_ecn = 2)    
    match.set_tcp_src_port(tcp_src_port = 25364)
    match.set_tcp_dst_port(tcp_dst_port = 8080)
    match.set_in_port(in_port = 0)    
    flow.add_match(match)
    
    # --- Ethernet Src & Dest Addresses, IPv4 Src & Dest Addresses,
    #     UDP Src & Dest Ports, IP DSCP, IP ECN, Input Port
    flow = FlowEntry()
    flow.set_flow_id(flow_id = 18)
    flow.set_flow_priority(flow_priority = 10009)
    
    instruction = Instruction(instruction_order = 0)
    action = DropAction(action_order = 0)
    instruction.add_apply_action(action)
    flow.add_instruction(instruction)
    
    match = Match()    
    match.set_eth_type(eth_type = 2048)
    match.set_eth_dst(eth_dst = "20:14:29:01:19:61")
    match.set_eth_src(eth_src = "00:00:00:11:23:ae")
    match.set_ipv4_src(ipv4_src = "19.1.2.3/10")
    match.set_ipv4_dst(ipv4_dst = "172.168.5.6/18")
    match.set_ip_proto(ip_proto = 17)
    match.set_ip_dscp(ip_dscp = 8)
    match.set_ip_ecn(ip_ecn = 3)    
    match.set_udp_src_port(udp_src_port = 25364)
    match.set_udp_dst_port(udp_dst_port = 8080)
    match.set_in_port(in_port = 3)    
    flow.add_match(match)
    
    # --- Ethernet Src & Dest Addresses, IPv4 Src & Dest Addresses,
    #     ICMPv4 Type & Code, IP DSCP, IP ECN, Input Port
    #     NOTES: ethernet type MUST be 2048 (0x800)
    #            IP Protocol Type MUST be 1
    flow = FlowEntry()
    flow.set_flow_id(flow_id = 19)
    flow.set_flow_priority(flow_priority = 1010)
    
    instruction = Instruction(instruction_order = 0)
    action = DropAction(action_order = 0)
    instruction.add_apply_action(action)
    flow.add_instruction(instruction)
    
    match = Match()    
    match.set_eth_type(eth_type = 2048)
    match.set_eth_dst(eth_dst = "ff:ff:29:01:19:61")
    match.set_eth_src(eth_src = "00:00:00:11:23:ae")
    match.set_ipv4_src(ipv4_src = "17.1.2.3/8")
    match.set_ipv4_dst(ipv4_dst = "172.168.5.6/16")
    match.set_ip_proto(ip_proto = 1)
    match.set_ip_dscp(ip_dscp = 27)
    match.set_ip_ecn(ip_ecn = 3)    
    match.set_icmpv4_type(icmpv4_type = 6)
    match.set_icmpv4_code(icmpv4_code = 3)
    match.set_in_port(in_port = 10)
    flow.add_match(match)
    
    # --- Ethernet Src & Dest Addresses, ARP Operation,
    #     ARP Src & Target Transport Addresses, ARP Src & Target Hw Addresses
    #     NOTE: ethernet-type MUST be 2054 (0x806)
    flow = FlowEntry()
    flow.set_flow_id(flow_id = 20)
    flow.set_flow_priority(flow_priority = 1011)
    
    instruction = Instruction(instruction_order = 0)
    action = DropAction(action_order = 0)
    instruction.add_apply_action(action)
    flow.add_instruction(instruction)
    
    match = Match()    
    match.set_eth_type(eth_type = 2054)
    match.set_eth_dst(eth_dst = "ff:ff:ff:ff:FF:ff")
    match.set_eth_src(eth_src = "00:00:fc:01:23:ae")
    match.set_arp_opcode(arp_opcode = 1)
    match.set_arp_src_transport_address(arp_src_tp_addr = "192.168.4.1")
    match.set_arp_tgt_transport_address(arp_tgt_tp_addr = "10.21.22.23")
    match.set_arp_src_hw_address(arp_src_hw_addr = "12:34:56:78:98:ab")
    match.set_arp_tgt_hw_address(arp_tgt_hw_addr = "fe:dc:ba:98:76:54")
    flow.add_match(match)
    
    # --- Ethernet Src & Dest Addresses, Ethernet Type, VLAN ID, VLAN PCP
    flow = FlowEntry()
    flow.set_flow_id(flow_id = 21)
    flow.set_flow_priority(flow_priority = 1012)
    
    instruction = Instruction(instruction_order = 0)    
    action = DropAction(action_order = 0)   
    instruction.add_apply_action(action)
    flow.add_instruction(instruction)
    
    match = Match()
    match.set_eth_type(eth_type = 2048)    
    match.set_eth_dst(eth_dst = "ff:ff:29:01:19:61")
    match.set_eth_src(eth_src = "00:00:00:11:23:ae")    
    match.set_vlan_id(vlan_id = 78)
    match.set_vlan_pcp(vlan_pcp = 3)
    flow.add_match(match)
    
    # --- Ethernet Src & Dest Addresses, MPLS Label, MPLS TC, MPLS BoS
    flow = FlowEntry()
    flow.set_flow_id(flow_id = 22)
    flow.set_flow_priority(flow_priority = 1013)
    
    instruction = Instruction(instruction_order = 1)    
    action = DropAction(action_order = 1)   
    instruction.add_apply_action(action)
    flow.add_instruction(instruction)
    
    match = Match()
    match.set_eth_type(eth_type = 34887)
    match.set_eth_dst(eth_dst = "ff:ff:29:01:19:61")
    match.set_eth_src(eth_src = "00:00:00:11:23:ae")
    
    match.set_mpls_lable(mpls_label = 567)
    match.set_mpls_tc(mpls_tc = 3)
    match.set_mpls_bos(mpls_bos = 1)
    flow.add_match(match)
    
    # --- IPv6 Src & Dest Addresses
    #     NOTE: ethernet type MUST be 34525 (0x86DD)
    flow = FlowEntry()
    flow.set_flow_id(flow_id = 23)
    flow.set_flow_priority(flow_priority = 1014)
    
    instruction = Instruction(instruction_order = 0)
    action = DropAction(action_order = 0)
    instruction.add_apply_action(action)
    flow.add_instruction(instruction)
    
    match = Match()    
    match.set_eth_type(eth_type = 34525 )
    match.set_ipv6_src(ipv6_src = "fe80::2acf:e9ff:fe21:6431/128")
    match.set_ipv6_dst(ipv6_dst = "aabb:1234:2acf:e9ff::fe21:6431/64")
    flow.add_match(match)

    # --- Metadata
    flow = FlowEntry()
    flow.set_flow_name(flow_name = "flow_with_metadata")
    flow.set_flow_id(flow_id = 24)
    flow.set_flow_priority(flow_priority = 1015)
    flow.set_flow_cookie(cookie = 19)
    flow.set_flow_cookie_mask(cookie_mask = 255)
    
    instruction = Instruction(instruction_order = 0)
    action = DropAction(action_order = 0)   
    instruction.add_apply_action(action)
    flow.add_instruction(instruction)
    
    match = Match()    
    metadata = "12345"
    match.set_metadata(metadata)    
    flow.add_match(match)
    
    # --- Metadata, Metadata Mask
    flow = FlowEntry()
    flow.set_flow_name(flow_name = "flow_with_metadata_and_metadata_mask")
    flow.set_flow_id(flow_id = 25)
    flow.set_flow_priority(flow_priority = 1016)
    flow.set_flow_cookie(cookie = 20)
    flow.set_flow_cookie_mask(cookie_mask = 255)
    flow.set_flow_hard_timeout(hard_timeout = 1200)
    flow.set_flow_idle_timeout(idle_timeout = 3400)
    
    instruction = Instruction(instruction_order = 0)    
    action = DropAction(action_order = 0)   
    instruction.add_apply_action(action)    
    flow.add_instruction(instruction)
    
    match = Match()
    match.set_metadata(metadata = "12345")    
    match.set_metadata_mask(metadata_mask = "0xFF")
    flow.add_match(match)
    
    # --- IPv6 Src & Dest Addresses, Metadata, IP DSCP, IP ECN, UDP Src & Dest Ports
    #     NOTE: ethernet type MUST be 34525 (0x86DD)
    flow = FlowEntry()
    flow.set_flow_id(flow_id = 26)
    flow.set_flow_priority(flow_priority = 1017)
    
    instruction = Instruction(instruction_order = 0)
    action = DropAction(action_order = 0)
    instruction.add_apply_action(action)
    flow.add_instruction(instruction)
    
    match = Match()    
    match.set_eth_type(eth_type = 34525)
    match.set_ipv6_src(ipv6_src = "1234:5678:9abc:def0:fdcd:a987:6543:210f/76")
    match.set_ipv6_dst(ipv6_dst = "fe80::2acf:e9ff:fe21:6431/128")
    metadata = "12345"
    match.set_metadata(metadata)    
    match.set_ip_proto(ip_proto = 17)
    match.set_ip_dscp(ip_dscp = 8)
    match.set_ip_ecn(ip_ecn = 3)    
    match.set_udp_src_port(udp_src_port = 25364)
    match.set_udp_dst_port(udp_dst_port = 8080)
    flow.add_match(match)
    
    # --- IPv6 Src & Dest Addresses, Metadata, IP DSCP, IP ECN, TCP Src & Dest Ports
    #     NOTES: ethernet type MUST be 34525 (0x86DD)
    #            IP Protocol MUST be 6
    flow = FlowEntry()
    flow.set_flow_id(flow_id = 27)
    flow.set_flow_priority(flow_priority = 1018)
    
    instruction = Instruction(instruction_order = 0)    
    action = DropAction(action_order = 0)   
    instruction.add_apply_action(action)    
    flow.add_instruction(instruction)
    
    match = Match()
    match.set_eth_type(eth_type = 34525)
    match.set_ipv6_src(ipv6_src = "1234:5678:9ABC:DEF0:FDCD:A987:6543:210F/76" )
    match.set_ipv6_dst(ipv6_dst = "fe80:2acf:e9ff:fe21::6431/94")
    metadata = "12345"
    match.set_metadata(metadata)    
    match.set_ip_proto(ip_proto = 6)
    match.set_ip_dscp(ip_dscp = 60)
    match.set_ip_ecn(ip_ecn = 3)
    match.set_tcp_src_port(tcp_src_port = 183)
    match.set_tcp_dst_port(tcp_dst_port = 8080)
    flow.add_match(match)

    # --- IPv6 Src & Dest Addresses, Metadata, IP DSCP, IP ECN, TCP Src & Dest Ports, IPv6 Label
    #     NOTES: ethernet type MUST be 34525 (0x86DD)
    #            IP Protocol MUST be 6
    flow = FlowEntry()
    flow.set_flow_id(flow_id = 28)
    flow.set_flow_priority(flow_priority = 1019)
    flow.set_flow_cookie(cookie = 23)
    flow.set_flow_hard_timeout(hard_timeout = 1200)
    flow.set_flow_idle_timeout(idle_timeout = 3400)
    
    instruction = Instruction(instruction_order = 0)    
    action = DropAction(action_order = 0)   
    instruction.add_apply_action(action)    
    flow.add_instruction(instruction)
    
    match = Match()
    match.set_eth_type(eth_type = 34525)
    match.set_ipv6_src(ipv6_src = "1234:5678:9ABC:DEF0:FDCD:A987:6543:210F/76")
    match.set_ipv6_dst(ipv6_dst = "fe80:2acf:e9ff:fe21::6431/94")
    metadata = "12345"
    match.set_metadata(metadata)    
    match.set_ipv6_flabel(ipv6_flabel = 33)   
    match.set_ip_proto(ip_proto = 6)
    match.set_ip_dscp(ip_dscp = 60)
    match.set_ip_ecn(ip_ecn = 3)
    match.set_tcp_src_port(tcp_src_port = 183)
    match.set_tcp_dst_port(tcp_dst_port = 8080)
    flow.add_match(match)
   
    # --- Tunnel ID
    flow = FlowEntry()
    flow.set_flow_id(flow_id = 29)
    flow.set_flow_priority(flow_priority = 1020)

    instruction = Instruction(instruction_order = 1)    
    action = DropAction(action_order = 1)   
    instruction.add_apply_action(action)
    flow.add_instruction(instruction)

    match = Match()
    match.set_tunnel_id(tunnel_id = 2591)
    flow.add_match(match)

    # --- IPv6 Src & Dest Addresses, Metadata, IP DSCP, IP ECN, ICMPv6 Type & Code, IPv6 Label
    #     NOTES: ethernet type MUST be 34525 (0x86DD)
    #            IP Protocol MUST be 58
    flow = FlowEntry()
    flow.set_flow_id(flow_id = 30)
    flow.set_flow_priority(flow_priority = 1021)
    flow.set_flow_cookie(cookie = 25)
    flow.set_flow_hard_timeout(hard_timeout = 1200)
    flow.set_flow_idle_timeout(idle_timeout = 3400)
    
    instruction = Instruction(instruction_order = 0)
    action = DropAction(action_order = 0)
    instruction.add_apply_action(action)
    flow.add_instruction(instruction)
    
    match = Match()    
    match.set_eth_type(eth_type = 34525)
    match.set_ipv6_src(ipv6_src = "1234:5678:9ABC:DEF0:FDCD:A987:6543:210F/76")
    match.set_ipv6_dst(ipv6_dst = "fe80:2acf:e9ff:fe21::6431/94")
    metadata = "12345"
    match.set_metadata(metadata)    
    match.set_ipv6_flabel(ipv6_flabel = 33)
    match.set_ip_proto(ip_proto = 58)
    match.set_ip_dscp(ip_dscp = 60)
    match.set_ip_ecn(ip_ecn = 3)   
    match.set_icmpv6_type(icmpv6_type = 6)
    match.set_icmpv6_code(icmpv6_code = 3)
    flow.add_match(match)
    
    # --- IPv6 Src & Dest Addresses, Metadata, IP DSCP, IP ECN, TCP Src & Dst Ports,
    #     IPv6 Label, IPv6 Ext Header
    #     NOTES: ethernet type MUST be 34525 (0x86DD)
    #            IP Protocol MUST be 58
    flow = FlowEntry()
    flow.set_flow_id(flow_id = 31)
    flow.set_flow_priority(flow_priority = 1022)
    flow.set_flow_cookie(cookie = 27)
    flow.set_flow_hard_timeout(hard_timeout = 1234)
    flow.set_flow_idle_timeout(idle_timeout = 3456)
    
    instruction = Instruction(instruction_order = 0)
    action = DropAction(action_order = 0)
    instruction.add_apply_action(action)
    flow.add_instruction(instruction)

    match = Match()    
    match.set_eth_type(eth_type = 34525)
    match.set_ipv6_src(ipv6_src = "1234:5678:9ABC:DEF0:FDCD:A987:6543:210F/76")
    match.set_ipv6_dst(ipv6_dst = "fe80:2acf:e9ff:fe21::6431/94")
    metadata = "12345"
    match.set_metadata(metadata)    
    match.set_ipv6_flabel(ipv6_flabel = 33)
    match.set_ipv6_exh_hdr(ipv6_exthdr = 0)  
    match.set_ip_proto(ip_proto = 6)
    match.set_ip_dscp(ip_dscp = 60)
    match.set_ip_ecn(ip_ecn = 3)   
    match.set_tcp_src_port(tcp_src_port = 183)
    match.set_tcp_dst_port(tcp_dst_port = 8080)
    flow.add_match(match)

    # --- Push VLAN
    # NOTES:
    #      33024(0x8100) -> ethernet type => VLAN tagged frame (Customer VLAN Tag Type)
    #      34984(0x88A8) -> ethernet type => QINQ VLAN tagged frame (Service VLAN tag identifier)
    #                       Provider Bridging (IEEE 802.1ad) & 
    #                       Shortest Path Bridging IEEE 802.1aq[
    flow = FlowEntry()
    flow.set_flow_name(flow_name = "push_vlan_flow")
    flow.set_flow_id(flow_id = 32)
    flow.set_flow_priority(flow_priority = 1023)
    flow.set_flow_cookie(cookie = 401)
    flow.set_flow_cookie_mask(cookie_mask = 255)
    flow.set_flow_hard_timeout(hard_timeout = 1200)
    flow.set_flow_idle_timeout(idle_timeout = 3400)
   
    instruction = Instruction(instruction_order = 0)
    action = PushVlanHeaderAction(action_order = 0)
    action.set_eth_type(eth_type = 33024)
    instruction.add_apply_action(action)    
    action = SetFieldAction(action_order = 1)
    action.set_vlan_id(vid = 79)
    instruction.add_apply_action(action)    
    action = OutputAction(action_order = 2, port = 5)
    instruction.add_apply_action(action)
    flow.add_instruction(instruction)
  
    match = Match()    
    match.set_eth_type(eth_type = 2048)
    match.set_eth_dst(eth_dst = "FF:FF:29:01:19:61")
    match.set_eth_src(eth_src = "00:00:00:11:23:AE")
    match.set_in_port(in_port = 1)
    flow.add_match(match)   
    
    # --- Push MPLS
    # NOTE: ethernet type MUST be 34887 (0x8847) => MPLS unicast
    # ??? Controller accepts the flow but no flow added on mininet simulated ofswitch
    flow = FlowEntry()
    flow.set_flow_name(flow_name = "push_mpls_lable")
    flow.set_flow_id(flow_id = 33)
    flow.set_flow_priority(flow_priority = 1024)
    flow.set_flow_cookie(cookie = 401)
    flow.set_flow_cookie_mask(cookie_mask = 255)
   
    instruction = Instruction(instruction_order = 3)
    action = PushMplsHeaderAction(action_order = 0)
    action.set_eth_type(eth_type = 34887)
    instruction.add_apply_action(action)        
    action = SetFieldAction(action_order = 1)
    action.set_mpls_label(mpls_label = 27)
    instruction.add_apply_action(action)    
    action = OutputAction(action_order = 2, port = 2)
    instruction.add_apply_action(action)
    flow.add_instruction(instruction)
    
    flow.add_instruction(instruction)
   
    match = Match()    
    match.set_eth_type(eth_type = 2048)
    match.set_in_port(in_port = 1)
    match.set_ipv4_dst(ipv4_dst = "10.0.0.4/32")
    flow.add_match(match)    
    
    # --- Swap MPLS   
    # NOTE: ethernet type MUST be 34887 (0x8847) => MPLS unicast
    # ??? Controller accepts the flow but no flow added on mininet simulated ofswitch
    flow = FlowEntry()
    flow.set_flow_name(flow_name = "change_mpls_lable")
    flow.set_flow_id(flow_id = 34)
    flow.set_flow_priority(flow_priority = 1025)
    flow.set_flow_cookie(cookie = 401)
    flow.set_flow_cookie_mask(cookie_mask = 255)
    
    instruction = Instruction(instruction_order = 2)    
    action = SetFieldAction(action_order = 1)
    action.set_mpls_label(mpls_label = 37)
    instruction.add_apply_action(action)        
    action = OutputAction(action_order = 2, port = 2)
    instruction.add_apply_action(action)
    flow.add_instruction(instruction)

    match = Match()    
    match.set_eth_type(eth_type = 34887)
    match.set_in_port(in_port = 1)
    mpls_label = 27
    match.set_mpls_lable(mpls_label = 27)
    flow.add_match(match)        
   
    # --- Pop MPLS
    #     NOTE: ethernet type MUST be 34887 (0x8847) => MPLS unicast
    # ??? Controller accepts the flow but no flow added on mininet simulated ofswitch 
    flow = FlowEntry()
    flow.set_flow_name(flow_name = "strip_mpls_lable")
    flow.set_flow_id(flow_id = 35)
    flow.set_flow_priority(flow_priority = 1026)
    flow.set_flow_cookie(cookie = 889)
    flow.set_flow_cookie_mask(cookie_mask = 255)
    
    instruction = Instruction(instruction_order = 0)
    action = PopMplsHeaderAction(action_order = 1)
    action.set_eth_type(eth_type = 34887)
    instruction.add_apply_action(action)    
    action = OutputAction(action_order = 2, port = 2, max_len = 60)
    instruction.add_apply_action(action)
    flow.add_instruction(instruction)

    match = Match()
    match.set_eth_type(eth_type = 34887)
    match.set_in_port(in_port = 1)
    match.set_mpls_lable(mpls_label = 37)
    flow.add_match(match)        
    
    # --- Output to TABLE
    # (Submit the packet to the first flow table
    #  NOTE: This destination port can only be used in 'packet-out' messages)
    # Represents the start of the OpenFlow pipeline. This port is only valid in an
    # output action in the action list of a packet-out message, and submits the
    # packet to the first flow table so that the packet can be processed through
    # the regular OpenFlow pipeline    
    flow = FlowEntry()
    flow.set_flow_name(flow_name = "output-to-TABLE")
    flow.set_flow_id(flow_id = 36)
    flow.set_flow_priority(flow_priority = 1027)
    flow.set_flow_cookie(cookie = 101)
    flow.set_flow_cookie_mask(cookie_mask = 255)
    flow.set_flow_hard_timeout(hard_timeout = 1200)
    flow.set_flow_idle_timeout(idle_timeout = 3400)
    
    instruction = Instruction(instruction_order = 0)
    action = OutputAction(action_order = 0, port = "TABLE", max_len=60)
    instruction.add_apply_action(action)    
    flow.add_instruction(instruction)
    
    match = Match()    
    match.set_eth_type(eth_type = 34525)
    match.set_ipv6_src(ipv6_src = "1234:5678:9ABC:DEF0:FDCD:A987:6543:210F/76")
    match.set_ipv6_dst(ipv6_dst = "fe80:2acf:e9ff:fe21::6431/94")
    metadata = "12345"
    match.set_metadata(metadata)    
    match.set_ip_proto(ip_proto = 6)
    match.set_ip_dscp(ip_dscp = 60)
    match.set_ip_ecn(ip_ecn = 3)   
    match.set_tcp_src_port(tcp_src_port = 183)
    match.set_tcp_dst_port(tcp_dst_port = 8080)
    flow.add_match(match)        
    
    # --- Output to INPORT
    # (Send the packet out the input port. This reserved port must be explicitly used
    #  in order to send back out of the input port)
    # Represents the packet ingress port. Can be used only as an output port,
    # send the packet out through its ingress port
    flow = FlowEntry()
    flow.set_flow_name(flow_name = "output-to-INPORT")
    flow.set_flow_id(flow_id = 37)
    flow.set_flow_priority(flow_priority = 1028)
    flow.set_flow_cookie(cookie = 102)
    flow.set_flow_cookie_mask(cookie_mask = 255)
    flow.set_flow_hard_timeout(hard_timeout = 1200)
    flow.set_flow_idle_timeout(idle_timeout = 3400)
    
    instruction = Instruction(instruction_order = 0)
    action = OutputAction(action_order = 0, port = "INPORT", max_len=60)
    instruction.add_apply_action(action)    
    flow.add_instruction(instruction)
    
    match = Match()    
    match.set_eth_type(eth_type = 2048)
    match.set_eth_dst(eth_dst = "ff:ff:29:01:19:61")
    match.set_eth_src(eth_src = "00:00:00:11:23:ae")
    match.set_ipv4_src(ipv4_src = "17.1.2.3/8")
    match.set_ipv4_dst(ipv4_dst = "172.168.5.6/16")
    match.set_ip_proto(ip_proto = 6)
    match.set_ip_dscp(ip_dscp = 2)
    match.set_ip_ecn(ip_ecn = 2)    
    match.set_tcp_src_port(tcp_src_port = 25364)
    match.set_tcp_dst_port(tcp_dst_port = 8080)
    flow.add_match(match)
    
    # --- Output to Physical Port Number
    flow = FlowEntry()
    flow.set_flow_name(flow_name = "output-to-physical-port")
    flow.set_flow_id(flow_id = 38)
    flow.set_flow_priority(flow_priority = 1029)
    flow.set_flow_cookie(cookie = 103)
    flow.set_flow_cookie_mask(cookie_mask = 255)
    flow.set_flow_hard_timeout(hard_timeout = 1200)
    flow.set_flow_idle_timeout(idle_timeout = 3400)
    
    instruction = Instruction(instruction_order = 0)
    action = OutputAction(action_order = 0, port = 1, max_len=60)
    instruction.add_apply_action(action)    
    flow.add_instruction(instruction)
    
    match = Match()    
    match.set_eth_type(eth_type = 2048)
    match.set_eth_dst(eth_dst = "ff:ff:29:01:19:61")
    match.set_eth_src(eth_src = "00:00:00:11:23:ae")
    match.set_ipv4_src(ipv4_src = "17.1.2.3/8")
    match.set_ipv4_dst(ipv4_dst = "172.168.5.6/16")
    match.set_ip_proto(ip_proto = 6)
    match.set_ip_dscp(ip_dscp = 2)
    match.set_ip_ecn(ip_ecn = 2)    
    match.set_tcp_src_port(tcp_src_port = 25364)
    match.set_tcp_dst_port(tcp_dst_port = 8080)
    flow.add_match(match)
    
    # --- Output to LOCAL
    # (Local openflow "port")
    # Represents the switch's local networking stack and its management stack.
    # Can be used as an ingress port or as an output port. The local port enables remote entities to
    # interact with the switch and its network services via the OpenFlow network, rather than via a
    # separate control network. With a suitable set of default flow entries it can be used to implement
    # an in-band controller connection.    
    flow = FlowEntry()
    flow.set_flow_name(flow_name = "output-to-LOCAL")
    flow.set_flow_id(flow_id = 39)
    flow.set_flow_priority(flow_priority = 1030)
    flow.set_flow_cookie(cookie = 104)
    flow.set_flow_cookie_mask(cookie_mask = 255)
    flow.set_flow_hard_timeout(hard_timeout = 1200)
    flow.set_flow_idle_timeout(idle_timeout = 3400)
    
    instruction = Instruction(instruction_order = 0)
    action = OutputAction(action_order = 0, port = "LOCAL", max_len=60)
    instruction.add_apply_action(action)    
    flow.add_instruction(instruction)
    
    match = Match()    
    match.set_eth_type(eth_type = 34525)
    match.set_ipv6_src(ipv6_src = "1234:5678:9ABC:DEF0:FDCD:A987:6543:210F/76")
    match.set_ipv6_dst(ipv6_dst = "fe80:2acf:e9ff:fe21::6431/94")
    match.set_metadata(metadata = "12345")
    match.set_ip_proto(ip_proto = 6)
    match.set_ip_dscp(ip_dscp = 60)
    match.set_ip_ecn(ip_ecn = 2)
    match.set_tcp_src_port(tcp_src_port = 183)
    match.set_tcp_dst_port(tcp_dst_port = 8080)
    flow.add_match(match)
    
    # --- Output to NORMAL
    # (Process with normal L2/L3 switching)
    # Represents the traditional non-OpenFlow pipeline of the switch.
    # Can be used only as an output port and processes the packet using the normal pipeline. If the
    # switch cannot forward packets from the OpenFlow pipeline to the normal pipeline, it must indicate
    # that it does not support this action.    
    flow = FlowEntry()
    flow.set_flow_name(flow_name = "output-NORMAL")
    flow.set_flow_id(flow_id = 39)
    flow.set_flow_priority(flow_priority = 1031)
    flow.set_flow_cookie(cookie = 105)
    flow.set_flow_cookie_mask(cookie_mask = 255)
    flow.set_flow_hard_timeout(hard_timeout = 1200)
    flow.set_flow_idle_timeout(idle_timeout = 3400)
    
    instruction = Instruction(instruction_order = 0)
    action = OutputAction(action_order = 0, port = "NORMAL", max_len=60)
    instruction.add_apply_action(action)    
    flow.add_instruction(instruction)
    
    match = Match()    
    match.set_eth_type(eth_type = 34525)
    match.set_ipv6_src(ipv6_src = "1234:5678:9ABC:DEF0:FDCD:A987:6543:210F/84")
    match.set_ipv6_dst(ipv6_dst = "fe80:2acf:e9ff:fe21::6431/90")
    match.set_metadata(metadata = "12345")
    match.set_ip_proto(ip_proto = 6)
    match.set_ip_dscp(ip_dscp = 45)
    match.set_ip_ecn(ip_ecn = 2)
    match.set_tcp_src_port(tcp_src_port = 20345)
    match.set_tcp_dst_port(tcp_dst_port = 80)
    flow.add_match(match)
    
    # --- Output to FLOOD
    # (All physical ports in VLAN, except input port and those blocked or link down)
    # Represents fooding using the normal pipeline of the switch. Can be used only as
    # an output port, in general will send the packet out all standard ports, but not to
    # the ingress port, nor ports that are in OFPPS_BLOCKED state. The switch may also
    # use the packet VLAN ID to select which ports to ood.    
    flow = FlowEntry()
    flow.set_flow_name(flow_name = "output-FLOOD")
    flow.set_flow_id(flow_id = 40)
    flow.set_flow_priority(flow_priority = 1032)
    flow.set_flow_cookie(cookie = 106)
    flow.set_flow_cookie_mask(cookie_mask = 255)
    flow.set_flow_hard_timeout(hard_timeout = 1200)
    flow.set_flow_idle_timeout(idle_timeout = 3400)
    
    instruction = Instruction(instruction_order = 0)
    action = OutputAction(action_order = 0, port = "FLOOD", max_len=60)
    instruction.add_apply_action(action)    
    flow.add_instruction(instruction)
    
    match = Match()    
    match.set_eth_type(eth_type = 34525)
    match.set_ipv6_src(ipv6_src = "1234:5678:9ABC:DEF0:FDCD:A987:6543:210F/84")
    match.set_ipv6_dst(ipv6_dst = "fe80:2acf:e9ff:fe21::6431/90")
    match.set_metadata(metadata = "12345")
    match.set_ip_proto(ip_proto = 6)
    match.set_ip_dscp(ip_dscp = 45)
    match.set_ip_ecn(ip_ecn = 2)
    match.set_tcp_src_port(tcp_src_port = 20345)
    match.set_tcp_dst_port(tcp_dst_port = 80)
    flow.add_match(match)
    
    # --- Output to ALL
    # (All physical ports except input port)
    # Represents all ports the switch can use for forwarding a specific packet. Can
    # be used only as an output port. In that case a copy of the packet is sent to all standard ports,
    # excluding the packet ingress port and ports that are configured OFPPC_NO_FWD
    flow = FlowEntry()
    flow.set_flow_name(flow_name = "output-to-ALL")
    flow.set_flow_id(flow_id = 41)
    flow.set_flow_priority(flow_priority = 1033)
    flow.set_flow_cookie(cookie = 107)
    flow.set_flow_cookie_mask(cookie_mask = 255)
    flow.set_flow_hard_timeout(hard_timeout = 1200)
    flow.set_flow_idle_timeout(idle_timeout = 3400)
    
    instruction = Instruction(instruction_order = 0)
    action = OutputAction(action_order = 0, port = "ALL", max_len=60)
    instruction.add_apply_action(action)    
    flow.add_instruction(instruction)
    
    match = Match()    
    match.set_eth_type(eth_type = 2048)
    match.set_eth_dst(eth_dst = "ff:ff:29:01:19:61")
    match.set_eth_src(eth_src = "00:00:00:11:23:ae")
    match.set_ipv4_src(ipv4_src = "19.1.2.3/10")
    match.set_ipv4_dst(ipv4_dst = "172.168.5.6/18")
    match.set_ip_proto(ip_proto = 17)
    match.set_ip_dscp(ip_dscp = 8)
    match.set_ip_ecn(ip_ecn = 3) 
    match.set_udp_src_port(udp_src_port = 25364)   
    match.set_udp_dst_port(udp_dst_port = 8080)
    match.set_in_port(in_port = 1)
    flow.add_match(match)
    
    # --- Output to CONTROLLER
    # (Send to controller)
    # Represents the control channel with the OpenFlow controller. Can be used as an
    # ingress port or as an output port. When used as an output port, encapsulate the
    # packet in a 'packet-in' message and send it using the OpenFlow protocol. When used
    # as an ingress port, this identifies a packet originating from the controller    
    flow = FlowEntry()
    flow.set_flow_name(flow_name = "output-to-CONTROLLER")
    flow.set_flow_id(flow_id = 41)
    flow.set_flow_priority(flow_priority = 1034)
    flow.set_flow_cookie(cookie = 108)
    flow.set_flow_cookie_mask(cookie_mask = 255)
    flow.set_flow_hard_timeout(hard_timeout = 1200)
    flow.set_flow_idle_timeout(idle_timeout = 3400)
    
    instruction = Instruction(instruction_order = 0)
    action = OutputAction(action_order = 0, port = "CONTROLLER", max_len=60)
    instruction.add_apply_action(action)    
    flow.add_instruction(instruction)
    
    match = Match()    
    match.set_eth_type(eth_type = 2048)
    match.set_eth_dst(eth_dst = "20:14:29:01:19:61")
    match.set_eth_src(eth_src = "00:00:00:11:23:ae")
    match.set_ipv4_src(ipv4_src = "19.1.2.3/10")
    match.set_ipv4_dst(ipv4_dst = "172.168.5.6/18")
    match.set_ip_proto(ip_proto = 17)
    match.set_ip_dscp(ip_dscp = 8)
    match.set_ip_ecn(ip_ecn = 3)
    match.set_udp_src_port(udp_src_port = 25364)
    match.set_udp_dst_port(udp_dst_port = 8080)
    match.set_in_port(in_port = 1)
    flow.add_match(match)

    # --- Output to ANY
    # (Wildcard port used only for flow mod (delete) and flow stats requests. Selects
    #  all flows regardless of output port, including flows with no output port)
    # Special value used in some OpenFlow commands when no port is specified (i.e.
    # port is wildcarded). Can neither be used as an ingress port nor as an output port   
    # ??? Controller accepts the flow but no flow added on mininet simulated ofswitch 
    flow = FlowEntry()
    flow.set_flow_name(flow_name = "output-to-ANY")
    flow.set_flow_id(flow_id = 42)
    flow.set_flow_priority(flow_priority = 1035)
    flow.set_flow_cookie(cookie = 109)
    flow.set_flow_cookie_mask(cookie_mask = 255)
    flow.set_flow_hard_timeout(hard_timeout = 1200)
    flow.set_flow_idle_timeout(idle_timeout = 3400)
    
    instruction = Instruction(instruction_order = 0)
    action = OutputAction(action_order = 0, port = "ANY", max_len=60)
    instruction.add_apply_action(action)    
    flow.add_instruction(instruction)
    
    match = Match()    
    match.set_eth_type(eth_type = 2048)
    match.set_eth_dst(eth_dst = "20:14:29:01:19:61")
    match.set_eth_src(eth_src = "00:00:00:11:23:ae")
    match.set_ipv4_src(ipv4_src = "19.1.2.3/10")
    match.set_ipv4_dst(ipv4_dst = "172.168.5.6/18")
    match.set_ip_proto(ip_proto = 17)
    match.set_ip_dscp(ip_dscp = 8)
    match.set_ip_ecn(ip_ecn = 3)    
    match.set_udp_src_port(udp_src_port = 25364)
    match.set_udp_dst_port(udp_dst_port = 8080)
    match.set_in_port(in_port = 0)
    flow.add_match(match)
    
    flow_payload = flow.get_payload()
    print "flow HTTP payload"
    print flow_payload
    
''' Test code - END'''
    
'''
enum ofp_instruction_type {
OFPIT_GOTO_TABLE = 1,     /* Setup the next table in the lookup pipeline */
OFPIT_WRITE_METADATA = 2, /* Setup the metadata field for use later in pipeline */
OFPIT_WRITE_ACTIONS = 3,  /* Write the action(s) onto the datapath action set */
OFPIT_APPLY_ACTIONS = 4,  /* Applies the action(s) immediately */
OFPIT_CLEAR_ACTIONS = 5,  /* Clears all actions from the datapath action set */
OFPIT_METER = 6,          /* Apply meter (rate limiter) */
OFPIT_EXPERIMENTER = 0xFFFF /* Experimenter instruction */
};
'''
'''
enum ofp_action_type {
OFPAT_OUTPUT = 0,        /* Output to switch port. */
OFPAT_COPY_TTL_OUT = 11, /* Copy TTL "outwards" -- from next-to-outermost to outermost */
OFPAT_COPY_TTL_IN = 12,  /* Copy TTL "inwards" -- from outermost to next-to-outermost */
OFPAT_SET_MPLS_TTL = 15, /* MPLS TTL */
OFPAT_DEC_MPLS_TTL = 16, /* Decrement MPLS TTL */
OFPAT_PUSH_VLAN = 17,    /* Push a new VLAN tag */
OFPAT_POP_VLAN = 18,     /* Pop the outer VLAN tag */
OFPAT_PUSH_MPLS = 19,    /* Push a new MPLS tag */
OFPAT_POP_MPLS = 20,     /* Pop the outer MPLS tag */
OFPAT_SET_QUEUE = 21,    /* Set queue id when outputting to a port */
OFPAT_GROUP = 22,        /* Apply group. */
OFPAT_SET_NW_TTL = 23,   /* IP TTL. */
OFPAT_DEC_NW_TTL = 24,   /* Decrement IP TTL. */
OFPAT_SET_FIELD = 25,    /* Set a header field using OXM TLV format. */
OFPAT_PUSH_PBB = 26,     /* Push a new PBB service tag (I-TAG) */
OFPAT_POP_PBB = 27,      /* Pop the outer PBB service tag (I-TAG) */
OFPAT_EXPERIMENTER = 0xffff
};
'''
'''
5.9 Instructions
Each flow entry contains a set of instructions that are executed when a packet matches the entry. These
instructions result in changes to the packet, action set and/or pipeline processing.
A switch is not required to support all instruction types, just those marked
\Required Instruction" below. The controller can also query the switch about which of the
\Optional Instruction" types it supports.

Optional Instruction: Meter meter_id: Direct packet to the specified meter. As the result of
the metering, the packet may be dropped (depending on meter configuration and state).

Optional Instruction: Apply-Actions action(s): Applies the specific action(s) immediately,
without any change to the Action Set. This instruction may be used to modify the packet between
two tables or to execute multiple actions of the same type. The actions are specified as an action
list (see 5.11).

Optional Instruction: Clear-Actions: Clears all the actions in the action set immediately.

Required Instruction: Write-Actions action(s): Merges the specified action(s) into the current
action set (see 5.10). If an action of the given type exists in the current set, overwrite it, otherwise
add it.

Optional Instruction: Write-Metadata metadata / mask: Writes the masked metadata value
into the metadata field. The mask specifies which bits of the metadata register should be modified
(i.e. new metadata = old metadata & ~mask | value & mask).

Required Instruction: Goto-Table next-table-id: Indicates the next table in the processing
pipeline. The table-id must be greater than the current table-id. The flow entries of the last table
of the pipeline can not include this instruction (see 5.1). OpenFlow switches with only a single
flow table are not required to implement this instruction.

The instruction set associated with a flow entry contains a maximum of one instruction of each type. The
instructions of the set execute in the order specified by this above list. In practice, the only constraints
are that the Meter instruction is executed before the Apply-Actions instruction, that the Clear-Actions
instruction is executed before the Write-Actions instruction, and that Goto-Table is executed last.

A switch must reject a flow entry if it is unable to execute the instructions associated with the flow
entry. In this case, the switch must return an unsupported flow error (see 6.4). Flow tables may not
support every match, every instruction or every action.

5.10 Action Set
An action set is associated with each packet. This set is empty by default. A flow entry can modify the
action set using a Write-Action instruction or a Clear-Action instruction associated with a particular
match. The action set is carried between flow tables. When the instruction set of a flow entry does
not contain a Goto-Table instruction, pipeline processing stops and the actions in the action set of the
packet are executed.
An action set contains a maximum of one action of each type.

5.12 Actions
A switch is not required to support all action types, just those marked "Required Action" below. The
controller can also query the switch about which of the "Optional Action" it supports.

Required Action: Output. The Output action forwards a packet to a specified OpenFlow port (see4.1). 
OpenFlow switches must support forwarding to physical ports, switch-defined logical ports and
the required reserved ports (see 4.5).

Optional Action: Set-Queue. The set-queue action sets the queue id for a packet. When the packet is
forwarded to a port using the output action, the queue id determines which queue attached to this port
is used for scheduling and forwarding the packet. Forwarding behavior is dictated by the configuration
of the queue and is used to provide basic Quality-of-Service (QoS) support (see section 7.2.2).

Required Action: Drop. There is no explicit action to represent drops. Instead, packets whose action
sets have no output actions should be dropped. This result could come from empty instruction sets or
empty action buckets in the processing pipeline, or after executing a Clear-Actions instruction.

Required Action: Group. Process the packet through the specified group. The exact interpretation
depends on group type.

Optional Action: Push-Tag/Pop-Tag. Switches may support the ability to push/pop tags as shown in Table 6.
To aid integration with existing networks, we suggest that the ability to push/pop VLAN tags be supported.
Newly pushed tags should always be inserted as the outermost tag in the outermost valid location for
that tag. When a new VLAN tag is pushed, it should be the outermost tag inserted, immediately after
the Ethernet header and before other tags. Likewise, when a new MPLS tag is pushed, it should be the
outermost tag inserted, immediately after the Ethernet header and before other tags.
When multiple push actions are added to the action set of the packet, they apply to the packet in the
order defined by the action set rules, first MPLS, then PBB, than VLAN (see 5.10). When multiple push
actions are included in an action list, they apply to the packet in the list order (see 5.11)
'''
