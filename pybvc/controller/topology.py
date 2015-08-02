import string
import json


#-------------------------------------------------------------------------------
# Class 'Topology'
#-------------------------------------------------------------------------------
class Topology():
    """ Class that represents Controller's view on a Network Topology instance.
    """
    def __init__(self, topo_json=None, topo_dict=None):
        self.topology_id = None
        self.node = []
        self.link = []
        
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
            js = string.replace(s, '-', '_')
            d = json.loads(js)
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
        self.node.append(node)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def add_link(self, link):
        assert(isinstance(link, Link))
        self.link.append(link)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_id(self):
        return self.topology_id
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_switch_names(self):
        snames = []
        for n in self.node:
            if (n.is_switch()):
                snames.append(n.node_id)
        
        return sorted(snames)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_host_names(self):
        snames = []
        for n in self.node:
            if (n.is_host()):
                snames.append(n.node_id)
        
        return sorted(snames)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_switches_cnt(self):
        cnt = 0
        for n in self.node:
            if (n.is_switch()):
                cnt += 1
        
        return cnt
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_hosts_cnt(self):
        cnt = 0
        for n in self.node:
            if (n.is_host()):
                cnt += 1
        
        return cnt
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_inter_switch_links_cnt(self):
        cnt = 0
        for l in self.link:
            if(l.is_switch_to_switch()):
                cnt += 1
        
        assert(cnt%2 == 0)
        return cnt/2

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
    def is_switch(self):
        p1 = 'openflow'
        return self.node_id.startswith(p1)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def is_host(self):
        p1 = 'host'
        return self.node_id.startswith(p1)

#-------------------------------------------------------------------------------
# Class 'Address'
#-------------------------------------------------------------------------------
class Address():
    """ Address information of the node.
        Helper class of the 'Node' class """
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self):
        self.id = None
        self.mac = None
        self.ip = None
        self.first_seen = None
        self.last_seen = None

#-------------------------------------------------------------------------------
# Class 'AttachmentPoint'
#-------------------------------------------------------------------------------
class AttachmentPoint():
    """ Node's link attachment point information.
        Helper class of the 'Node' class """
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self):
        self.tp_id = None
        self.active = None
        self.corresponding_tp= None
    
#-------------------------------------------------------------------------------
# Class 'TerminationPoint'
#-------------------------------------------------------------------------------
class TerminationPoint():
    """ Node's link termination point information.
        Helper class of the 'Node' class """
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self):
        self.tp_id = None

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

