
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

controller.py: Controller's properties and communication methods


"""

import json
import xmltodict
import requests

from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError, Timeout
from pybvc.common.result import Result
from pybvc.common.status import OperStatus, STATUS
from pybvc.common.utils import (find_key_values_in_dict,
                                dbg_print,
                                find_key_value_in_dict)
from pybvc.controller.topology import Topology
from pybvc.controller.inventory import (Inventory,
                                        OpenFlowCapableNode,
                                        NetconfCapableNode,
                                        NetconfConfigModule)


class Controller():
    """ Class that represents a Controller device. """
    def __init__(self, ipAddr, portNum, adminName, adminPassword, timeout=5):
        """Initializes this object properties."""
        self.ipAddr = ipAddr
        self.portNum = portNum
        self.adminName = adminName
        self.adminPassword = adminPassword
        self.timeout = timeout

    def to_string(self):
        """ Returns string representation of this object. """
        return str(vars(self))

    def to_json(self):
        """ Returns JSON representation of this object. """
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True,
                          indent=4)

    def brief_json(self):
        """ Returns JSON representation of this object (brief info). """
        d = {'ipAddr': self.ipAddr,
             'portNum': self.portNum,
             'adminName': self.adminName,
             'adminPassword': self.adminPassword}
        return json.dumps(d, default=lambda o: o.__dict__, sort_keys=True,
                          indent=4)

    def http_get_request(self, url, data, headers, timeout=None):
        """ Sends HTTP GET request to a remote server
            and returns the response.

        :param string url: The complete url including protocol:
                           http://www.example.com/path/to/resource
        :param string data: The data to include in the body of the request.
                            Typically set to None.
        :param dict headers: The headers to include in the request.
        :param string timeout: Pass a timeout for longlived queries
        :return: The response from the http request.
        :rtype: None or `requests.response`
            <http://docs.python-requests.org/en/latest/api/#requests.Response>

        """

        resp = None
        if timeout is None:
            timeout = self.timeout

        try:
            resp = requests.get(url,
                                auth=HTTPBasicAuth(self.adminName,
                                                   self.adminPassword),
                                data=data, headers=headers, timeout=timeout)
        except (ConnectionError, Timeout) as e:
            print "Error: " + repr(e)

        return (resp)

    def http_post_request(self, url, data, headers):
        """ Sends HTTP POST request to a remote server
            and returns the response.

        :param string url: The complete url including protocol:
                           http://www.example.com/path/to/resource
        :param string data: The data to include in the body of the request.
                            Typically set to None.
        :param dict headers: The headers to include in the request.
        :return: The response from the http request.
        :rtype: None or `requests.response`
            <http://docs.python-requests.org/en/latest/api/#requests.Response>

        """

        resp = None

        try:
            resp = requests.post(url,
                                 auth=HTTPBasicAuth(self.adminName,
                                                    self.adminPassword),
                                 data=data, headers=headers,
                                 timeout=self.timeout)
        except (ConnectionError, Timeout) as e:
            print "Error: " + repr(e)

        return (resp)

    def http_put_request(self, url, data, headers):
        """ Sends HTTP PUT request to a remote server
            and returns the response.

        :param string url: The complete url including protocol:
                           http://www.example.com/path/to/resource
        :param string data: The data to include in the body of the request.
                            Typically set to None.
        :param dict headers: The headers to include in the request.
        :return: The response from the http request.
        :rtype: None or `requests.response`
            <http://docs.python-requests.org/en/latest/api/#requests.Response>

        """

        resp = None

        try:
            resp = requests.put(url,
                                auth=HTTPBasicAuth(self.adminName,
                                                   self.adminPassword),
                                data=data, headers=headers,
                                timeout=self.timeout)
        except (ConnectionError, Timeout) as e:
            print "Error: " + repr(e)

        return (resp)

    def http_delete_request(self, url, data, headers):
        """ Sends HTTP DELETE request to a remote server
            and returns the response.

        :param string url: The complete url including protocol:
                           http://www.example.com/path/to/resource
        :param string data: The data to include in the body of the request.
                            Typically set to None.
        :param dict headers: The headers to include in the request.
        :return: The response from the http request.
        :rtype: None or `requests.response`
            <http://docs.python-requests.org/en/latest/api/#requests.Response>

        """
        resp = None

        try:
            resp = requests.delete(url,
                                   auth=HTTPBasicAuth(self.adminName,
                                                      self.adminPassword),
                                   data=data, headers=headers,
                                   timeout=self.timeout)
        except (ConnectionError, Timeout) as e:
            print "Error: " + repr(e)

        return (resp)

    def get_nodes_operational_list(self):
        status = OperStatus()
        templateUrl = ("http://{}:{}/restconf/operational/"
                       "opendaylight-inventory:nodes")
        url = templateUrl.format(self.ipAddr, self.portNum)
        nlist = []

        resp = self.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif(resp.status_code == 200):
            # If format of the response differs from our expectation then
            # code in 'except' clause suppose to handle such condition
            try:
                p1 = 'nodes'
                p2 = 'node'
                itemslist = json.loads(resp.content)[p1][p2]
                for item in itemslist:
                    p3 = 'id'
                    node_id = item[p3]
                    nlist.append(str(node_id))
                status.set_status(STATUS.OK)
            except(Exception):
                msg = "TODO (unexpected data format in response)"
                dbg_print(msg)
                status.set_status(STATUS.DATA_NOT_FOUND, resp)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return Result(status, nlist)

    def get_node_info(self, nodeId):
        status = OperStatus()
        templateUrl = ("http://{}:{}/restconf/operational/"
                       "opendaylight-inventory:nodes/node/{}")
        url = templateUrl.format(self.ipAddr, self.portNum, nodeId)
        info = None

        resp = self.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif(resp.status_code == 200):
            # If format of the response differs from our expectation then
            # code in 'except' clause suppose to handle such condition
            try:
                p1 = 'node'
                info = json.loads(resp.content)[p1][0]
            except(Exception):
                msg = "TODO (unexpected data format in response)"
                dbg_print(msg)
            finally:
                status.set_status(STATUS.OK if info else STATUS.DATA_NOT_FOUND,
                                  resp)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return Result(status, info)

    def check_node_config_status(self, nodeId):
        """Return the configuration status of the node:

        :param string nodeId: Identifier for the node for which to get
                              the config status
        :return: Configuration status of the node.
        :rtype: None or :class:`pybvc.common.status.OperStatus`

        - STATUS.CONN_ERROR: If the controller did not respond.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded
                                      but did not provide any status.
        - STATUS.NODE_CONFIGURED: If the node is configured.
        - STATUS.DATA_NOT_FOUND: If node is not configured.

        """

        status = OperStatus()
        templateUrl = ("http://{}:{}/restconf/config/"
                       "opendaylight-inventory:nodes/node/{}")
        url = templateUrl.format(self.ipAddr, self.portNum, nodeId)

        resp = self.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif(resp.status_code == 200):
            status.set_status(STATUS.NODE_CONFIGURED)
        else:
            status.set_status(STATUS.DATA_NOT_FOUND, resp)

        return Result(status, None)

    def check_node_conn_status(self, nodeId):
        """Return the connection status of the node to the controller:

        :param string nodeId: Identifier for the node for which to get
                              the config status
        :return: Status of the node's connection to the controller.
        :rtype: None or :class:`pybvc.common.status.OperStatus`

        - STATUS.CONN_ERROR: If the controller did not respond.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded
                                      but did not provide any status.
        - STATUS.NODE_CONNECTED: If the node is connected
        - STATUS.NODE_DISCONNECTED: If the node is not connected
        - STATUS.DATA_NOT_FOUND: If node is not configured.
        - STATUS.HTTP_ERROR: If the controller responded with
                             an error status code.

        """
        status = OperStatus()
        templateUrl = ("http://{}:{}/restconf/operational/"
                       "opendaylight-inventory:nodes")
        url = templateUrl.format(self.ipAddr, self.portNum)

        resp = self.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif(resp.status_code == 200):
            # If format of the response differs from our expectation then
            # code in 'except' clause suppose to handle such condition
            try:
                found = False
                connected = False
                p1 = 'nodes'
                p2 = 'node'
                itemslist = json.loads(resp.content)[p1][p2]
                for item in itemslist:
                    p3 = 'id'
                    p4 = 'netconf-node-inventory:connected'
                    p5 = 'openflow'
                    if(item[p3] == nodeId):
                        found = True
                        # OpenFlow devices that are connected to the
                        # Controller appear in the inventory with 'openflow'
                        # prefix as part of the node 'id'. If device with
                        # given nodeId is found in the Controller's inventory
                        # its status is 'connected'.
                        if(nodeId.startswith(p5)):
                            connected = True
                            break
                        else:
                            # Controller does not report connection status for
                            # a NETCONF device until successfully connected to
                            # to that device
                            if(p4 in item and item[p4]):
                                connected = True
                            break

                if(connected):
                    status.set_status(STATUS.NODE_CONNECTED)
                elif(found):
                    status.set_status(STATUS.NODE_DISONNECTED)
                else:
                    status.set_status(STATUS.NODE_NOT_FOUND)
            except(Exception):
                msg = "TODO (unexpected data format in response)"
                dbg_print(msg)
                status.set_status(STATUS.DATA_NOT_FOUND, resp)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return Result(status, None)

    def get_all_nodes_in_config(self):
        """Return a list of nodes in the controller's configuration data store

        :return: Status, list of nodes in the config data store
                 of the controller
        :rtype: :class:`pybvc.common.status.OperStatus`, list

        - STATUS.CONN_ERROR: If the controller did not respond. List is empty.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not
                                      provide any status. List is empty.
        - STATUS.OK:  Success. List is valid.
        - STATUS.DATA_NOT_FOUND: Success. List is empty.
        - STATUS.HTTP_ERROR: If the controller responded with an error
                             status code.

        """
        status = OperStatus()
        templateUrl = ("http://{}:{}/restconf/config/"
                       "opendaylight-inventory:nodes")
        url = templateUrl.format(self.ipAddr, self.portNum)
        nlist = []

        resp = self.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif(resp.status_code == 200):
            # If format of the response differs from our expectation then
            # code in 'except' clause suppose to handle such condition
            p1 = 'nodes'
            p2 = 'node'
            try:
                itemslist = json.loads(resp.content)[p1][p2]
                for item in itemslist:
                    p3 = 'id'
                    node_id = item[p3]
                    nlist.append(str(node_id))
                status.set_status(STATUS.OK)
            except(Exception):
                msg = "TODO (unexpected data format in response)"
                dbg_print(msg)
                status.set_status(STATUS.DATA_NOT_FOUND, resp)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return Result(status, nlist)

    def get_all_nodes_conn_status(self):
        """Return a list of nodes and the status of their connection
           to the controller.

        :return: Status, list of nodes the status of their
                 connection to the controller
        :rtype: :class:`pybvc.common.status.OperStatus`,
                 list of dict [{node:<node id>, connected:<boolean>},...]

        - STATUS.CONN_ERROR: If the controller did not respond. List is empty.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not
                                      provide any status. List is empty.
        - STATUS.OK:  Success. List is valid.
        - STATUS.DATA_NOT_FOUND:  Success.  List is empty.
        - STATUS.HTTP_ERROR: If the controller responded with an error
                             status code.

        """

        status = OperStatus()
        templateUrl = ("http://{}:{}/restconf/operational/"
                       "opendaylight-inventory:nodes")
        url = templateUrl.format(self.ipAddr, self.portNum)
        nlist = []

        resp = self.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif(resp.status_code == 200):
            # If format of the response differs from our expectation then
            # the code in 'except' clause suppose to handle such condition
            try:
                p1 = 'nodes'
                p2 = 'node'
                p3 = 'id'
                p4 = 'netconf-node-inventory:connected'
                p5 = 'connected'
                p6 = 'openflow'
                itemslist = json.loads(resp.content).get(p1).get(p2)
                for item in itemslist:
                    node_id = item[p3]
                    nd = dict()
                    nd.update({p2: str(node_id)})
                    # OpenFlow devices that are connected to the
                    # Controller appear in the inventory with 'openflow'
                    # prefix as part of the node 'id'. If device with
                    # given nodeId is found in the Controller's inventory
                    # its status is 'connected'
                    if (node_id.startswith(p6)):
                        nd.update({p5: True})
                    # Controller does not report connection status for
                    # a NETCONF device until successfully connected to
                    # to that device
                    elif ((p4 in item) and (item[p4] is True)):
                        nd.update({p5: True})
                    else:
                        nd.update({p5: False})
                    nlist.append(nd)
                status.set_status(STATUS.OK)
            except(Exception):
                msg = "TODO (unexpected data format in response)"
                dbg_print(msg)
                status.set_status(STATUS.DATA_NOT_FOUND, resp)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return Result(status, nlist)

    def get_netconf_nodes_in_config(self):
        """Return a list of NETCONF nodes in the controller's configuration
           data store

        :return: Status, list of nodes in the config data store
                 of the controller
        :rtype: :class:`pybvc.common.status.OperStatus`, list

        - STATUS.CONN_ERROR: If the controller did not respond. List is empty.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not
                                      provide any status. List is empty.
        - STATUS.OK: Success. List is valid.
        - STATUS.DATA_NOT_FOUND:  Success. List is empty.
        - STATUS.HTTP_ERROR: If the controller responded with an error
                             status code.

        """

        status = OperStatus()
        templateUrl = ("http://{}:{}/restconf/config/"
                       "opendaylight-inventory:nodes")
        url = templateUrl.format(self.ipAddr, self.portNum)
        nlist = []

        resp = self.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif(resp.status_code == 200):
            # If format of the response differs from our expectation then
            # code in 'except' clause suppose to handle such condition
            try:
                p1 = 'nodes'
                p2 = 'node'
                itemslist = json.loads(resp.content)[p1][p2]
                for item in itemslist:
                    p3 = 'id'
                    p4 = 'openflow'
                    # OpenFlow devices that are connected to the
                    # Controller appear in the inventory with 'openflow'
                    # prefix as part of the node 'id'. So we use an extra
                    # check in order to ignore OpenFlow devices.
                    node_id = item[p3]
                    if(node_id.startswith(p4) is False):
                        nlist.append(str(node_id))
                status.set_status(STATUS.OK)
            except(Exception):
                msg = "TODO (unexpected data format in response)"
                dbg_print(msg)
                status.set_status(STATUS.DATA_NOT_FOUND, resp)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return Result(status, nlist)

    def get_netconf_nodes_conn_status(self):
        """Return a list of NETCONF nodes and the status of their connection
           to the controller.

        :return: Status, list of nodes the status of their connection
                 to the controller
        :rtype: :class:`pybvc.common.status.OperStatus`,
                 list of dict [{node:<node id>, connected:<boolean>},...]

        - STATUS.CONN_ERROR: If the controller did not respond. List is empty.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not
                                      provide any status. List is empty.
        - STATUS.OK:  Success. List is valid.
        - STATUS.DATA_NOT_FOUND:  Success.  List is empty.
        - STATUS.HTTP_ERROR: If the controller responded with an error
                             status code.

        """

        status = OperStatus()
        templateUrl = ("http://{}:{}/restconf/operational/"
                       "opendaylight-inventory:nodes")
        url = templateUrl.format(self.ipAddr, self.portNum)
        nlist = []

        resp = self.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif(resp.status_code == 200):
            # If format of the response differs from our expectation then
            # code in 'except' clause suppose to handle such condition
            try:
                p1 = 'nodes'
                p2 = 'node'
                p3 = 'id'
                p4 = 'netconf-node-inventory:connected'
                p5 = 'connected'
                p6 = 'openflow'
                itemslist = json.loads(resp.content)[p1][p2]
                for item in itemslist:
                    node_id = item[p3]
                    # OpenFlow devices that are connected to the
                    # Controller appear in the inventory with 'openflow'
                    # prefix as part of the node 'id'. So we use an extra check
                    # for the 'openflow' prefixes in order to ignore them
                    if (node_id.startswith(p6) is False):
                        nd = dict()
                        nd.update({p2: str(node_id)})
                        # Controller does not report connection status for
                        # a NETCONF device until successfully connected to
                        # to that device
                        if ((p4 in item) and (item[p4] is True)):
                            nd.update({p5: True})
                        else:
                            nd.update({p5: False})
                        nlist.append(nd)
                status.set_status(STATUS.OK)
            except(Exception):
                msg = "TODO (unexpected data format in response)"
                dbg_print(msg)
                status.set_status(STATUS.DATA_NOT_FOUND, resp)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return Result(status, nlist)

    def get_schemas(self, nodeName):
        """Return a list of YANG model schemas for the node.

        :param string nodeName: Name of the node
        :return: Status, list of YANG schemas for the node.
        :rtype: :class:`pybvc.common.status.OperStatus`,
                JSON listing information about the YANG schemas for the node

        - STATUS.CONN_ERROR: If the controller did not respond. List is empty.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not
                                      provide any status. List is empty.
        - STATUS.OK:  Success. List is valid.
        - STATUS.HTTP_ERROR: If the controller responded with an error
                             status code.

        """

        status = OperStatus()
        templateUrl = ("http://{}:{}/restconf/operational/"
                       "opendaylight-inventory:nodes/node/{}/"
                       "yang-ext:mount/"
                       "ietf-netconf-monitoring:netconf-state/schemas")
        url = templateUrl.format(self.ipAddr, self.portNum, nodeName)
        slist = None

        resp = self.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif(resp.status_code == 200):
            # If format of the response differs from our expectation then
            # the code in 'except' clause suppose to handle such condition
            p1 = 'schemas'
            p2 = 'schema'
            try:
                slist = json.loads(resp.content)[p1][p2]
                status.set_status(STATUS.OK)
            except(Exception):
                msg = "TODO (unexpected data format in response)"
                dbg_print(msg)
                status.set_status(STATUS.DATA_NOT_FOUND, resp)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return Result(status, slist)

    def get_schema(self, nodeName, schemaId, schemaVersion):
        """Return a YANG schema for the indicated schema on the indicated node.

        :param string nodeName: Name of the node
        :param string schemaId: Id of the schema
        :param string schemaVersion: Version of the schema
        :return: Status, YANG schema.
        :rtype: :class:`pybvc.common.status.OperStatus`, YANG schema

        - STATUS.CONN_ERROR: If the controller did not respond. schema is
          empty.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not
                                      provide any status. schema is empty.
        - STATUS.OK: Success. Result is valid.
        - STATUS.DATA_NOT_FOUND: Data missing or in unexpected format.
        - STATUS.HTTP_ERROR: If the controller responded with an error
                             status code.

        """

        status = OperStatus()
        templateUrl = ("http://{}:{}/restconf/operations/"
                       "opendaylight-inventory:nodes/node/{}/"
                       "yang-ext:mount/ietf-netconf-monitoring:get-schema")
        url = templateUrl.format(self.ipAddr, self.portNum, nodeName)
        headers = {'content-type': 'application/yang.data+json',
                   'accept': 'text/json, text/html, application/xml, */*'}
        payload = {'input': {'identifier': schemaId,
                             'version': schemaVersion, 'format': 'yang'}}
        schema = None

        resp = self.http_post_request(url, json.dumps(payload), headers)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif(resp.status_code == 200):
            if(resp.headers.get('content-type') == "application/xml"):
                # If format of the response differs from our expectation then
                # code in 'except' clause suppose to handle such condition
                try:
                    doc = xmltodict.parse(resp.content, xml_attribs=False)
                    p1 = 'data'
                    data = find_key_value_in_dict(doc, p1)
                    if(data and isinstance(data, basestring)):
                        schema = data
                        status.set_status(STATUS.OK)
                    else:
                        raise ValueError()
                except(Exception):
                    msg = "TODO (unexpected data format in response)"
                    dbg_print(msg)
                    status.set_status(STATUS.DATA_NOT_FOUND)
            else:
                msg = "TODO (not implemented content-type parser)"
                dbg_print(msg)
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return Result(status, schema)

    def get_netconf_operations(self, nodeName):
        """Return a list of operations supported by the indicated node.

        :param string nodeName: Name of the node
        :return: A tuple:  Status, operations supported by indicated node.
        :rtype: :class:`pybvc.common.status.OperStatus`,
                JSON listing the operations

        - STATUS.CONN_ERROR: If the controller did not respond.
                             Operations info is empty.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did
                                      not provide any status.
                                      Operations info is empty.
        - STATUS.OK: Success. Operations info is valid.
        - STATUS.DATA_NOT_FOUND:  Data missing or in unexpected format.
        - STATUS.HTTP_ERROR: If the controller responded with an error
                             status code.

        """

        status = OperStatus()
        templateUrl = ("http://{}:{}/restconf/operations/"
                       "opendaylight-inventory:nodes/node/{}/yang-ext:mount/")
        url = templateUrl.format(self.ipAddr, self.portNum, nodeName)
        olist = None
        resp = self.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif(resp.status_code == 200):
            # If format of the response differs from our expectation then
            # the code in 'except' clause suppose to handle such condition
            try:
                p1 = 'operations'
                olist = json.loads(resp.content)[p1]
                status.set_status(STATUS.OK)
            except(Exception):
                msg = "TODO (unexpected data format in response)"
                dbg_print(msg)
                status.set_status(STATUS.DATA_NOT_FOUND, resp)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return Result(status, olist)

    def get_config_modules(self):
        """Return a list of configuration modules.

        :return: Status, configuration modules.
        :rtype: :class:`pybvc.common.status.OperStatus`,
                JSON listing modules and their operational state

        - STATUS.CONN_ERROR: If the controller did not respond.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did
                                      not provide any status.
        - STATUS.OK:  Success.
        - STATUS.DATA_NOT_FOUND: Data missing or in unexpected format.
        - STATUS.HTTP_ERROR: If the controller responded with an error
                             status code.

        """

        status = OperStatus()
        templateUrl = ("http://{}:{}/restconf/operational/"
                       "opendaylight-inventory:nodes/node/controller-config/"
                       "yang-ext:mount/config:modules")
        url = templateUrl.format(self.ipAddr, self.portNum)
        mlist = None

        resp = self.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif(resp.status_code == 200):
            # If format of the response differs from our expectation then
            # the code in 'except' clause suppose to handle such condition
            try:
                p1 = 'modules'
                p2 = 'module'
                mlist = json.loads(resp.content.replace('\\\n', ''))[p1][p2]
                status.set_status(STATUS.OK)
            except(Exception):
                msg = "TODO (unexpected data format in response)"
                dbg_print(msg)
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return Result(status, mlist)

    def get_module_operational_state(self, moduleType, moduleName):
        """Return operational state for specified module.

        :param string moduleType: module type
        :param string moduleName: module name
        :return: Status, operational state for specified module.
        :rtype: :class:`pybvc.common.status.OperStatus`,
                JSON providing operational state

        - STATUS.CONN_ERROR: If the controller did not respond.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did
                                      not provide any status.
                                      State info is empty.
        - STATUS.OK: Success. State info is valid.
        - STATUS.DATA_NOT_FOUND: Data missing or in unexpected format.
        - STATUS.HTTP_ERROR: If the controller responded with an error
                             status code.

        """

        status = OperStatus()
        templateUrl = ("http://{}:{}/restconf/operational/"
                       "opendaylight-inventory:nodes/node/controller-config/"
                       "yang-ext:mount/config:modules/module/{}/{}")
        url = templateUrl.format(self.ipAddr, self.portNum, moduleType,
                                 moduleName)
        module = None

        resp = self.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif(resp.status_code == 200):
            # If format of the response differs from our expectation then
            # the code in 'except' clause suppose to handle such condition
            try:
                p1 = 'module'
                module = json.loads(resp.content)[p1]
                status.set_status(STATUS.OK)
            except(Exception):
                msg = "TODO (unexpected data format in response)"
                dbg_print(msg)
                status.set_status(STATUS.DATA_NOT_FOUND, resp)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return Result(status, module)

    def get_sessions_info(self, nodeName):
        """Return sessions for indicated node.

        :param string nodeName: Name of the node
        :return: Status, list of sessions for indicated node
        :rtype: :class:`pybvc.common.status.OperStatus`,
                JSON providing sessions

        - STATUS.CONN_ERROR: If the controller did not respond.
        .                     Session info is empty.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not
        .                             provide any status. Session info is
        .                             empty.
        - STATUS.OK: Success. Session info is valid.
        - STATUS.DATA_NOT_FOUND: Data missing or in unexpected format.
        - STATUS.HTTP_ERROR: If the controller responded with an error
        .                    status code.

        """

        status = OperStatus()
        templateUrl = ("http://{}:{}/restconf/operational/"
                       "opendaylight-inventory:nodes/node/{}/"
                       "yang-ext:mount/"
                       "ietf-netconf-monitoring:netconf-state/sessions")
        url = templateUrl.format(self.ipAddr, self.portNum, nodeName)
        slist = None

        resp = self.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif(resp.status_code == 200):
            # If format of the response differs from our expectation then
            # the code in 'except' clause suppose to handle such condition
            try:
                p1 = 'sessions'
                slist = json.loads(resp.content)[p1]
                status.set_status(STATUS.OK)
            except(Exception):
                msg = "TODO (unexpected data format in response)"
                dbg_print(msg)
                status.set_status(STATUS.DATA_NOT_FOUND, resp)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return Result(status, slist)

    def get_streams_info(self):
        """Return streams available for subscription.

        :return: Status, list of streams
        :rtype: :class:`pybvc.common.status.OperStatus`,
                 JSON providing list of streams

        - STATUS.CONN_ERROR: If the controller did not respond.
                             Stream info is empty.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not
                                      provide any status. stream info is empty.
        - STATUS.OK: Success. Stream info is valid.
        - STATUS.DATA_NOT_FOUND: Data missing or in unexpected format.
        - STATUS.HTTP_ERROR: If the controller responded with an error
                             status code.

        """

        status = OperStatus()
        templateUrl = "http://{}:{}/restconf/streams"
        url = templateUrl.format(self.ipAddr, self.portNum)
        slist = None

        resp = self.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif(resp.status_code == 200):
            # If format of the response differs from our expectation then
            # the code in 'except' clause suppose to handle such condition
            try:
                p1 = 'streams'
                slist = json.loads(resp.content)[p1]
                status.set_status(STATUS.OK)
            except(Exception):
                msg = "TODO (unexpected data format in response)"
                dbg_print(msg)
                status.set_status(STATUS.DATA_NOT_FOUND, resp)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return Result(status, slist)

    def get_service_providers_info(self):
        """Return a list of service providers available.

        :return: Status, list of service providers
        :rtype: :class:`pybvc.common.status.OperStatus`,
                 JSON providing list of service providers

        - STATUS.CONN_ERROR: If the controller did not respond.
        .                    Provider info is empty.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not
        .                             provide any status. provider info is
        .                             empty.
        - STATUS.OK: Success. Provider info is valid.
        - STATUS.DATA_NOT_FOUND: Data missing or in unexpected format.
        - STATUS.HTTP_ERROR: If the controller responded with an error
        .                    status code.

        """

        status = OperStatus()
        templateUrl = ("http://{}:{}/restconf/config/"
                       "opendaylight-inventory:nodes/node/"
                       "controller-config/"
                       "yang-ext:mount/config:services")
        url = templateUrl.format(self.ipAddr, self.portNum)
        slist = None

        resp = self.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif(resp.status_code == 200):
            # If format of the response differs from our expectation then
            # the code in 'except' clause suppose to handle such condition
            try:
                p1 = 'services'
                p2 = 'service'
                slist = json.loads(resp.content)[p1][p2]
                status.set_status(STATUS.OK)
            except(Exception):
                msg = "TODO (unexpected data format in response)"
                dbg_print(msg)
                status.set_status(STATUS.DATA_NOT_FOUND, resp)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return Result(status, slist)

    def get_service_provider_info(self, name):
        """Return info about a single service provider.

        :param string name: Name of the provider
        :return: Status, info about the service provider
        :rtype: :class:`pybvc.common.status.OperStatus`,
                 JSON providing info about the service provider

        - STATUS.CONN_ERROR: If the controller did not respond.
        .                    Provider info is empty.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not
        .                             provide any status. provider info is
        .                             empty.
        - STATUS.OK: Success. Provider info is valid.
        - STATUS.DATA_NOT_FOUND: Data missing or in unexpected format.
        - STATUS.HTTP_ERROR: If the controller responded with an error
        .                    status code.

        """

        status = OperStatus()
        templateUrl = ("http://{}:{}/restconf/config/"
                       "opendaylight-inventory:nodes/node/"
                       "controller-config/"
                       "yang-ext:mount/config:services/service/{}")
        url = templateUrl.format(self.ipAddr, self.portNum, name)
        service = None

        resp = self.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif(resp.status_code == 200):
            # If format of the response differs from our expectation then
            # the code in 'except' clause suppose to handle such condition
            try:
                p1 = 'service'
                service = json.loads(resp.content)[p1]
                status.set_status(STATUS.OK)
            except(Exception):
                msg = "TODO (unexpected data format in response)"
                dbg_print(msg)
                status.set_status(STATUS.DATA_NOT_FOUND, resp)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return Result(status, service)

    def add_netconf_node(self, node):
        """ Connect a netconf device to the controller
            (for example connect vrouter to controller via NETCONF)

        :param node: :class:`pybvc.controller.netconfnode.NetconfNode`
        :return: Status, JSON response from controller.
        :rtype: :class:`pybvc.common.status.OperStatus`,
                 JSON providing response from adding netconf noed.

        - STATUS.CONN_ERROR: If the controller did not respond.
        .                    Provider info is empty.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not
        .                             provide any status. Provider info is
        .                             empty.
        - STATUS.OK: Success. Provider info is valid.
        - STATUS.HTTP_ERROR: If the controller responded with an error
        .                    status code.
        """

        status = OperStatus()
        templateUrl = ("http://{}:{}/restconf/config/"
                       "opendaylight-inventory:nodes/node/"
                       "controller-config/yang-ext:mount/config:modules")
        ns = "urn:opendaylight:params:xml:ns:yang:controller"
        xmlPayloadTemplate = '''
        <module xmlns="{}:config">
          <type xmlns:prefix="{}:md:sal:connector:netconf">
             prefix:sal-netconf-connector
          </type>
          <name>{}</name>
          <address xmlns="{}:md:sal:connector:netconf">{}</address>
          <port xmlns="{}:md:sal:connector:netconf">{}</port>
          <username xmlns="{}:md:sal:connector:netconf">{}</username>
          <password xmlns="{}:md:sal:connector:netconf">{}</password>
          <tcp-only xmlns="{}:md:sal:connector:netconf">{}</tcp-only>
          <event-executor xmlns="{}:md:sal:connector:netconf">
            <type xmlns:prefix="{}:netty">prefix:netty-event-executor</type>
            <name>global-event-executor</name>
          </event-executor>
          <binding-registry xmlns="{}:md:sal:connector:netconf">
            <type xmlns:prefix="{}:md:sal:binding">
               prefix:binding-broker-osgi-registry
            </type>
            <name>binding-osgi-broker</name>
          </binding-registry>
          <dom-registry xmlns="{}:md:sal:connector:netconf">
            <type xmlns:prefix="{}:md:sal:dom">
               prefix:dom-broker-osgi-registry
            </type>
            <name>dom-broker</name>
          </dom-registry>
          <client-dispatcher xmlns="{}:md:sal:connector:netconf">
            <type xmlns:prefix="{}:config:netconf">
               prefix:netconf-client-dispatcher
            </type>
            <name>global-netconf-dispatcher</name>
          </client-dispatcher>
          <processing-executor xmlns="{}:md:sal:connector:netconf">
            <type xmlns:prefix="{}:threadpool">prefix:threadpool</type>
            <name>global-netconf-processing-executor</name>
          </processing-executor>
        </module>
        '''
        payload = xmlPayloadTemplate.format(ns, ns, node.name,
                                            ns, node.ipAddr,
                                            ns, node.portNum,
                                            ns, node.adminName,
                                            ns, node.adminPassword,
                                            ns, node.tcpOnly,
                                            ns, ns, ns, ns, ns,
                                            ns, ns, ns, ns, ns)
        url = templateUrl.format(self.ipAddr, self.portNum)
        headers = {'content-type': 'application/xml',
                   'accept': 'application/xml'}
        resp = self.http_post_request(url, payload, headers)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif(resp.status_code == 200 or resp.status_code == 204):
            status.set_status(STATUS.OK)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return Result(status, resp)

    def delete_netconf_node(self, netconfdev=None, nodename=None):
        """ Disconnect a netconf device from the controller
        :param netconfdev:
                         :class:`pybvc.controller.netconfnode.NetconfNode`
        :return: Status, None.
        :rtype: :class:`pybvc.common.status.OperStatus`,
                 JSON providing response from adding netconf noed.
        - STATUS.CONN_ERROR: If the controller did not respond.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not
                                      provide any status.
        - STATUS.OK:  Success.
        - STATUS.HTTP_ERROR: If the controller responded with an error
                             status code.
        """
        status = OperStatus()
        templateUrl = ("http://{}:{}/restconf/config/"
                       "opendaylight-inventory:nodes/node/"
                       "controller-config/"
                       "yang-ext:mount/config:modules/module/"
                       "odl-sal-netconf-connector-cfg:"
                       "sal-netconf-connector/{}")
        assert(netconfdev or nodename)
        nm = netconfdev.name if netconfdev else nodename
        url = templateUrl.format(self.ipAddr, self.portNum, nm)

        resp = self.http_delete_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif(resp.status_code == 200):
            status.set_status(STATUS.OK)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        return Result(status, None)

    # -------------------------------------------------------------------------
    # NOTE: It is unclear which NETCONF node attributes are allowed for dynamic
    #       configuration changes. For now just follow an example that is
    #       published on ODL wiki.
    # -------------------------------------------------------------------------
    def modify_netconf_node_in_config(self, netconfdev):
        """ Modify connected netconf device's info in the controller

        :param netconfdev:
                         :class:`pybvc.controller.netconfnode.NetconfNode`
        :return: Status, None.
        :rtype: :class:`pybvc.common.status.OperStatus`,
                 JSON providing response from adding netconf noed.
        - STATUS.CONN_ERROR: If the controller did not respond.
        - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not
                                      provide any status.
        - STATUS.OK: Success.
        - STATUS.HTTP_ERROR: If the controller responded with an error
                             status code.
        """
        status = OperStatus()
        templateUrl = ("http://{}:{}/restconf/config/"
                       "opendaylight-inventory:nodes/node/"
                       "controller-config/yang-ext:mount/config:modules")
        url = templateUrl.format(self.ipAddr, self.portNum)
        ns = "urn:opendaylight:params:xml:ns:yang:controller"
        xmlPayloadTemplate = '''
        <module xmlns="{}:config">
          <type xmlns:prefix="{}:md:sal:connector:netconf">
             prefix:sal-netconf-connector
          </type>
          <name>{}</name>
          <username xmlns="{}:md:sal:connector:netconf">{}</username>
          <password xmlns="{}:md:sal:connector:netconf">{}</password>
        </module>
        '''
        payload = xmlPayloadTemplate.format(ns, ns,
                                            netconfdev.devName,
                                            netconfdev.adminName,
                                            netconfdev.adminPassword)
        headers = {'content-type': 'application/xml',
                   'accept': 'application/xml'}

        resp = self.http_post_request(url, payload, headers)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif(resp.status_code == 200):
            status.set_status(STATUS.OK)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return Result(status, None)

    def get_ext_mount_config_url(self, node):
        templateUrl = ("http://{}:{}/restconf/config/"
                       "opendaylight-inventory:nodes/node/{}/"
                       "yang-ext:mount/")
        url = templateUrl.format(self.ipAddr, self.portNum, node)
        return url

    def get_ext_mount_operational_url(self, node):
        templateUrl = ("http://{}:{}/restconf/operational/"
                       "opendaylight-inventory:nodes/node/{}/"
                       "yang-ext:mount/")
        url = templateUrl.format(self.ipAddr, self.portNum, node)
        return url

    def get_node_operational_url(self, node):
        templateUrl = ("http://{}:{}/restconf/operational/"
                       "opendaylight-inventory:nodes/node/{}")
        url = templateUrl.format(self.ipAddr, self.portNum, node)
        return url

    def get_node_config_url(self, node):
        templateUrl = ("http://{}:{}/restconf/config/"
                       "opendaylight-inventory:nodes/node/{}")
        url = templateUrl.format(self.ipAddr, self.portNum, node)
        return url

    def get_openflow_nodes_operational_list(self):
        status = OperStatus()
        templateUrl = ("http://{}:{}/restconf/operational/"
                       "opendaylight-inventory:nodes")
        url = templateUrl.format(self.ipAddr, self.portNum)
        nlist = []
        resp = self.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif(resp.status_code == 200):
            # If format of the response differs from our expectation then
            # code in 'except' clause suppose to handle such condition
            try:
                p1 = 'nodes'
                p2 = 'node'
                p3 = 'id'
                p4 = 'openflow'
                itemslist = json.loads(resp.content)[p1][p2]
                for item in itemslist:
                    if(item[p3].startswith(p4)):
                        nlist.append(item[p3])
                status.set_status(STATUS.OK)
            except(Exception):
                msg = "TODO (unexpected data format in response)"
                dbg_print(msg)
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return Result(status, sorted(nlist))

    def get_openflow_operational_flows_total_cnt(self):
        status = OperStatus()
        templateUrl = ("http://{}:{}/restconf/operational/"
                       "opendaylight-inventory:nodes")
        url = templateUrl.format(self.ipAddr, self.portNum)
        cnt = 0
        resp = self.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif(resp.status_code == 200):
            # If format of the response differs from our expectation then
            # the code in 'except' clause suppose to handle such condition
            try:
                p1 = 'nodes'
                p2 = 'opendaylight-flow-statistics:aggregate-flow-statistics'
                p3 = 'flow-count'
                d = json.loads(resp.content)[p1]
                vlist = find_key_values_in_dict(d, p2)
                if vlist:
                    for item in vlist:
                        cnt += item[p3]
                status.set_status(STATUS.OK)
            except(Exception):
                msg = "TODO (unexpected data format in response)"
                dbg_print(msg)
                status.set_status(STATUS.DATA_NOT_FOUND, resp)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return Result(status, cnt)

    def get_topology_ids(self):
        status = OperStatus()
        templateUrl = ("http://{}:{}/restconf/operational/"
                       "network-topology:network-topology")
        tnames = []

        url = templateUrl.format(self.ipAddr, self.portNum)
        resp = self.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif(resp.status_code == 200):
            # If format of the response differs from our expectation then
            # code in 'except' clause suppose to handle such condition
            try:
                p1 = 'network-topology'
                p2 = 'topology'
                p3 = 'topology-id'
                tlist = json.loads(resp.content)[p1][p2]
                for item in tlist:
                    tnames.append(item[p3])
                status.set_status(STATUS.OK)
            except(Exception):
                msg = "TODO (unexpected data format in response)"
                dbg_print(msg)
                status.set_status(STATUS.DATA_NOT_FOUND, resp)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return Result(status, sorted(tnames))

    def build_topology_object(self, topo_name):
        status = OperStatus()
        templateUrl = ("http://{}:{}/restconf/operational/"
                       "network-topology:network-topology/topology/{}")
        topo_obj = None

        url = templateUrl.format(self.ipAddr, self.portNum, topo_name)
        resp = self.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif(resp.status_code == 200):
            # If format of the response differs from our expectation then
            # code in 'except' clause suppose to handle such condition
            try:
                p1 = 'topology'
                p2 = 'topology-id'
                d = json.loads(resp.content)
                tlist = d[p1]
                for item in tlist:
                    if item[p2] == topo_name:
                        topo_obj = Topology(topo_dict=item)
                        break
                status.set_status(STATUS.OK)
            except(Exception):
                msg = "TODO (unexpected data format in response)"
                dbg_print(msg)
                status.set_status(STATUS.DATA_NOT_FOUND, resp)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return Result(status, topo_obj)

    def build_inventory_object(self, operational=True):
        status = OperStatus()
        templateUrl = "http://{}:{}/restconf/{}/opendaylight-inventory:nodes"
        inv_obj = None

        inv_type = "operational" if operational else "config"
        url = templateUrl.format(self.ipAddr, self.portNum, inv_type)
        resp = self.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif(resp.status_code == 200):
            # If format of the response differs from our expectation then
            # code in 'except' clause suppose to handle such condition
            p1 = 'nodes'
            p2 = 'node'
            try:
                d = json.loads(resp.content)
                v = d[p1][p2]
                inv_obj = Inventory(inv_json=json.dumps(v))
                status.set_status(STATUS.OK)
            except(Exception):
                msg = "TODO (unexpected data format in response)"
                dbg_print(msg)
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return Result(status, inv_obj)

    def build_openflow_node_inventory_object(self, node_id, operational=True):
        status = OperStatus()
        templateUrl = ("http://{}:{}/restconf/{}/"
                       "opendaylight-inventory:nodes/node/{}")
        inv_obj = None

        inv_type = "operational" if operational else "config"
        url = templateUrl.format(self.ipAddr, self.portNum, inv_type, node_id)
        resp = self.http_get_request(url, data=None, headers=None)

        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif(resp.status_code == 200):
            # If format of the response differs from our expectation then
            # code in 'except' clause suppose to handle such condition
            try:
                p1 = 'node'
                d = json.loads(resp.content)
                v = d[p1][0]
                inv_obj = OpenFlowCapableNode(inv_json=json.dumps(v))
                status.set_status(STATUS.OK)
            except(Exception):
                msg = "TODO (unexpected data format in response)"
                dbg_print(msg)
                status.set_status(STATUS.DATA_NOT_FOUND)
        elif(resp.status_code == 404):
            status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return Result(status, inv_obj)

    def build_netconf_node_inventory_object(self, node_id, operational=True):
        status = OperStatus()
        templateUrl = ("http://{}:{}/restconf/{}/"
                       "opendaylight-inventory:nodes/node/{}")
        inv_obj = None

        inv_type = "operational" if operational else "config"
        url = templateUrl.format(self.ipAddr, self.portNum, inv_type, node_id)
        resp = self.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif(resp.status_code == 200):
            # If format of the response differs from our expectation then
            # code in 'except' clause suppose to handle such condition
            try:
                p1 = 'node'
                d = json.loads(resp.content)[p1]
                inv_obj = NetconfCapableNode(clazz='VRouter5600',
                                             inv_dict=d[0])
                status.set_status(STATUS.OK)
            except(Exception) as e:
                print "!!! %s" % e
                msg = "TODO (unexpected data format in response)"
                dbg_print(msg)
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return Result(status, inv_obj)

    def build_netconf_config_objects(self):
        status = OperStatus()
        objs = []
        templateUrl = (
            "http://{}:{}/restconf/operational/"
            "opendaylight-inventory:nodes/node/controller-config/"
            "yang-ext:mount/config:modules")
        url = templateUrl.format(self.ipAddr, self.portNum)
        resp = self.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif(resp.status_code == 200):
            # If format of the response differs from our expectation then
            # code in 'except' clause suppose to handle such condition
            try:
                p1 = 'modules'
                p2 = 'module'
                p3 = 'type'
                p4 = 'odl-sal-netconf-connector-cfg:sal-netconf-connector'
                mlist = json.loads(resp.content.replace('\\\n', ''))[p1][p2]
                for item in mlist:
                    if(item[p3] == p4):
                        objs.append(NetconfConfigModule(item))
                status.set_status(STATUS.OK)
            except(Exception):
                msg = "TODO (unexpected data format in response)"
                dbg_print(msg)
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return Result(status, objs)

    def build_netconf_config_object(self, netconf_id):
        status = OperStatus()
        templateUrl = (
            "http://{}:{}/restconf/operational/"
            "opendaylight-inventory:nodes/node/controller-config/"
            "yang-ext:mount/config:modules/module/"
            "odl-sal-netconf-connector-cfg:sal-netconf-connector/{}")
        url = templateUrl.format(self.ipAddr, self.portNum, netconf_id)
        cfg_obj = None

        resp = self.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif(resp.status_code == 200):
            # If format of the response differs from our expectation then
            # code in 'except' clause suppose to handle such condition
            try:
                p1 = 'module'
                module = json.loads(resp.content)[p1]
                cfg_obj = NetconfConfigModule(module[0])
                status.set_status(STATUS.OK)
            except(Exception):
                msg = "TODO (unexpected data format in response)"
                dbg_print(msg)
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return Result(status, cfg_obj)

    def create_data_change_event_subscription(self, datastore, scope, path):
        status = OperStatus()
        stream_name = None
        templateUrl = ("http://{}:{}/restconf/operations/"
                       "sal-remote:create-data-change-event-subscription")
        url = templateUrl.format(self.ipAddr, self.portNum)
        headers = {'content-type': 'application/yang.data+json',
                   'accept': 'text/json, text/html, application/xml, */*'}
        payload = {'input': {'path': path,
                             'datastore': datastore,
                             'scope': scope}}
        resp = self.http_post_request(url, json.dumps(payload), headers)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif(resp.status_code == 200):
            # If format of the response differs from our expectation then
            # code in 'except' clause suppose to handle such condition
            try:
                p1 = 'output'
                p2 = 'stream-name'
                doc = xmltodict.parse(resp.content)
                stream_name = doc[p1][p2]
                status.set_status(STATUS.OK)
            except(Exception):
                msg = "TODO (unexpected data format in response)"
                dbg_print(msg)
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return Result(status, stream_name)

    def subscribe_to_stream(self, stream_name):
        status = OperStatus()
        stream_location = None
        templateUrl = "http://{}:{}/restconf/streams/stream/{}"
        url = templateUrl.format(self.ipAddr, self.portNum, stream_name)

        resp = self.http_get_request(url, data=None, headers=None)
        if(resp is None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content is None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif(resp.status_code == 200):
            # If format of the response differs from our expectation then
            # code in 'except' clause suppose to handle such condition
            try:
                p1 = 'location'
                stream_location = resp.headers[p1]
                status.set_status(STATUS.OK)
            except:
                msg = "TODO (unexpected data format in response)"
                dbg_print(msg)
                status.set_status(STATUS.DATA_NOT_FOUND, resp)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)

        return Result(status, stream_location)

    def get_network_topology_yang_schema_path(self, topo_id=None):
        base_path = "/network-topology:network-topology"
        ext = "/network-topology:topology[network-topology:topology-id=\"{}\"]"
        path = base_path
        if topo_id:
            path += ext.format(topo_id)

        return path

    def get_inventory_nodes_yang_schema_path(self):
        base_path = "/opendaylight-inventory:nodes"
        return base_path
