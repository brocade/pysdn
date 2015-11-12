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

@authors: Gary Greenberg
@status: Development
@version: 1.0.0

controller.py: BSC Overlay Manager Application's properties and communication methods


"""

from pysdn.common.result import Result
from pysdn.common.status import OperStatus, STATUS
from pysdn.controller.controller import Controller


# Class that represents an Overlay Application running on a Controller instance.
class Ovrly_mgr(Controller, object):
    def __init__(self, ipAddr, portNum, adminName, adminPassword, timeout):
        super(Ovrly_mgr, self).__init__(ipAddr, portNum, adminName, adminPassword, timeout=5)

    def get_ovrl_mgr_hvsr_config_url(self, hvsr_ip, hvr_port):
        templateUrl = "http://{}:{}/restconf/config/brocade-app-overlay:devices/device/{}:{}"
        url = templateUrl.format(self.ipAddr, self.portNum, hvsr_ip, hvr_port)

        return url

    def get_ovrl_mgr_hvsr_oper_url(self, hvsr_ip, hvr_port):
        templateUrl = "http://{}:{}/restconf/operational/brocade-app-overlay:devices/device/{}:{}"
        url = templateUrl.format(self.ipAddr, self.portNum, hvsr_ip, hvr_port)

        return url

    def get_ovrl_mgr_tunnel_hvsr2hvsr_config_url(self, tunnel_name):
        templateUrl = "http://{}:{}/restconf/config/brocade-app-overlay:tunnels/tunnel/{}/"
        url = templateUrl.format(self.ipAddr, self.portNum, tunnel_name)

        return url

    def get_ovrl_mgr_hvsr_vtep_config_url(self, vtep_hvsr):
        templateUrl = "http://{0}:{1}/restconf/config/brocade-app-overlay:devices/device/{2}:{3}/vteps/{4}{5}"
        url = templateUrl.format(self.ipAddr, self.portNum, vtep_hvsr['hvsrIp'], vtep_hvsr['hvsrPortNum'],
                                 vtep_hvsr['vtepName'], vtep_hvsr['hvsrName'])

        return url

    """
    ----------------------
    Register a Hypervisor
    ----------------------
    HTTP Method: PUT
    URL: http://<CONTROLLER_IP>:8181/restconf/config/brocade-app-overlay:devices/device/<HYPERVISOR_IP>:<PORT_NUMBER>
     :params:
            - hvsr_ip: VTEP hypervisor IP
            - hvsr_port: VTEP hypervisor port

     :return: Configuration status of the node.
     :rtype: None or :class:`pybvc.common.status.OperStatus`
            - STATUS.CONN_ERROR: If the controller did not respond.
            - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not provide any status.
     """

    def register_hypervisor(self, vtep_hvsr):

        status = OperStatus()

        url = self.get_ovrl_mgr_hvsr_config_url(vtep_hvsr['hvsrIp'], vtep_hvsr['hvsrPortNum'])
        var = '{{\"device\": [{{\"ip-address\": \"{0}\",\"user-name\": \"\",\"portnumber\": \"{1}\",\"device-type\": \"hypervisor\",\"name\": \"\",\"device-id\": \"{2}:{3}\",\"password\": \"\"}}]}}'
        payload = var.format(vtep_hvsr['hvsrIp'], vtep_hvsr['hvsrPortNum'], vtep_hvsr['hvsrIp'],
                             vtep_hvsr['hvsrPortNum'])
        headers = {"content-type": "application/json", "accept": "application/json"}

        print(payload)

        resp = self.http_put_request(url, payload, headers)

        print(resp)

        if resp is None:
            status.set_status(STATUS.CONN_ERROR)
        elif resp.content is None:
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif resp.status_code == 200:
            status.set_status(STATUS.NODE_CONFIGURED)
        else:
            status.set_status(STATUS.DATA_NOT_FOUND, resp)

        return Result(status, None)

    """
    ----------------------------
    View details of a hypervisor
    ----------------------------
    HTTP Method: GET
    URL: http://<CONTROLLER_IP>:8181/restconf/operational/brocade-app-overlay:devices/device/<HYPERVISOR_IP>:<PORT_NUMBER>/
     :params:
            - hvsr_ip: VTEP hypervisor IP
            - hvsr_port: VTEP hypervisor port
     :return: Configuration status of the node.
     :rtype: None or :class:`pybvc.common.status.OperStatus`
            - STATUS.CONN_ERROR: If the controller did not respond.
            - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not provide any status.
     """

    def get_hypervisor_details(self, vtep_hvsr):

        status = OperStatus()

        url = self.get_ovrl_mgr_hvsr_oper_url(vtep_hvsr['hvsrIp'], vtep_hvsr['hvsrPortNum'])
        payload = None
        headers = {"content-type": "application/json", "accept": "application/json"}
        timeout = None

        print(url)

        resp = self.http_get_request(url, payload, headers, timeout)

        print(resp)

        if resp is None:
            status.set_status(STATUS.CONN_ERROR)
        elif resp.content is None:
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif resp.status_code == 200:
            status.set_status(STATUS.NODE_CONFIGURED)
        else:
            status.set_status(STATUS.DATA_NOT_FOUND, resp)

        return Result(status, None)

    """
    -------------------
    Delete a hypervisor
    -------------------
    HTTP Method: DELETE
    URL: http://<CONTROLLER_IP>:8181/restconf/config/brocade-app-overlay:devices/device/<HYPERVISOR_IP>:<PORT_NUMBER>/
     :params:
            - hvsr_ip: VTEP hypervisor IP
            - hvsr_port: VTEP hypervisor port

     :return: Configuration status of the node.
     :rtype: None or :class:`pybvc.common.status.OperStatus`
            - STATUS.CONN_ERROR: If the controller did not respond.
            - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not provide any status.
     """

    def delete_hypervisor(self, vtep_hvsr):

        status = OperStatus()

        url = self.get_ovrl_mgr_hvsr_config_url(vtep_hvsr['hvsrIp'], vtep_hvsr['hvsrPortNum'])
        payload = None
        headers = {"content-type": "application/json", "accept": "application/json"}

        resp = self.http_delete_request(url, payload, headers)

        print(resp)

        if resp is None:
            status.set_status(STATUS.CONN_ERROR)
        elif resp.content is None:
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif resp.status_code == 200:
            status.set_status(STATUS.NODE_CONFIGURED)
        else:
            status.set_status(STATUS.DATA_NOT_FOUND, resp)

        return Result(status, None)

    """
    -------------------------------
    Register a VTEP on a hypervisor
    -------------------------------
    HTTP Method: PUT
    URL: http://<CONTROLLER_IP>:8181/restconf/config/brocade-app-overlay:devices/device/<HYPERVISOR_IP>:<PORT_NUMBER> /vteps/Vtep1Hypervisor1
     :params:
            - vtep_num:
            - hvsr_num:
            - hvsr_port: VTEP hypervisor port
            - hvsr_ip: VTEP hypervisor IP
            - hvsr_port: VTEP hypervisor port

            {
                "vteps": [
                    {
                        "name": "Vtep1Hypervisor1",
                        "ip-address":"<VTEP_IP>",
                        "configuration": {
                            "brocade-app-overlay-ovs-vtep:switch-name": "Switch1Hypervisor1"
                    }
            }

     :return: Configuration status of the node.
     :rtype: None or :class:`pybvc.common.status.OperStatus`
            - STATUS.CONN_ERROR: If the controller did not respond.
            - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not provide any status.
     """

    def resister_vtep_on_hypervisor(self, vtep_hvsr):

        status = OperStatus()

        url = self.get_ovrl_mgr_hvsr_vtep_config_url(vtep_hvsr)
        var = '{{\"vteps\": [{{\"name\": \"{0}\",\"ip-address\":\"{1}\",\"configuration\": {{\"brocade-app-overlay-ovs-vtep:switch-name\": \"{2}\"}}}}'
        payload = var.format(vtep_hvsr['vtep_hvsr_name'], vtep_hvsr['hvsrIp'], vtep_hvsr['switchName'])
        headers = {"content-type": "application/json", "accept": "application/json"}

        print(url)

        resp = self.http_put_request(url, payload, headers)

        print(resp)

        if resp is None:
            status.set_status(STATUS.CONN_ERROR)
        elif resp.content is None:
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif resp.status_code == 200:
            status.set_status(STATUS.NODE_CONFIGURED)
        else:
            status.set_status(STATUS.DATA_NOT_FOUND, resp)

        return Result(status, None)

    """
    ---------------------------------------
    Create a tunnel between two hypervisors
    ---------------------------------------
    HTTP Method: PUT
    URL: http://<CONTROLLER_IP>:8181/restconf/config/brocade-app-overlay:tunnels/tunnel/tunnelHypHyp/
     :params:
            - tnl_name: Tunnel name
            - vni_id: VXLAN VNI ID
            - vtep_hvsrA: VTEP hypervisor A
            - vtep_hvsrB: VTEP hypervisor B

    Payload: {
                   "tunnel": [
                       {
                           "tunnel-name": "tunnelHypHyp",
                           "vni-id": 345,
                           "tunnel-endpoints": [
                               {
                                   "device-id": "<HYPERVISOR1_IP>:<PORT_NUMBER>",
                                   "vtep-name": "Vtep1Hypervisor1"
                               },
                               {
                                   "device-id": "<HYPERVISOR2_IP>:<PORT_NUMBER>",
                                   "vtep-name": "Vtep1Hypervisor2"
                               }
                       ]
               }

     :return: Configuration status of the node.
     :rtype: None or :class:`pybvc.common.status.OperStatus`
            - STATUS.CONN_ERROR: If the controller did not respond.
            - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not provide any status.
     """

    def create_tunnel_between_two_hypervisors(self, tnl_name, vni_id, vtep_hvsrA, vtep_hvsrB):

        status = OperStatus()

        url = self.get_ovrl_mgr_tunnel_hvsr2hvsr_config_url(tnl_name)

        var = '{{\"tunnel\": [{{\"tunnel-name\": \"{0}\",\"vni-id\": \"{1}\",\"tunnel-endpoints\": [{{\"device-id\": \"{2}:{3}\",\"vtep-name\": \"{4}\"}},{{\"device-id/": \"{5}:{6}\",\"vtep-name\": \"{7}\"}}]}}'
        payload = var.format(tnl_name, vni_id,
                             vtep_hvsrA['hvsrIp'], vtep_hvsrA['hvsrPortNum'], vtep_hvsrA['vtep_hvsr_name'],
                             vtep_hvsrB['hvsrIp'], vtep_hvsrB['hvsrPortNum'], vtep_hvsrB['vtep_hvsr_name'])
        headers = {"content-type": "application/json", "accept": "application/json"}

        print(payload)

        resp = self.http_put_request(url, payload, headers)

        print(resp)

        if resp is None:
            status.set_status(STATUS.CONN_ERROR)
        elif resp.content is None:
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif resp.status_code == 200:
            status.set_status(STATUS.NODE_CONFIGURED)
        else:
            status.set_status(STATUS.DATA_NOT_FOUND, resp)

        return Result(status, None)

    """
    -------------------------------
    Delete a VTEP from a hypervisor
    -------------------------------
    HTTP Method: DELETE
    URL: URL: http://<CONTROLLER_IP>:8181/restconf/config/brocade-app-overlay:devices/device/<HYPERVISOR_IP>:<PORT_NUMBER>/
     :params:
            - vtep_num:
            - hvsr_num:
            - hvsr_port: VTEP hypervisor port
            - hvsr_ip: VTEP hypervisor IP
            - hvsr_port: VTEP hypervisor port

     :return: Configuration status of the node.
     :rtype: None or :class:`pybvc.common.status.OperStatus`
            - STATUS.CONN_ERROR: If the controller did not respond.
            - STATUS.CTRL_INTERNAL_ERROR: If the controller responded but did not provide any status.
     """

    def delete_vtep_from_hypervisor(self, vtep_hvsr):

        status = OperStatus()

        url = self.get_ovrl_mgr_hvsr_vtep_config_url(vtep_hvsr)
        payload = None
        headers = {"content-type": "application/json", "accept": "application/json"}

        print(url)

        resp = self.http_delete_request(url, payload, headers)

        print(resp)

        if resp is None:
            status.set_status(STATUS.CONN_ERROR)
        elif resp.content is None:
            status.set_status(STATUS.CTRL_INTERNAL_ERROR)
        elif resp.status_code == 200:
            status.set_status(STATUS.NODE_CONFIGURED)
        else:
            status.set_status(STATUS.DATA_NOT_FOUND, resp)

        return Result(status, None)
