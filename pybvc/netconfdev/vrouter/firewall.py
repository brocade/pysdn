
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

firewall.py: Firewall specific properties and access methods


"""

import json
import urllib2

from pybvc.common.utils import remove_empty_from_dict


class Firewall():
    """ A class that defines a Firewall. """
    _mn1 = "vyatta-security:security"
    _mn2 = "vyatta-security-firewall:firewall"
    _mn3 = "vyatta-security-firewall:name"

    def __init__(self, name):
        self.tagnode = name
        self.default_action = None
        self.default_log = None
        self.description = None
        self.rule = []

    def to_string(self):
        """ Return Firewall as a string """
        return str(vars(self))

    def to_json(self):
        """ Return Firewall as JSON """
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True,
                          indent=4)

    def get_payload(self):
        s = self.to_json()
        s = s.replace('typename', 'type-name')
        d1 = json.loads(s)
        d2 = remove_empty_from_dict(d1)
        payload = {self._mn3: d2}
        return json.dumps(payload, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def get_url_extension(self):
        s = ("%s/%s/name/%s" %
             (self._mn1, self._mn2, urllib2.quote(self.tagnode)))
        return s

    def add_rule(self, rule):
        """ Add a rule to Firewall.
        :param rule: Rule to be added to Firewall.
                    :class:`pybvc.netconfdev.vrouter.vrouter5600.Rule`
        """
        assert isinstance(rule, Rule)
        self.rule.append(rule)

    def get_rules(self):
        """Return the Rules of a Firewall
        :return: Rules of the Firewall
        :rtype: :class:`pybvc.netconfdev.vrouter.vrouter5600.Rules`
        """
        rules = []
        for item in self.rule:
            rules.append(item)
        return rules


class Rule():
    """The class that defines a Rule.
    :param int number: The number for the Rule.
    """

    def __init__(self, number):
        self.tagnode = number
        self.source = Object()
        self.icmp = Object()

    def to_string(self):
        """ Return Rule as string """
        return str(vars(self))

    def to_json(self):
        """ Return Rule as JSON """
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True,
                          indent=4)

    def add_action(self, action):
        """Add an action to the Rule.
        :param string action: The action to be taken for the Rule:  accept,
               drop
        :return: No return value
        """
        self.action = action

    def add_source_address(self, srcAddr):
        """Add source address to Rule. If the packet matches this then the
           action is taken.
        :param string srcAddr: The IP address to match against the source IP
           of packet.
        :return: No return value
        """
        self.source.address = srcAddr

    def add_icmp_typename(self, typeName):
        """Add typename for ICMP to Rule.  If the packet matches this then the
           action is taken.
        :param string typeName: The ICMP type name to test packet against.
        :return: No return value.
        """
        self.protocol = "icmp"
        self.icmp.typename = typeName


class DataplaneInterfaceFirewall():
    _mn1 = "vyatta-interfaces:interfaces"
    _mn2 = "vyatta-interfaces-dataplane:dataplane"
    _mn3 = "vyatta-security-firewall:firewall"

    def __init__(self, ifName):
        ''' Interface name '''
        self.tagnode = ifName
        ''' Firewall options '''
        self.firewall = DataplaneInterfaceFirewallOptions()

    def add_in_policy(self, policy_name):
        self.firewall.add_in_policy(policy_name)

    def add_out_policy(self, policy_name):
        self.firewall.add_out_policy(policy_name)

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)

    def get_url_extension(self):
        return (self._mn1 + "/" + self._mn2 + "/" +
                self.tagnode + "/" + self._mn3)

    def get_name(self):
        return self.tagnode

    def get_payload(self):
        s = self.firewall.to_json()
        s = s.replace('inlist', "in")
        s = s.replace('outlist', "out")
        payload = {self._mn3: json.loads(s)}
        return json.dumps(payload, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


class DataplaneInterfaceFirewallOptions():
    ''' Class representing Firewall options (inbound/outbound forwarding rules)
        Helper class of the 'DataplaneInterfaceFirewall' class '''

    def __init__(self):
        ''' Inbound forwarding rules '''
        self.inlist = []
        ''' Outbound forwarding rules '''
        self.outlist = []

    def add_in_policy(self, policy_name):
        self.inlist.append(policy_name)

    def add_out_policy(self, policy_name):
        self.outlist.append(policy_name)

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)


class Object():
    pass
