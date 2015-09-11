
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

netconfnode.py: Controller's NETCONF node specific properties


"""

import json


class NetconfNode(object):
    """ Class that represents a NETCONF capable server device.

        :param controller: :class:`pybvc.controller.controller.Controller`
        :param string nodeName: The name of the node
        :param string ipAddr:  The ip address for the netconf device
        :param int portNum:  The port number to communicate NETCONF to the
           device
        :param string adminName:  The username to authenticate setup of the
         NETCONF communication
        :param string adminPassword:  The password to authenticate setup of
         the NETCONF communication
        :param boolean tcpOnly:  Use TCP only or not.
        :return: The newly created NetconfNode instance.
        :rtype: :class:`pybvc.controller.netconfnode.NetconfNode`
    """

    def __init__(self, controller=None, nodeName=None, ipAddr=None,
                 portNum=None,
                 adminName=None, adminPassword=None, tcpOnly=False):
        """ Initializes this object properties. """
        self.ctrl = controller
        self.name = nodeName
        self.ipAddr = ipAddr
        self.tcpOnly = tcpOnly
        self.portNum = portNum
        self.adminName = adminName
        self.adminPassword = adminPassword

    def to_string(self):
        """ Returns string representation of this object. """
        return str(vars(self))

    def to_json(self):
        """ Returns JSON representation of this object. """
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4)
