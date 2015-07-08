import string
import json

from pybvc.common.utils import dict_keys_dashed_to_underscored

#-------------------------------------------------------------------------------
# Class 'Topology'
#-------------------------------------------------------------------------------
class Topology():
    """ Class that represents Controller's view on a Network Topology instance.
    """
    def __init__(self, topo_json=None, topo_dict=None):
        self.topology_id = None
        self.nodes = []
        self.links = []
        self.switches = []
        self.hosts = []
        
        assert_msg = "[Topology] either '%s' or '%s' should be used, " \
                     "not both" % ('topo_json', 'topo_dict')
        assert(((topo_json != None) and (topo_dict != None)) == False), assert_msg
        if (topo_dict != None):
            self.__init_from_dict__(topo_dict)
            return
        
        if (topo_json != None):
            self.__init_from_json__(topo_json)
            return
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init_from_json__(self, s):
        if (isinstance(s, basestring)):
            obj = json.loads(s)
            d = dict_keys_dashed_to_underscored(obj)
            for k, v in d.items():
                if ('topology_id' == k):
                    self.topology_id = v
                elif ('node' == k):
                    if (isinstance(v, list)):
                        for i in v:
                            node = Node(i)
                            self.add_node(node)
                elif ('link' == k):
                    if (isinstance(v, list)):
                        for i in v:
                            link = Link(i)
                            self.add_link(link)
                else:
                    assert(False)
        else:
            raise TypeError("[Topology] wrong argument type '%s'"
                            " (JSON 'string' is expected)" % type(s))
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init_from_dict__(self, d):
        if (isinstance(d, dict)):
            js = json.dumps(d)
            self.__init_from_json__(js)
        else:
            raise TypeError("[Topology] wrong argument type '%s'"
                            " ('dict' is expected)" % type(d))
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def to_string(self):
        """ Returns string representation of this object. """
        return str(vars(self))
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def add_node(self, node):
        assert(isinstance(node, Node))
        self.nodes.append(node)
        if (node.is_switch()):
            self.switches.append(node)
        elif (node.is_host()):
            self.hosts.append(node)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def add_link(self, link):
        assert(isinstance(link, Link))
        self.links.append(link)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_id(self):
        return self.topology_id
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_switch_ids(self):
        snames = []
        for n in self.nodes:
            if (n.is_switch()):
                snames.append(n.node_id)
        
        return sorted(snames)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_host_ids(self):
        snames = []
        for n in self.nodes:
            if (n.is_host()):
                snames.append(n.node_id)
        
        return sorted(snames)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_switches_cnt(self):
        return len(self.switches)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_hosts_cnt(self):
        return len(self.hosts)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_inter_switch_links_cnt(self):
        cnt = 0
        for l in self.links:
            if(l.is_switch_to_switch()):
                cnt += 1
        
        assert(cnt%2 == 0)
        return cnt/2
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_nodes(self):
        return self.nodes
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_switches(self):
        return sorted(self.switches, key=lambda n: n.get_id())
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_switch(self, switch_id):
        for item in self.switches:
            if(item.get_id() == switch_id):
                return item
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_hosts(self):
        return self.hosts
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_peer_list_for_node(self, node):
        plist = []
        print node.get_id()
        for link in self.links:
            if(link.is_dst_node(node)):
                plist.append(link)
        
        return plist
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_peer_list_for_node_port_(self, node, pnum):
        plist = []
        for link in self.links:
            if(link.is_dst_node_port(node, pnum)):
                src_node_id = link.get_src_node_id()
                if(src_node_id):
                    src_node = self.get_node_by_id(src_node_id)
                    if(src_node):
                        plist.append(src_node)
        
        return plist
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_node_by_id(self, node_id):
        node = None
        for item in self.nodes:
            if item.get_id() == node_id:
                node = item
                break
        
        return node

