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

@status: Development
@version: 1.3.1

nos.py: Brocade VDX specific properties and communication methods


"""

import json

from pysdn.controller.netconfnode import NetconfNode
from pysdn.common.result import Result
from pysdn.common.status import OperStatus, STATUS


class NOS(object):
    """ Class that represents an instance of NOS
        (NETCONF capable server device).
        :rtype: :class:`pysdn.netconfdev.vdx.nos.NOS'
        """

    def to_string(self):
        """ Returns string representation of this object. """
        return str(vars(self))

    def to_json(self):
        """ Returns JSON representation of this object. """
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True,
                          indent=4)
    @staticmethod
    def get_portprofile(session, name):
        """
        Return port profiles
        """
        status = OperStatus()
        cfg = None
        templateModelRef = "brocade-port-profile:port-profile-global"
        modelref = templateModelRef
        url = session.get_ext_mount_config_url(name)
        url += modelref
        resp = session.http_get_request(url, data=None, headers=None)
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

    @staticmethod
    def get_syslog(session, name):
        """
        Return Syslog Configuration
        """
        status = OperStatus()
        cfg = None
        templateModelRef = "brocade-ras:logging"
        modelref = templateModelRef
        url = session.get_ext_mount_config_url(name)
        url += modelref
        resp = session.http_get_request(url, data=None, headers=None)
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

    @staticmethod
    def get_schemas(session, name):
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
        return session.get_schemas(name)

    @staticmethod
    def get_schema(session, name, schema_id, schema_version):
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
        return session.get_schema(name, schema_id, schema_version)

    @staticmethod
    def get_cfg(session, name):
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
        url = session.get_ext_mount_config_url(name)
        resp = session.http_get_request(url, data=None, headers=None)
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

    @staticmethod
    def get_interfaces_list(session,timeout=None):
            """ Get the list of interfaces on the VDX.
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
            result = NOS.get_interfaces_cfg(session, timeout)
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

    @staticmethod
    def get_interfaces_cfg(session, name, timeout=20):
            """ Return the configuration for the interfaces on VDX
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
            url = session.get_ext_mount_config_url(name)
            url += modelref
            resp = session.http_get_request(url, data=None, headers=None, timeout=timeout)
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

    @staticmethod
    def get_vlan(session, name, vlanid, timeout=20):
        """
        Get VLAN
        """
        status = OperStatus()
        headers = {'content-type': 'application/yang.data+json'}
        cfg = None
        templateModelRef = "brocade-interface:interface-vlan/interface/vlan/{}".format(vlanid)
        modelref = templateModelRef
        url = session.get_ext_mount_config_url(name)
        url += modelref
        resp = session.http_get_request(url, None, headers=headers, timeout=None)
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

    @staticmethod
    def create_vlan(session, name, vlanid, timeout=20):
        """
        Create VLAN
        """
        status = OperStatus()
        headers = {'content-type': 'application/yang.data+json'}
        cfg = None
        templateModelRef = "brocade-interface:interface-vlan/interface"
        modelref = templateModelRef
        url = session.get_ext_mount_config_url(name)
        url += modelref
        payload = {"vlan": {"name": vlanid}}
        resp = session.http_post_request(url, json.dumps(payload), headers=headers, timeout=None)
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

    @staticmethod
    def delete_vlan(session, name, vlanid, timeout=20):
        """
        Create VLAN
        """
        status = OperStatus()
        headers = {'content-type': 'application/yang.data+json'}
        cfg = None
        templateModelRef = "brocade-interface:interface-vlan/interface/vlan/{}".format(vlanid)
        modelref = templateModelRef
        url = session.get_ext_mount_config_url(name)
        url += modelref
        resp = session.http_delete_request(url, data=None, headers=headers)

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


