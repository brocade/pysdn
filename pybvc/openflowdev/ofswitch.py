
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

ofswitch.py: OpenFlow switch properties and methods


"""

import json
import urllib2

from collections import OrderedDict

from pybvc.controller.openflownode import OpenflowNode
from pybvc.common.result import Result
from pybvc.common.status import OperStatus, STATUS
from pybvc.common.utils import (find_key_values_in_dict,
                                replace_str_value_in_dict,
                                find_key_value_in_dict,
                                find_dict_in_list,
                                strip_none,
                                dict_keys_dashed_to_underscored,
                                dbg_print)


class OFSwitch(OpenflowNode):
    """ Class that represents an instance of 'OpenFlow Switch'
        (OpenFlow capable device). """

    def __init__(self, ctrl=None, name=None, dpid=None):
        """ Initializes this object properties. """
        super(OFSwitch, self).__init__(ctrl, name)
        self.dpid = dpid
        self.ports = []

    def to_string(self):
        """ Returns string representation of this object. """
        return str(vars(self))

    def to_json(self):
        """ Returns JSON representation of this object. """
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def get_switch_info(self):
        status = OperStatus()
        info = {}
        ctrl = self.ctrl
        myname = self.name
        url = ctrl.get_node_operational_url(myname)
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
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
        return Result(status, info)

    def get_features_info(self):
        status = OperStatus()
        info = {}
        ctrl = self.ctrl
        myname = self.name
        url = ctrl.get_node_operational_url(myname)
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
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
        return Result(status, info)

    def get_ports_list(self):
        status = OperStatus()
        plist = []
        ctrl = self.ctrl
        myname = self.name
        url = ctrl.get_node_operational_url(myname)
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            obj = json.loads(resp.content)
            p1 = 'node'
            if(p1 in obj and isinstance(obj[p1], list)):
                vlist = obj[p1]
                p2 = 'node-connector'
                d = find_dict_in_list(vlist, p2)
                if (d is not None) and isinstance(d[p2], list):
                    items = d[p2]
                    p3 = 'flow-node-inventory:port-number'
                    for item in items:
                        if(isinstance(item, dict) and p3 in item):
                            plist.append(item[p3])
                status.set_status(STATUS.OK)
            else:
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return Result(status, sorted(plist))

    def get_port_detail_info(self, portnum):
        status = OperStatus()
        info = None
        templateUrlExt = "/node-connector/{}:{}"
        urlext = templateUrlExt.format(self.name, portnum)
        ctrl = self.ctrl
        url = ctrl.get_node_operational_url(self.name)
        url += urlext
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            p = 'node-connector'
            d = json.loads(resp.content)
            v = d.get(p, None)
            if (isinstance(v, list) and len(v) != 0):
                info = v[0]
            status.set_status(STATUS.OK
                              if info is not None
                              else STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return Result(status, info)

    def get_port_brief_info(self, portnum):
        status = OperStatus()
        info = {}
        templateUrlExt = "/node-connector/{}:{}"
        urlext = templateUrlExt.format(self.name, portnum)
        ctrl = self.ctrl
        url = ctrl.get_node_operational_url(self.name)
        url += urlext
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            d = json.loads(resp.content)
            p = 'node-connector'
            v = find_key_value_in_dict(d, p)
            if (isinstance(v, list) and len(v) == 1):
                try:
                    d = v[0]
                    info['id'] = d['id']
                    info['number'] = d['flow-node-inventory:port-number']
                    info['name'] = d['flow-node-inventory:name']
                    info['MAC address'] = \
                        d['flow-node-inventory:hardware-address']
                    s = d['flow-node-inventory:current-feature']
                    info['current feature'] = s.upper()
                    status.set_status(STATUS.OK)
                except () as e:
                    print "Error: " + repr(e)
                    status.set_status(STATUS.DATA_NOT_FOUND)
            else:
                msg = "TODO (unexpected data format in response)"
                dbg_print(msg)
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return Result(status, info)

    def get_ports_brief_info(self):
        status = OperStatus()
        info = []
        ctrl = self.ctrl
        myname = self.name
        url = ctrl.get_node_operational_url(myname)
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
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
                        port['number'] = \
                            item['flow-node-inventory:port-number']
                        port['name'] = item['flow-node-inventory:name']
                        port['MAC address'] = \
                            item['flow-node-inventory:hardware-address']
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
        return Result(status, info)

    def add_modify_flow(self, flow_entry):
        status = OperStatus()
        templateUrlExt = "/table/{}/flow/{}"
        headers = {'content-type': 'application/yang.data+json'}
        resp = None
        if isinstance(flow_entry, FlowEntry):
            ctrl = self.ctrl
            url = ctrl.get_node_config_url(self.name)
            urlext = templateUrlExt.format(flow_entry.get_flow_table_id(),
                                           flow_entry.get_flow_id())
            url += urlext
            payload = flow_entry.get_payload()
            resp = ctrl.http_put_request(url, payload, headers)
            if(resp is None):
                status.set_status(STATUS.CONN_ERROR)
            elif(resp.content is None):
                status.set_status(STATUS.CTRL_INTERNAL_ERROR)
            elif (resp.status_code == 200):
                status.set_status(STATUS.OK)
            else:
                status.set_status(STATUS.HTTP_ERROR, resp)
        else:
            msg = "TODO (unexpected data format in response)"
            dbg_print(msg)
            status.set_status(STATUS.MALFORM_DATA)
        return Result(status, resp)

    def add_modify_flow_json(self, table_id, flow_id, flow_json):
        status = OperStatus()
        model_ref = "flow-node-inventory:flow"
        templateUrlExt = "/table/{}/flow/{}"
        headers = {'content-type': 'application/yang.data+json'}
        resp = None
        if isinstance(flow_json, basestring):
            ctrl = self.ctrl
            url = ctrl.get_node_config_url(self.name)
            urlext = templateUrlExt.format(table_id, flow_id)
            url += urlext
            payload = {model_ref: json.loads(flow_json)}
            resp = ctrl.http_put_request(url, json.dumps(payload), headers)
            if(resp is None):
                status.set_status(STATUS.CONN_ERROR)
            elif(resp.content is None):
                status.set_status(STATUS.CTRL_INTERNAL_ERROR)
            elif (resp.status_code == 200):
                status.set_status(STATUS.OK)
            else:
                status.set_status(STATUS.HTTP_ERROR, resp)
        else:
            dbg_print("DEBUG: unsupported data format ")
            status.set_status(STATUS.MALFORM_DATA)
        return Result(status, resp)

    def delete_flow(self, table_id, flow_id):
        status = OperStatus()
        templateUrlExt = "/table/{}/flow/{}"
        ctrl = self.ctrl
        url = ctrl.get_node_config_url(self.name)
        urlext = templateUrlExt.format(table_id, urllib2.quote(str(flow_id)))
        url += urlext
        resp = ctrl.http_delete_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            status.set_status(STATUS.OK)
        elif (resp.status_code == 404):
            status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return Result(status, None)

    def delete_flows(self, flow_table_id):
        status = OperStatus()
        templateUrlExt = "/table/{}"
        ctrl = self.ctrl
        url = ctrl.get_node_config_url(self.name)
        urlext = templateUrlExt.format(flow_table_id)
        url += urlext
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

    def get_flow(self, tableid, flowid, operational=True):
        status = OperStatus()
        flow = None
        templateUrlExt = "/flow-node-inventory:table/{}/flow/{}"
        urlext = templateUrlExt.format(tableid, urllib2.quote(str(flowid)))
        ctrl = self.ctrl
        url = ""
        if (operational):
            url = ctrl.get_node_operational_url(self.name)
        else:
            url = ctrl.get_node_config_url(self.name)
        url += urlext
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            p = 'flow-node-inventory:flow'
            d = json.loads(resp.content)
            v = d.get(p, None)
            if (isinstance(v, list) and len(v) != 0):
                flow = v[0]
            status.set_status(STATUS.OK
                              if flow is not None
                              else STATUS.DATA_NOT_FOUND)
        elif (resp.status_code == 404):
            status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return Result(status, flow)

    def get_operational_flow(self, tableid, flowid):
        return self.get_flow(tableid, flowid, operational=True)

    def get_configured_flow(self, tableid, flowid):
        return self.get_flow(tableid, flowid, operational=False)

    def get_flows(self, tableid, operational=True):
        status = OperStatus()
        flows = None
        templateUrlExt = "/flow-node-inventory:table/{}"
        urlext = templateUrlExt.format(tableid)
        ctrl = self.ctrl
        url = ""
        if (operational):
            url = ctrl.get_node_operational_url(self.name)
        else:
            url = ctrl.get_node_config_url(self.name)
        url += urlext
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            p1 = 'flow-node-inventory:table'
            p2 = 'flow'
            d = json.loads(resp.content)
            v = d.get(p1, None)
            if (isinstance(v, list) and len(v) != 0):
                flows = v[0].get(p2, None)
            status.set_status(STATUS.OK
                              if flows is not None
                              else STATUS.DATA_NOT_FOUND)
        elif (resp.status_code == 404):
            status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return Result(status, flows)

    def get_operational_flows(self, tableid):
        return self.get_flows(tableid, operational=True)

    def get_configured_flows(self, tableid):
        return self.get_flows(tableid, operational=False)

    def get_FlowEntry(self, table_id, flow_id, operational=True):
        flowEntry = None
        result = self.get_flow(table_id, flow_id, operational)
        status = result.get_status()
        if(status.eq(STATUS.OK)):
            d = result.get_data()
            flowEntry = FlowEntry(flow_dict=d)
        return Result(status, flowEntry)

    def get_operational_FlowEntry(self, tableid, flowid):
        return self.get_FlowEntry(tableid, flowid, True)

    def get_configured_FlowEntry(self, tableid, flowid):
        return self.get_FlowEntry(tableid, flowid, False)

    def get_FlowEntries(self, tableid, operational=True):
        # list of 'FlowEntry objects
        flows = []
        result = self.get_flows(tableid, operational)
        status = result.get_status()
        if(status.eq(STATUS.OK)):
            data = result.get_data()
            for item in data:
                fe = FlowEntry(flow_dict=item)
                flows.append(fe)
        return Result(status, flows)

    def get_operational_FlowEntries(self, flow_table_id):
        return self.get_FlowEntries(flow_table_id, True)

    def get_configured_FlowEntries(self, flow_table_id):
        return self.get_FlowEntries(flow_table_id, False)

    def get_group_ids(self, operational=True):
        """ Retrieve list of group IDs available on the Controller
            (refer to operational or configuration data store)
        """
        status = OperStatus()
        group_ids = []
        ctrl = self.ctrl
        url = ""
        if (operational):
            url = ctrl.get_node_operational_url(self.name)
        else:
            url = ctrl.get_node_config_url(self.name)
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            p1 = 'node'
            d = json.loads(resp.content)
            l1 = d.get(p1, None)
            if (isinstance(l1, list) and l1):
                p2 = 'flow-node-inventory:group'
                l2 = l1[0].get(p2, None)
                if (isinstance(l2, list) and l2):
                    p3 = 'group-id'
                    for item in l2:
                        gid = item.get(p3, None)
                        if gid:
                            group_ids.append(gid)
                status.set_status(STATUS.OK if group_ids
                                  else STATUS.DATA_NOT_FOUND)
        elif (resp.status_code == 404):
            status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return Result(status, sorted(group_ids))

    def get_operational_group_ids(self):
        """ Retrieve list of group IDs in the operational data store
            of the Controller
        """
        return self.get_group_ids(operational=True)

    def get_configured_group_ids(self):
        """ Retrieve list of group IDs in the configuration data store
            of the Controller
        """
        return self.get_group_ids(operational=False)

    def add_modify_group(self, group_entry):
        """ Create a new or modify an existing group in the configuration
            data store of the Controller
        """
        status = OperStatus()
        templateUrlExt = "/flow-node-inventory:group/{}"
        headers = {'content-type': 'application/yang.data+json'}
        resp = None
        if isinstance(group_entry, GroupEntry):
            ctrl = self.ctrl
            url = ctrl.get_node_config_url(self.name)
            urlext = templateUrlExt.format(group_entry.get_group_id())
            url += urlext
            payload = group_entry.get_payload()
            resp = ctrl.http_put_request(url, payload, headers)
            if(resp is None):
                status.set_status(STATUS.CONN_ERROR)
            elif(resp.content is None):
                status.set_status(STATUS.CTRL_INTERNAL_ERROR)
            elif (resp.status_code == 200):
                status.set_status(STATUS.OK)
            else:
                status.set_status(STATUS.HTTP_ERROR, resp)
        else:
            dbg_print("DEBUG: unsupported data format ")
            status.set_status(STATUS.MALFORM_DATA)
        return Result(status, resp)

    def add_modify_group_json(self, group_id, group_json):
        """ Create a new or modify an existing group in the configuration
            data store of the Controller
        """
        status = OperStatus()
        model_ref = "flow-node-inventory:group"
        templateUrlExt = "/" + model_ref + "/{}"
        headers = {'content-type': 'application/yang.data+json'}
        resp = None
        if isinstance(group_json, basestring):
            ctrl = self.ctrl
            url = ctrl.get_node_config_url(self.name)
            urlext = templateUrlExt.format(group_id)
            url += urlext
            payload = {model_ref: json.loads(group_json)}
            resp = ctrl.http_put_request(url, json.dumps(payload), headers)
            if(resp is None):
                status.set_status(STATUS.CONN_ERROR)
            elif(resp.content is None):
                status.set_status(STATUS.CTRL_INTERNAL_ERROR)
            elif (resp.status_code == 200):
                status.set_status(STATUS.OK)
            else:
                status.set_status(STATUS.HTTP_ERROR, resp)
        else:
            dbg_print("DEBUG: unsupported data format ")
            status.set_status(STATUS.MALFORM_DATA)

        return Result(status, resp)

    def delete_group(self, group_id):
        """ Remove given group from the configuration data store
            of the Controller
        """
        status = OperStatus()
        templateUrlExt = "/flow-node-inventory:group/{}"
        ctrl = self.ctrl
        url = ctrl.get_node_config_url(self.name)
        urlext = templateUrlExt.format(group_id)
        url += urlext
        resp = ctrl.http_delete_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            status.set_status(STATUS.OK)
        elif (resp.status_code == 404):
            status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return Result(status, None)

    def get_group(self, group_id, operational=True, decode_object=False):
        """ Retrieve group information from the Controller,
            (refer to operational or configuration data store)
        """
        status = OperStatus()
        group = None
        templateUrlExt = "/flow-node-inventory:group/{}"
        urlext = templateUrlExt.format(group_id)
        ctrl = self.ctrl
        url = ""
        if (operational):
            url = ctrl.get_node_operational_url(self.name)
        else:
            url = ctrl.get_node_config_url(self.name)
        url += urlext
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            p = 'flow-node-inventory:group'
            l = json.loads(resp.content).get(p, None)
            if (isinstance(l, list) and l):
                d = l[0]
                if decode_object:
                    group = GroupEntry(group_dict=d)
                else:
                    group = d

            status.set_status(STATUS.OK if group else STATUS.DATA_NOT_FOUND)
        elif (resp.status_code == 404):
            status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return Result(status, group)

    def get_operational_group(self, group_id, decode_object=False):
        """ Retrieve group information from the Controller's
            operational data store
        """
        return self.get_group(group_id, True, decode_object)

    def get_configured_group(self, group_id, decode_object=False):
        """ Retrieve group information from the Controller's
            configuration data store
        """
        return self.get_group(group_id, False, decode_object)

    def get_configured_groups(self, decode_object=False):
        groups = []
        result = self.get_groups(operational=False)
        status = result.get_status()
        if(status.eq(STATUS.OK)):
            data = result.get_data()
            for d in data:
                if decode_object:
                    group = GroupEntry(group_dict=d)
                else:
                    group = d

                groups.append(group)

        return Result(status, groups)

    def get_group_description(self, group_id, decode_object=False):
        """ Retrieve description of the given group (along with
            the group's bucket actions) from the Controller's
            operational data store
        """
        status = OperStatus()
        group = None
        templateUrlExt = "/flow-node-inventory:group/{}" + \
                         "/opendaylight-group-statistics:group-desc"
        urlext = templateUrlExt.format(group_id)
        ctrl = self.ctrl
        url = ctrl.get_node_operational_url(self.name)
        url += urlext
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            p = 'opendaylight-group-statistics:group-desc'
            d = json.loads(resp.content).get(p, None)
            if decode_object:
                group = GroupDescription(d)
            else:
                group = d

            status.set_status(STATUS.OK if group else STATUS.DATA_NOT_FOUND)
        elif (resp.status_code == 404):
            status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return Result(status, group)

    def get_groups_description(self, decode_object=False):
        """ Retrieve description of all groups (along with
            the group's bucket actions) from the Controller's
            operational data store
        """
        groups = []
        result = self.get_groups(operational=True)
        status = result.get_status()
        if(status.eq(STATUS.OK)):
            data = result.get_data()
            p1 = 'opendaylight-group-statistics:group-desc'
            for item in data:
                d = item.get(p1)
                if d:
                    if decode_object:
                        group = GroupDescription(d)
                    else:
                        group = d

                    groups.append(group)

        return Result(status, groups)

    def get_group_statistics(self, group_id, decode_object=False):
        """  Retrieve statistics for the given group in the Controller's
             operational data store
        """
        status = OperStatus()
        group = None
        templateUrlExt = "/flow-node-inventory:group/{}" + \
                         "/opendaylight-group-statistics:group-statistics/"
        urlext = templateUrlExt.format(group_id)
        ctrl = self.ctrl
        url = ctrl.get_node_operational_url(self.name)
        url += urlext
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            p = 'opendaylight-group-statistics:group-statistics'
            d = json.loads(resp.content).get(p, None)
            if decode_object:
                group = GroupStatistics(d)
            else:
                group = d

            status.set_status(STATUS.OK if group else STATUS.DATA_NOT_FOUND)
        elif (resp.status_code == 404):
            status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return Result(status, group)

    def get_groups_statistics(self, decode_object=False):
        """  Retrieve statistics for all groups in the Controller's
             operational data store
        """
        groups = []
        result = self.get_groups(operational=True)
        status = result.get_status()
        if(status.eq(STATUS.OK)):
            data = result.get_data()
            p1 = 'opendaylight-group-statistics:group-statistics'
            for item in data:
                d = item.get(p1)
                if d:
                    if decode_object:
                        group = GroupStatistics(d)
                    else:
                        group = d

                    groups.append(group)

        return Result(status, groups)

    def get_group_features(self, decode_object=False):
        """ Retrieve from the Controller's operational data store
            information about group features supported by the
            OpenFlow switch
        """
        status = OperStatus()
        group_features = None
        templateUrlExt = "/opendaylight-group-statistics:group-features"
        urlext = templateUrlExt
        ctrl = self.ctrl
        url = ctrl.get_node_operational_url(self.name)
        url += urlext
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            p = 'opendaylight-group-statistics:group-features'
            d = json.loads(resp.content).get(p, None)
            if decode_object:
                group_features = GroupFeatures(d)
            else:
                group_features = d

            status.set_status(STATUS.OK
                              if group_features
                              else STATUS.DATA_NOT_FOUND)
        elif (resp.status_code == 404):
            status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return Result(status, group_features)

    def get_groups(self, operational=True):
        status = OperStatus()
        groups = None
        ctrl = self.ctrl

        url = ""
        if (operational):
            url = ctrl.get_node_operational_url(self.name)
        else:
            url = ctrl.get_node_config_url(self.name)

        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            p1 = 'node'
            d = json.loads(resp.content)
            l1 = d.get(p1, None)
            if (isinstance(l1, list) and l1):
                p2 = 'flow-node-inventory:group'
                l2 = l1[0].get(p2, None)
                if (isinstance(l2, list) and l2):
                    groups = l2
            status.set_status(STATUS.OK
                              if groups
                              else STATUS.DATA_NOT_FOUND)
        elif (resp.status_code == 404):
            status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return Result(status, groups)

    def get_GroupEntry(self, group_id, operational=True):
        groupEntry = None
        result = self.get_group(group_id, operational)
        status = result.get_status()
        if(status.eq(STATUS.OK)):
            d = result.get_data()
            groupEntry = GroupEntry(group_dict=d)

        return Result(status, groupEntry)

    def get_operational_GroupEntry(self, group_id):
        return self.get_GroupEntry(group_id, True)

    def get_configured_GroupEntry(self, group_id):
        return self.get_GroupEntry(group_id, False)

    def get_GroupEntries(self, operational=True):
        groups = []  # list of 'GroupEntry objects
        result = self.get_groups(operational)
        status = result.get_status()
        if(status.eq(STATUS.OK)):
            data = result.get_data()
            for item in data:
                ge = GroupEntry(group_dict=item)
                groups.append(ge)

        return Result(status, groups)

    def get_operational_GroupEntries(self):
        return self.get_GroupEntries(True)

    def get_configured_GroupEntries(self):
        return self.get_GroupEntries(False)

    def get_port_queue_stats(self, port_num, queue_id, decode_obj=False):
        status = OperStatus()
        queue_stats = None
        s = ("opendaylight-queue-statistics:"
             "flow-capable-node-connector-queue-statistics")
        templateUrlExt = ("/node-connector/{}:{}/"
                          "flow-node-inventory:queue/{}/") + s
        ctrl = self.ctrl
        myname = self.name
        url = ctrl.get_node_operational_url(myname)
        urlext = templateUrlExt.format(myname, port_num, queue_id)
        url += urlext

        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            d = json.loads(resp.content).get(s, None)
            if d:
                queue_stats = QueueStats(queue_id, d) if decode_obj else d
            status.set_status(STATUS.OK
                              if queue_stats
                              else STATUS.DATA_NOT_FOUND)
        elif (resp.status_code == 404):
            status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return Result(status, queue_stats)

    def get_port_queues_stats(self, port_num, decode_obj=False):
        status = OperStatus()
        queue_stats = []
        templateUrlExt = "/node-connector/{}:{}/"
        ctrl = self.ctrl
        myname = self.name
        url = ctrl.get_node_operational_url(myname)
        urlext = templateUrlExt.format(myname, port_num)
        url += urlext

        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            p = 'node-connector'
            l = json.loads(resp.content).get(p)
            if isinstance(l, list) and isinstance(l[0], dict):
                p1 = 'flow-node-inventory:queue'
                l1 = l[0].get(p1)
                if isinstance(l1, list) and l1:
                    p2 = 'queue-id'
                    p3 = ('opendaylight-queue-statistics:'
                          'flow-capable-node-connector-queue-statistics')
                    for item in l1:
                        qi = item.get(p2)
                        qs = item.get(p3)
                        if qi is not None and qs is not None:
                            stats = QueueStats(qi, qs) if decode_obj else qs
                            queue_stats.append(stats)

            status.set_status(STATUS.OK
                              if queue_stats
                              else STATUS.DATA_NOT_FOUND)
        elif (resp.status_code == 404):
            status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return Result(status, queue_stats)

    def get_meter_features(self, decode_object=False):
        """ Retrieve from the Controller's operational data store
            information about metering features supported by the
            OpenFlow switch
        """

        status = OperStatus()
        meter_features = None
        templateUrlExt = "/opendaylight-meter-statistics:meter-features"
        urlext = templateUrlExt
        ctrl = self.ctrl
        url = ctrl.get_node_operational_url(self.name)
        url += urlext
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            p = 'opendaylight-meter-statistics:meter-features'
            d = json.loads(resp.content).get(p, None)
            if d:
                if decode_object:
                    meter_features = MeterFeatures(d)
                else:
                    meter_features = d
            else:
                msg = "TODO (unexpected data format in response)"
                dbg_print(msg)
            status.set_status(STATUS.OK
                              if meter_features
                              else STATUS.DATA_NOT_FOUND)
        elif (resp.status_code == 404):
            status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return Result(status, meter_features)


class FlowEntry(object):
    """ Class for creating and interacting with OpenFlow flows """

    ''' Reference name in the YANG data tree on the Controller '''
    _mn = "flow-node-inventory:flow"

    def __attrs__(self):
        ''' Unique identifier of this FlowEntry in the Controller's
            data store
        '''
        self.id = None
        ''' Opaque Controller-issued identifier '''
        self.cookie = None
        ''' Mask used to restrict the cookie bits that must match
            when the command is OFPFC_MODIFY* or OFPFC_DELETE*. A
            value of 0 indicates no restriction
        '''
        self.cookie_mask = None
        ''' ID of the table to put the flow in '''
        self.table_id = None
        ''' Priority level of flow entry '''
        self.priority = None
        ''' Idle time before discarding (seconds) '''
        self.idle_timeout = None
        ''' Max time before discarding (seconds) '''
        self.hard_timeout = None
        ''' Modify/Delete entry strictly matching wildcards and priority '''
        self.strict = None
        ''' For OFPFC_DELETE* commands, require matching entries to include
            this as an output port.
            A value of OFPP_ANY indicates no restriction.
        '''
        self.out_port = None
        ''' For OFPFC_DELETE* commands, require matching entries to include
            this as an output group.
            A value of OFPG_ANY indicates no restriction
        '''
        self.out_group = None
        ''' Bitmap of OFPFF_* flags '''
        self.flags = None
        ''' This FlowEntry name in the FlowTable (internal Controller's
            inventory attribute) '''
        self.flow_name = None
        ''' This FlowEntry identifier in the FlowTable (internal
            Controller's inventory attribute)
        '''
        self.id = None
        ''' ??? (internal Controller's inventory attribute) '''
        self.installHw = None
        ''' Boolean flag used to enforce OpenFlow switch to do ordered
            message processing. Barrier request/reply messages are used
            by the controller to ensure message dependencies
            have been met or to receive notifications for completed
            operations. When the controller wants to ensure message
            dependencies have been met or wants to receive notifications for
            completed operations, it may use an OFPT_BARRIER_REQUEST message.
            This message has no body. Upon receipt, the switch must finish
            processing all previously-received messages, including
            sending corresponding reply or error messages, before
            executing any messages beyond the Barrier Request.
        '''
        self.barrier = None
        ''' Buffered packet to apply to, or OFP_NO_BUFFER. Not meaningful
            for OFPFC_DELETE*
        '''
        self.buffer_id = None
        '''  Flow match fields '''
        self.match = None
        ''' Instructions to be executed when a flow matches this flow entry
            match fields
        '''
        self.instructions = {'instruction': []}

    def __init__(self, flow_json=None, flow_dict=None):
        self.__attrs__()
        assert_msg = ("[FlowEntry] either '%s' or '%s' should be used, "
                      "not both" % ('flow_json', 'flow_dict'))
        assert(not ((flow_json is not None) and
                    (flow_dict is not None))), assert_msg
        if (flow_dict is not None):
            self.__init_from_dict__(flow_dict)
        elif (flow_json is not None):
            self.__init_from_json__(flow_json)

    def __init_from_json__(self, s):
        if (s is not None and isinstance(s, basestring)):
            js = s.replace('opendaylight_flow_statistics:flow_statistics',
                           'flow_statistics')
            obj = json.loads(js)
            d = dict_keys_dashed_to_underscored(obj)
            for k, v in d.items():
                if (k == 'match'):
                    match = Match(v)
                    self.add_match(match)
                elif (k == 'instructions'):
                    instructions = Instructions(v)
                    self.add_instructions(instructions)
                else:
                    setattr(self, k, v)
        else:
            raise TypeError("[FlowEntry] wrong argument type '%s'"
                            " (JSON 'string' is expected)" % type(s))

    def __init_from_dict__(self, d):
        if (d is not None and isinstance(d, dict)):
            js = json.dumps(d)
            self.__init_from_json__(js)
        else:
            raise TypeError("[FlowEntry] wrong argument type '%s'"
                            " ('dict' is expected)" % type(d))

    def to_json(self):
        """ Return FlowEntry as JSON """
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def to_yang_json(self, strip=False):
        s = self.to_json()
        # Convert all 'underscored' keywords to 'dash-separated' form used
        # by ODL YANG models naming conventions
        s = s.replace('_', '-')
        # Following are exceptions from the common ODL rules for having all
        # multi-part keywords in YANG models being hash separated
        s = s.replace('table-id', 'table_id')
        s = s.replace('cookie-mask', 'cookie_mask')
        if strip:
            # ignore unassigned ("empty") attributes
            d1 = json.loads(s)
            d2 = strip_none(d1)
            s = json.dumps(d2, sort_keys=True, indent=4)
        return s

    def get_payload(self):
        """ Return FlowEntry as a payload for the HTTP request body """
        s = self.to_json()
        # Convert all 'underscored' keywords to 'dash-separated' form used
        # by ODL YANG models naming conventions
        s = s.replace('_', '-')
        # Following are exceptions from the common ODL rules for having all
        # multi-part keywords in YANG models being hash separated
        s = s.replace('table-id', 'table_id')
        s = s.replace('cookie-mask', 'cookie_mask')
        d1 = json.loads(s)
        d2 = strip_none(d1)
        payload = {self._mn: d2}
        return json.dumps(payload, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def to_ofp_oxm_syntax(self):
        odc = OrderedDict()
        # Flow Cookie
        v = self.get_flow_cookie()
        if (v is not None):
            odc['cookie'] = hex(int(v))
        # Flow Duration
        v = self.get_duration()
        if (v is not None):
            odc['duration'] = "{}s".format(v)
        # Flow Table ID
        v = self.get_flow_table_id()
        if (v is not None):
            odc['table'] = v
        # Flow Counters
        v = self.get_pkts_cnt()
        if (v is not None):
            odc['n_packets'] = v
        v = self.get_bytes_cnt()
        if (v is not None):
            odc['n_bytes'] = v
        # Flow Timeouts
        v = self.get_flow_idle_timeout()
        if (v is not None):
            odc['idle_timeout'] = v
        v = self.get_flow_hard_timeout()
        if (v is not None):
            odc['hard_timeout'] = v
        # Flow Priority
        v = self.get_flow_priority()
        if (v is not None):
            odc['priority'] = v
        sc = json.dumps(odc, separators=(',', '='))
        sc = sc.translate(None, '"{} ').replace(':', '=')

        # Flow Match
        sm = ""
        m = self.get_match_fields()
        if (m is not None):
            odm = OrderedDict()
            v = m.get_in_port()
            if (v is not None):
                odm['in_port'] = v
            v = m.get_eth_type()
            if (v is not None):
                odm['eth_type'] = hex(int(v))
            v = m.get_eth_src()
            if (v is not None):
                odm['eth_src'] = v
            v = m.get_eth_dst()
            if (v is not None):
                odm['eth_dst'] = v
            v = m.get_vlan_id()
            if (v is not None):
                odm['vlan_vid'] = v
            v = m.get_vlan_pcp()
            if (v is not None):
                odm['vlan_pcp'] = v
            v = m.get_ip_proto()
            if (v is not None):
                odm['ip_proto'] = v
            v = m.get_ip_dscp()
            if (v is not None):
                odm['ip_dscp'] = v
            v = m.get_ip_ecn()
            if (v is not None):
                odm['ip_ecn'] = v
            v = m.get_icmp4_type()
            if (v is not None):
                odm['icmpv4_type'] = v
            v = m.get_icmpv4_code()
            if (v is not None):
                odm['icmpv4_code'] = v
            v = m.get_icmpv6_type()
            if (v is not None):
                odm['icmpv6_type'] = v
                v = m.get_icmpv6_code()
            if (v is not None):
                odm['icmpv6_code'] = v
            v = m.get_ipv4_src()
            if (v is not None):
                odm['ipv4_src'] = v
            v = m.get_ipv4_dst()
            if (v is not None):
                odm['ipv4_dst'] = v
            v = m.get_ipv6_src()
            if (v is not None):
                odm['ipv6_src'] = v
            v = m.get_ipv6_dst()
            if (v is not None):
                odm['ipv6_dst'] = v
                v = m.get_ipv6_flabel()
            if (v is not None):
                odm['ipv6_flabel'] = v
            v = m.get_ipv6_exh_hdr()
            if (v is not None):
                odm['ipv6_exthdr'] = v
            v = m.get_udp_src()
            if (v is not None):
                odm['udp_src'] = v
            v = m.get_udp_dst()
            if (v is not None):
                odm['udp_dst'] = v
            v = m.get_tcp_src()
            if (v is not None):
                odm['tcp_src'] = v
            v = m.get_tcp_dst()
            if (v is not None):
                odm['tcp_dst'] = v
            v = m.get_sctp_src()
            if (v is not None):
                odm['sctp_src'] = v
            v = m.get_sctp_dst()
            if (v is not None):
                odm['sctp_dst'] = v
            v = m.get_arp_opcode()
            if (v is not None):
                odm['arp_op'] = v
            v = m.get_arp_src_transport_address()
            if (v is not None):
                odm['arp_spa'] = v
            v = m.get_arp_tgt_transport_address()
            if (v is not None):
                odm['arp_tpa'] = v
            v = m.get_arp_src_hw_address()
            if (v is not None):
                odm['arp_sha'] = v
            v = m.get_arp_tgt_hw_address()
            if (v is not None):
                odm['arp_tpa'] = v
            v = m.get_mpls_label()
            if (v is not None):
                odm['mpls_label'] = v
            v = m.get_mpls_tc()
            if (v is not None):
                odm['mpls_tc'] = v
            v = m.get_mpls_bos()
            if (v is not None):
                odm['mpls_bos'] = v
            v = m.get_tunnel_id()
            if (v is not None):
                odm['tunnel_id'] = v
            v = m.get_metadata()
            if (v is not None):
                odm['metadata'] = v

            sm = json.dumps(odm, separators=(',', '='))
            sm = sm.translate(None, '"{} ')
            sm = "matches={" + sm + "}"

        # Flow Instructions/Actions
        instructions = self.get_instructions()
        apply_actions = []
        for instruction in instructions:
            if instruction.is_apply_actions_type():
                actions = instruction.get_apply_actions()
                for action in actions:
                    s = action.to_ofp_oxm_syntax()
                    if (s):
                        apply_actions.append(s)
                    else:
                        msg = ("[FlowEntry->to_ofp_oxm_syntax]"
                               " no value for action %s" % action)
                        dbg_print(msg)

        sa = "actions={"
        actions_list = apply_actions
        if(actions_list):
            sa += ",".join(actions_list)
        sa += "}"
        return sc + " " + sm + " " + sa

    def set_flow_table_id(self, table_id):
        self.table_id = table_id

    def get_flow_table_id(self):
        res = None
        p = 'table_id'
        if hasattr(self, p):
            res = self.table_id
        return res

    def set_flow_name(self, flow_name):
        self.flow_name = flow_name

    def get_flow_name(self):
        return self.flow_name

    def set_flow_id(self, flow_id):
        self.id = flow_id

    def get_flow_id(self):
        return self.id

    def set_flow_install_hw(self, install_hw):
        self.installHw = install_hw

    def get_flow_install_hw(self):
        return self.installHw

    def set_flow_barrier(self, barrier):
        self.barrier = barrier

    def get_flow_barrier(self, barrier):
        return self.barrier

    def set_flow_priority(self, flow_priority):
        self.priority = flow_priority

    def get_flow_priority(self):
        res = None
        p = 'priority'
        if hasattr(self, p):
            res = self.priority
        return res

    def set_flow_hard_timeout(self, hard_timeout):
        self.hard_timeout = hard_timeout

    def get_flow_hard_timeout(self):
        res = None
        p = 'hard_timeout'
        if hasattr(self, p):
            res = self.hard_timeout
        return res

    def set_flow_idle_timeout(self, idle_timeout):
        self.idle_timeout = idle_timeout

    def get_flow_idle_timeout(self):
        res = None
        p = 'idle_timeout'
        if hasattr(self, p):
            res = self.idle_timeout
        return res

    def set_flow_cookie(self, cookie):
        self.cookie = cookie

    def get_flow_cookie(self):
        if hasattr(self, 'cookie'):
            return self.cookie
        else:
            return None

    def set_flow_cookie_mask(self, cookie_mask):
        self.cookie_mask = cookie_mask

    def get_flow_cookie_mask(self):
        return self.cookie_mask

    def set_flow_strict(self, strict):
        self.strict = strict

    def get_flow_strict(self):
        return self.strict

    def get_duration(self):
        res = None
        p = 'flow_statistics'
        if (hasattr(self, p) and isinstance(getattr(self, p), dict)):
            p1 = 'duration'
            v = find_key_value_in_dict(self.flow_statistics, p1)
            if (v is not None and type(v) is dict):
                p2 = 'second'
                p3 = 'nanosecond'
                if (p2 in v and p3 in v):
                    s = v['second']
                    ns = v['nanosecond']
                    res = float(s * 1000000000 + ns) / 1000000000
        return res

    def get_pkts_cnt(self):
        res = None
        p = 'flow_statistics'
        if (hasattr(self, p) and isinstance(getattr(self, p), dict)):
            p1 = 'packet_count'
            v = find_key_value_in_dict(self.flow_statistics, p1)
            if (v is not None and type(v) is int):
                res = v
        return res

    def get_bytes_cnt(self):
        res = None
        p = 'flow_statistics'
        if (hasattr(self, p) and isinstance(getattr(self, p), dict)):
            p1 = 'byte_count'
            v = find_key_value_in_dict(self.flow_statistics, p1)
            if (v is not None and type(v) is int):
                res = v
        return res

    def add_instruction(self, instruction):
        if isinstance(instruction, Instruction):
            self.instructions['instruction'].append(instruction)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('Instruction' instance is expected)" %
                            instruction)

    def get_instructions(self):
        res = None
        p = 'instructions'
        if (hasattr(self, p)):
            attr = getattr(self, p)
            p2 = 'instruction'
            if (isinstance(attr, dict) and p2 in attr):
                res = attr[p2]
        return res

    def add_instructions(self, instructions):
        if isinstance(instructions, Instructions):
            l = instructions.get_instructions()
            for instruction in l:
                self.add_instruction(instruction)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('Instructions' instance is expected)" %
                            instructions)

    def add_match(self, match):
        if isinstance(match, Match):
            if(hasattr(self, 'match') and self.match is not None):
                assert(False), "[FlowEntry] 'match' attribute is already set"
            self.match = match
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('Match' instance is expected)" % match)

    def get_match_fields(self):
        res = None
        p = 'match'
        if (hasattr(self, p)):
            res = getattr(self, p)
        return res


class Instructions():
    ''' 'Class representing OpenFlow flow instructions set '''

    def __attrs__(self):
        self.instructions = []

    def __init__(self, d=None):
        self.__attrs__()
        if (d is not None):
            self.__init_from_dict__(d)

    def __init_from_dict__(self, d):
        if (d is not None and isinstance(d, dict)):
            for k, v in d.items():
                if (k == 'instruction'):
                    if isinstance(v, list):
                        for item in v:
                            if (isinstance(item, dict)):
                                inst = Instruction(d=item)
                                self.add_instruction(inst)
                    elif isinstance(v, dict):
                        inst = Instruction(d=v)
                        self.add_instruction(inst)
                    else:
                        msg = "DEBUG: key=%s, value=%s" \
                              " - unexpected data format" % (k, v)
                        dbg_print(msg)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)

    def add_instruction(self, instruction):
        self.instructions.append(instruction)

    def get_instructions(self):
        res = None
        p = 'instructions'
        if (hasattr(self, p)):
            res = getattr(self, p)
        return res


class Instruction():
    """ Class representing an OpenFlow flow instruction """

    def __attrs__(self):
        self.order = None
        self.apply_actions = {'action': []}
#  TODO      self.goto_table = {}
#  TODO      self.write_metadata = {}
#  TODO      self.write_actions = {}
#  TODO      self.clear_actions = {}
#  TODO      self.meter = {}

    def __init__(self, instruction_order=None, d=None):
        self.__attrs__()
        if (d is not None):
            self.__init_from_dict__(d)
        else:
            self.order = instruction_order

    def __init_from_dict__(self, d):
        if(d is not None and isinstance(d, dict)):
            p1 = 'apply_actions'
            p2 = 'action'
            p3 = 'order'
            for k, v in d.items():
                if (k == p1):
                    if p2 in v:
                        if isinstance(v[p2], list):
                            for a in v[p2]:
                                if isinstance(a, dict):
                                    action = self.create_action_from_dict(a)
                                    assert(action)
                                    self.add_apply_action(action)
                                else:
                                    msg = ("TODO -> unsupported "
                                           "data type '%s'" %
                                           type(a))
                                    dbg_print(msg)
                        elif isinstance(v[p2], dict):
                            action = self.create_action_from_dict(v[p2])
                            assert(action)
                            self.add_apply_action(action)
                        else:
                            msg = ("TODO -> unsupported data type '%s'" %
                                   type(v[p2]))
                            dbg_print(msg)
                elif p3:
                    self.order = v
                else:
                    setattr(self, k, v)
        else:
            raise TypeError("[Instruction] wrong argument type '%s'"
                            " ('dict' is expected)" % type(d))

    def add_apply_action(self, action):
        self.apply_actions['action'].append(action)

    def _sort_order(self, var):
        return var.order

    def get_apply_actions(self):
        res = None
        p = 'apply_actions'
        if (hasattr(self, p)):
            res = getattr(self, p)['action']
            res = sorted(res, key=self._sort_order)
        return res

    def is_apply_actions_type(self):
        res = False
        p = 'apply_actions'
        if (hasattr(self, p)):
            res = True
        return res

    def create_action_from_dict(self, d):
        if isinstance(d, dict):
            action = None

            # OpenFlow 1.0 and 1.3 actions
            p0 = 'output_action'        # OFPAT_OUTPUT (0)

            # OpenFlow 1.0 actions
            p1 = 'set_vlan_id_action'   # OFPAT_SET_VLAN_VID (1)
            p2 = 'set_vlan_pcp_action'  # OFPAT_SET_VLAN_PCP (2)
            p3 = 'strip_vlan_action'    # OFPAT_STRIP_VLAN (3)
            p4 = 'set_dl_src_action'    # OFPAT_SET_DL_SRC (4)
            p5 = 'set_dl_dst_action'    # OFPAT_SET_DL_DST (5)
            p6 = 'set_nw_src_action'    # OFPAT_SET_NW_SRC (6)
            p7 = 'set_nw_dst_action'    # OFPAT_SET_NW_DST (7)
            p8 = 'set_nw_tos_action'    # OFPAT_SET_NW_TOS (8)
            p9 = 'set_tp_src_action'    # OFPAT_SET_TP_SRC (9)
            p10 = 'set_tp_dst_action'   # OFPAT_SET_TP_DST (10)

            # OpenFlow 1.3 actions
# TODO       p11 = 'copy_ttl_out'         # OFPAT_COPY_TTL_OUT (11)
# TODO       p12 = 'copy_ttl_in'          # OFPAT_COPY_TTL_IN (12)
            p15 = 'set_mpls_ttl_action'  # OFPAT_SET_MPLS_TTL (15)
            p16 = 'dec_mpls_ttl'         # OFPAT_DEC_MPLS_TTL (16)
            p17 = 'push_vlan_action'     # OFPAT_PUSH_VLAN (17)
            p18 = 'pop_vlan_action'      # OFPAT_POP_VLAN (18)
            p19 = 'push_mpls_action'     # OFPAT_PUSH_MPLS (19)
            p20 = 'pop_mpls_action'      # OFPAT_POP_MPLS (20)
            p21 = 'set_queue_action'     # OFPAT_SET_QUEUE (21)
            p22 = 'group_action'         # OFPAT_GROUP (22)
            p23 = 'set_nw_ttl_action'    # OFPAT_SET_NW_TTL (23)
            p24 = 'dec_nw_ttl'           # OFPAT_DEC_NW_TTL (24)
            p25 = 'set_field'            # OFPAT_SET_FIELD (25)
            p26 = 'push_pbb_action'      # OFPAT_PUSH_PBB (26)
            p27 = 'pop_pbb_action'       # OFPAT_POP_PBB (27)

            action_order = d.get('order', None)
            if (p0 in d):
                action = OutputAction(order=action_order, d=d[p0])
            elif (p1 in d):
                action = SetVlanIdAction(order=action_order, d=d[p1])
            elif (p2 in d):
                action = SetVlanPCPAction(order=action_order, d=d[p2])
            elif (p3 in d):
                action = StripVlanAction(order=action_order)
            elif (p4 in d):
                action = SetDlSrcAction(order=action_order, d=d[p4])
            elif (p5 in d):
                action = SetDlDstAction(order=action_order, d=d[p5])
            elif (p6 in d):
                action = SetNwSrcAction(order=action_order, d=d[p6])
            elif (p7 in d):
                action = SetNwDstAction(order=action_order, d=d[p7])
            elif (p8 in d):
                action = SetNwTosAction(order=action_order, d=d[p8])
            elif (p9 in d):
                action = SetTpSrcAction(order=action_order, d=d[p9])
            elif (p10 in d):
                action = SetTpDstAction(order=action_order, d=d[p10])
#  TODO      elif (p11 in d):
#                action = CopyTtlOutAction(order=action_order, d=d[p11])
#  TODO      elif (p12 in d):
#                action = CopyTtlInAction(order=action_order, d=d[p12])
            elif (p15 in d):
                action = SetMplsTTLAction(order=action_order, d=d[p15])
            elif (p16 in d):
                action = DecMplsTTLAction(order=action_order)
            elif (p17 in d):
                action = PushVlanHeaderAction(order=action_order, d=d[p17])
            elif (p18 in d):
                action = PopVlanHeaderAction(order=action_order)
            elif (p19 in d):
                action = PushMplsHeaderAction(order=action_order, d=d[p19])
            elif (p20 in d):
                action = PopMplsHeaderAction(order=action_order, d=d[p20])
            elif (p21 in d):
                action = SetQueueAction(order=action_order, d=d[p21])
            elif (p22 in d):
                action = GroupAction(order=action_order, d=d[p22])
            elif (p23 in d):
                action = SetNwTTLAction(order=action_order, d=d[p23])
            elif (p24 in d):
                action = DecNwTTLAction(order=action_order)
            elif (p25 in d):
                action = SetFieldAction(order=action_order, d=d[p25])
            elif (p26 in d):
                action = PushPBBHeaderAction(order=action_order, d=d[p26])
            elif (p27 in d):
                action = PopPBBHeaderAction(order=action_order)
            elif ('drop_action' in d):
                action = DropAction(order=action_order)
            else:
                msg = "Found unsupported action in d='%s'" % d
                dbg_print(msg)

            return action
        else:
            raise TypeError("[Instruction] wrong argument type '%s'"
                            " ('dict' is expected)" % type(d))


class Action(object):

    def __init__(self, order=None):
        self.order = order

    def set_order(self, order):
        self.order = order


class OutputAction(Action):
    """ The Output action forwards a packet to a specified OpenFlow port.
        OpenFlow switches must support forwarding to physical ports,
        switch-defined logical ports and the required reserved ports.
        (OpenFlow Switch Specification Version 1.0 and 1.3)
    """

    def __attrs__(self):
        self.output_action = {'output_node_connector': None,
                              'max_length': None}

    def __init__(self, order=None, port=None, max_len=None, d=None):
        super(OutputAction, self).__init__(order)
        self.__attrs__()
        if(d is not None):
            self.__init_from_dict__(d)
        else:
            self.set_outport(port)
            self.set_max_len(max_len)

    def __init_from_dict__(self, d):
        if(d is not None and isinstance(d, dict)):
            for k, v in d.items():
                if (k == 'output_node_connector'):
                    self.set_outport(v)
                elif (k == 'max_length'):
                    self.set_max_len(v)
                else:
                    msg = ("[OutputAction] TODO -> k=%s, v=%s" % (k, v))
                    dbg_print(msg)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)

    def set_outport(self, port):
        self.output_action['output_node_connector'] = port

    def get_outport(self):
        res = None
        p = 'output_action'
        if (hasattr(self, p)):
            res = getattr(self, p)['output_node_connector']
        return res

    def set_max_len(self, max_len):
        self.output_action['max_length'] = max_len

    def get_max_len(self):
        res = None
        p = 'output_action'
        if (hasattr(self, p)):
            v = getattr(self, p)['max_length']
            if (v != 0):
                res = v
        return res

    def set_order(self, order):
        self.order = order

    def to_ofp_oxm_syntax(self):
        s = None
        p = self.get_outport()
        if (p):
            s = "output=%s" % p
            l = self.get_max_len()
            if (l):
                s += ":" + str(l)
        return s


class DropAction(Action):
    """ There is no explicit action to represent drops. Instead,
        packets whose action sets have no output actions should
        be dropped. This result could come from empty instruction
        sets or empty action buckets in the processing pipeline,
        or after executing a Clear-Actions instruction.
        (OpenFlow Switch Specification Version 1.0 and 1.3)
    """

    def __attrs__(self):
        self.drop_action = {}

    def __init__(self, order=None):
        super(DropAction, self).__init__(order)
        self.__attrs__()

    def set_order(self, order):
        self.order = order

    def to_ofp_oxm_syntax(self):
        s = "drop"
        return s


class SetVlanIdAction(Action):
    """ Set the 802.1q VLAN ID.
        If no VLAN is present, a new header is added with the specified
        VLAN ID and priority of zero. If a VLAN header already exists,
        the VLAN ID is replaced with the specified value.
        (OpenFlow Switch Specification Version 1.0)
    """

    def __attrs__(self):
        self.set_vlan_id_action = {'vlan_id': None}

    def __init__(self, order=None, vid=None, d=None):
        super(SetVlanIdAction, self).__init__(order)
        self.__attrs__()
        if(d is not None):
            self.__init_from_dict__(d)
        else:
            self.set_vid(vid)

    def __init_from_dict__(self, d):
        if(d is not None and isinstance(d, dict)):
            for k, v in d.items():
                if (k == 'vlan_id'):
                    self.set_vid(v)
                else:
                    msg = ("[SetVlanIdAction] TODO -> k='%s', v='%s'" % (k, v))
                    dbg_print(msg)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)

    def set_vid(self, vid):
        self.set_vlan_id_action['vlan_id'] = vid

    def get_vid(self):
        return self.set_vlan_id_action['vlan_id']

    def to_ofp_oxm_syntax(self):
        s = None
        vid = self.get_vid()
        if (vid):
            s = "set_vlan_vid=%s" % vid
        return s


class SetVlanPCPAction(Action):
    """ Set VLAN priority.
        If no VLAN is present, a new header is added with the specified
        priority and a VLAN ID of zero. If a VLAN header already exists,
        the priority field is replaced with the specified value.
        (OpenFlow Switch Specification Version 1.0)
    """

    def __attrs__(self):
        self.set_vlan_pcp_action = {'vlan_pcp': None}

    def __init__(self, order=None, vlan_pcp=None, d=None):
        super(SetVlanPCPAction, self).__init__(order)
        self.__attrs__()
        if(d is not None):
            self.__init_from_dict__(d)
        else:
            self.set_vlan_pcp(vlan_pcp)

    def __init_from_dict__(self, d):
        if(d is not None and isinstance(d, dict)):
            for k, v in d.items():
                if (k == 'vlan_pcp'):
                    self.set_vlan_pcp(v)
                else:
                    msg = ("[SetVlanPCPAction] TODO -> "
                           "k='%s', v='%s'" % (k, v))
                    dbg_print(msg)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)

    def set_vlan_pcp(self, vlan_pcp):
        self.set_vlan_pcp_action['vlan_pcp'] = vlan_pcp

    def get_vlan_pcp(self):
        return self.set_vlan_pcp_action['vlan_pcp']

    def to_ofp_oxm_syntax(self):
        s = None
        pcp = self.get_vlan_pcp()
        if (pcp):
            s = "set_vlan_pcp=%s" % pcp
        return s

'''
class SetVlanCfiAction(Action):
    """ Seems to be ODL proprietary action type ???
        CFI (1-bit field) was formerly designated Canonical Format Indicator
        with a value of 0 indicating a MAC address in canonical format. It is
        always set to zero for Ethernet. CFI was used for compatibility between
        Ethernet and Token Ring networks. If a frame received at an Ethernet
        port had a CFI set to 1, then that frame would not be bridged to an
        untagged port.
        Currently renamed as Drop eligible indicator (DEI).
        May be used separately or in conjunction with PCP to indicate
        frames eligible to be dropped in the presence of congestion.
    """

    def __init__(self, order=None, vlan_cfi=None):
        super(SetVlanCfiAction, self).__init__(order)
        self.set_vlan_cfi_action = {'vlan_cfi': vlan_cfi}

    def set_vlan_cfi(self, vlan_cfi):
        self.set_vlan_cfi_action['vlan_cfi'] = vlan_cfi
'''


class StripVlanAction(Action):
    """ Strip VLAN header if present.
        (OpenFlow Switch Specification Version 1.0)
    """

    def __attrs__(self):
        self.strip_vlan_action = {}

    def __init__(self, order=None):
        super(StripVlanAction, self).__init__(order)
        self.__attrs__()

    def to_ofp_oxm_syntax(self):
        s = "strip_vlan"
        return s


class SetDlSrcAction(Action):
    """ Modify Ethernet source MAC address.
        Replace the existing Ethernet source MAC address
        with the new value.
        (OpenFlow Switch Specification Version 1.0)
    """

    def __attrs__(self):
        self.set_dl_src_action = {'address': None}

    def __init__(self, order=None, mac_addr=None, d=None):
        super(SetDlSrcAction, self).__init__(order)
        self.__attrs__()
        if(d is not None):
            self.__init_from_dict__(d)
        else:
            self.set_dl_src(mac_addr)

    def __init_from_dict__(self, d):
        if(d is not None and isinstance(d, dict)):
            for k, v in d.items():
                if (k == 'address'):
                    self.set_dl_src(v)
                else:
                    msg = ("[SetDlSrcAction] TODO -> k='%s', v='%s'" % (k, v))
                    dbg_print(msg)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)

    def set_dl_src(self, mac_addr):
        self.set_dl_src_action['address'] = mac_addr

    def get_dl_src(self):
        return self.set_dl_src_action['address']

    def to_ofp_oxm_syntax(self):
        s = None
        mac = self.get_dl_src()
        if (mac):
            s = "set_dl_src=%s" % mac
        return s


class SetDlDstAction(Action):
    """ Modify Ethernet destination MAC address.
        Replace the existing Ethernet destination MAC address
        with the new value.
        (OpenFlow Switch Specification Version 1.0)
    """

    def __attrs__(self):
        self.set_dl_dst_action = {'address': None}

    def __init__(self, order=None, mac_addr=None, d=None):
        super(SetDlDstAction, self).__init__(order)
        self.__attrs__()
        if(d is not None):
            self.__init_from_dict__(d)
        else:
            self.set_dl_dst(mac_addr)

    def __init_from_dict__(self, d):
        if(d is not None and isinstance(d, dict)):
            for k, v in d.items():
                if (k == 'address'):
                    self.set_dl_dst(v)
                else:
                    msg = ("[SetDlDstAction] TODO -> k='%s', v='%s'" % (k, v))
                    dbg_print(msg)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)

    def set_dl_dst(self, mac_addr):
        self.set_dl_dst_action['address'] = mac_addr

    def get_dl_dst(self):
        return self.set_dl_dst_action['address']

    def to_ofp_oxm_syntax(self):
        s = None
        mac = self.get_dl_dst()
        if (mac):
            s = "set_dl_dst=%s" % mac
        return s


class SetNwSrcAction(Action):
    """ Modify IPv4 source address.
        Replace the existing IP source address with new value and
        update the IP checksum (and TCP/UDP checksum if applicable).
        This action is only applicable to IPv4 packets.
        (OpenFlow Switch Specification Version 1.0)
    """

    def __attrs__(self):
        self.set_nw_src_action = {'ipv4_address': None}

    def __init__(self, order=None, ip_addr=None, d=None):
        super(SetNwSrcAction, self).__init__(order)
        self.__attrs__()
        if(d is not None):
            self.__init_from_dict__(d)
        else:
            self.set_nw_src(ip_addr)

    def __init_from_dict__(self, d):
        if(d is not None and isinstance(d, dict)):
            for k, v in d.items():
                if (k == 'ipv4_address'):
                    self.set_nw_src(v)
                else:
                    msg = ("[SetNwSrcAction] TODO -> k='%s', v='%s'" % (k, v))
                    dbg_print(msg)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)

    def set_nw_src(self, ip_addr):
        self.set_nw_src_action['ipv4_address'] = ip_addr

    def get_nw_src(self):
        return self.set_nw_src_action['ipv4_address']

    def to_ofp_oxm_syntax(self):
        s = None
        src = self.get_nw_src()
        if (src):
            s = "set_nw_src=%s" % src
        return s


class SetNwDstAction(Action):
    """ Modify IPv4 destination address.
        Replace the existing IP destination address with new value and
        update the IP checksum (and TCP/UDP checksum if applicable).
        This action is only applicable to IPv4 packets.
        (OpenFlow Switch Specification Version 1.0)
    """

    def __attrs__(self):
        self.set_nw_dst_action = {'ipv4_address': None}

    def __init__(self, order=None, ip_addr=None, d=None):
        super(SetNwDstAction, self).__init__(order)
        self.__attrs__()
        if(d is not None):
            self.__init_from_dict__(d)
        else:
            self.set_nw_dst(ip_addr)

    def __init_from_dict__(self, d):
        if(d is not None and isinstance(d, dict)):
            for k, v in d.items():
                if (k == 'ipv4_address'):
                    self.set_nw_dst(v)
                else:
                    msg = ("[SetNwDstAction] TODO -> k='%s', v='%s'" % (k, v))
                    dbg_print(msg)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)

    def set_nw_dst(self, ip_addr):
        self.set_nw_dst_action['ipv4_address'] = ip_addr

    def get_nw_dst(self):
        return self.set_nw_dst_action['ipv4_address']

    def to_ofp_oxm_syntax(self):
        s = None
        dst = self.get_nw_dst()
        if (dst):
            s = "set_nw_dst=%s" % dst
        return s


class SetNwTosAction(Action):
    """ Modify IPv4 ToS bits.
        Replace the existing IP ToS field.
        This action is only applied to IPv4 packets.
        (OpenFlow Switch Specification Version 1.0)
    """

    def __attrs__(self):
        ''' Value with which to replace existing IPv4 ToS field
            NOTE: The modern redefinition of the ToS field is a 6 bit
                  Differentiated Services Code Point (DSCP) field (the
                  6 upper bits of the original TOS field) and a 2 bit
                  Explicit Congestion Notification (ECN) field.
        '''
        self.set_nw_tos_action = {'tos': None}

    def __init__(self, order=None, tos=None, d=None):
        super(SetNwTosAction, self).__init__(order)
        self.__attrs__()
        if(d is not None):
            self.__init_from_dict__(d)
        else:
            self.set_tos(tos)

    def __init_from_dict__(self, d):
        if(d is not None and isinstance(d, dict)):
            for k, v in d.items():
                if (k == 'tos'):
                    self.set_tos(v)
                else:
                    msg = ("[SetNwTosAction] TODO -> k='%s', v='%s'" % (k, v))
                    dbg_print(msg)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)

    def set_tos(self, tos):
        self.set_nw_tos_action['tos'] = tos

    def get_tos(self):
        return self.set_nw_tos_action['tos']

    def to_ofp_oxm_syntax(self):
        s = None
        tos = self.get_tos()
        if (tos):
            s = "set_nw_tos=%s" % tos
        return s


class SetTpSrcAction(Action):
    """ Modify transport source port.
        Replace the existing TCP/UDP source port with new value and
        update the TCP/UDP checksum.
        This action is only applicable to TCP and UDP packets.
        (OpenFlow Switch Specification Version 1.0)
    """

    def __attrs__(self):
        self.set_tp_src_action = {'port': None}

    def __init__(self, order=None, port=None, d=None):
        super(SetTpSrcAction, self).__init__(order)
        self.__attrs__()
        if(d is not None):
            self.__init_from_dict__(d)
        else:
            self.set_tp_src(port)

    def __init_from_dict__(self, d):
        if(d is not None and isinstance(d, dict)):
            for k, v in d.items():
                if (k == 'port'):
                    self.set_tp_src(v)
                else:
                    msg = ("[SetTpSrcAction] TODO -> k='%s', v='%s'" % (k, v))
                    dbg_print(msg)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)

    def set_tp_src(self, port):
        self.set_tp_src_action['port'] = port

    def get_tp_src(self):
        return self.set_tp_src_action['port']

    def to_ofp_oxm_syntax(self):
        s = None
        src = self.get_tp_src()
        if (src):
            s = "set_tp_src=%s" % src
        return s


class SetTpDstAction(Action):
    """ Modify transport destination port.
        Replace the existing TCP/UDP destination port with new value and
        update the TCP/UDP checksum.
        This action is only applicable to TCP and UDP packets.
        (OpenFlow Switch Specification Version 1.0)
    """

    def __attrs__(self):
        self.set_tp_dst_action = {'port': None}

    def __init__(self, order=None, port=None, d=None):
        super(SetTpDstAction, self).__init__(order)
        self.__attrs__()
        if(d is not None):
            self.__init_from_dict__(d)
        else:
            self.set_tp_dst(port)

    def __init_from_dict__(self, d):
        if(d is not None and isinstance(d, dict)):
            for k, v in d.items():
                if (k == 'port'):
                    self.set_tp_dst(v)
                else:
                    msg = ("[SetTpDstAction] TODO -> k='%s', v='%s'" % (k, v))
                    dbg_print(msg)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)

    def set_tp_dst(self, port):
        self.set_tp_dst_action['port'] = port

    def get_tp_dst(self):
        return self.set_tp_dst_action['port']

    def to_ofp_oxm_syntax(self):
        s = None
        dst = self.get_tp_dst()
        if (dst):
            s = "set_tp_dst=%s" % dst
        return s


class PushVlanHeaderAction(Action):
    """ Push a new VLAN header onto the packet. The 'ethernet_type'
        is used as the Ethernet Type for the tag, only 0x8100 or 0x88a8
        values should be used.
        (OpenFlow Switch Specification Version 1.3)
    """

    def __attrs__(self):
        self.push_vlan_action = {'ethernet_type': None, 'tag': None,
                                 'pcp': None, 'cfi': None, 'vlan_id': None}

    def __init__(self, order=None, eth_type=None, tag=None, pcp=None,
                 cfi=None, vid=None, d=None):
        super(PushVlanHeaderAction, self).__init__(order)
        self.__attrs__()
        if (d is not None):
            self.__init_from_dict__(d)
        else:
            self.set_eth_type(eth_type)
            self.set_tag(tag)
            self.set_pcp(pcp)
            self.set_cfi(cfi)
            self.set_vid(vid)

    def __init_from_dict__(self, d):
        if (d is not None and isinstance(d, dict)):
            for k, v in d.items():
                if (k == 'ethernet_type'):
                    self.set_eth_type(v)
                else:
                    msg = ("[PushVlanHeaderAction] TODO -> "
                           "k=%s, v=%s" % (k, v))
                    dbg_print(msg)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)

    def set_eth_type(self, eth_type):
        self.push_vlan_action['ethernet_type'] = eth_type

    def get_eth_type(self):
        res = None
        p = 'push_vlan_action'
        if (hasattr(self, p)):
            res = getattr(self, p)['ethernet_type']
        return res

    def set_tag(self, tag):
        self.push_vlan_action['tag'] = tag

    def set_pcp(self, pcp):
        self.push_vlan_action['pcp'] = pcp

    def set_cfi(self, cfi):
        self.push_vlan_action['cfi'] = cfi

    def set_vid(self, vid):
        self.push_vlan_action['vlan_id'] = vid

    def set_order(self, order):
        self.order = order

    def to_ofp_oxm_syntax(self):
        s = None
        eth_type = self.get_eth_type()
        if (eth_type):
            s = "push_vlan=%s" % str(hex(int(eth_type)))
        return s


class PopVlanHeaderAction(Action):
    """ Pop the outer-most VLAN header from the packet.
        (OpenFlow Switch Specification Version 1.3)
    """

    def __attrs__(self):
        self.pop_vlan_action = {}

    def __init__(self, order=None):
        super(PopVlanHeaderAction, self).__init__(order)
        self.__attrs__()

    def to_ofp_oxm_syntax(self):
        s = "pop_vlan"
        return s


class PushMplsHeaderAction(Action):
    """ Push a new MPLS shim header onto the packet. The 'ethernet_type' is
        used as the Ethernet Type for the tag, only 0x8847 or 0x8848 values
        should be used.
        (OpenFlow Switch Specification Version 1.3)
    """

    def __attrs__(self):
        self.push_mpls_action = {'ethernet_type': None}

    def __init__(self, order=None, ethernet_type=None, d=None):
        super(PushMplsHeaderAction, self).__init__(order)
        self.__attrs__()
        if (d is not None):
            self.__init_from_dict__(d)
        else:
            self.set_eth_type(ethernet_type)

    def __init_from_dict__(self, d):
        if (d is not None and isinstance(d, dict)):
            for k, v in d.items():
                if (k == 'ethernet_type'):
                    self.set_eth_type(v)
                else:
                    msg = ("[PushMplsHeaderAction] TODO -> "
                           "k=%s, v=%s" % (k, v))
                    dbg_print(msg)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)

    def set_eth_type(self, eth_type):
        self.push_mpls_action['ethernet_type'] = eth_type

    def get_eth_type(self):
        res = None
        p = 'push_mpls_action'
        if (hasattr(self, p)):
            res = getattr(self, p)['ethernet_type']
        return res

    def to_ofp_oxm_syntax(self):
        s = None
        eth_type = self.get_eth_type()
        if (eth_type):
            s = "push_mpls=%s" % str(hex(int(eth_type)))
        return s


class PopMplsHeaderAction(Action):
    """ Pop the outer-most MPLS tag or shim header from the packet.
        The 'ethernet_type' is used as the Ethernet Type for the
        resulting packet (Ethernet Type for the MPLS payload).
        (OpenFlow Switch Specification Version 1.3)
    """

    def __attrs__(self):
        self.pop_mpls_action = {'ethernet_type': None}

    def __init__(self, order=0, ethernet_type=None, d=None):
        super(PopMplsHeaderAction, self).__init__(order)
        self.__attrs__()
        if (d is not None):
            self.__init_from_dict__(d)
        else:
            self.set_eth_type(ethernet_type)

    def __init_from_dict__(self, d):
        if (d is not None and isinstance(d, dict)):
            for k, v in d.items():
                if (k == 'ethernet_type'):
                    self.set_eth_type(v)
                else:
                    msg = ("[PopMplsHeaderAction] TODO -> "
                           "k=%s, v=%s" % (k, v))
                    dbg_print(msg)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)

    def set_eth_type(self, eth_type):
        self.pop_mpls_action['ethernet_type'] = eth_type

    def get_eth_type(self):
        return self.pop_mpls_action['ethernet_type']

    def to_ofp_oxm_syntax(self):
        s = None
        eth_type = self.get_eth_type()
        if (eth_type):
            s = "pop_mpls=%s" % str(hex(int(eth_type)))
        return s


class SetMplsTTLAction(Action):
    """ Replace the existing MPLS TTL. Only applies to packets with
        an existing MPLS shim header.
        (OpenFlow Switch Specification Version 1.3)
    """

    def __attrs__(self):
        self.set_mpls_ttl_action = {'mpls_ttl': None}

    def __init__(self, order=0, ttl=None, d=None):
        super(SetMplsTTLAction, self).__init__(order)
        self.__attrs__()
        if (d is not None):
            self.__init_from_dict__(d)
        else:
            self.set_ttl(ttl)

    def __init_from_dict__(self, d):
        if (d is not None and isinstance(d, dict)):
            for k, v in d.items():
                if (k == 'mpls_ttl'):
                    self.set_ttl(v)
                else:
                    msg = ("[PushMplsHeaderAction] TODO -> "
                           "k=%s, v=%s" % (k, v))
                    dbg_print(msg)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)

    def set_ttl(self, ttl):
        self.set_mpls_ttl_action['mpls_ttl'] = ttl

    def get_ttl(self):
        return self.set_mpls_ttl_action['mpls_ttl']

    def to_ofp_oxm_syntax(self):
        s = None
        ttl = self.get_ttl()
        if (ttl):
            s = "set_mpls_ttl=%s" % ttl
        return s


class DecMplsTTLAction(Action):
    """ Decrement the MPLS TTL. Only applies to packets with
        an existing MPLS shim header.
        (OpenFlow Switch Specification Version 1.3)
    """

    def __attrs__(self):
        self.dec_mpls_ttl = {}

    def __init__(self, order=0):
        super(DecMplsTTLAction, self).__init__(order)
        self.__attrs__()

    def to_ofp_oxm_syntax(self):
        s = "dec_mpls_ttl"
        return s


class SetNwTTLAction(Action):
    """ Replace the existing IPv4 TTL or IPv6 Hop Limit and
        update the IP checksum.
        Only applies to IPv4 and IPv6 packets.
        (OpenFlow Switch Specification Version 1.3)
    """

    def __attrs__(self):
        self.set_nw_ttl_action = {'nw_ttl': None}

    def __init__(self, order=0, ttl=None, d=None):
        super(SetNwTTLAction, self).__init__(order)
        self.__attrs__()
        if (d is not None):
            self.__init_from_dict__(d)
        else:
            self.set_ttl(ttl)

    def __init_from_dict__(self, d):
        if (d is not None and isinstance(d, dict)):
            for k, v in d.items():
                if (k == 'nw_ttl'):
                    self.set_ttl(v)
                else:
                    msg = ("[SetNwTTLAction] TODO -> k=%s, v=%s" % (k, v))
                    dbg_print(msg)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)

    def set_ttl(self, ttl):
        self.set_nw_ttl_action['nw_ttl'] = ttl

    def get_ttl(self):
        return self.set_nw_ttl_action['nw_ttl']

    def to_ofp_oxm_syntax(self):
        s = None
        ttl = self.get_ttl()
        if (ttl):
            s = "set_nw_ttl=%s" % ttl
        return s


class DecNwTTLAction(Action):
    """ Decrement the IPv4 TTL or IPv6 Hop Limit field and
        update the IP checksum.
        Only applies to IPv4 and IPv6 packets.
        (OpenFlow Switch Specification Version 1.3)
    """

    def __attrs__(self):
        self.dec_nw_ttl = {}

    def __init__(self, order=0):
        super(DecNwTTLAction, self).__init__(order)
        self.__attrs__()

    def to_ofp_oxm_syntax(self):
        s = "dec_nw_ttl"
        return s


class CopyTTLOutwardsAction(Action):
    """ Copy the TTL from next-to-outermost to outermost header with TTL.
        Copy can be IP-to-IP, MPLS-to-MPLS, or IP-to-MPLS.
        (OpenFlow Switch Specification Version 1.3)
    """

    def __attrs__(self):
        self.copy_ttl_out = {}

    def __init__(self, order=0):
        super(CopyTTLOutwardsAction, self).__init__(order)
        self.__attrs__()

    def to_ofp_oxm_syntax(self):
        s = "copy_ttl_out"
        return s


class CopyTTLInwardsAction(Action):
    """ Copy the TTL from outermost to next-to-outermost header with TTL.
        Copy can be IP-to-IP, MPLS-to-MPLS, or MPLS-to-IP.
        (OpenFlow Switch Specification Version 1.3)
    """

    def __attrs__(self):
        self.copy_ttl_in = {}

    def __init__(self, order=0):
        super(CopyTTLInwardsAction, self).__init__(order)
        self.__attrs__()

    def to_ofp_oxm_syntax(self):
        s = "copy_ttl_in"
        return s


class SetQueueAction(Action):
    """ The set-queue action sets the queue id for a packet. When the
        packet is forwarded to a port using the output action, the queue
        id determines which queue attached to this port is used for
        scheduling and forwarding the packet. Forwarding behavior is
        dictated by the configuration of the queue and is used to provide
        basic Quality-of-Service (QoS) support.
        (OpenFlow Switch Specification Version 1.3)
    """

    def __attrs__(self):
        self.set_queue_action = {'queue': None, 'queue_id': None}

    def __init__(self, order=None, queue=None, queue_id=None, d=None):
        super(SetQueueAction, self).__init__(order)
        self.__attrs__()
        if (d is not None):
            self.__init_from_dict__(d)
        else:
            self.set_queue(queue)
            self.set_gueue_id(queue_id)

    def __init_from_dict__(self, d):
        if (d is not None and isinstance(d, dict)):
            for k, v in d.items():
                if (k == 'queue'):
                    self.set_gueue(v)
                elif (k == 'queue_id'):
                    self.set_gueue_id(v)
                else:
                    msg = ("[SetQueueAction] TODO -> k=%s, v=%s" % (k, v))
                    dbg_print(msg)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)

    def set_queue(self, queue):
        self.set_queue_action['queue'] = queue

    def set_gueue_id(self, queue_id):
        self.set_queue_action['queue_id'] = queue_id

    def get_queue_id(self):
        return self.set_queue_action['queue_id']

    def to_ofp_oxm_syntax(self):
        s = None
        qid = self.get_queue_id()
        if (qid):
            s = "set_queue=%s" % qid
        return s


class GroupAction(Action):
    """ Process the packet through the specified group.
        The exact interpretation depends on group type.
        (OpenFlow Switch Specification Version 1.3)
    """

    def __attrs__(self):
        self.group_action = {'group': None, 'group_id': None}

    def __init__(self, order=None, group=None, group_id=None, d=None):
        super(GroupAction, self).__init__(order)
        self.__attrs__()
        if (d is not None):
            self.__init_from_dict__(d)
        else:
            self.set_group(group)
            self.set_group_id(group_id)

    def __init_from_dict__(self, d):
        if (d is not None and isinstance(d, dict)):
            for k, v in d.items():
                if (k == 'group'):
                    self.set_group(v)
                elif (k == 'group_id'):
                    self.set_group_id(v)
                else:
                    msg = ("[GroupAction] TODO -> k=%s, v=%s" % (k, v))
                    dbg_print(msg)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)

    def set_group(self, group):
        self.group_action['group'] = group

    def set_group_id(self, group_id):
        self.group_action['group_id'] = group_id

    def get_group_id(self):
        return self.group_action['group_id']

    def to_ofp_oxm_syntax(self):
        s = None
        grp_id = self.get_group_id()
        if (grp_id):
            s = "group=%s" % grp_id
        return s


class SetFieldAction(Action):
    """ The Extensible set_field action reuses the OXM encoding defined
        for matches, and enables to rewrite any header field in a single
        action. This allows any new match field, including experimenter
        fields, to be available for rewrite.
        The various Set-Field actions are identified by their field type
        and modify the values of respective header fields in the packet.
        While not strictly required, the support of rewriting various
        header fields using Set-Field actions greatly increase the
        usefulness of an OpenFlow implementation. To aid integration with
        existing networks, we suggest that VLAN modification actions be
        supported. Set-Field actions should always be applied to the
        outermost-possible header (e.g. a 'Set VLAN ID' action always sets
        the ID of the outermost VLAN tag), unless the field type specifies
        otherwise.
        (OpenFlow Switch Specification Version 1.3)
    """

    def __attrs__(self):
        self.set_field = {'vlan_match': None,
                          'protocol_match_fields': None,
                          'ip_match': None,
                          'ethernet_match': None,
                          'ipv4_source': None,
                          'ipv4_destination': None,
                          'tcp_source_port': None,
                          'tcp_destination_port': None,
                          'udp_source_port': None,
                          'udp_destination_port': None}

    def __init__(self, order=None, d=None):
        super(SetFieldAction, self).__init__(order)
        self.__attrs__()
        if (d is not None):
            self.__init_from_dict__(d)

    def __init_from_dict__(self, d):
        if (d is not None and isinstance(d, dict)):
            for k, v in d.items():
                if (k == 'vlan_match'):
                    self.set_field[k] = VlanMatch(v)
                elif (k == 'protocol_match_fields'):
                    self.set_field[k] = ProtocolMatchFields(v)
                elif (k == 'ethernet_match'):
                    self.set_field[k] = EthernetMatch(v)
                elif (k == 'ip_match'):
                    self.set_field[k] = IpMatch(v)
                elif (k == 'ipv4_source'):
                    self.set_field[k] = v
                elif (k == 'ipv4_destination'):
                    self.set_field[k] = v
                elif (k == 'tcp_source_port'):
                    self.set_field[k] = v
                elif (k == 'tcp_destination_port'):
                    self.set_field[k] = v
                elif (k == 'udp_source_port'):
                    self.set_field[k] = v
                elif (k == 'udp_destination_port'):
                    self.set_field[k] = v
                else:
                    msg = ("[SetFieldAction] TODO -> k=%s, v=%s" % (k, v))
                    dbg_print(msg)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "(dictionary is expected)" % d)

    def set_vlan_id(self, vid):
        if(self.set_field['vlan_match'] is None):
            self.set_field['vlan_match'] = VlanMatch()
        self.set_field['vlan_match'].set_vid(vid)

    def get_vlan_id(self):
        res = None
        p = 'set_field'
        if (hasattr(self, p)):
            m = getattr(self, p)['vlan_match']
            if (m is not None):
                res = m.get_vid()
        return res

    def set_vlan_pcp(self, vlan_pcp):
        if(self.set_field['vlan_match'] is None):
            self.set_field['vlan_match'] = VlanMatch()
        self.set_field['vlan_match'].set_pcp(vlan_pcp)

    def get_vlan_pcp(self):
        res = None
        p = 'set_field'
        if (hasattr(self, p)):
            m = getattr(self, p)['vlan_match']
            if (m is not None):
                res = m.get_pcp()
        return res

    def set_eth_src(self, mac_addr):
        if(self.set_field['ethernet_match'] is None):
            self.set_field['ethernet_match'] = EthernetMatch()
        self.set_field['ethernet_match'].set_src(mac_addr)

    def get_eth_src(self):
        res = None
        p = 'set_field'
        if (hasattr(self, p)):
            m = getattr(self, p)['ethernet_match']
            if (m is not None):
                res = m.get_src()
        return res

    def set_eth_dst(self, mac_addr):
        if(self.set_field['ethernet_match'] is None):
            self.set_field['ethernet_match'] = EthernetMatch()
        self.set_field['ethernet_match'].set_dst(mac_addr)

    def get_eth_dst(self):
        res = None
        p = 'set_field'
        if (hasattr(self, p)):
            m = getattr(self, p)['ethernet_match']
            if (m is not None):
                res = m.get_dst()
        return res

    def set_ipv4_src(self, ipv4_addr):
        self.set_field['ipv4_source'] = ipv4_addr

    def get_ipv4_src(self):
        return self.set_field['ipv4_source']

    def set_ipv4_dst(self, ipv4_addr):
        self.set_field['ipv4_destination'] = ipv4_addr

    def get_ipv4_dst(self):
        return self.set_field['ipv4_destination']

    def set_tcp_src(self, tcp_port):
        self.set_field['tcp_source_port'] = tcp_port

    def get_tcp_src(self):
        return self.set_field['tcp_source_port']

    def set_tcp_dst(self, tcp_port):
        self.set_field['tcp_destination_port'] = tcp_port

    def get_tcp_dst(self):
        return self.set_field['tcp_destination_port']

    def set_udp_src(self, udp_port):
        self.set_field['udp_source_port'] = udp_port

    def get_udp_src(self):
        return self.set_field['udp_source_port']

    def set_udp_dst(self, udp_port):
        self.set_field['udp_destination_port'] = udp_port

    def get_udp_dst(self):
        return self.set_field['udp_destination_port']

    def set_mpls_label(self, mpls_label):
        if(self.set_field['protocol_match_fields'] is None):
            self.set_field['protocol_match_fields'] = ProtocolMatchFields()
        self.set_field['protocol_match_fields'].set_mpls_label(mpls_label)

    def get_mpls_label(self):
        res = None
        p1 = 'set_field'
        p2 = 'protocol_match_fields'
        if (hasattr(self, p1)):
            m = getattr(self, p1)[p2]
            if (m is not None):
                res = m.get_mpls_label()
        return res

    def set_ip_dscp(self, dscp):
        p = 'ip_match'
        if(self.set_field[p] is None):
            self.set_field[p] = IpMatch()
        self.set_field[p].set_ip_dscp(dscp)

    def get_ip_dscp(self):
        res = None
        p1 = 'set_field'
        p2 = 'ip_match'
        if (hasattr(self, p1)):
            m = getattr(self, p1)[p2]
            if (m is not None):
                res = m.get_ip_dscp()
        return res

    def set_ip_ecn(self, ecn):
        p = 'ip_match'
        if(self.set_field[p] is None):
            self.set_field[p] = IpMatch()
        self.set_field[p].set_ip_ecn(ecn)

    def get_ip_ecn(self):
        res = None
        p1 = 'set_field'
        p2 = 'ip_match'
        if (hasattr(self, p1)):
            m = getattr(self, p1)[p2]
            if (m is not None):
                res = m.get_ip_ecn()
        return res

    def to_ofp_oxm_syntax(self):
        s = "set_field->%s=%s"

        v = self.get_vlan_id()
        if (v is not None):
            return (s % ("vlan_vid", v))

        v = self.get_vlan_pcp()
        if (v is not None):
            return (s % ("vlan_pcp", v))

        v = self.get_eth_src()
        if (v is not None):
            return (s % ("eth_src", v))

        v = self.get_eth_dst()
        if(v is not None):
            return (s % ("eth_dst", v))

        v = self.get_ipv4_src()
        if (v is not None):
            return (s % ("ipv4_src", v))

        v = self.get_ipv4_dst()
        if (v is not None):
            return (s % ("ipv4_dst", v))

        v = self.get_tcp_src()
        if (v is not None):
            return (s % ("tcp_src", v))

        v = self.get_tcp_dst()
        if (v is not None):
            return (s % ("tcp_dst", v))

        v = self.get_udp_src()
        if (v is not None):
            return (s % ("udp_src", v))

        v = self.get_udp_dst()
        if(v is not None):
            return (s % ("udp_dst", v))

        v = self.get_mpls_label()
        if (v is not None):
            return (s % ("mpls_label", v))

        v = self.get_ip_dscp()
        if (v is not None):
            return (s % ("ip_dscp", v))

        v = self.get_ip_ecn()
        if (v is not None):
            return (s % ("ip_ecn", v))

        msg = "[SetFieldAction->to_ofp_oxm_syntax] no value found"
        dbg_print(msg)

        return None


class PushPBBHeaderAction(Action):
    """ Push a new PBB service instance header (I-TAG TCI) onto the packet.
        The 'ethernet_type' is used as the Ethernet Type for the tag. Only
        Ethernet Type  0x88E7 should be used
        PBB - Provider Backbone Bridges is an Ethernet data-plane technology
        .     (also known as MAC-in-MAC) that involves encapsulating an
        .     Ethernet datagram inside another one with new source and
        .     destination addresses.
        (OpenFlow Switch Specification Version 1.3)
    """

    def __attrs__(self):
        self.push_pbb_action = {'ethernet_type': None}

    def __init__(self, order=0, ethernet_type=None, d=None):
        super(PushPBBHeaderAction, self).__init__(order)
        self.__attrs__()
        if (d is not None):
            self.__init_from_dict__(d)
        else:
            self.set_eth_type(ethernet_type)

    def __init_from_dict__(self, d):
        if (d is not None and isinstance(d, dict)):
            for k, v in d.items():
                if (k == 'ethernet_type'):
                    self.set_eth_type(v)
                else:
                    msg = ("[PushPBBHeaderAction] TODO -> k=%s, v=%s" % (k, v))
                    dbg_print(msg)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)

    def set_eth_type(self, ethernet_type):
        self.push_pbb_action['ethernet_type'] = ethernet_type


class PopPBBHeaderAction(Action):
    """ Pop the outer-most PBB service instance header (I-TAG TCI)
        from the packet
        PBB - Provider Backbone Bridges is an Ethernet data-plane technology
        .     (also known as MAC-in-MAC) that involves encapsulating an
        .     Ethernet datagram inside another one with new source and
        .     destination addresses.
        (OpenFlow Switch Specification Version 1.3)
    """

    def __attrs__(self):
        self.pop_pbb_action = {}

    def __init__(self, order=0):
        super(PopPBBHeaderAction, self).__init__(order)
        self.__attrs__()

'''
class FloodAction(Action):
    """ Flood the packet along the minimum spanning tree, not including the
        incoming interface.
        The sentence 'along the minimum spanning tree' implies: flood the
        packet on all the ports that are not disabled by Spanning Tree
        Protocol.
        Seems to be ODL proprietary action type ???
    """

    def __init__(self, order=0):
        super(FloodAction, self).__init__(order)
        self.flood_action = {}


class FloodAllAction(Action):
    """ Send the packet out all interfaces, not including the incoming
        interface.
        Seems to be ODL proprietary action type ???
    """

    def __init__(self, order=0):
        super(FloodAllAction, self).__init__(order)
        self.flood_all_action = {}


class HwPathAction(Action):
    """ Seems to be ODL proprietary action type ??? """

    def __init__(self, order=0):
        super(HwPathAction, self).__init__(order)
        self.hw_path_action = {}


class SwPathAction(Action):
    """ Seems to be ODL proprietary action type ??? """

    def __init__(self, order=0):
        super(SwPathAction, self).__init__(order)
        self.sw_path_action = {}


class LoopbackAction(Action):
    """ Seems to be ODL proprietary action type ??? """

    def __init__(self, order=0):
        super(LoopbackAction, self).__init__(order)
        self.loopback_action = {}
'''


class Match(object):
    """ Class that represents OpenFlow flow matching attributes """

    def __attrs__(self):
        ''' Ingress port. Numerical representation of in-coming port,
            starting at 1 (may be a physical or switch-defined logical port)
        '''
        self.in_port = None
        ''' Physical port (in 'ofp_packet_in messages'), underlying physical
            port when packet received on a logical port)
        '''
        self.in_phy_port = None
        ''' Ethernet match fields:
            - ethernet destination MAC address
            - ethernet source MAC address
            - ethernet type of the OpenFlow packet payload (after
            .    VLAN tags)
        '''
        self.ethernet_match = None
        ''' IPv4 source address (can use subnet mask) '''
        self.ipv4_source = None
        ''' IPv4 destination address (can use subnet mask) '''
        self.ipv4_destination = None
        ''' IP match fields:
            - Differentiated Service Code Point (DSCP). Part of the IPv4
            . ToS field or the IPv6 Traffic Class field.
            - ECN bits of the IP header. Part of the IPv4 ToS field or
            . the IPv6 Traffic Class field
            - IPv4 or IPv6 protocol number
        '''
        self.ip_match = None
        ''' IPv6 source address (can use subnet mask) '''
        self.ipv6_source = None
        ''' IPv6 destination address (can use subnet mask) '''
        self.ipv6_destination = None
        ''' The target address in an IPv6 Neighbor Discovery message '''
        self.ipv6_nd_target = None
        ''' The source link-layer address option in an
            IPv6 Neighbor Discovery message
        '''
        self.ipv6_nd_sll = None
        ''' The target link-layer address option in an
            IPv6 Neighbor Discovery message
        '''
        self.ipv6_nd_tll = None
        ''' IPv6 flow label '''
        self.ipv6_label = None
        ''' IPv6 Extension Header pseudo-field '''
        self.ipv6_ext_header = None
        ''' Protocol match fields:
           - The LABEL in the first MPLS shim header
           - The TC in the first MPLS shim header
           - The BoS bit (Bottom of Stack bit) in the first MPLS shim header
           - The I-SID in the first PBB service instance tag
        '''
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
            - ICMP code
        '''
        self.icmpv4_match = None
        ''' ICMPv6 match fields
            - ICMPv6 type
            - ICMPv6 code
        '''
        self.icmpv6_match = None
        ''' VLAN match fields:
            - VLAN-ID from 802.1Q header (the CFI bit indicate
            .  the presence of a valid VLAN-ID)
            - VLAN-PCP from 802.1Q header
        '''
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

    def __init__(self, d=None):
        self.__attrs__()
        if (d is not None):
            self.__init_from_dict__(d)

    def __init_from_dict__(self, d):
        if d is not None and isinstance(d, dict):
            for k, v in d.items():
                if (k == 'ethernet_match'):
                    self.ethernet_match = EthernetMatch(d[k])
                elif (k == 'ip_match'):
                    self.ip_match = IpMatch(d[k])
                elif (k == 'protocol_match_fields'):
                    self.protocol_match_fields = ProtocolMatchFields(d[k])
                elif (k == 'icmpv4_match'):
                    self.icmpv4_match = IcmpMatch(d[k])
                elif (k == 'icmpv6_match'):
                    self.icmpv6_match = IcmpV6Match(d[k])
                elif (k == 'vlan_match'):
                    self.vlan_match = VlanMatch(d[k])
                else:
                    setattr(self, k, v)
        else:
            raise TypeError("[Match] wrong argument type '%s'"
                            " ('dict is expected)" % type(d))

    def set_eth_type(self, eth_type):
        if(self.ethernet_match is None):
            self.ethernet_match = EthernetMatch()
        self.ethernet_match.set_type(eth_type)

    def get_eth_type(self):
        res = None
        p = 'ethernet_match'
        if (hasattr(self, p) and isinstance(getattr(self, p), EthernetMatch)):
            em = getattr(self, p)
            res = em.get_type()
        return res

    def set_eth_src(self, eth_src):
        if(self.ethernet_match is None):
            self.ethernet_match = EthernetMatch()
        self.ethernet_match.set_src(eth_src)

    def get_eth_src(self):
        res = None
        p = 'ethernet_match'
        if (hasattr(self, p) and isinstance(getattr(self, p), EthernetMatch)):
            em = getattr(self, p)
            res = em.get_src()
            if (res is not None):
                res = res.lower()
        return res

    def set_eth_dst(self, eth_dst):
        if(self.ethernet_match is None):
            self.ethernet_match = EthernetMatch()
        self.ethernet_match.set_dst(eth_dst)

    def get_eth_dst(self):
        res = None
        p = 'ethernet_match'
        if (hasattr(self, p) and isinstance(getattr(self, p), EthernetMatch)):
            em = getattr(self, p)
            res = em.get_dst()
            if (res is not None):
                res = res.lower()
        return res

    def set_vlan_id(self, vlan_id):
        if(self.vlan_match is None):
            self.vlan_match = VlanMatch()
        self.vlan_match.set_vid(vlan_id)

    def get_vlan_id(self):
        res = None
        p = 'vlan_match'
        if (hasattr(self, p) and isinstance(getattr(self, p), VlanMatch)):
            vm = getattr(self, p)
            res = vm.get_vid()
        return res

    def set_vlan_pcp(self, vlan_pcp):
        if(self.vlan_match is None):
            self.vlan_match = VlanMatch()
        self.vlan_match.set_pcp(vlan_pcp)

    def get_vlan_pcp(self):
        res = None
        p = 'vlan_match'
        if (hasattr(self, p) and isinstance(getattr(self, p), VlanMatch)):
            vm = getattr(self, p)
            res = vm.get_pcp()
        return res

    def set_ipv4_src(self, ipv4_src):
        self.ipv4_source = ipv4_src

    def get_ipv4_src(self):
        res = None
        p = 'ipv4_source'
        if (hasattr(self, p)):
            res = getattr(self, p)
        return res

    def set_ipv4_dst(self, ipv4_dst):
        self.ipv4_destination = ipv4_dst

    def get_ipv4_dst(self):
        res = None
        p = 'ipv4_destination'
        if (hasattr(self, p)):
            res = getattr(self, p)
        return res

    def set_ipv6_src(self, ipv6_src):
        self.ipv6_source = ipv6_src

    def get_ipv6_src(self):
        res = None
        p = 'ipv6_source'
        if (hasattr(self, p)):
            res = getattr(self, p)
            res = res.lower() if res else res
        return res

    def set_ipv6_dst(self, ipv6_dst):
        self.ipv6_destination = ipv6_dst

    def get_ipv6_dst(self):
        res = None
        p = 'ipv6_destination'
        if (hasattr(self, p)):
            res = getattr(self, p)
            res = res.lower() if res else res
        return res

    def set_ipv6_flabel(self, ipv6_flabel):
        if(self.ipv6_label is None):
            self.ipv6_label = Ipv6Label()
        self.ipv6_label.set_flabel(ipv6_flabel)

    def get_ipv6_flabel(self):
        res = None
        p = 'ipv6_label'
        if (hasattr(self, p) and isinstance(getattr(self, p), Ipv6Label)):
            ipl = getattr(self, p)
            res = ipl.get_flabel()
        return res

    def set_ipv6_exh_hdr(self, ipv6_exthdr):
        if(self.ipv6_ext_header is None):
            self.ipv6_ext_header = Ipv6ExtHdr()
        self.ipv6_ext_header.set_exthdr(ipv6_exthdr)

    def get_ipv6_exh_hdr(self):
        res = None
        p = 'ipv6_ext_header'
        if (hasattr(self, p) and isinstance(getattr(self, p), Ipv6ExtHdr)):
            eh = getattr(self, p)
            res = eh.get_exthdr()
        return res

    def set_ip_dscp(self, ip_dscp):
        if(self.ip_match is None):
            self.ip_match = IpMatch()
        self.ip_match.ip_dscp = ip_dscp

    def get_ip_dscp(self):
        res = None
        p = 'ip_match'
        if (hasattr(self, p) and isinstance(getattr(self, p), IpMatch)):
            ipm = getattr(self, p)
            res = ipm.get_ip_dscp()
        return res

    def set_ip_ecn(self, ip_ecn):
        if(self.ip_match is None):
            self.ip_match = IpMatch()
        self.ip_match.ip_ecn = ip_ecn

    def get_ip_ecn(self):
        res = None
        p = 'ip_match'
        if (hasattr(self, p) and isinstance(getattr(self, p), IpMatch)):
            ipm = getattr(self, p)
            res = ipm.get_ip_ecn()
        return res

    def set_ip_proto(self, ip_proto):
        if(self.ip_match is None):
            self.ip_match = IpMatch()
        self.ip_match.ip_protocol = ip_proto

    def get_ip_proto(self):
        res = None
        p = 'ip_match'
        if (hasattr(self, p) and isinstance(getattr(self, p), IpMatch)):
            ipm = getattr(self, p)
            res = ipm.get_ip_proto()
        return res

    def set_udp_src(self, udp_port):
        self.udp_source_port = udp_port

    def get_udp_src(self):
        res = None
        p = 'udp_source_port'
        if hasattr(self, p):
            res = getattr(self, p)
        return res

    def set_udp_dst(self, udp_port):
        self.udp_destination_port = udp_port

    def get_udp_dst(self):
        res = None
        p = 'udp_destination_port'
        if hasattr(self, p):
            res = getattr(self, p)
        return res

    def set_tcp_src(self, tcp_port):
        self.tcp_source_port = tcp_port

    def get_tcp_src(self):
        res = None
        p = 'tcp_source_port'
        if hasattr(self, p):
            res = getattr(self, p)
        return res

    def set_tcp_dst(self, tcp_port):
        self.tcp_destination_port = tcp_port

    def get_tcp_dst(self):
        res = None
        p = 'tcp_destination_port'
        if hasattr(self, p):
            res = getattr(self, p)
        return res

    def set_sctp_src(self, sctp_port):
        self.sctp_source_port = sctp_port

    def get_sctp_src(self):
        res = None
        p = 'sctp_source_port'
        if hasattr(self, p):
            res = getattr(self, p)
        return res

    def set_sctp_dst(self, sctp_port):
        self.sctp_destination_port = sctp_port

    def get_sctp_dst(self):
        res = None
        p = 'sctp_destination_port'
        if hasattr(self, p):
            res = getattr(self, p)
        return res

    def set_icmpv4_type(self, icmpv4_type):
        if(self.icmpv4_match is None):
            self.icmpv4_match = IcmpMatch()
        self.icmpv4_match.set_type(icmpv4_type)

    def get_icmp4_type(self):
        res = None
        p = 'icmpv4_match'
        if (hasattr(self, p) and isinstance(getattr(self, p), IcmpMatch)):
            icm = getattr(self, p)
            res = icm.get_type()
        return res

    def set_icmpv4_code(self, icmpv4_code):
        if(self.icmpv4_match is None):
            self.icmpv4_match = IcmpMatch()
        self.icmpv4_match.set_code(icmpv4_code)

    def get_icmpv4_code(self):
        res = None
        p = 'icmpv4_match'
        if (hasattr(self, p) and isinstance(getattr(self, p), IcmpMatch)):
            icm = getattr(self, p)
            res = icm.get_code()
        return res

    def set_icmpv6_type(self, icmpv6_type):
        if(self.icmpv6_match is None):
            self.icmpv6_match = IcmpV6Match()
        self.icmpv6_match.set_type(icmpv6_type)

    def get_icmpv6_type(self):
        res = None
        p = 'icmpv6_match'
        if (hasattr(self, p) and isinstance(getattr(self, p), IcmpV6Match)):
            icm = getattr(self, p)
            res = icm.get_type()
        return res

    def set_icmpv6_code(self, icmpv6_code):
        if(self.icmpv6_match is None):
            self.icmpv6_match = IcmpV6Match()
        self.icmpv6_match.set_code(icmpv6_code)

    def get_icmpv6_code(self):
        res = None
        p = 'icmpv6_match'
        if (hasattr(self, p) and isinstance(getattr(self, p), IcmpV6Match)):
            icm = getattr(self, p)
            res = icm.get_code()
        return res

    def set_in_port(self, in_port):
        self.in_port = in_port

    def get_in_port(self):
        res = None
        p = 'in_port'
        if hasattr(self, p):
            res = getattr(self, p)
            if (res is not None):
                res = str(res)
                res = res.rsplit(':', 1)[-1]
        return res

    def set_in_phy_port(self, in_phy_port):
        self.in_phy_port = in_phy_port

    def get_in_phy_port(self):
        res = None
        p = 'in_phy_port'
        if hasattr(self, p):
            res = getattr(self, p)
        return res

    def set_arp_opcode(self, arp_opcode):
        self.arp_op = arp_opcode

    def get_arp_opcode(self):
        res = None
        p = 'arp_op'
        if hasattr(self, p):
            res = getattr(self, p)
        return res

    def set_arp_src_transport_address(self, arp_src_tp_addr):
        self.arp_source_transport_address = arp_src_tp_addr

    def get_arp_src_transport_address(self):
        res = None
        p = 'arp_source_transport_address'
        if hasattr(self, p):
            res = getattr(self, p)
        return res

    def set_arp_tgt_transport_address(self, arp_tgt_tp_addr):
        self.arp_target_transport_address = arp_tgt_tp_addr

    def get_arp_tgt_transport_address(self):
        res = None
        p = 'arp_target_transport_address'
        if hasattr(self, p):
            res = getattr(self, p)
        return res

    def set_arp_src_hw_address(self, arp_src_hw_addr):
        if(self.arp_source_hardware_address is None):
            self.arp_source_hardware_address = {}
        self.arp_source_hardware_address['address'] = arp_src_hw_addr

    def get_arp_src_hw_address(self):
        res = None
        p = 'arp_source_hardware_address'
        if hasattr(self, p):
            v = getattr(self, p)
            if (v is not None):
                res = v['address']
                res = res.lower() if res else res
        return res

    def set_arp_tgt_hw_address(self, arp_tgt_hw_addr):
        if(self.arp_target_hardware_address is None):
            self.arp_target_hardware_address = {}
        self.arp_target_hardware_address['address'] = arp_tgt_hw_addr

    def get_arp_tgt_hw_address(self):
        res = None
        p = 'arp_target_hardware_address'
        if hasattr(self, p):
            v = getattr(self, p)
            if (v is not None):
                res = v['address']
                res = res.lower() if res else res
        return res

    def set_mpls_label(self, mpls_label):
        if(self.protocol_match_fields is None):
            self.protocol_match_fields = ProtocolMatchFields()
        self.protocol_match_fields.set_mpls_label(mpls_label)

    def get_mpls_label(self):
        res = None
        p = 'protocol_match_fields'
        if (hasattr(self, p) and isinstance(getattr(self, p),
                                            ProtocolMatchFields)):
            pm = getattr(self, p)
            res = pm.get_mpls_label()
        return res

    def set_mpls_tc(self, mpls_tc):
        if(self.protocol_match_fields is None):
            self.protocol_match_fields = ProtocolMatchFields()
        self.protocol_match_fields.set_mpls_tc(mpls_tc)

    def get_mpls_tc(self):
        res = None
        p = 'protocol_match_fields'
        if (hasattr(self, p) and isinstance(getattr(self, p),
                                            ProtocolMatchFields)):
            pm = getattr(self, p)
            res = pm.get_mpls_tc()
        return res

    def set_mpls_bos(self, mpls_bos):
        if(self.protocol_match_fields is None):
            self.protocol_match_fields = ProtocolMatchFields()
        self.protocol_match_fields.set_mpls_bos(mpls_bos)

    def get_mpls_bos(self):
        res = None
        p = 'protocol_match_fields'
        if (hasattr(self, p) and isinstance(getattr(self, p),
                                            ProtocolMatchFields)):
            pm = getattr(self, p)
            res = pm.get_mpls_bos()
        return res

    def set_tunnel_id(self, tunnel_id):
        if(self.tunnel is None):
            self.tunnel = Tunnel()
        self.tunnel.set_id(tunnel_id)

    def get_tunnel_id(self):
        res = None
        p = 'tunnel'
        if (hasattr(self, p) and isinstance(getattr(self, p), Tunnel)):
            t = getattr(self, p)
            res = t.get_id()
        return res

    def set_metadata(self, metadata):
        if(self.metadata is None):
            self.metadata = Metadata()
        self.metadata.set_metadata(metadata)

    def get_metadata(self):
        res = None
        p = 'metadata'
        if (hasattr(self, p) and isinstance(getattr(self, p), Metadata)):
            m = getattr(self, p)
            res = m.get_metadata()
        return res

    def set_metadata_mask(self, metadata_mask):
        if(self.metadata is None):
            self.metadata = Metadata()
        self.metadata.set_metadata_mask(metadata_mask)

    def get_metadata_mask(self):
        res = None
        p = 'metadata'
        if (hasattr(self, p) and isinstance(getattr(self, p), Metadata)):
            m = getattr(self, p)
            res = m.get_metadata_mask()
        return res


class EthernetMatch(Match):
    """ Ethernet specific match fields """

    def __attrs__(self):
        self.ethernet_type = None
        self.ethernet_source = None
        self.ethernet_destination = None

    def __init__(self, d=None):
        self.__attrs__()
        if (d is not None):
            self.__init_from_dict__(d)

    def __init_from_dict__(self, d):
        if (d is not None and isinstance(d, dict)):
            for k, v in d.items():
                setattr(self, k, v)
        else:
            raise TypeError("[Match] wrong argument type '%s'"
                            " ('dict is expected)" % type(d))

    def set_type(self, eth_type):
        if(self.ethernet_type is None):
            self.ethernet_type = {}
        self.ethernet_type['type'] = eth_type

    def get_type(self):
        res = None
        p = 'ethernet_type'
        if (hasattr(self, p) and isinstance(getattr(self, p), dict)):
            d = getattr(self, p)
            p1 = 'type'
            if (p1 in d):
                res = d[p1]
        return res

    def set_src(self, eth_src):
        if(self.ethernet_source is None):
            self.ethernet_source = {}
        self.ethernet_source['address'] = eth_src

    def get_src(self):
        res = None
        p = 'ethernet_source'
        if (hasattr(self, p) and isinstance(getattr(self, p), dict)):
            d = getattr(self, p)
            p1 = 'address'
            if (p1 in d):
                res = d[p1]
        return res

    def set_dst(self, eth_dst):
        if(self.ethernet_destination is None):
            self.ethernet_destination = {}
        self.ethernet_destination['address'] = eth_dst

    def get_dst(self):
        res = None
        p = 'ethernet_destination'
        if (hasattr(self, p) and isinstance(getattr(self, p), dict)):
            d = getattr(self, p)
            p1 = 'address'
            if (p1 in d):
                res = d[p1]
        return res


class VlanMatch(Match):
    """ VLAN specific match fields """

    def __attrs__(self):
        ''' VLAN-ID from 802.1Q header '''
        self.vlan_id = None
        ''' VLAN-PCP from 802.1Q header '''
        self.vlan_pcp = None

    def __init__(self, d=None):
        self.__attrs__()
        if (d is not None):
            self.__init_from_dict__(d)

    def __init_from_dict__(self, d):
        if d is not None and isinstance(d, dict):
            for k, v in d.items():
                if (k == 'vlan_id'):
                    self.vlan_id = VlanId(v)
                else:
                    setattr(self, k, v)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)

    def set_vid(self, vid):
        if(self.vlan_id is None):
            self.vlan_id = VlanId()
        self.vlan_id.set_vid(vid)

    def get_vid(self):
        res = None
        p = 'vlan_id'
        if (hasattr(self, p) and isinstance(getattr(self, p), VlanId)):
            vm = getattr(self, p)
            res = vm.get_vid()
        return res

    def set_pcp(self, pcp):
        self.vlan_pcp = pcp

    def get_pcp(self):
        res = None
        p = 'vlan_pcp'
        if (hasattr(self, p)):
            res = getattr(self, p)
        return res


class VlanId(VlanMatch):
    """ Helper subclass of VlanMatch class to help in serialization
        of VLAN ID information encoded in match rules of a flow entry
    """

    def __attrs__(self):
        ''' VLAN-ID from 802.1Q header '''
        self.vlan_id = None
        ''' Flag that indicates that 'vlan_id' value is set and matching
            is only for packets with VID equal to 'vlan_id' value
        '''
        self.vlan_id_present = False

    def __init__(self, d=None):
        self.__attrs__()
        if (d is not None):
            self.__init_from_dict__(d)

    def __init_from_dict__(self, d):
        if d is not None and isinstance(d, dict):
            for k, v in d.items():
                setattr(self, k, v)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)

    def set_vid(self, vid):
        self.vlan_id = vid
        self.vlan_id_present = True

    def get_vid(self):
        res = None
        p = 'vlan_id'
        if (hasattr(self, p)):
            res = getattr(self, p)
        return res


class IcmpMatch(Match):
    """ ICMPv4 specific match fields """

    def __attrs__(self):
        ''' ICMP type '''
        self.icmpv4_type = None
        ''' ICMP code '''
        self.icmpv4_code = None

    def __init__(self, d=None):
        self.__attrs__()
        if (d is not None):
            self.__init_from_dict__(d)

    def __init_from_dict__(self, d):
        if d is not None and isinstance(d, dict):
            for k, v in d.items():
                setattr(self, k, v)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)

    def set_type(self, icmp_type):
        self.icmpv4_type = icmp_type

    def get_type(self):
        res = None
        p = 'icmpv4_type'
        if (hasattr(self, p)):
            res = getattr(self, p)
        return res

    def set_code(self, icmp_code):
        self.icmpv4_code = icmp_code

    def get_code(self):
        res = None
        p = 'icmpv4_code'
        if (hasattr(self, p)):
            res = getattr(self, p)
        return res


class IcmpV6Match(Match):
    """ ICMPv6 specific match fields """

    def __attrs__(self):
        ''' ICMPv6 type '''
        self.icmpv6_type = None
        ''' ICMPv6 code '''
        self.icmpv6_code = None

    def __init__(self, d=None):
        self.__attrs__()
        if (d is not None):
            self.__init_from_dict__(d)

    def __init_from_dict__(self, d):
        if (d is not None and isinstance(d, dict)):
            for k, v in d.items():
                setattr(self, k, v)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)

    def set_type(self, icmpv6_type):
        self.icmpv6_type = icmpv6_type

    def get_type(self):
        res = None
        p = 'icmpv6_type'
        if (hasattr(self, p)):
            res = getattr(self, p)
        return res

    def set_code(self, icmpv6_code):
        self.icmpv6_code = icmpv6_code

    def get_code(self):
        res = None
        p = 'icmpv6_code'
        if (hasattr(self, p)):
            res = getattr(self, p)
        return res


class IpMatch(Match):
    """ IPv4 protocol specific match fields """

    def __attrs__(self):
        ''' "IP DSCP (6 bits in ToS field) '''
        self.ip_dscp = None
        ''' IP ECN (2 bits in ToS field) '''
        self.ip_ecn = None
        ''' IPv4 or IPv6 Protocol Number '''
        self.ip_protocol = None

    def __init__(self, d=None):
        self.__attrs__()
        if (d is not None):
            self.__init_from_dict__(d)

    def __init_from_dict__(self, d):
        if (d is not None and isinstance(d, dict)):
            for k, v in d.items():
                setattr(self, k, v)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)

    def set_ip_dscp(self, ip_dscp):
        self.ip_dscp = ip_dscp

    def get_ip_dscp(self):
        res = None
        p = 'ip_dscp'
        if hasattr(self, p):
            res = getattr(self, p)
        return res

    def set_ip_ecn(self, ip_ecn):
        self.ip_ecn = ip_ecn

    def get_ip_ecn(self):
        res = None
        p = 'ip_ecn'
        if hasattr(self, p):
            res = getattr(self, p)
        return res

    def set_ip_proto(self, ip_proto):
        self.ip_protocol = ip_proto

    def get_ip_proto(self):
        res = None
        p = 'ip_protocol'
        if hasattr(self, p):
            res = getattr(self, p)
        return res


class Ipv6Label(Match):
    """ IPv6 Flow Label """

    def __attrs__(self):
        self.ipv6_flabel = None
        self.flabel_mask = None

    def __init__(self, flabel=None, flabel_mask=None):
        self.__attrs__()
        self.set_flabel(flabel)
        self.set_flabel_mask(flabel_mask)

    def set_flabel(self, flabel, flabel_mask=None):
        self.ipv6_flabel = flabel
        self.flabel_mask = flabel_mask

    def get_flabel(self):
        res = None
        p = 'ipv6_flabel'
        if (hasattr(self, p)):
            res = getattr(self, p)
        return res

    def set_flabel_mask(self, flabel_mask):
        self.flabel_mask = flabel_mask

    def get_flabel_mask(self):
        res = None
        p = 'flabel_mask'
        if (hasattr(self, p)):
            res = getattr(self, p)
        return res


class Ipv6ExtHdr(Match):
    """ IPv6 Extension Header pseudo-field """

    def __attrs__(self):
        self.ipv6_exthdr = None
        self.ipv6_exthdr_mask = None

    def __init__(self, exthdr=None, exthdr_mask=None):
        self.__attrs__()
        self.set_exthdr(exthdr)
        self.set_exthdr_mask(exthdr_mask)

    def set_exthdr(self, exthdr, exthdr_mask=None):
        self.ipv6_exthdr = exthdr
        self.ipv6_exthdr_mask = exthdr_mask

    def get_exthdr(self):
        res = None
        p = 'ipv6_exthdr'
        if (hasattr(self, p)):
            res = getattr(self, p)
        return res

    def set_exthdr_mask(self, exthdr_mask):
        self.ipv6_exthdr_mask = exthdr_mask

    def get_exthdr_mask(self):
        res = None
        p = 'ipv6_exthdr_mask'
        if (hasattr(self, p)):
            res = getattr(self, p)
        return res


class ProtocolMatchFields(Match):
    """ Protocol match fields """

    def __attrs__(self):
        ''' The LABEL in the first MPLS shim header '''
        self.mpls_label = None
        ''' The TC in the first MPLS shim header '''
        self.mpls_tc = None
        ''' The BoS bit (Bottom of Stack bit) in the first MPLS shim header '''
        self.mpls_bos = None
        ''' The I-SID in the first PBB service instance tag '''
        self.pbb = None

    def __init__(self, d=None):
        self.__attrs__()
        if (d is not None):
            self.__init_from_dict__(d)

    def __init_from_dict__(self, d):
        if (d is not None and isinstance(d, dict)):
            for k, v in d.items():
                setattr(self, k, v)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('dict' is expected)" % d)

    def set_mpls_label(self, mpls_label):
        self.mpls_label = mpls_label

    def get_mpls_label(self):
        res = None
        p = 'mpls_label'
        if (hasattr(self, p)):
            res = getattr(self, p)
        return res

    def set_mpls_tc(self, mpls_tc):
        self.mpls_tc = mpls_tc

    def get_mpls_tc(self):
        res = None
        p = 'mpls_tc'
        if (hasattr(self, p)):
            res = getattr(self, p)
        return res

    def set_mpls_bos(self, mpls_bos):
        self.mpls_bos = mpls_bos

    def get_mpls_bos(self):
        res = None
        p = 'mpls_bos'
        if (hasattr(self, p)):
            res = getattr(self, p)
        return res


class Pbb(ProtocolMatchFields):
    """ The I-SID in the first PBB service instance tag """

    def __attrs__(self):
        self.pbb_isid = None
        self.pbb_mask = None

    def __init__(self):
        self.__attrs__()

    def set_pbb_isid(self, pbb_isid):
        self.pbb_isid = pbb_isid

    def set_pbb_mask(self, pbb_mask):
        self.pbb_mask = pbb_mask


class ArpSrcHwAddrMatch(Match):
    """ ARP source hardware address """

    def __attrs__(self):
        self.address = None

    def __init__(self):
        self.__attrs__()


class ArpTgtHwAddrMatch(Match):
    ''' ARP target hardware address '''

    def __attrs__(self):
        self.address = None

    def __init__(self):
        self.__attrs__()


class Tunnel(Match):
    """ Metadata associated with a logical port """

    def __attrs__(self):
        self.tunnel_id = None

    def __init__(self):
        self.__attrs__()

    def set_id(self, tunnel_id):
        self.tunnel_id = tunnel_id

    def get_id(self):
        res = None
        p = 'tunnel_id'
        if (hasattr(self, p)):
            res = getattr(self, p)
        return res


class Metadata(Match):
    """ Table metadata. Used to pass information between tables """

    def __attrs__(self):
        self.metadata = None
        self.metadata_mask = None

    def __init__(self):
        self.__attrs__()

    def set_metadata(self, metadata):
        self.metadata = metadata

    def get_metadata(self):
        res = None
        p = 'metadata'
        if (hasattr(self, p)):
            res = getattr(self, p)
        return res

    def set_metadata_mask(self, metadata_mask):
        self.metadata_mask = metadata_mask

    def get_metadata_mask(self):
        res = None
        p = 'metadata_mask'
        if (hasattr(self, p)):
            res = getattr(self, p)
        return res


class GroupEntry():
    """ Class that represents a group entry in the OpenFlow Group Table """

    ''' Reference name in the YANG data tree on the Controller '''
    _mn = "flow-node-inventory:group"

    def __attrs__(self):
        ''' Uniquely identifies a group within a switch. '''
        self.group_id = None
        ''' Group type, should be one of the following:
               OFPGT_ALL      - All group (multicast/broadcast)
               OFPGT_SELECT   - Select group
               OFPGT_INDIRECT - Indirect group
               OFPGT_FF       - Fast failover group
        '''
        self.group_type = None
        ''' Associative name for this group.
            Controller's specific attribute (optional) '''
        self.group_name = None
        ''' Unclear what is it for ???
            Controller's specific attribute (optional) '''
        self.container_name = None
        ''' Unclear, what is it for ???
            Would assume it serves for the same purpose as in FlowEntry.
            Controller's specific attribute (optional)
        '''
        self.barrier = None
        ''' An ordered list of action buckets in this group.
            Each action bucket contains a set of actions to execute
            and associated parameters.
        '''
        self.buckets = {'bucket': []}

    def __init__(self, group_id=None, group_type=None, group_dict=None):
        self.__attrs__()
        if (group_dict is not None):
            self.__init_from_dict__(group_dict)
        else:
            self.group_id = group_id
            self.group_type = group_type

    def __init_from_json__(self, js):
        if (js is not None and isinstance(js, basestring)):
            obj = json.loads(js)
            d = dict_keys_dashed_to_underscored(obj)
            p1 = 'buckets'
            p2 = 'bucket'
            for k, v in d.items():
                if k == p1:
                    b = d.get(p1).get(p2)
                    if b:
                        if isinstance(b, list):
                            for i in b:
                                bucket = GroupBucket(bucket_dict=i)
                                self.buckets[p2].append(bucket)
                else:
                    setattr(self, k, v)
        else:
            raise TypeError("[GroupEntry] wrong argument type '%s'"
                            " (JSON 'string' is expected)" % type(js))

    def __init_from_dict__(self, d):
        if (d is not None and isinstance(d, dict)):
            js = json.dumps(d)
            self.__init_from_json__(js)
        else:
            raise TypeError("[GroupEntry] wrong argument type '%s'"
                            " ('dict' is expected)" % type(d))

    def to_string(self):
        """ Returns string representation of this object. """
        return str(vars(self))

    def to_json(self):
        """ Return GroupEntry represented as JSON object """
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def to_yang_json(self, strip=False):
        s = self.to_json()
        # Convert all 'underscored' keywords to 'dash-separated' form used
        # by ODL YANG models naming conventions
        s = s.replace('_', '-')
        # Following are exceptions from the common ODL rules for having all
        # multi-part keywords in YANG models being hash separated
#        s = s.replace('table-id', 'table_id')
#        s = s.replace('cookie-mask', 'cookie_mask')
        if strip:
            # ignore unassigned ("empty") attributes
            d1 = json.loads(s)
            d2 = strip_none(d1)
            s = json.dumps(d2, sort_keys=True, indent=4)

        return s

    def get_payload(self):
        """ Return GroupEntry as a payload for the HTTP request body """
        s = self.to_json()
        # Convert all 'underscored' keywords to 'dash-separated' form used
        # by ODL YANG models naming conventions
        s = s.replace('_', '-')
        # Following are exceptions from the common ODL rules for having all
        # multi-part keywords in YANG models being hash separated
        s = s.replace('watch-group', 'watch_group')
        s = s.replace('watch-port', 'watch_port')
        d1 = json.loads(s)
        d2 = strip_none(d1)
        payload = {self._mn: d2}
        return json.dumps(payload, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def to_ofp_oxm_syntax(self):
        gl = []
        gl.append('group_id=%s' % self.group_id)
        gl.append('type=%s' % self.group_type.replace('group-', ''))

        bl = []
        buckets = self.get_buckets()
        for b in buckets:
            s = b.to_ofp_oxm_syntax()
            bl.append(s)

        s = ",".join(gl + bl)
        return s

    def set_group_id(self, group_id):
        self.group_id = group_id

    def get_group_id(self):
        return self.group_id

    def set_group_type(self, group_type):
        self.group_type = group_type

    def get_group_type(self):
        return self.group_type

    def set_group_name(self, name):
        self.group_name = name

    def get_group_name(self):
        return self.group_name

    def set_container_name(self, name):
        self.container_name = name

    def get_container_name(self):
        return self.container_name

    def set_barrier(self, barrier):
        self.barrier = barrier

    def get_barrier(self, barrier):
        return self.barrier

    def add_bucket(self, bucket):
        if isinstance(bucket, GroupBucket):
            self.buckets['bucket'].append(bucket)
        else:
            raise TypeError("!!!Error, argument '%s' is of a wrong type "
                            "('GroupBucket' instance is expected)" % bucket)

    def _sort_buckets(self, b):
        return b.get_id()

    def get_buckets(self):
        bl = self.buckets['bucket']
        return sorted(bl, key=self._sort_buckets)


class GroupBucket():
    """ Helper class for representing 'buckets' property
        of the GroupEntry class
    """

    def __attrs__(self):
        ''' Identifier (index) of the bucket within the group '''
        self.bucket_id = None
        ''' Relative weight of this bucket.
            Only defined for select groups. '''
        self.weight = None
        ''' Port whose state affects whether this bucket is live.
            Indicates the port whose liveness controls whether this
            bucket is a candidate for forwarding.
            Only required for fast failover groups, but may be optionally
            implemented for other group types also '''
        self.watch_port = None
        ''' Group whose state affects whether this bucket is live.
            Indicates the group whose liveness controls whether this
            bucket is a candidate for forwarding.
            Only required for fast failover groups, but may be optionally
            implemented for other group types also '''
        self.watch_group = None
        ''' Set of actions to execute by this bucket '''
        self.action = []

    def __init__(self, bucket_id=None, bucket_dict=None):
        self.__attrs__()
        if (bucket_dict is not None):
            self.__init_from_dict__(bucket_dict)
        else:
            self.bucket_id = bucket_id

    def __init_from_json__(self, js):
        if (js is not None and isinstance(js, basestring)):
            obj = json.loads(js)
            d = dict_keys_dashed_to_underscored(obj)
            p1 = 'action'
            for k, v in d.items():
                if (k == p1):
                    if isinstance(v, list):
                        for a in v:
                            if isinstance(a, dict):
                                action = self.create_action_from_dict(a)
                                assert(action)
                                self.add_action(action)
                            else:
                                msg = ("TODO -> unsupported data type '%s'" %
                                       type(a))
                                dbg_print(msg)
                    elif isinstance(v, dict):
                        action = self.create_action_from_dict(a)
                        assert(action)
                        self.add_action(action)
                    else:
                        msg = ("TODO -> unsupported data type '%s'" % type(v))
                        dbg_print(msg)
                else:
                    setattr(self, k, v)
        else:
            raise TypeError("[GroupBucket] wrong argument type '%s'"
                            " (JSON 'string' is expected)" % type(js))

    def __init_from_dict__(self, d):
        if (d is not None and isinstance(d, dict)):
            js = json.dumps(d)
            self.__init_from_json__(js)
        else:
            raise TypeError("[GroupBucket] wrong argument type '%s'"
                            " ('dict' is expected)" % type(d))

    def to_string(self):
        """ Returns string representation of this object. """
        return str(vars(self))

    def to_json(self):
        """ Return this object represented as JSON """
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def create_action_from_dict(self, d):
        action = Instruction().create_action_from_dict(d)
        return action

    def to_ofp_oxm_syntax(self, skip_garbage=False):
        """ Controller returns value of 2**32-1 (4294967295)
            for unassigned counters, 'skip_garbage' flag
            set True tells to ignore them
        """
        bl = []
        v = self.weight
        if (v):
            skip = skip_garbage and (v == ((2 ** 32) - 1))
            if not skip:
                bl.append('weight=%s' % v)
        v = self.watch_port
        if (v):
            skip = skip_garbage and (v == ((2 ** 32) - 1))
            if not skip:
                bl.append('watch_port=%s' % v)
        v = self.watch_group
        if (v):
            skip = skip_garbage and (v == ((2 ** 32) - 1))
            if not skip:
                bl.append('watch_group=%s' % v)

        al = []
        actions = self.get_actions()
        for action in actions:
            s = action.to_ofp_oxm_syntax()
            if (s):
                al.append(s)
            else:
                msg = ("[GroupBucket->to_ofp_oxm_syntax]"
                       " no value for action %s" % action)
                dbg_print(msg)
        sa = "actions={"
        if (al):
            sa += ",".join(al)
        sa += "}"

        bl.append(sa)
        s = "bucket={" + ",".join(bl) + "}"
        return s

    def get_id(self):
        return self.bucket_id

    def set_weight(self, weight):
        self.weight = weight

    def get_weight(self):
        return self.weight

    def set_watch_port(self, port):
        self.watch_port = port

    def get_watch_port(self):
        return self.watch_port

    def set_watch_group(self, group_id):
        self.watch_group = group_id

    def get_watch_group(self):
        return self.watch_group

    def add_action(self, action):
        self.action.append(action)

    def get_actions(self):
        return self.action


class GroupInfo():
    """ Represents current state of an OpenFlow group entry
        in the Controller's operational data store.
        (OpenFlow switch context specific data)
    """
    def __attrs__(self):
        self.group_id = None
        self.group_type = None
        self.buckets = {'bucket': []}
        self.group_desc = None
        self.group_statistics = None

    def __init__(self, group_info):
        self.__attrs__()
        if (isinstance(group_info, dict)):
            d = dict_keys_dashed_to_underscored(group_info)
            p1 = 'buckets'
            p2 = 'opendaylight_group_statistics:group_desc'
            p3 = 'opendaylight_group_statistics:group_statistics'
            for k, v in d.items():
                if (k == p1):
                    bl = v.get('bucket', [])
                    for item in bl:
                        b = GroupBucket(bucket_dict=item)
                        self.add_bucket(b)
                elif (k == p2):
                    self.group_desc = GroupDescription(v)
                elif (k == p3):
                    self.group_statistics = GroupStatistics(v)
                elif (hasattr(self, k)):
                    setattr(self, k, v)
                else:
                    msg = ("TODO -> unexpected attribute '%s'" % k)
                    dbg_print(msg)
        else:
            raise TypeError("[GroupInfo] wrong argument type '%s'"
                            " (dictionary is expected)" % type(group_info))

    def get_id(self):
        return self.group_id

    def add_bucket(self, bucket):
        assert (isinstance(bucket, GroupBucket))
        self.buckets['bucket'].append(bucket)

    def _sort_buckets(self, b):
        return b.get_id()

    def get_buckets(self):
        bl = self.buckets['bucket']
        return sorted(bl, key=self._sort_buckets)

    def get_description(self):
        return self.group_desc

    def get_statistics(self):
        return self.group_statistics

    def to_ofp_oxm_syntax(self):
        gl = []
        gl.append('group_id=%s' % self.group_id)
        gl.append('type=%s' % self.group_type.replace('group-', ''))

        bl = []
        buckets = self.get_buckets()
        for b in buckets:
            s = b.to_ofp_oxm_syntax(skip_garbage=True)
            bl.append(s)

        s = ",".join(gl + bl)
        return s


class GroupFeatures():
    """ Represents Group Features of an OpenFlow device
        (group types, max number of groups for each type,
        group capabilities and group supported actions).
    """

    # mapping of group type names to their numerical values
    # in the OFPGT_* enum
    types_map = {'all': 0, 'select': 1, 'indirect': 2, 'ff': 3}
    # mapping of group capability names to their bit positions
    # in the OFPGFC_* bitmap
    capabilities_map = {'select-weight': 1, 'select-liveness': 2,
                        'chaining': 4, 'chaining-checks': 8}
    # mapping of bit positions for OFPAT_* action types to
    # the corresponding action names
    actions_bitmap = {
        0: 'OUTPUT',         # Output to switch port
        1: 'SET_VLAN_VID',   # Set the 802.1q VLAN id
        2: 'SET_VLAN_PCP',   # Set the 802.1q priority
        3: 'STRIP_VLAN',     # Strip the 802.1q header
        4: 'SET_DL_SRC',     # Ethernet source address
        5: 'SET_DL_DST',     # Ethernet destination address
        6: 'SET_NW_SRC',     # IP source address
        7: 'SET_NW_DST',     # IP destination address/
        8: 'SET_NW_TOS',     # IP ToS (DSCP field, 6 bits)
        9: 'SET_TP_SRC',     # TCP/UDP source port
        10: 'SET_TP_DST',    # TCP/UDP destination port
        11: 'COPY-TTL-OUT',  # Copy TTL "outwards"
        12: 'COPY-TTL-IN',   # Copy TTL "inwards"
        15: 'SET-MPLS-TTL',  # MPLS TTL
        16: 'DEC-MPLS-TTL',  # Decrement MPLS TTL
        17: 'PUSH-VLAN',     # Push a new VLAN tag
        18: 'POP-VLAN',      # Pop the outer VLA
        19: 'PUSH-MPLS',     # Push a new MPLS tag
        20: 'POP-MPLS',      # Pop the outer MPLS tag
        21: 'SET-QUEUE',     # Set queue id when outputting to a port
        22: 'GROUP',         # Apply group
        23: 'SET-NW-TTL',    # IP TTL
        24: 'DEC-NW-TTL',    # Decrement IP TTL
        25: 'SET-FIELD',     # Set a header field using OXM TLV format
        26: 'PUSH-PBB',      # Push a new PBB service tag (I-TAG)
        27: 'POP-PBB'        # Pop the outer PBB service tag (I-TAG)
    }
    actions_bitmap_size = 28

    def __attrs__(self):
        ''' Maximum number of groups for each type '''
        self.max_groups = []
        ''' Group types:
               ALL      - All (multicast/broadcast) group
               SELECT   - Select group
               INDIRECT - Indirect group
               FF       - Fast failover group
        '''
        self.group_types_supported = []
        ''' Group capabilities:
               SELECT_WEIGHT   - Support weight for select groups
               SELECT_LIVENESS - Support liveness for select groups
               CHAINING        - Support chaining groups
               CHAINING_CHECKS - Check chaining for loops and delete
        '''
        self.group_capabilities_supported = []
        ''' Set of bitmaps of actions supported by each group type.
            The first bitmap applies to the OFPGT_AL group type.
            The bitmask uses the values from ofp_action_type
            as the number of bits to shift left for an associated action.
            For example, OFPAT_OUTPUT would use the mask 0x00000001
        '''
        self.actions = []

    def __init__(self, features):
        self.__attrs__()
        if (isinstance(features, dict)):
            d = dict_keys_dashed_to_underscored(features)
            for k, v in d.items():
                if(hasattr(self, k)):
                    setattr(self, k, v)
                else:
                    msg = ("TODO -> unexpected attribute '%s'" % k)
                    dbg_print(msg)
        else:
            raise TypeError("[GroupFeatures] wrong argument type '%s'"
                            " (dictionary is expected)" % type(features))

    def _sort_key_capabilities(self, var):
        return self.capabilities_map.get(var.lower())

    def _sort_key_types(self, var):
        return self.types_map.get(var.lower())

    def get_max_groups(self):
        return self.max_groups

    def get_capabilities(self):
        l = self.group_capabilities_supported
        p = 'opendaylight-group-types:'
        l1 = [i.encode('ascii', 'ignore').replace(p, '').upper() for i in l]
        res = sorted(l1, key=self._sort_key_capabilities)
        return res

    def get_types(self):
        l = self.group_types_supported
        p = 'opendaylight-group-types:' + 'group-'
        l1 = [i.encode('ascii', 'ignore').replace(p, '').upper() for i in l]
        res = sorted(l1, key=self._sort_key_types)
        return res

    def get_actions(self):
        res = []
        bitmap_list = self.actions
        for bitmap in bitmap_list:
            names = self._action_bitmap_to_names(bitmap)
            res.append(names)

        return res

    def _action_bitmap_to_names(self, bitmap):
        names = []
        for i in range(0, self.actions_bitmap_size):
            if ((1 << i) & bitmap):
                # print "i=%2d, act=%s" % (i, group_action_types.get(i))
                name = self.actions_bitmap.get(i)
                if name:
                    names.append(name)

        return names


class GroupStatistics():
    """ Statistics data for an OpenFlow Group """

    def __attrs__(self):
        self.group_id = None
        self.ref_count = None
        self.packet_count = None
        self.byte_count = None
        self.duration = {'second': None, 'nanosecond': None}
        self.buckets = {'bucket_counter': []}

    def __init__(self, stats):
        self.__attrs__()
        if (isinstance(stats, dict)):
            d = dict_keys_dashed_to_underscored(stats)
            for k, v in d.items():
                if (k == 'buckets'):
                    bl = v.get('bucket_counter')
                    for item in bl:
                        bc = BucketCounter(item)
                        self.buckets['bucket_counter'].append(bc)
                elif (hasattr(self, k)):
                    setattr(self, k, v)
                else:
                    msg = ("TODO -> unexpected attribute '%s'" % k)
                    dbg_print(msg)
        else:
            raise TypeError("[GroupStatistics] wrong argument type '%s'"
                            " (dictionary is expected)" % type(stats))

    def to_json(self):
        """ Return this object as JSON """
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def to_yang_json(self, strip=False):
        s = self.to_json()
        # Convert all 'underscored' keywords to 'dash-separated' form used
        # by ODL YANG models naming conventions
        s = s.replace('_', '-')
        if strip:
            # ignore unassigned ("empty") attributes
            d1 = json.loads(s)
            d2 = strip_none(d1)
            s = json.dumps(d2, sort_keys=True, indent=4)

        return s

    def get_group_id(self):
        return self.group_id

    def get_duration(self):
        s = self.duration['second']
        ns = self.duration['nanosecond']
        res = float(s * 1000000000 + ns) / 1000000000
        return res

    def add_bucket(self, bucket):
        assert (isinstance(bucket, BucketCounter))
        self.buckets['bucket_counter'].append(bucket)

    def _sort_buckets(self, b):
        return b.get_id()

    def get_buckets(self):
        bl = self.buckets['bucket_counter']
        return sorted(bl, key=self._sort_buckets)

    def to_ofp_oxm_syntax(self):
        gl = []
        gl.append('group_id=%s' % self.group_id)
        gl.append('ref_count=%s' % self.ref_count)
        gl.append('packet_count=%s' % self.packet_count)
        gl.append('byte_count=%s' % self.byte_count)
        gl.append('duration=%s' % self.get_duration())

        bl = []
        buckets = self.get_buckets()
        for b in buckets:
            s = b.to_ofp_oxm_syntax()
            bl.append(s)

        s = ",".join(gl + bl)
        return s


class BucketCounter():
    """ Group Buckets statistics data.
        Helper class of the GroupStatistics class.
    """

    def __attrs__(self):
        self.bucket_id = None
        self.packet_count = None
        self.byte_count = None

    def __init__(self, d):
        self.__attrs__()
        if (isinstance(d, dict)):
            d = dict_keys_dashed_to_underscored(d)
            for k, v in d.items():
                if (hasattr(self, k)):
                    setattr(self, k, v)
                else:
                    msg = ("TODO -> unexpected attribute '%s'" % k)
                    dbg_print(msg)
        else:
            raise TypeError("[BucketCounter] wrong argument type '%s'"
                            " (dictionary is expected)" % type(d))

    def get_id(self):
        return self.bucket_id

    def to_ofp_oxm_syntax(self):
        bl = []
        bl.append('packet_count=%s' % self.packet_count)
        bl.append('byte_count=%s' % self.byte_count)
        s = "bucket={" + ",".join(bl) + "}"
        return s


class GroupDescription():
    """ Description of an OpenFlow Group. """

    def __attrs__(self):
        self.group_id = None
        self.group_type = None
        self.buckets = {'bucket': []}

    def __init__(self, stats):
        self.__attrs__()
        if (isinstance(stats, dict)):
            d = dict_keys_dashed_to_underscored(stats)
            for k, v in d.items():
                if (k == 'buckets'):
                    bl = v.get('bucket')
                    for item in bl:
                        b = GroupBucket(bucket_dict=item)
                        self.add_bucket(b)
                elif (hasattr(self, k)):
                    setattr(self, k, v)
                else:
                    msg = ("TODO -> unexpected attribute '%s'" % k)
                    dbg_print(msg)
        else:
            raise TypeError("[GroupDescription] wrong argument type '%s'"
                            " (dictionary is expected)" % type(stats))

    def to_json(self):
        """ Return this object as JSON """
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def to_yang_json(self, strip=False):
        s = self.to_json()
        # Convert all 'underscored' keywords to 'dash-separated' form used
        # by ODL YANG models naming conventions
        s = s.replace('_', '-')
        if strip:
            # ignore unassigned ("empty") attributes
            d1 = json.loads(s)
            d2 = strip_none(d1)
            s = json.dumps(d2, sort_keys=True, indent=4)

        return s

    def get_id(self):
        return self.group_id

    def add_bucket(self, bucket):
        assert (isinstance(bucket, GroupBucket))
        self.buckets['bucket'].append(bucket)

    def _sort_buckets(self, b):
        return b.get_id()

    def get_buckets(self):
        bl = self.buckets['bucket']
        return sorted(bl, key=self._sort_buckets)

    def to_ofp_oxm_syntax(self):
        gl = []
        gl.append('group_id=%s' % self.group_id)
        gl.append('type=%s' % self.group_type.replace('group-', ''))

        bl = []
        buckets = self.get_buckets()
        for b in buckets:
            s = b.to_ofp_oxm_syntax(skip_garbage=True)
            bl.append(s)

        s = ",".join(gl + bl)
        return s


class QueueStats():
    """ Queue statistics for a port """

    def __attrs__(self):
        ''' Queue identifier '''
        self.qid = None
        ''' Number of transmitted packets '''
        self.transmitted_packets = None
        ''' Number of transmitted bytes '''
        self.transmitted_bytes = None
        ''' Number of packets dropped due to overrun '''
        self.transmission_errors = None
        ''' Time queue has been alive '''
        self.duration = {}

    def __init__(self, queue_id, stats):
        self.__attrs__()
        if (isinstance(stats, dict)):
            self.qid = queue_id
            d = dict_keys_dashed_to_underscored(stats)
            for k, v in d.items():
                if (hasattr(self, k)):
                    setattr(self, k, v)
                else:
                    msg = ("TODO -> unexpected attribute '%s'" % k)
                    dbg_print(msg)
        else:
            raise TypeError("[QueueStats] wrong argument type '%s'"
                            " (dictionary is expected)" % type(stats))

    def to_json(self):
        """ Return this object as JSON """
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def queue_id(self):
        return self.qid

    def tx_pkts(self):
        return self.transmitted_packets

    def tx_bytes(self):
        return self.transmitted_bytes

    def tx_errs(self):
        res = self.transmission_errors
        # Following statement is a temporary hack.
        #    For unassigned counter Controller returns value that
        #    is equal to the upper max range for the 'Counter64'
        #    IETF integer type
        res = 0 if res == 18446744073709551615 else res
        return res

    def time_alive(self):
        s = self.duration.get('second', 0)
        ns = self.duration.get('nanosecond', 0)
        res = float(s * 1000000000 + ns) / 1000000000
        return res


class MeterFeatures():
    """ Represents Metering Features of an OpenFlow device. """

    # mapping of meter band type names to their numerical values
    # in the OFPMT_* enum
    types_map = {'drop': 1, 'dscp-remark': 2, 'experimenter': 65535}
    # mapping of meter capability names to their bit positions
    # in the OFPMF_* bitmap
    capabilities_map = {'kbps': 1, 'pktps': 2, 'burst': 4, 'stats': 8}

    def __attrs__(self):
        ''' Maximum number of meters. '''
        self.max_meter = None
        ''' Maximum bands per meters. '''
        self.max_bands = None
        ''' Maximum color value. '''
        self.max_color = None
        ''' Metering band types:
                drop         - Drop packet
                dscp_remark  - Remark DSCP in the IP header
                experimenter - Experimenter meter band
         '''
        self.meter_band_supported = []
        ''' Metering capabilities:
                kbps  - Rate value in kb/s (kilo-bit per second)
                pktps - Rate value in packet/sec
                burst - Do burst size
                stats - Collect statistics
         '''
        self.meter_capabilities_supported = []

    def __init__(self, features):
        self.__attrs__()
        if (isinstance(features, dict)):
            d = dict_keys_dashed_to_underscored(features)
            for k, v in d.items():
                if(hasattr(self, k)):
                    setattr(self, k, v)
                else:
                    msg = ("TODO -> unexpected attribute '%s'" % k)
                    dbg_print(msg)
        else:
            raise TypeError("[MeterFeatures] wrong argument type '%s'"
                            " (dictionary is expected)" % type(features))

    def _sort_key_capabilities(self, var):
        return self.capabilities_map.get(var.lower())

    def _sort_key_types(self, var):
        return self.types_map.get(var.lower())

    def get_max_meters(self):
        return self.max_meter

    def get_max_bands(self):
        return self.max_bands

    def get_max_colors(self):
        return self.max_color

    def get_band_types(self):
        p = "opendaylight-meter-types:" + "meter-band-"
        l = self.meter_band_supported
        l1 = [i.encode('ascii', 'ignore').replace(p, '').upper() for i in l]
        res = sorted(l1, key=self._sort_key_types)
        return res

    def get_capabilities(self):
        p = "opendaylight-meter-types:" + "meter-"
        l = self.meter_capabilities_supported
        l1 = [i.encode('ascii', 'ignore').replace(p, '').upper() for i in l]
        res = sorted(l1, key=self._sort_key_capabilities)
        return res