#-------------------------------------------------------------------------------
# Class 'Node'
#-------------------------------------------------------------------------------
class Node():
    """ A node in the topology instance.
        Helper class of the 'Topology' class """
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, d):
        assert(isinstance(d, dict))
        for k, v in d.items():
            setattr(self, k, v)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def to_string(self):
        """ Returns string representation of this object. """
        return str(vars(self))
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def to_json(self):
        """ Returns JSON representation of this object. """
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def is_switch(self):
        p1 = 'openflow'
        return self.node_id.startswith(p1)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def is_host(self):
        p1 = 'host'
        return self.node_id.startswith(p1)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_type_str(self):
        type_str = ""
        if(self.is_host()):
            type_str = "host"
        elif (self.is_switch()):
            type_str = "switch"
        else:
            assert(False)
        
        return type_str
        
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_id(self):
        return self.node_id
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_port_numbers(self):
        pnums = []
        if self.is_switch():
            p1 = 'termination_point'
            p2 = 'tp_id'
            if hasattr(self, p1):
                tplist =  getattr(self, p1)
                assert(isinstance(tplist, list))
                for item in tplist:
                    if isinstance(item, dict) and p2 in item:
                        s = self.get_id() + ":"
                        pnum = item[p2].replace(s, '')
                        pnums.append(pnum)
        
        return sorted(pnums)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_mac_address(self):
        mac_addr = None
        p = 'host_tracker_service:id'
        if(hasattr(self, p)):
            mac_addr = getattr(self, p)
        
        return mac_addr
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_ip_address_for_mac(self, mac_addr):
        ip_addr = None
        p1 = 'host_tracker_service:addresses'
        p2 = 'mac'
        p3 = 'ip'
        if(hasattr(self, p1)):
            attr = getattr(self, p1)
            if(isinstance(attr, list)):
                for item in attr:
                    if isinstance(item, dict) and p2 in item and p3 in item:
                        if (item[p2] == mac_addr):
                            ip_addr = item[p3]
                            break
        
        return ip_addr
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_openflow_id(self):
        if self.is_switch():
            return self.get_id()
        else:
            return None

#-------------------------------------------------------------------------------
# Class 'TerminationPoint'
#-------------------------------------------------------------------------------
class Link():
    """ A link in the topology instance.
        Helper class of the 'Topology' class """
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, d):
        assert(isinstance(d, dict))
        for k, v in d.items():
            setattr(self, k, v)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def to_string(self):
        """ Returns string representation of this object. """
        return str(vars(self))
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def is_switch_to_switch(self):
        res = False
        src_node = self.source['source_node']
        dst_node = self.destination['dest_node']
        if(src_node.startswith('openflow') and dst_node.startswith('openflow') and src_node != dst_node):
            res = True
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def is_loopback(self):
        res = False
        src_node = self.source['source_node']
        dst_node = self.destination['dest_node']
        if(src_node.startswith('openflow') and dst_node.startswith('openflow') and src_node == dst_node):
            res = True
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def is_host_to_switch(self):
        res = False
        src_node = self.source['source_node']
        dst_node = self.destination['dest_node']
        if(src_node.startswith('host') and dst_node.startswith('openflow')):
            res = True
        
        return res
        
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def is_switch_to_host(self):
        res = False
        src_node = self.source['source_node']
        dst_node = self.destination['dest_node']
        if(src_node.startswith('openflow') and dst_node.startswith('host')):
            res = True
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def is_dst_node(self, node):
        res = False
        p1 = 'destination'
        p2 = 'dest_node'
        if(hasattr(self, p1)):
            dst = getattr(self, p1)
            if(p2 in dst and dst[p2] == node.get_id()):
                res = True
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def is_dst_node_port(self, node, pnum):
        res = False
        p1 = 'destination'
        p2 = 'dest_node'
        p3 = 'dest_tp'
        if(hasattr(self, p1)):
            attr = getattr(self, p1)
            if(p2 in attr and p3 in attr):
                node_id = node.get_id()
                tp_id = node_id  + ":" + pnum
                res = (attr[p2] == node_id and attr[p3] == tp_id)
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_src_node_id(self):
        src_node_id = None
        p1 = 'source'
        p2 = 'source_node'
        if(hasattr(self, p1)):
            attr = getattr(self, p1)
            if(isinstance(attr, dict) and p2 in attr):
                src_node_id = attr[p2]
        
        return src_node_id
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_id(self):
        p = 'link_id'
        if(hasattr(self, p)):
            return getattr(self, p)
        else:
            assert(0)

