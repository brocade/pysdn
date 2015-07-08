"""
Copyright (c) 2015

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
 - Redistributions of source code must retain the above copyright notice,
   this list of conditions and the following disclaimer.
-  Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.
-  Neither the name of the copyright holder nor the names of its contributors
   may be used to endorse or promote products derived from this software
   without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOS EARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES;LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

@authors: Sergei Garbuzov
@status: Development
@version: 1.1.0

notification.py: Parser for notification events received from Controller


"""

import os
import re
import string
import xmltodict

yang_namespace_to_prefix_map = {
    'urn:opendaylight:model:topology:inventory' : 'nt1',
    'urn:TBD:params:xml:ns:yang:network-topology' : 'nt2',
    'urn:opendaylight:inventory' : 'inv',
    'urn:opendaylight:flow:inventory' : 'flownode',
    'urn:opendaylight:host-tracker' : 'host-track',
}

def yang_nsname_to_prefix(nsname):
    if nsname in yang_namespace_to_prefix_map:
        return yang_namespace_to_prefix_map[nsname]
    else:
        return nsname

def yang_prefix_to_nsname(prefix):
    for k, v in yang_namespace_to_prefix_map:
        if v == prefix:
            return k
    
    return prefix

#-------------------------------------------------------------------------------
# Class 'NetworkTopologyChangeNotification'
#-------------------------------------------------------------------------------
class NetworkTopologyChangeNotification():
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, event):
        d = xmltodict.parse(event)
        try:
            p1 = 'notification'
            notification = d[p1]
            
            p2 = 'eventTime'
            self.timestamp = notification[p2]
            
            self.events = []
            p3 = 'data-changed-notification'
            p4 = 'data-change-event'
            events = notification[p3][p4]
            if isinstance(events, list):
                for item in events:
                    tc_evt = TopoChangeEvent(item)
                    self.events.append(tc_evt)
            elif isinstance(events, dict):
                tc_evt = TopoChangeEvent(events)
                self.events.append(tc_evt)
            else:
                assert(False), "TBD data=%s, type=%s" % (events, type(events))
            
            self.added_switches = []
            self.removed_switches = []
            self.added_hosts = []
            self.removed_hosts = []
            
            self.added_links = []
            self.removed_links = []
            
            for event in self.events:
                if event.created():
                    if event.is_switch():
                        self.added_switches.append(event.get_node_id())
                    elif event.is_host():
                        self.added_hosts.append(event.get_node_id())
                    elif event.is_link():
                        self.added_links.append(event.get_link_id())
                elif event.deleted():
                    if event.is_switch():
                        self.removed_switches.append(event.get_node_id())
                    elif event.is_host():
                        self.removed_hosts.append(event.get_node_id())
                    elif event.is_link():
                        self.removed_links.append(event.get_link_id())
        except() as e:
            assert(False)
            print "Error, %s" % e
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_time(self):
        return self.timestamp
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def switches_added(self):
        return self.added_switches
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def switches_removed(self):
        return self.removed_switches
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def hosts_added(self):
        return self.added_hosts 
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def hosts_removed(self):
        return self.removed_hosts
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def links_added(self):
        return self.added_links
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def links_removed(self):
        return self.removed_links
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def print_events(self):
        for event in self.events:
            if event.is_link():
                print "\n".strip()
                event.do_print()
                print "\n".strip()
            else:
                print "\n".strip()
                event.do_print()
                print "\n".strip()
    
#-------------------------------------------------------------------------------
# Class 'TopoChangeEvent'
#-------------------------------------------------------------------------------
class TopoChangeEvent():
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, event):
        p = 'path'
        if isinstance(event, dict):
            for k,v in event.items():
                if k == p:
                    self.path_info = PathInfo(v)
                else:
                    setattr(self, k, v)
        else:
            assert (False), " TBD evt=%s, type=%s" % (event, type(event))
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def created(self):
        res = False
        p = 'operation'
        if hasattr(self, p):
            attr = getattr(self, p)
            res = (attr == 'created')
            
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def deleted(self):
        res = False
        p = 'operation'
        if hasattr(self, p):
            attr = getattr(self, p)
            res = (attr == 'deleted')
            
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def updated(self):
        res = False
        p = 'operation'
        if hasattr(self, p):
            attr = getattr(self, p)
            res = (attr == 'updated')
            
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_path(self):
        path = None
        p = 'path'
        if hasattr(self, p):
            p3 = '#text'
            attr = getattr(self, p)
            path = attr[p3]
            
        return path
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def is_node(self):
        res = False
        p = 'path_info'
        if hasattr(self, p):
            path = self.path_info.path
            basename = os.path.basename(path)
            if basename:
                p1 = '.*node-id$'
                r = re.search(p1, basename)
                if r != None:
                    res = True
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def is_switch(self):
        res = False
        if self.is_node():
            node_id = self.get_node_id()
            if node_id and node_id.startswith('openflow'):
                res = True
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def is_host(self):
        res = False
        if self.is_node():
            node_id = self.get_node_id()
            if node_id and node_id.startswith('host'):
                res = True
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_node_id(self):
        node_id = None
        p = 'path_info'
        if hasattr(self, p):
            path = self.path_info.path
            chunks = repr(path).split(']')
            if chunks:
                p = 'node-id='
                for s in chunks:
                    idx = s.find(p)
                    if(idx >= 0):
                        node_id = s[idx + len(p):].translate(None , "[]'\"")
                        break
            
        return node_id
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def is_link(self):
        res = False
        p = 'path_info'
        if hasattr(self, p):
            path = self.path_info.path
            basename = os.path.basename(path)
            if basename:
                p1 = '.*link-id$'
                r = re.search(p1, basename)
                if r != None:
                    res = True
        
        return res
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_link_id(self):
        link_id = None
        p = 'path_info'
        if hasattr(self, p):
            path = self.path_info.path
            chunks = repr(path).split(']')
            if chunks:
                p = 'link-id='
                for s in chunks:
                    idx = s.find(p)
                    if(idx >= 0):
                        link_id = s[idx + len(p):].translate(None , "[]'\"")
                        break
        
        return link_id
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def do_print(self):
        print " <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<"
        print " operation: %s" % self.operation
        self.path_info.do_print()
        print " >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"

#-------------------------------------------------------------------------------
# Class 'PathInfo'
#-------------------------------------------------------------------------------
class PathInfo():
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, info):
        if isinstance(info, dict):
            p1 = '#text'
            p2 = '@xmlns'
            try:
                path = info[p1]
                namespaces = []
                for k, v in info.items():
                    if k.startswith(p2):
                        pfx = yang_nsname_to_prefix(v)
                        d = {'ns': v, 'pfx': pfx}
                        namespaces.append(d)
                        nickname = k.split(':')[-1]
                        path = string.replace(path, nickname, pfx)
                
                self.namespaces = namespaces
                self.path = path
            except:
                print "Error, unexpected data format"
        else:
            assert (False), " TBD evt=%s, type=%s" % (info, type(info))
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def do_print(self):
        for ns in self.namespaces:
            print " namespace: %s (prefix: %s)" % (ns['ns'], ns['pfx'])
        print " path: %s" % self.path
