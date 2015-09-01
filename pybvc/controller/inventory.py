
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

inventory.py: Controller's inventory parser


"""

import re
import json

from pybvc.common.utils import dict_keys_dashed_to_underscored
from pybvc.common.utils import strip_none


class Inventory():
    ''' Class that represents current state of
        the Controller's inventory store '''

    def __init__(self, inv_json=None):
        self.openflow_nodes = []
        self.netconf_nodes = []
        if (inv_json is not None):
            self.__init_from_json__(inv_json)
            return

    def add_openflow_node(self, node):
        assert(isinstance(node, OpenFlowCapableNode))
        self.openflow_nodes.append(node)

    def add_netconf_node(self, node):
        assert(isinstance(node, NetconfCapableNode))
        self.netconf_nodes.append(node)

    def __init_from_json__(self, s):
        if (isinstance(s, basestring)):
            l = json.loads(s)
            assert(isinstance(l, list))
            p1 = 'id'
            p2 = 'openflow'
            p3 = 'netconf_node_inventory:initial_capability'
            devices = [{'clazz': 'NOS', 'filter': 'brocade-interface@2012-04-24.yang'},
                       {'clazz': 'VRouter5600', 'filter': 'vyatta-interfaces?revision=2014-12-02'},
                       {'clazz': 'controller', 'filter': 'controller:netty:eventexecutor?revision=2013-11-12'}]
            for item in l:
                if isinstance(item, dict):
                    d = dict_keys_dashed_to_underscored(item)
                    if p1 in d and isinstance(d[p1], basestring):
                        if (d[p1].startswith(p2)):
                            node = OpenFlowCapableNode(inv_dict=d)
                            self.add_openflow_node(node)
                    if p3 in d:
                        # Netconf
                        capabilities = d.get(p3)
                        nodes = [[d, dev['clazz']] for c in capabilities for
                                 dev in devices if dev['filter'] in c]
                        for node in nodes:
                            if node is not None:
                                node = NetconfCapableNode(clazz=node[1],
                                                          inv_dict=node[0])
                                self.add_netconf_node(node)
                                break
                            else:
                                node = NetconfCapableNode(clazz='unknown',
                                                          inv_dict=d)
                                self.add_netconf_node(node)

        else:
            raise TypeError("[Inventory] wrong argument type '%s'"
                            " (JSON 'string' is expected)" % type(s))

    def get_openflow_node_ids(self):
        ids = []
        for item in self.openflow_nodes:
            ids.append(item.get_id())
        return sorted(ids)

    def get_openflow_node(self, node_id):
        node = None
        for item in self.openflow_nodes:
            if node_id == item.get_id():
                node = item
                break
        return node

    def get_openflow_node_flows_cnt(self, node_id):
        cnt = 0
        node = self.get_openflow_node(node_id)
        if node:
            assert(isinstance(node, OpenFlowCapableNode))
            cnt = node.get_flows_cnt()
        return cnt

    def get_netconf_node_ids(self):
        ids = []
        for item in self.netconf_nodes:
            ids.append(item.get_id())
        return sorted(ids)

    def get_netconf_node(self, node_id):
        node = None
        for item in self.netconf_nodes:
            if node_id == item.get_id():
                node = item
                break
        return node


class OpenFlowCapableNode():
    ''' Class that represents current state of an OpenFlow capable node
        in the Controller's inventory store
        Helper class of the 'Inventory' class '''

    def __init__(self, inv_json=None, inv_dict=None):
        self.ports = []
        # Group support capabilities of the switch
        self.group_features = []
        # Current groups on the switch
        self.groups = []

        if (inv_json):
            self.__init_from_json__(inv_json)
            return

        if(inv_dict):
            self.__init_from_dict__(inv_dict)
            return

    def __init_from_json__(self, s):
        assert(isinstance(s, basestring))
        obj = json.loads(s)
        d = dict_keys_dashed_to_underscored(obj)
        p1 = 'node_connector'
        p2 = 'opendaylight_group_statistics:group_features'
        p3 = 'flow_node_inventory:group'
        for k, v in d.items():
            if p1 == k and isinstance(v, list):
                for p in v:
                    of_port = OpenFlowPort(p)
                    self.ports.append(of_port)
            elif p2 == k:
                self.group_features = GroupFeatures(v)
            elif p3 == k and isinstance(v, list):
                for g in v:
                    of_group = GroupInfo(g)
                    self.groups.append(of_group)
            else:
                setattr(self, k, v)

    def __init_from_dict__(self, d):
        assert(isinstance(d, dict))
        js = json.dumps(d)
        self.__init_from_json__(js)

    def to_string(self):
        """ Returns string representation of this object. """
        return str(vars(self))

    def to_json(self):
        """ Returns JSON representation of this object. """
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True,
                          indent=4)

    def get_id(self):
        return self.id

    def get_manufacturer_info(self):
        info = ""
        p = 'flow_node_inventory:manufacturer'
        if hasattr(self, p):
            info = getattr(self, p)
        else:
            assert(False)
        return info

    def get_hardware_info(self):
        info = ""
        p = 'flow_node_inventory:hardware'
        if hasattr(self, p):
            info = getattr(self, p)
        else:
            assert(False)
        return info

    def get_software_info(self):
        info = ""
        p = 'flow_node_inventory:software'
        if hasattr(self, p):
            info = getattr(self, p)
        else:
            assert(False)
        return info

    def get_description(self):
        descr = ""
        p = 'flow_node_inventory:description'
        if hasattr(self, p):
            descr = getattr(self, p)
        else:
            assert(False)
        return descr

    def get_capabilities(self):
        capabilities = []
        p1 = 'flow_node_inventory:switch_features'
        d = self.__dict__
        if (p1 in d):
            p2 = 'capabilities'
            if p2 in d[p1] and isinstance(d[p1][p2], list):
                p3 = 'flow-node-inventory:flow-feature-capability-'
                for item in d[p1][p2]:
                    s = item.replace(p3, "").replace('_', ' ').upper()
                    capabilities.append(s)
        return capabilities

    def get_ip_address(self):
        addr = ""
        p = 'flow_node_inventory:ip_address'
        if hasattr(self, p):
            addr = getattr(self, p)
        else:
            assert(False)
        return addr

    def get_flows_cnt(self):
        flow_cnt = 0
        p1 = 'flow_node_inventory:table'
        p2 = 'opendaylight_flow_statistics:aggregate_flow_statistics'
        p3 = 'flow_count'
        flow_table = self.__dict__[p1]
        for item in flow_table:
            if (isinstance(item, dict) and p2 in item):
                flow_cnt += item[p2][p3]
        return flow_cnt

    def get_serial_number(self):
        sn = ""
        p = 'flow_node_inventory:serial_number'
        if hasattr(self, p):
            sn = getattr(self, p)
        else:
            assert(False)
        return sn

    def get_max_buffers_info(self):
        n = ""
        p1 = 'flow_node_inventory:switch_features'
        p2 = 'max_buffers'
        d = self.__dict__
        if (p1 in d and p2 in d[p1]):
            n = self.__dict__[p1][p2]
        return n

    def get_max_tables_info(self):
        n = ""
        p1 = 'flow_node_inventory:switch_features'
        p2 = 'max_tables'
        d = self.__dict__
        if (p1 in d and p2 in d[p1]):
            n = self.__dict__[p1][p2]
        return n

    def get_flow_tables_cnt(self):
        cnt = ""
        p = 'flow_node_inventory:table'
        if hasattr(self, p):
            cnt = len(getattr(self, p))
        else:
            assert(False)
        return cnt

    def get_flows_in_table_cnt(self, table_id):
        flow_cnt = 0
        p1 = 'flow_node_inventory:table'
        p2 = 'opendaylight_flow_statistics:aggregate_flow_statistics'
        p3 = 'flow_count'
        flow_table = self.__dict__[p1]
        for item in flow_table:
            if (isinstance(item, dict) and p2 in item):
                if(item['id'] == table_id):
                    flow_cnt += item[p2][p3]
                    break
        return flow_cnt

    def get_port_ids(self):
        port_ids = []
        for item in self.ports:
            port_id = item.get_port_id()
            port_ids.append(port_id)
        return sorted(port_ids)

    def get_port_number(self, port_id):
        pnum = None
        for item in self.ports:
            if(item.get_port_id() == port_id):
                pnum = item.get_port_number()
                break
        return pnum

    def get_port_name(self, port_id):
        pname = None
        for item in self.ports:
            if(item.get_port_id() == port_id):
                pname = item.get_port_name()
                break
        return pname

    def get_port_obj(self, port_id):
        port_obj = None
        for item in self.ports:
            if(item.get_port_id() == port_id):
                port_obj = item
        return port_obj

    def get_group_features(self):
        return self.group_features

    def get_groups_total_num(self):
        return len(self.groups)

    def get_group_ids(self):
        ids = []
        for item in self.groups:
            ids.append(item.get_id())
        return sorted(ids)

    def get_group(self, group_id):
        return None


class OpenFlowPort():
    ''' Class that represents current state of an OpenFlow enabled port
        Helper class of the 'OpenFlowCapableNode' class '''

    def __init__(self, d):
        assert(isinstance(d, dict))
        for k, v in d.items():
            setattr(self, k, v)

    def to_string(self):
        """ Returns string representation of this object. """
        return str(vars(self))

    def to_json(self):
        """ Returns JSON representation of this object. """
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True,
                          indent=4)

    def get_port_id(self):
        pid = ""
        p = 'id'
        if hasattr(self, p):
            pid = getattr(self, p)
        else:
            assert(False)
        return pid

    def get_port_number(self):
        pnum = ""
        p = 'flow_node_inventory:port_number'
        if hasattr(self, p):
            pnum = getattr(self, p)
        else:
            assert(False)
        return pnum

    def get_port_name(self):
        pname = ""
        p = 'flow_node_inventory:name'
        if hasattr(self, p):
            pname = getattr(self, p)
        else:
            assert(False)
        return pname

    def get_mac_address(self):
        pmac = ""
        p = 'flow_node_inventory:hardware_address'
        if hasattr(self, p):
            pmac = getattr(self, p)
        else:
            assert(False)
        return pmac.lower()

    def get_link_state(self):
        state = ""
        p1 = 'flow_node_inventory:state'
        p2 = 'link_down'
        d = self.__dict__
        if (p1 in d and p2 in d[p1]):
            state = "UP" if(d[p1][p2] is False) else "DOWN"
        return state

    def get_forwarding_state(self):
        state = ""
        p1 = 'flow_node_inventory:state'
        p2 = 'blocked'
        d = self.__dict__
        if (p1 in d and p2 in d[p1]):
            state = "FORWARDING" if(d[p1][p2] is False) else "BLOCKED"
        return state

    def get_packets_received(self):
        pkts_cnt = 0
        p1 = 'opendaylight_port_statistics:\
              flow_capable_node_connector_statistics'
        p2 = 'packets'
        d = self.__dict__
        if (p1 in d and p2 in d[p1]):
            p3 = 'received'
            if (p3 in d[p1][p2]):
                pkts_cnt = d[p1][p2][p3]
        return pkts_cnt

    def get_packets_transmitted(self):
        pkts_cnt = 0
        p1 = 'opendaylight_port_statistics:\
             flow_capable_node_connector_statistics'
        p2 = 'packets'
        d = self.__dict__
        if (p1 in d and p2 in d[p1]):
            p3 = 'transmitted'
            if (p3 in d[p1][p2]):
                pkts_cnt = d[p1][p2][p3]
        return pkts_cnt

    def get_bytes_received(self):
        bytes_cnt = 0
        p1 = 'opendaylight_port_statistics:\
              flow_capable_node_connector_statistics'
        p2 = 'bytes'
        d = self.__dict__
        if (p1 in d and p2 in d[p1]):
            p3 = 'received'
            if (p3 in d[p1][p2]):
                bytes_cnt = d[p1][p2][p3]

        return bytes_cnt

    def get_bytes_transmitted(self):
        bytes_cnt = 0
        p1 = 'opendaylight_port_statistics:\
              flow_capable_node_connector_statistics'
        p2 = 'bytes'
        d = self.__dict__
        if (p1 in d and p2 in d[p1]):
            p3 = 'transmitted'
            if (p3 in d[p1][p2]):
                bytes_cnt = d[p1][p2][p3]
        return bytes_cnt

    def get_current_features(self):
        features = []
        p = 'flow_node_inventory:current_feature'
        d = self.__dict__
        if (p in d and isinstance(d[p], basestring)):
            s = d[p].upper().replace('_', '-')
            features = s.split()
        return features


class GroupInfo():
    """ Helper class that represents current state of an OpenFlow
        group entry in the Controller's operational data store
        (OpenFlow switch context specific data)
    """
    def __init__(self, group_info):
        if (isinstance(group_info, dict)):
            d = dict_keys_dashed_to_underscored(group_info)
            for k, v in d.items():
                setattr(self, k, v)
        else:
            raise TypeError("[GroupInfo] wrong argument type '%s'"
                            " (dictionary is expected)" % type(group_info))

    def get_id(self):
        myid = ""
        p = 'group_id'
        if hasattr(self, p):
            myid = getattr(self, p)
        else:
            assert(False)
        return myid


class GroupFeatures():
    """ Helper class that is used to represent group features on the switch
        (group types, max number of groups for each type, group capabilities
        and group supported actions) """
    # mapping of group type names to their numerical values
    # in the OFPGT_* enum
    group_types = {'group-all': 0, 'group-select': 1,
                   'group-indirect': 2, 'group-ff': 3}
    # mapping of group capability names to their bit positions
    # in the OFPGFC_* bitmap
    group_capabilities = {'select-weight': 1, 'select-liveness': 2,
                          'chaining': 4, 'chaining-checks': 8}
    # mapping of bit positions for OFPAT_* action types to
    # the corresponding action names
    actions_bitmap = {
        0: 'OUTPUT',        # Output to switch port
        1: 'SET_VLAN_VID',  # Set the 802.1q VLAN id
        2: 'SET_VLAN_PCP',  # Set the 802.1q priority
        3: 'STRIP_VLAN',    # Strip the 802.1q header
        4: 'SET_DL_SRC',    # Ethernet source address
        5: 'SET_DL_DST',    # Ethernet destination address
        6: 'SET_NW_SRC',    # IP source address
        7: 'SET_NW_DST',    # IP destination address/
        8: 'SET_NW_TOS',    # IP ToS (DSCP field, 6 bits)
        9: 'SET_TP_SRC',    # TCP/UDP source port
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

    def __init__(self, features):
        if (isinstance(features, dict)):
            d = dict_keys_dashed_to_underscored(features)
            for k, v in d.items():
                setattr(self, k, v)
        else:
            raise TypeError("[GroupFeatures] wrong argument type '%s'"
                            " (dictionary is expected)" % type(features))

    def _sort_key_capabilities(self, var):
        return self.group_capabilities.get(var.lower())

    def _sort_key_types(self, var):
        return self.group_types.get(var.lower())

    def get_max_groups(self):
        """ The 'max_groups' field is the maximum number of groups
            for each type of group
        """
        res = None
        p = 'max_groups'
        if hasattr(self, p):
            res = self.max_groups
        return res

    def get_capabilities(self):
        """ The 'capabilities' field uses a combination of the
            following flags:
               OFPGFC_SELECT_WEIGHT   - Support weight for select groups
               OFPGFC_SELECT_LIVENESS - Support liveness for select groups
               OFPGFC_CHAINING        - Support chaining groups
               OFPGFC_CHAINING_CHECKS - Check chaining for loops and delete
        """
        res = None
        p1 = 'group_capabilities_supported'
        if hasattr(self, p1):
            l = self.group_capabilities_supported
            p2 = 'opendaylight-group-types:'
            l1 = [i.encode('ascii', 'ignore').replace(p2, '').upper()
                  for i in l]
            res = sorted(l1, key=self._sort_key_capabilities)
        return res

    def get_types(self):
        """ The 'types' field is a bitmap of group types supported
            by the switch
        """
        res = None
        p1 = 'group_types_supported'
        if hasattr(self, p1):
            l = self.group_types_supported
            p2 = 'opendaylight-group-types:'
            l1 = [i.encode('ascii', 'ignore').replace(p2, '').upper()
                  for i in l]
            res = sorted(l1, key=self._sort_key_types)
        return res

    def get_actions(self):
        """ The 'actions' field is a set of bitmaps of actions supported
            by each group type. The first bitmap applies to the OFPGT_ALL
            group type. The bitmask uses the values from ofp_action_type
            as the number of bits to shift left for an associated action.
            For example, OFPAT_OUTPUT would use the mask 0x00000001
        """
        res = []
        p = 'actions'
        if hasattr(self, p):
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
    def __init__(self, stats):
        if (isinstance(stats, dict)):
            d = dict_keys_dashed_to_underscored(stats)
            for k, v in d.items():
                setattr(self, k, v)
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


class GroupDescription():
    def __init__(self, stats):
        if (isinstance(stats, dict)):
            d = dict_keys_dashed_to_underscored(stats)
            for k, v in d.items():
                setattr(self, k, v)
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

    def get_group_id(self):
        return self.group_id


class NetconfCapableNode():
    ''' Class that represents current state of a NETCONF capable node
        Helper class of the 'Inventory' class '''

    def __init__(self, clazz, inv_json=None, inv_dict=None):
        self.clazz = clazz
        if (inv_dict is not None):
            self.__init_from_dict__(inv_dict)
            return
        if (inv_json is not None):
            self.__init_from_json__(inv_json)
            return

    def __init_from_json__(self, s):
        assert(isinstance(s, basestring))
        obj = json.loads(s)
        d = dict_keys_dashed_to_underscored(obj)
        for k, v in d.items():
            setattr(self, k, v)

    def __init_from_dict__(self, d):
        assert(isinstance(d, dict))
        js = json.dumps(d)
        self.__init_from_json__(js)

    def to_string(self):
        """ Returns string representation of this object. """
        return str(vars(self))

    def to_json(self):
        """ Returns JSON representation of this object. """
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True,
                          indent=4)

    def get_id(self):
        myid = ""
        p = 'id'
        if hasattr(self, p):
            myid = getattr(self, p)
        else:
            assert(False)
        return myid

    def is_connected(self):
        res = None
        p = "netconf_node_inventory:connected"
        if hasattr(self, p):
            res = getattr(self, p)
        else:
            assert(False)
        return res

    def get_conn_status(self):
        status = "CONNECTED" if self.is_connected else "DISCONNECTED"
        return status

    def get_initial_capabilities(self):
        clist = []
        p = 'netconf_node_inventory:initial_capability'
        if hasattr(self, p):
            attr = getattr(self, p)
            assert(isinstance(attr, list))
            for item in attr:
                s = self._capability_str_to_schema_str(item)
                clist.append(s)
        else:
            assert(False)

        return clist

    def get_current_capabilities(self):
        pass

    def _capability_str_to_schema_str(self, capability_str):
        revision = ""
        schema = ""
        s = re.split(r'[(?)]', capability_str)
        for i in range(1, len(s)):
            if i == 2:
                revision = s[i].replace('revision=', '').replace('_', '-')
            elif i == 3:
                schema = s[i].replace('_', '-')

        return "%s@%s.yang" % (schema, revision)


class NetconfConfigModule():
    ''' Class that represents NETCONF node configuration module
        on the Controller '''

    def __init__(self, d):
        assert(isinstance(d, dict))
        p = 'odl-sal-netconf-connector-cfg:'
        js = json.dumps(d)
        obj = json.loads(js.replace(p, ''))
        d1 = dict_keys_dashed_to_underscored(obj)
        for k, v in d1.items():
            setattr(self, k, v)

    def to_string(self):
        """ Returns string representation of this object. """
        return str(vars(self))

    def to_json(self):
        """ Returns JSON representation of this object. """
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True,
                          indent=4)

    def get_name(self):
        name = ""
        p = 'name'
        if hasattr(self, p):
            name = getattr(self, p)
        else:
            assert(False)

        return name

    def get_ip_address(self):
        addr = ""
        p = 'address'
        if hasattr(self, p):
            addr = getattr(self, p)
        else:
            assert(False)

        return addr

    def get_tcp_port(self):
        port = ""
        p = 'port'
        if hasattr(self, p):
            port = getattr(self, p)
        else:
            assert(False)

        return port

    def get_conn_timeout(self):
        timeout = ""
        p = 'connection_timeout_millis'
        if hasattr(self, p):
            timeout = getattr(self, p)
        else:
            assert(False)

        return timeout

    def get_retry_conn_timeout(self):
        timeout = ""
        p = 'between_attempts_timeout_millis'
        if hasattr(self, p):
            timeout = getattr(self, p)
        else:
            assert(False)

        return timeout

    def get_max_conn_attempts(self):
        cnt = ""
        p = 'max_connection_attempts'
        if hasattr(self, p):
            cnt = getattr(self, p)
        else:
            assert(False)

        return cnt

    def get_admin_name(self):
        uname = ""
        p = 'username'
        if hasattr(self, p):
            uname = getattr(self, p)
        else:
            assert(False)

        return uname

    def get_admin_pswd(self):
        pswd = ""
        p = 'password'
        if hasattr(self, p):
            pswd = getattr(self, p)
        else:
            assert(False)

        return pswd
