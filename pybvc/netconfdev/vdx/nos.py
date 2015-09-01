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

@authors: Sergei Garbuzov, Gary Berger
@status: Development
@version: 1.3.1

nos.py: Brocade VDX specific properties and communication methods


"""

import json

from pybvc.controller.netconfnode import NetconfNode
from pybvc.common.result import Result
from pybvc.common.status import OperStatus, STATUS
# from pybvc.netconfdev.vrouter.protocols import StaticRoute


class NOS(NetconfNode):
    """ Class that represents an instance of NOS
        (NETCONF capable server device).
        :param ctrl: :class:`pybvc.controller.controller.Controller`
        :param string name: The name
        :param string ipAddr: The ip address
        :param int portNum: The port number to communicate NETCONF
        :param string adminName:  The username to authenticate setup
                                  of the NETCONF communication
        :param string adminPassword:  The password to authenticate setup
                                      of the NETCONF communication
        :param boolean tcpOnly:  Use TCP only or not.
        :return: The newly created instance.
        :rtype: :class:`pybvc.netconfdev.vdx.nos.NOS'
        """

    def __init__(self, ctrl, name, ip_address, port_number, admin_name,
                 admin_password, tcp_only=False):
        NetconfNode.__init__(self, ctrl. name, ip_address, port_number,
                             admin_name, admin_name, tcp_only)

    def to_string(self):
        """ Returns string representation of this object. """
        return str(vars(self))

    def to_json(self):
        """ Returns JSON representation of this object. """
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True,
                          indent=4)

    def get_schemas(self):
        """ Return a list of YANG model schemas implemented
        :return: A tuple: Status, list of YANG model schemas
        :rtype: instance of the `Result` class (containing JSON listing
                information about the YANG schemas for the node)
        - STATUS.CONN_ERROR: If the controller did not respond. List is empty.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not
                                      provide any status. List is empty.
        - STATUS.OK: Success. List is valid.
        - STATUS.HTTP_ERROR: If the controller responded with an error
                            status code.
        """
        ctrl = self.ctrl
        myname = self.name
        return ctrl.get_schemas(myname)

    def get_schema(self, schema_id, schema_version):
        """Return a YANG model definition for the indicated schema
        :param string schema_id: id of schema
        :param string schema_version: version of the schema
        :return: A tuple: Status, YANG model schema.
        :rtype: instance of the `Result` class (containing YANG schema)
        - STATUS.CONN_ERROR: If the controller did not respond. Schema is
        . empty.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not
        .                             provide any status. Schema is empty.
        - STATUS.OK: Success. Result is valid.
        - STATUS.DATA_NOT_FOUND: Data missing or in unexpected format.
        - STATUS.HTTP_ERROR: If the controller responded with an error
                             status code.
        """
        ctrl = self.ctrl
        myname = self.name
        return ctrl.get_schema(myname, schema_id, schema_version)

    def get_cfg(self):
        """Return configuration
        :return: A tuple: Status, JSON for configuration.
        :rtype: instance of the `Result` class (containing configuration data)
        - STATUS.CONN_ERROR: If the controller did not respond.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not
                                      provide any status.
        - STATUS.OK: Success. Result is valid.
        - STATUS.HTTP_ERROR: If the controller responded with an error
                             status code.
        """
        status = OperStatus()
        cfg = None
        ctrl = self.ctrl
        myname = self.name
        url = ctrl.get_ext_mount_config_url(myname)
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            cfg = resp.content
            status.set_status(STATUS.OK)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return Result(status, cfg)


def get_interfaces_list(self):
        """ Get the list of interfaces on the VRouter5600.
        :return: A tuple: Status, list of interface names.
        :rtype: instance of the `Result` class
        - STATUS.CONN_ERROR: If the controller did not respond.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not
                                      provide any status.
        - STATUS.OK:  Success. Result is valid.
        - STATUS.HTTP_ERROR: If the controller responded with an error
                             status code.
        """
        ifList = []
        result = self.get_interfaces_cfg()
        status = result.get_status()
        if(status.eq(STATUS.OK)):
            cfg = result.get_data()
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
        return Result(status, ifList)


def get_interfaces_cfg(self):
        """ Return the configuration for the interfaces on the VRouter5600
        :return: A tuple: Status, configuration of the interfaces
        :rtype: instance of the `Result` class (containing configuration data)
        - STATUS.CONN_ERROR: If the controller did not respond.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not
                                      provide any status.
        - STATUS.OK:  Success. Result is valid.
        - STATUS.HTTP_ERROR: If the controller responded with an error
                             status code.
        """
        status = OperStatus()
        cfg = None
        templateModelRef = "brocade-interface:interface"
        modelref = templateModelRef
        ctrl = self.ctrl
        url = ctrl.get_ext_mount_config_url(self.name)
        url += modelref
        resp = ctrl.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            cfg = resp.content
            status.set_status(STATUS.OK)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return Result(status, cfg)
