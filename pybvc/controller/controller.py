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
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
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

controller.py: Controller's properties and communication methods


"""

import json
import xmltodict
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError, Timeout
from framework.common.result import Result
from framework.common.status import OperStatus, STATUS
from framework.common.utils import find_dict_in_list


#-------------------------------------------------------------------------------
# Class 'Controller'
#-------------------------------------------------------------------------------
class Controller():
    """ Class that represents a Controller device. """
    
    def __init__(self, ipAddr, portNum, adminName, adminPassword, timeout=5):
        """Initializes this object properties."""
        self.ipAddr = ipAddr
        self.portNum = portNum
        self.adminName = adminName
        self.adminPassword = adminPassword
        self.timeout = timeout
    
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
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
    
    def brief_json(self):
        """ Returns JSON representation of this object (brief info). """
        d = {'ipAddr': self.ipAddr, 
             'portNum': self.portNum, 
             'adminName': self.adminName, 
             'adminPassword' : self.adminPassword}
        return json.dumps(d, default=lambda o: o.__dict__, sort_keys=True, indent=4)

    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def http_get_request(self, url, data, headers):
        """ Sends HTTP GET request to a remote server and returns the response.
        
        :param string url: The complete url including protocol: http://www.example.com/path/to/resource
        :param string data:  The data to include in the body of the request.  Typically set to None.
        :param dict headers:  The headers to include in the request.
        :return: The response from the http request.
        :rtype: None or `requests.response <http://docs.python-requests.org/en/latest/api/#requests.Response>`
        
        """
        
        resp = None
        
        try:
            resp = requests.get(url,
                                auth=HTTPBasicAuth(self.adminName, self.adminPassword),
                                data=data, headers=headers, timeout=self.timeout)
        except (ConnectionError, Timeout) as e:
            print "Error: " + repr(e)
        
        return (resp)
        
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def http_post_request(self, url, data, headers):
        """Sends HTTP POST request to a remote server and returns the response.        
        
        :param string url: The complete url including protocol: http://www.example.com/path/to/resource
        :param string data:  The data to include in the body of the request.  Typically set to None.
        :param dict headers:  The headers to include in the request.
        :return: The response from the http request.
        :rtype: None or `requests.response <http://docs.python-requests.org/en/latest/api/#requests.Response>`
        
        """
        
        resp = None
        
        try:
            resp = requests.post(url,
                                 auth=HTTPBasicAuth(self.adminName, self.adminPassword),
                                 data=data, headers=headers, timeout=self.timeout)
        except (ConnectionError, Timeout) as e:
            print "Error: " + repr(e)
        
        return (resp)

    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def http_put_request(self, url, data, headers):
        """Sends HTTP PUT request to a remote server and returns the response.        
        
        :param string url: The complete url including protocol: http://www.example.com/path/to/resource
        :param string data:  The data to include in the body of the request.  Typically set to None.
        :param dict headers:  The headers to include in the request.
        :return: The response from the http request.
        :rtype: None or `requests.response <http://docs.python-requests.org/en/latest/api/#requests.Response>`
        
        """
        
        resp = None
        
        try:
            resp = requests.put(url,
                                auth=HTTPBasicAuth(self.adminName, self.adminPassword),
                                data=data, headers=headers, timeout=self.timeout)
        except (ConnectionError, Timeout) as e:
            print "Error: " + repr(e)
        
        return (resp)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def http_delete_request(self, url, data, headers):
        """Sends HTTP DELETE request to a remote server and returns the response.        
        
        :param string url: The complete url including protocol: http://www.example.com/path/to/resource
        :param string data:  The data to include in the body of the request.  Typically set to None.
        :param dict headers:  The headers to include in the request.
        :return: The response from the http request.
        :rtype: None or `requests.response <http://docs.python-requests.org/en/latest/api/#requests.Response>`

        """
        resp = None
        
        try:
            resp = requests.delete(url,
                                   auth=HTTPBasicAuth(self.adminName, self.adminPassword),
                                   data=data, headers=headers, timeout=self.timeout)
        except (ConnectionError, Timeout) as e:
            print "Error: " + repr(e)
        
        return (resp)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_nodes_operational_list(self):
        status = OperStatus()
        templateUrl = "http://{}:{}/restconf/operational/opendaylight-inventory:nodes"
        url = templateUrl.format(self.ipAddr, self.portNum)
        nlist = [] 
        
        resp = self.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            p1 = 'nodes'
            p2 = 'node'
            if(p1 in resp.content and p2 in resp.content):
                elemlist = json.loads(resp.content).get(p1).get(p2)
                for elem in elemlist:
                    p3 = 'id'
                    if(p3 in elem):
                        nlist.append(str(elem[p3]))
                status.set_status(STATUS.OK)
            else:
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return Result(status, nlist)     
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_node_info(self, nodeId):
        status = OperStatus()
        templateUrl = "http://{}:{}/restconf/operational/opendaylight-inventory:nodes/node/{}"
        url = templateUrl.format(self.ipAddr, self.portNum, nodeId)
        info = [] 
        
        resp = self.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            p1 = 'node'
            if(p1 in resp.content):
                info = json.loads(resp.content).get(p1)
                status.set_status(STATUS.OK)
            else:
                status.set_status(STATUS.DATA_NOT_FOUND, resp)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return Result(status, info)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def check_node_config_status(self, nodeId):
        """Return the configuration status of the node:  
        
        :param string nodeId: Identifier for the node for which to get the config status 
        :return: Configuration status of the node. 
        :rtype: None or :class:`pybvc.common.status.OperStatus` 
        
        - STATUS.CONN_ERROR: if the controller did not respond.
        - STATUS.CTRL_INTERNAL_ERROR: if the controller responded but did not provide any status.
        - STATUS.NODE_CONFIGURED: if the node is configured.  
        - STATUS.DATA_NOT_FOUND: if node is not configured. 
        
        """
        
        status = OperStatus()
        templateUrl = "http://{}:{}/restconf/config/opendaylight-inventory:nodes/node/{}"
        url = templateUrl.format(self.ipAddr, self.portNum, nodeId)
        
        resp = self.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            status.set_status(STATUS.NODE_CONFIGURED)
        else:
            status.set_status(STATUS.DATA_NOT_FOUND, resp)
        
        return Result(status, None)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def check_node_conn_status(self, nodeId):
        """Return the connection status of the node to the controller:  
        
        :param string nodeId: Identifier for the node for which to get the config status
        :return: Status of the node's connection to the controller.
        :rtype: None or :class:`pybvc.common.status.OperStatus`
        
        - STATUS.CONN_ERROR: if the controller did not respond.
        - STATUS.CTRL_INTERNAL_ERROR: if the controller responded but did not provide any status.
        - STATUS.NODE_CONNECTED: if the node is connected
        - STATUS.NODE_DISCONNECTED: if the node is not connected
        - STATUS.DATA_NOT_FOUND: if node is not configured.
        - STATUS.HTTP_ERROR: if the controller responded with an error status code.
        
        """
        status = OperStatus()
        templateUrl = "http://{}:{}/restconf/operational/opendaylight-inventory:nodes"
        url = templateUrl.format(self.ipAddr, self.portNum)
        
        resp = self.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            found = False
            connected = False
            p1 = 'nodes'
            p2 = 'node'
            if(p1 in resp.content and p2 in resp.content):
                itemlist = json.loads(resp.content).get(p1).get(p2)
                for item in itemlist:
                    p3 = 'id'
                    if(p3 in item and item[p3] == nodeId):
                        found = True
                        p4 = 'netconf-node-inventory:connected'
                        if (p4 in item and item[p4] == True):
                            connected = True
                        break
            if(connected):
                status.set_status(STATUS.NODE_CONNECTED)
            elif(found):
                status.set_status(STATUS.NODE_DISONNECTED)
            else:
                status.set_status(STATUS.NODE_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return Result(status, None)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_all_nodes_in_config(self):
        """Return a list of nodes in the controller's configuration data store
        
        :return: A tuple:  Status, list of nodes in the config data store of the controller
        :rtype: :class:`pybvc.common.status.OperStatus`, list
        
        - STATUS.CONN_ERROR:  if the controller did not respond. List is empty.
        - STATUS.CTRL_INTERNAL_ERROR:  if the controller responded but did not provide any status. List is empty.
        - STATUS.OK:  Success. List is valid.
        - STATUS.DATA_NOT_FOUND:  Success.  List is empty.
        - STATUS.HTTP_ERROR:  if the controller responded with an error status code.
        
        """
        status = OperStatus()
        templateUrl = "http://{}:{}/restconf/config/opendaylight-inventory:nodes"
        url = templateUrl.format(self.ipAddr, self.portNum)
        nlist = [] 
        
        resp = self.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            p1 = 'nodes'
            p2 = 'node'
            if(p1 in resp.content and p2 in resp.content):
                elemlist = json.loads(resp.content).get(p1).get(p2)
                for elem in elemlist:
                    p3 = 'id'
                    if(p3 in elem):
                        nlist.append(str(elem[p3]))
                status.set_status(STATUS.OK)
            else:
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return Result(status, nlist)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_all_nodes_conn_status(self):
        """Return a list of nodes and the status of their connection to the controller.
        
        :return: A tuple:  Status, list of nodes the status of their connection to the controller
        :rtype: :class:`pybvc.common.status.OperStatus`, list of dict [{node:<node id>, connected:<boolean>},...]
        
        - STATUS.CONN_ERROR:  if the controller did not respond. List is empty.
        - STATUS.CTRL_INTERNAL_ERROR:  if the controller responded but did not provide any status. List is empty.
        - STATUS.OK:  Success. List is valid.  
        - STATUS.DATA_NOT_FOUND:  Success.  List is empty.
        - STATUS.HTTP_ERROR:  if the controller responded with an error status code.
        
        """
        
        status = OperStatus()
        templateUrl = "http://{}:{}/restconf/operational/opendaylight-inventory:nodes"
        url = templateUrl.format(self.ipAddr, self.portNum)
        nlist = [] 
        
        resp = self.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            p1 = 'nodes'
            p2 = 'node'
            if(p1 in resp.content and p2 in resp.content):
                status.set_status(STATUS.OK)
                itemlist = json.loads(resp.content).get(p1).get(p2)
                for item in itemlist:
                    p3 = 'id'
                    if (p3 in item):
                        nd = dict()
                        nd.update({p2 : item[p3]})
                        p4 = 'netconf-node-inventory:connected'
                        p5 = 'connected'
                        # OpenFlow devices on the Controller are always prefixed with the
                        # 'openflow' keyword.
                        # An OpenFlow device is connecting to the Controller (not vice versa,
                        # as in case with NETCONF). So if we see an OpenFlow device in the
                        # Controller's operational inventory store then 'connected' status
                        # for the device is True.
                        p6 = 'openflow'
                        if (p6 in item[p3]):
                            nd.update({p5 : True})
                        elif ((p4 in item) and (item[p4] == True)):
                            nd.update({p5 : True})
                        else:
                            nd.update({p5 : False})
                        nlist.append(nd)
            else:
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return Result(status, nlist)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_netconf_nodes_in_config(self):
        """Return a list of NETCONF nodes in the controller's configuration data store
        
        :return: A tuple:  Status, list of nodes in the config data store of the controller
        :rtype: :class:`pybvc.common.status.OperStatus`, list
        
        - STATUS.CONN_ERROR:  if the controller did not respond. List is empty.
        - STATUS.CTRL_INTERNAL_ERROR:  if the controller responded but did not provide any status. List is empty.
        - STATUS.OK:  Success. List is valid.
        - STATUS.DATA_NOT_FOUND:  Success.  List is empty.
        - STATUS.HTTP_ERROR:  if the controller responded with an error status code.
        
        """
        
        status = OperStatus()
        templateUrl = "http://{}:{}/restconf/config/opendaylight-inventory:nodes"
        url = templateUrl.format(self.ipAddr, self.portNum)
        nlist = []
        
        resp = self.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            p1 = 'nodes'
            p2 = 'node'
            if(p1 in resp.content and p2 in resp.content):
                elemlist = json.loads(resp.content).get(p1).get(p2)
                for elem in elemlist:
                    p3 = 'id'
                    # OpenFlow devices on the Controller are always prefixed
                    # with the 'openflow' keyword So we use an extra check for
                    # the 'openflow' prefixed entries in order to ignore them
                    p4 = 'openflow'
                    if(p3 in elem and p4 not in elem[p3]):
                        nlist.append(str(elem[p3]))
                status.set_status(STATUS.OK)
            else:
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return Result(status, nlist)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_netconf_nodes_conn_status(self):
        """Return a list of NETCONF nodes and the status of their connection to the controller.
        
        :return: A tuple:  Status, list of nodes the status of their connection to the controller
        :rtype: :class:`pybvc.common.status.OperStatus`, list of dict [{node:<node id>, connected:<boolean>},...]
        
        - STATUS.CONN_ERROR:  if the controller did not respond. List is empty.
        - STATUS.CTRL_INTERNAL_ERROR:  if the controller responded but did not provide any status. List is empty.
        - STATUS.OK:  Success. List is valid.
        - STATUS.DATA_NOT_FOUND:  Success.  List is empty.
        - STATUS.HTTP_ERROR:  if the controller responded with an error status code.
        
        """
        
        status = OperStatus()
        templateUrl = "http://{}:{}/restconf/operational/opendaylight-inventory:nodes"
        url = templateUrl.format(self.ipAddr, self.portNum)
        nlist = [] 
        
        resp = self.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            p1 = 'nodes'
            p2 = 'node'
            if(p1 in resp.content and p2 in resp.content):
                status.set_status(STATUS.OK)
                itemlist = json.loads(resp.content).get(p1).get(p2)
                for item in itemlist:
                    p3 = 'id'
                    # OpenFlow devices on the Controller are always prefixed with
                    # the 'openflow' keyword. So we use an extra check for the
                    # 'openflow' in order to ignore them
                    p4 = 'openflow'
                    if (p3 in item and p4 not in item[p3]):
                        nd = dict()
                        nd.update({p2 : item[p3]})
                        p5 = 'netconf-node-inventory:connected'
                        p6 = 'connected'
                        if ((p5 in item) and (item[p5] == True)):
                            nd.update({p6 : True})
                        else:
                            nd.update({p6 : False})
                        nlist.append(nd)
            else:
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return Result(status, nlist)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_schemas(self, nodeName):
        """Return a list of YANG model schemas for the node.
        
        :param string nodeName: name of the node from the :py:meth:get_all_nodes_in_config 
        :return: A tuple:  Status, list of YANG schemas for the node.
        :rtype: :class:`pybvc.common.status.OperStatus`, JSON listing information about the YANG schemas for the node
        
        - STATUS.CONN_ERROR:  if the controller did not respond. List is empty.
        - STATUS.CTRL_INTERNAL_ERROR:  if the controller responded but did not provide any status. List is empty.
        - STATUS.OK:  Success. List is valid.
        - STATUS.HTTP_ERROR:  if the controller responded with an error status code.
        
        """
        
        status = OperStatus()
        templateUrl = "http://{}:{}/restconf/operational/opendaylight-inventory:nodes/node/{}/yang-ext:mount/ietf-netconf-monitoring:netconf-state/schemas"
        url = templateUrl.format(self.ipAddr, self.portNum, nodeName)
        slist = None
        
        resp = self.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            p1 = 'schemas'
            p2 = 'schema'
            if(p1 in resp.content and p2 in resp.content):
                status = OperStatus(STATUS.OK)
                data = json.loads(resp.content).get(p1).get(p2)
                slist = data
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return Result(status, slist)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_schema(self, nodeName, schemaId, schemaVersion):
        """Return a YANG schema for the indicated schema on the indicated node.
        
        :param string nodeName: name of the node from the :py:meth:get_all_nodes_in_config 
        :param string schemaId: id of schema
        :param string schemaVersion: version of the schema
        :return: A tuple:  Status, YANG schema.
        :rtype: :class:`pybvc.common.status.OperStatus`, YANG schema 
        
        - STATUS.CONN_ERROR:  if the controller did not respond. schema is empty.
        - STATUS.CTRL_INTERNAL_ERROR:  if the controller responded but did not provide any status. schema is empty.
        - STATUS.OK:  Success. result is valid.
        - STATUS.DATA_NOT_FOUND:  Data missing or in unexpected format.
        - STATUS.HTTP_ERROR:  if the controller responded with an error status code.
        
        """
        
        status = OperStatus()
        templateUrl = "http://{}:{}/restconf/operations/opendaylight-inventory:nodes/node/{}/yang-ext:mount/ietf-netconf-monitoring:get-schema"
        url = templateUrl.format(self.ipAddr, self.portNum, nodeName) 
        headers = {'content-type': 'application/yang.data+json', 'accept': 'text/json, text/html, application/xml, */*'}
        payload = {'input': {'identifier' : schemaId, 'version' : schemaVersion, 'format' : 'yang'}}
        schema = None
        
        resp = self.http_post_request(url, json.dumps(payload), headers)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            if(resp.headers.get('content-type') == "application/xml"):
                doc = xmltodict.parse(resp.content)
                try:
                    p1 = 'get-schema'
                    p2 = 'output'
                    p3 = 'data'
                    schema = doc[p1][p2][p3]
                    status.set_status(STATUS.OK)
                except (KeyError, TypeError, ValueError) as e:
                    print repr(e)
                    status.set_status(STATUS.DATA_NOT_FOUND)
            else:
                status.set_status(STATUS.DATA_NOT_FOUND)
                print "TBD: not implemented content type parser"
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return Result(status, schema)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_netconf_operations(self, nodeName):
        """Return a list of operations supported by the indicated node.
        
        :param string nodeName: name of the node from the :py:meth:get_all_nodes_in_config 
        :return: A tuple:  Status, operations supported by indicated node.
        :rtype: :class:`pybvc.common.status.OperStatus`, JSON listing the operations 
        
        - STATUS.CONN_ERROR:  if the controller did not respond. operations info is empty.
        - STATUS.CTRL_INTERNAL_ERROR:  if the controller responded but did not provide any status. operations info is empty.
        - STATUS.OK:  Success. operations info is valid.
        - STATUS.DATA_NOT_FOUND:  Data missing or in unexpected format.
        - STATUS.HTTP_ERROR:  if the controller responded with an error status code.
        
        """
        
        status = OperStatus()
        templateUrl = "http://{}:{}/restconf/operations/opendaylight-inventory:nodes/node/{}/yang-ext:mount/"
        url = templateUrl.format(self.ipAddr, self.portNum, nodeName)
        olist = None
        
        resp = self.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            p1 = 'operations'
            if(p1 in resp.content):
                olist = json.loads(resp.content).get(p1)
                status.set_status(STATUS.OK)
            else:
                status.set_status(STATUS.DATA_NOT_FOUND, resp)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return Result(status, olist)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_all_modules_operational_state(self):
        """Return a list of modules and their operational state.
        
        :return: A tuple:  Status, modules and their operational state.
        :rtype: :class:`pybvc.common.status.OperStatus`, JSON listing modules and their operational state 
        
        - STATUS.CONN_ERROR:  if the controller did not respond. state info is empty.
        - STATUS.CTRL_INTERNAL_ERROR:  if the controller responded but did not provide any status. state info is empty.
        - STATUS.OK:  Success. state info is valid.
        - STATUS.DATA_NOT_FOUND:  Data missing or in unexpected format.
        - STATUS.HTTP_ERROR:  if the controller responded with an error status code.
        
        """
        
        status = OperStatus()
        templateUrl = "http://{}:{}/restconf/operational/opendaylight-inventory:nodes/node/controller-config/yang-ext:mount/config:modules"
        url = templateUrl.format(self.ipAddr, self.portNum)
        mlist = None
        
        resp = self.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            try:
                p1 = 'modules'
                p2 = 'module'
                mlist = json.loads(resp.content.replace('\\\n','')).get(p1).get(p2)
                status.set_status(STATUS.OK)
            except (KeyError, TypeError, ValueError)as  e:
                print repr(e)
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return Result(status, mlist)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_module_operational_state(self, moduleType, moduleName):
        """Return operational state for specified module.
        
        :param string moduleType: module type
        :param string moduleName: module name
        :return: A tuple:  Status, operational state for specified module.
        :rtype: :class:`pybvc.common.status.OperStatus`, JSON providing operational state
        
        - STATUS.CONN_ERROR:  if the controller did not respond. state info is empty.
        - STATUS.CTRL_INTERNAL_ERROR:  if the controller responded but did not provide any status. state info is empty.
        - STATUS.OK:  Success. state info is valid.
        - STATUS.DATA_NOT_FOUND:  Data missing or in unexpected format.
        - STATUS.HTTP_ERROR:  if the controller responded with an error status code.
        
        """
        
        status = OperStatus()
        templateUrl = "http://{}:{}/restconf/operational/opendaylight-inventory:nodes/node/controller-config/yang-ext:mount/config:modules/module/{}/{}"
        url = templateUrl.format(self.ipAddr, self.portNum, moduleType, moduleName)
        module = None
        
        resp = self.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            p1 = 'module'
            if(p1 in resp.content):
                module = json.loads(resp.content).get(p1)
                status.set_status(STATUS.OK)
            else:
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return Result(status, module)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_sessions_info(self, nodeName):
        """Return sessions for indicated node.
        
        :param string nodeName: name of the node from the :py:meth:get_all_nodes_in_config
        :return: A tuple:  Status, list of sessions for indicated node 
        :rtype: :class:`pybvc.common.status.OperStatus`, JSON providing sessions
        
        - STATUS.CONN_ERROR:  if the controller did not respond. session info is empty.
        - STATUS.CTRL_INTERNAL_ERROR:  if the controller responded but did not provide any status. session info is empty.
        - STATUS.OK:  Success. session info is valid.
        - STATUS.DATA_NOT_FOUND:  Data missing or in unexpected format.
        - STATUS.HTTP_ERROR:  if the controller responded with an error status code.
        
        """
        
        status = OperStatus()
        templateUrl = "http://{}:{}/restconf/operational/opendaylight-inventory:nodes/node/{}/yang-ext:mount/ietf-netconf-monitoring:netconf-state/sessions"
        url = templateUrl.format(self.ipAddr, self.portNum, nodeName)
        slist = None
        
        resp = self.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            p1 = 'sessions'
            if(p1 in resp.content):
                slist = json.loads(resp.content).get(p1)
                status.set_status(STATUS.OK)
            else:
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return Result(status, slist)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_streams_info(self):
        """Return streams available for subscription.
        
        :return: A tuple:  Status, list of streams 
        :rtype: :class:`pybvc.common.status.OperStatus`, JSON providing list of streams
        
        - STATUS.CONN_ERROR:  if the controller did not respond. stream info is empty.
        - STATUS.CTRL_INTERNAL_ERROR:  if the controller responded but did not provide any status. stream info is empty.
        - STATUS.OK:  Success. stream info is valid.
        - STATUS.DATA_NOT_FOUND:  Data missing or in unexpected format.
        - STATUS.HTTP_ERROR:  if the controller responded with an error status code.
        
        """
        
        status = OperStatus()
        templateUrl = "http://{}:{}/restconf/streams"        
        url = templateUrl.format(self.ipAddr, self.portNum)
        slist = None
        
        resp = self.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            p1 = 'streams'
            if(p1 in resp.content):
                slist = json.loads(resp.content).get(p1)
                status.set_status(STATUS.OK)
            else:
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return Result(status, slist)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_service_providers_info(self):
        """Return a list of service providers available.
        
        :return: A tuple:  Status, list of service providers 
        :rtype: :class:`pybvc.common.status.OperStatus`, JSON providing list of service providers
        
        - STATUS.CONN_ERROR:  if the controller did not respond. provider info is empty.
        - STATUS.CTRL_INTERNAL_ERROR:  if the controller responded but did not provide any status. provider info is empty.
        - STATUS.OK:  Success. provide info is valid.
        - STATUS.DATA_NOT_FOUND:  Data missing or in unexpected format.
        - STATUS.HTTP_ERROR:  if the controller responded with an error status code.
        
        """
        
        status = OperStatus()
        templateUrl = "http://{}:{}/restconf/config/opendaylight-inventory:nodes/node/controller-config/yang-ext:mount/config:services"
        url = templateUrl.format(self.ipAddr, self.portNum)
        slist = None
        
        resp = self.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            p1 = 'services'
            p2 = 'service'
            if(p1 in resp.content and p2 in resp.content):
                slist = json.loads(resp.content).get(p1).get(p2)
                status.set_status(STATUS.OK)
            else:
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return Result(status, slist)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_service_provider_info(self, name):
        """Return info about a single service provider.
        
        :param string name: name of the provider from the :py:meth:get_service_providers_info 
        :return: A tuple:  Status, info about the service provider 
        :rtype: :class:`pybvc.common.status.OperStatus`, JSON providing info about the service provider

        - STATUS.CONN_ERROR:  if the controller did not respond. provider info is empty.
        - STATUS.CTRL_INTERNAL_ERROR:  if the controller responded but did not provide any status. provider info is empty.
        - STATUS.OK:  Success. provide info is valid.
        - STATUS.DATA_NOT_FOUND:  Data missing or in unexpected format.
        - STATUS.HTTP_ERROR:  if the controller responded with an error status code.
        
        """
        
        status = OperStatus()
        templateUrl = "http://{}:{}/restconf/config/opendaylight-inventory:nodes/node/controller-config/yang-ext:mount/config:services/service/{}"
        url = templateUrl.format(self.ipAddr, self.portNum, name)         
        service = None
        
        resp = self.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            p1 = 'service'
            if(p1 in resp.content):
                service = json.loads(resp.content).get(p1)
                status.set_status(STATUS.OK)
            else:
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return Result(status, service)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def add_netconf_node(self, node):
        """ Connect a netconf device to the controller (for example connect vrouter to controller via NetConf)
        
        :param node: :class:`pybvc.controller.netconfnode.NetconfNode`
        :return: A tuple:  Status, JSON response from controller.
        :rtype: :class:`pybvc.common.status.OperStatus`, JSON providing response from adding netconf noed.
        
        - STATUS.CONN_ERROR:  if the controller did not respond. provider info is empty.
        - STATUS.CTRL_INTERNAL_ERROR:  if the controller responded but did not provide any status. provider info is empty.
        - STATUS.OK:  Success. provide info is valid.
        - STATUS.HTTP_ERROR:  if the controller responded with an error status code.
        
        """
        
        status = OperStatus()
        templateUrl = "http://{}:{}/restconf/config/opendaylight-inventory:nodes/node/controller-config/yang-ext:mount/config:modules"
        xmlPayloadTemplate = '''
        <module xmlns="urn:opendaylight:params:xml:ns:yang:controller:config">
          <type xmlns:prefix="urn:opendaylight:params:xml:ns:yang:controller:md:sal:connector:netconf">prefix:sal-netconf-connector</type>
          <name>{}</name>
          <address xmlns="urn:opendaylight:params:xml:ns:yang:controller:md:sal:connector:netconf">{}</address>
          <port xmlns="urn:opendaylight:params:xml:ns:yang:controller:md:sal:connector:netconf">{}</port>
          <username xmlns="urn:opendaylight:params:xml:ns:yang:controller:md:sal:connector:netconf">{}</username>
          <password xmlns="urn:opendaylight:params:xml:ns:yang:controller:md:sal:connector:netconf">{}</password>
          <tcp-only xmlns="urn:opendaylight:params:xml:ns:yang:controller:md:sal:connector:netconf">{}</tcp-only>
          <event-executor xmlns="urn:opendaylight:params:xml:ns:yang:controller:md:sal:connector:netconf">
            <type xmlns:prefix="urn:opendaylight:params:xml:ns:yang:controller:netty">prefix:netty-event-executor</type>
            <name>global-event-executor</name>
          </event-executor>
          <binding-registry xmlns="urn:opendaylight:params:xml:ns:yang:controller:md:sal:connector:netconf">
            <type xmlns:prefix="urn:opendaylight:params:xml:ns:yang:controller:md:sal:binding">prefix:binding-broker-osgi-registry</type>
            <name>binding-osgi-broker</name>
          </binding-registry>
          <dom-registry xmlns="urn:opendaylight:params:xml:ns:yang:controller:md:sal:connector:netconf">
            <type xmlns:prefix="urn:opendaylight:params:xml:ns:yang:controller:md:sal:dom">prefix:dom-broker-osgi-registry</type>
            <name>dom-broker</name>
          </dom-registry>
          <client-dispatcher xmlns="urn:opendaylight:params:xml:ns:yang:controller:md:sal:connector:netconf">
            <type xmlns:prefix="urn:opendaylight:params:xml:ns:yang:controller:config:netconf">prefix:netconf-client-dispatcher</type>
            <name>global-netconf-dispatcher</name>
          </client-dispatcher>
          <processing-executor xmlns="urn:opendaylight:params:xml:ns:yang:controller:md:sal:connector:netconf">
            <type xmlns:prefix="urn:opendaylight:params:xml:ns:yang:controller:threadpool">prefix:threadpool</type>
            <name>global-netconf-processing-executor</name>
          </processing-executor>
        </module>
        '''
        payload = xmlPayloadTemplate.format(node.name, node.ipAddr, node.portNum, node.adminName, node.adminPassword, node.tcpOnly)
        url = templateUrl.format(self.ipAddr, self.portNum)
        headers = {'content-type': 'application/xml', 'accept': 'application/xml'}
        
        resp = self.http_post_request(url, payload, headers)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200 or resp.status_code == 204):
            status.set_status(STATUS.OK)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return Result(status, resp)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def delete_netconf_node(self, netconfdev):
        """ Disconnect a netconf device from the controller
        
        :param netconfdev: :class:`pybvc.controller.netconfnode.NetconfNode`
        :return: A tuple:  Status, None.
        :rtype: :class:`pybvc.common.status.OperStatus`, JSON providing response from adding netconf noed.
        
        - STATUS.CONN_ERROR:  if the controller did not respond. 
        - STATUS.CTRL_INTERNAL_ERROR:  if the controller responded but did not provide any status. 
        - STATUS.OK:  Success. 
        - STATUS.HTTP_ERROR:  if the controller responded with an error status code. 
        
        """
        
        status = OperStatus()
        templateUrl = "http://{}:{}/restconf/config/opendaylight-inventory:nodes/node/controller-config/yang-ext:mount/config:modules/module/odl-sal-netconf-connector-cfg:sal-netconf-connector/{}"
        url = templateUrl.format(self.ipAddr, self.portNum, netconfdev.name)
        
        resp = self.http_delete_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            status.set_status(STATUS.OK)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return Result(status, None)
    
    #---------------------------------------------------------------------------
    # TBD: 
    # NOTE: It is unclear which NETCONF node attributes are allowed for dynamic
    #       configuration changes. For now just follow an example that is
    #       published on ODL wiki:
    #       https://wiki.opendaylight.org/view/OpenDaylight_Controller:Config:Examples:Netconf
    #---------------------------------------------------------------------------
    def modify_netconf_node_in_config(self, netconfdev):
        """ Modify connected netconf device's info in the controller
        
        :param netconfdev: :class:`pybvc.controller.netconfnode.NetconfNode`
        :return: A tuple:  Status, None.
        :rtype: :class:`pybvc.common.status.OperStatus`, JSON providing response from adding netconf noed.
        
        - STATUS.CONN_ERROR:  if the controller did not respond.
        - STATUS.CTRL_INTERNAL_ERROR:  if the controller responded but did not provide any status.
        - STATUS.OK:  Success.
        - STATUS.HTTP_ERROR:  if the controller responded with an error status code. 
        
        """
        
        status = OperStatus()
        templateUrl = "http://{}:{}/restconf/config/opendaylight-inventory:nodes/node/controller-config/yang-ext:mount/config:modules"
        url = templateUrl.format(self.ipAddr, self.portNum)
        xmlPayloadTemplate = '''
        <module xmlns="urn:opendaylight:params:xml:ns:yang:controller:config">
          <type xmlns:prefix="urn:opendaylight:params:xml:ns:yang:controller:md:sal:connector:netconf">prefix:sal-netconf-connector</type>
          <name>{}</name>
          <username xmlns="urn:opendaylight:params:xml:ns:yang:controller:md:sal:connector:netconf">{}</username>
          <password xmlns="urn:opendaylight:params:xml:ns:yang:controller:md:sal:connector:netconf">{}</password>
        </module>
        '''
        payload = xmlPayloadTemplate.format(netconfdev.devName, netconfdev.adminName, netconfdev.adminPassword)
        headers = {'content-type': 'application/xml', 'accept': 'application/xml'}
        
        resp = self.http_post_request(url, payload, headers)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            status.set_status(STATUS.OK)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return Result(status, None)
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_ext_mount_config_url(self, node):
        templateUrl = "http://{}:{}/restconf/config/opendaylight-inventory:nodes/node/{}/yang-ext:mount/"
        url = templateUrl.format(self.ipAddr, self.portNum, node)
        return url
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_ext_mount_operational_url(self, node):
        templateUrl = "http://{}:{}/restconf/operational/opendaylight-inventory:nodes/node/{}/yang-ext:mount/"
        url = templateUrl.format(self.ipAddr, self.portNum, node)
        return url
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_node_operational_url(self, node):
        templateUrl = "http://{}:{}/restconf/operational/opendaylight-inventory:nodes/node/{}"
        url = templateUrl.format(self.ipAddr, self.portNum, node)
        return url

    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_node_config_url(self, node):
        templateUrl = "http://{}:{}/restconf/config/opendaylight-inventory:nodes/node/{}"
        url = templateUrl.format(self.ipAddr, self.portNum, node)
        return url

    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_openflow_nodes_operational_list(self):
        status = OperStatus()
        templateUrl = "http://{}:{}/restconf/operational/opendaylight-inventory:nodes"
        url = templateUrl.format(self.ipAddr, self.portNum)
        nlist = []
        resp = self.http_get_request(url, data=None, headers=None)
        if(resp == None):
            status.set_status(STATUS.CONN_ERROR)
        elif(resp.content == None):
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif (resp.status_code == 200):
            p1 = 'nodes'
            p2 = 'node'
            if(p1 in resp.content and p2 in resp.content):
                elist = json.loads(resp.content).get(p1).get(p2)
                if isinstance (elist, list):
                    p3 = 'id'
                    p4 = 'openflow'
                    for item in elist:
                        if (isinstance (item, dict) and p3 in item and item[p3].startswith(p4)):
                            nlist.append(item[p3])
                status.set_status(STATUS.OK)
            
            else:
                status.set_status(STATUS.DATA_NOT_FOUND)
        else:
            status.set_status(STATUS.HTTP_ERROR, resp)
        
        return Result(status, nlist) 
    
