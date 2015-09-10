
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

protocols.py: Protocols specific properties and access methods


"""

import json

from pybvc.common.utils import (strip_none,
                                remove_empty_from_dict,
                                dict_keys_underscored_to_dashed)


class StaticRoute():
    ''' Class representing static route parameters '''
    _mn1 = "vyatta-protocols:protocols"
    _mn2 = "vyatta-protocols-static:static"

    def __init__(self):
        ''' Static ARP translation (list) '''
        self.arp = []

        ''' Interface based static route '''
        self.interface_route = []

        ''' Interface based IPv6 static route (list) '''
        self.interface_route6 = []

        ''' Static route (list) '''
        self.route = []

        ''' Static IPv6 route (list) '''
        self.route6 = []

        ''' Policy route table (range 1..128) (list) '''
        self.table = []

    def to_string(self):
        """ Return this object as a string """
        return str(vars(self))

    def to_json(self):
        """ Return this object as JSON """
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True,
                          indent=4)

    def get_payload(self):
        s = self.to_json()
        obj = json.loads(s)
        obj1 = strip_none(obj)
        obj2 = remove_empty_from_dict(obj1)
        obj3 = dict_keys_underscored_to_dashed(obj2)
        payload = {self._mn2: obj3}
        return json.dumps(payload, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def get_url_extension(self):
        s = ("%s/%s") % (self._mn1, self._mn2)
        return s

    def set_interface_route(self, ip_prefix):
        route = self._find_create_interface_route(ip_prefix)
        assert (isinstance(route, InterfaceRoute))
        return route

    def set_interface_route_next_hop_interface(self, ip_prefix, if_name,
                                               disable=None, distance=None):
        route = self._find_create_interface_route(ip_prefix)
        assert (isinstance(route, InterfaceRoute))
        route.set_next_hop_interface(if_name, disable, distance)

    def _find_create_interface_route(self, ip_prefix):
        route = None
        for item in self.interface_route:
            if (item.tagnode == ip_prefix):
                route = item
                break

        if (route is None):
            route = InterfaceRoute(ip_prefix)
            self.interface_route.append(route)
        return route


class InterfaceRoute():
    ''' Helper sub-class of the 'Static' class
        Interface based static route '''

    def __init__(self, ip_prefix):
        ''' IPv4 Prefix '''
        self.tagnode = ip_prefix
        ''' Next-hop interfaces '''
        self.next_hop_interface = []

    def set_next_hop_interface(self, ifName, disable=None, distance=None):
        next_hop = self._find_create_next_hop_interface(ifName)
        assert (isinstance(next_hop, NextHopInterface))
        if (disable is not None):
            next_hop.set_disable(disable)
        if (distance is not None):
            next_hop.set_distance(distance)

    def disable_next_hop_interface(self, ifName):
        next_hop = self._find_create_next_hop_interface(ifName)
        assert (isinstance(next_hop, NextHopInterface))
        next_hop.set_disable(True)

    def enable_next_hop_interface(self, ifName):
        next_hop = self._find_create_next_hop_interface(ifName)
        assert (isinstance(next_hop, NextHopInterface))
        next_hop.set_disable(False)

    def set_next_hop_interface_distance(self, ifName, distance):
        next_hop = self._find_create_next_hop_interface(ifName)
        assert (isinstance(next_hop, NextHopInterface))
        next_hop.set_distance(distance)

    def _find_create_next_hop_interface(self, ifName):
        next_hop = None
        for item in self.next_hop_interface:
            if (item.tagnode == ifName):
                next_hop = item
                break
        if (next_hop is None):
            next_hop = NextHopInterface(ifName)
            self.next_hop_interface.append(next_hop)
        return next_hop


class NextHopInterface():
    ''' Helper sub-class of the 'InterfaceRoute' class
        Next-hop interface '''

    def __init__(self, name):
        ''' Interface name '''
        self.tagnode = name
        ''' Disable IPv4 interface static route '''
        self.disable = None
        ''' Distance value for this route (range 1..255) '''
        self.distance = None

    def set_disable(self, value):
        if (value):
            self.disable = ""
        else:
            self.disable = None

    def set_distance(self, value):
        self.distance = value
