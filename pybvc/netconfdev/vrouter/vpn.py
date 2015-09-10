
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

vpn.py: Virtual Private Network (VPN) specific properties and access methods


"""

import json

from pybvc.common.utils import (strip_none,
                                remove_empty_from_dict,
                                dict_keys_underscored_to_dashed)


class Vpn():
    ''' Class representing Virtual Private Network (VPN) configuration '''
    _mn1 = "vyatta-security:security"
    _mn2 = "vyatta-security-vpn-ipsec:vpn"

    def __init__(self):
        self.ipsec = Ipsec()
        self.l2tp = L2tp()
        self.rsa_keys = RsaKeys()

    def to_json(self):
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

    def set_ipsec(self, ipsec):
        if ipsec is not None and isinstance(ipsec, Ipsec):
            self.ipsec = ipsec
        else:
            raise TypeError("")

    def set_l2tp(self, l2tp):
        if l2tp is not None and isinstance(l2tp, L2tp):
            self.l2tp = l2tp
        else:
            raise TypeError("")

    def set_rsa_keys(self, rsa_keys):
        if rsa_keys is not None and isinstance(rsa_keys, RsaKeys):
            self.rsa_keys = rsa_keys
        else:
            raise TypeError("")

    def set_local_key(self, path):
        if isinstance(path, basestring):
            self.rsa_keys.set_local_key(path)
        else:
            raise TypeError("")

    def set_rsa_key(self, name, value):
        if (isinstance(name, basestring) and isinstance(value, basestring)):
            self.rsa_keys.set_rsa_key(name, value)
        else:
            raise TypeError("")

    def set_nat_traversal(self, value):
        if (isinstance(value, bool)):
            self.ipsec.set_nat_traversal(value)
        else:
            raise TypeError("")

    def set_nat_allow_network(self, ipnet):
        self.ipsec.set_nat_allow_network(ipnet)

    def set_l2tp_remote_access_user_auth_mode(self, mode):
        self.l2tp.remote_access.set_auth_mode(mode)

    def set_l2tp_remote_access_user(self, name, pswd):
        self.l2tp.remote_access.set_local_user(name, pswd)

    def set_l2tp_remote_access_ipsec_auth_mode(self, mode):
        self.l2tp.remote_access.set_ipsec_mode(mode)

    def set_l2tp_remote_access_ipsec_auth_pre_shared_secret(self, secret):
            self.l2tp.remote_access.set_ipsec_pre_shared_secret(secret)

    def set_l2tp_remote_access_ipsec_auth_ca_cert_file(self, path):
        self.l2tp.remote_access.ipsec_settings.authentication\
            .set_ca_cert_file(path)

    def set_l2tp_remote_access_ipsec_auth_crl_file(self, path):
        self.l2tp.remote_access.ipsec_settings.authentication\
            .set_crl_file(path)

    def set_l2tp_remote_access_ipsec_auth_srv_cert_file(self, path):
        self.l2tp.remote_access.ipsec_settings.authentication\
            .set_srv_cert_file(path)

    def set_l2tp_remote_access_ipsec_auth_srv_key_file(self, path):
        self.l2tp.remote_access.ipsec_settings.authentication\
            .set_srv_key_file(path)

    def set_l2tp_remote_access_ipsec_auth_srv_key_pswd(self, pswd):
        self.l2tp.remote_access.ipsec_settings.authentication\
            .set_srv_key_pswd(pswd)

    def set_l2tp_remote_access_client_ip_pool(self, start, end):
        self.l2tp.remote_access.set_client_ip_pool(start, end)

    def set_l2tp_remote_access_outside_address(self, ipaddr):
        self.l2tp.remote_access.set_outside_address(ipaddr)

    def set_l2tp_remote_access_outside_nexthop(self, ipaddr):
        self.l2tp.remote_access.set_outside_nexthop(ipaddr)

    def set_l2tp_remote_access_description(self, description):
        self.l2tp.remote_access.set_description(description)

    def set_l2tp_remote_access_server_ip_pool(self, start, end):
        self.l2tp.remote_access.set_server_ip_pool(start, end)

    def set_l2tp_remote_access_dhcp_interface(self, interface):
        self.l2tp.remote_access.set_dhcp_interface(interface)

    def set_l2tp_remote_access_primary_dns_server(self, ipaddr):
        self.l2tp.remote_access.set_primary_dns_server(ipaddr)

    def set_l2tp_remote_access_secondary_dns_server(self, ipaddr):
        self.l2tp.remote_access.set_secondary_dns_server(ipaddr)

    def set_l2tp_remote_access_primary_wins_server(self, ipaddr):
        self.l2tp.remote_access.set_primary_wins_server(ipaddr)

    def set_l2tp_remote_access_secondary_wins_server(self, ipaddr):
        self.l2tp.remote_access.set_secondary_wins_server(ipaddr)

    def set_l2tp_remote_access_mtu(self, mtu):
        self.l2tp.remote_access.set_mtu(mtu)

    def set_ipsec_esp_group_lifetime(self, esp_grp_name, lifetime):
        esp_grp = self._find_create_esp_group(esp_grp_name)
        assert (isinstance(esp_grp, EspGroup))
        esp_grp.set_lifetime(lifetime)

    def set_ipsec_esp_group_proposal_encryption(self, esp_grp_name,
                                                proposal_num,
                                                encryption_cipher):
        esp_grp = self._find_create_esp_group(esp_grp_name)
        assert (isinstance(esp_grp, EspGroup))
        esp_grp.set_proposal_encryption(proposal_num, encryption_cipher)

    def set_ipsec_esp_group_proposal_hash(self, esp_grp_name,
                                          proposal_num,
                                          hash_algorith):
        esp_grp = self._find_create_esp_group(esp_grp_name)
        assert (isinstance(esp_grp, EspGroup))
        esp_grp.set_proposal_hash(proposal_num, hash_algorith)

    def _find_create_esp_group(self, esp_grp_name):
        esp_grp = None
        for item in self.ipsec.esp_group:
            if (item.tagnode == esp_grp_name):
                esp_grp = item
                break
        if (esp_grp is None):
            esp_grp = EspGroup(esp_grp_name)
            self.ipsec.esp_group.append(esp_grp)
        return esp_grp

    def set_ipsec_ike_group_lifetime(self, ike_grp_name, lifetime):
        ike_grp = self._find_create_ike_group(ike_grp_name)
        assert (isinstance(ike_grp, IkeGroup))
        ike_grp.set_lifetime(lifetime)

    def set_ipsec_ike_group_proposal_encryption(self, ike_grp_name,
                                                proposal_num,
                                                encryption_cipher):
        ike_grp = self._find_create_ike_group(ike_grp_name)
        assert (isinstance(ike_grp, IkeGroup))
        ike_grp.set_proposal_encryption(proposal_num, encryption_cipher)

    def set_ipsec_ike_group_proposal_hash(self, ike_grp_name,
                                          proposal_num,
                                          hash_algorith):
        ike_grp = self._find_create_ike_group(ike_grp_name)
        assert (isinstance(ike_grp, IkeGroup))
        ike_grp.set_proposal_hash(proposal_num, hash_algorith)

    def set_ipsec_ike_group_proposal_dh_group(self, ike_grp_name,
                                              proposal_num,
                                              dh_group):
        ike_grp = self._find_create_ike_group(ike_grp_name)
        assert (isinstance(ike_grp, IkeGroup))
        ike_grp.set_proposal_dh_group(proposal_num, dh_group)

    def _find_create_ike_group(self, ike_grp_name):
        ike_grp = None
        for item in self.ipsec.ike_group:
            if (item.tagnode == ike_grp_name):
                ike_grp = item
                break
        if (ike_grp is None):
            ike_grp = IkeGroup(ike_grp_name)
            self.ipsec.ike_group.append(ike_grp)
        return ike_grp

    def set_ipsec_site_to_site_peer_description(self, peer_node, description):
        self.ipsec.site_to_site.set_peer_description(peer_node, description)

    def set_ipsec_site_to_site_peer_auth_mode(self, peer_node, auth_mode):
        self.ipsec.site_to_site.set_peer_auth_mode(peer_node, auth_mode)

    def set_ipsec_site_to_site_peer_auth_preshared_secret(self, peer_node,
                                                          secret):
        self.ipsec.site_to_site.set_peer_auth_preshared_secret(peer_node,
                                                               secret)

    def set_ipsec_site_to_site_peer_auth_rsa_key_name(self, peer_node,
                                                      rsa_key_name):
        self.ipsec.site_to_site.set_peer_auth_rsa_key_name(peer_node,
                                                           rsa_key_name)

    def set_ipsec_site_to_site_peer_auth_remote_id(self, peer_node, remote_id):
        self.ipsec.site_to_site.set_peer_auth_remote_id(peer_node, remote_id)

    def set_ipsec_site_to_site_peer_auth_ca_cert_file(self, peer_node, path):
        self.ipsec.site_to_site.set_peer_auth_ca_cert_file(peer_node, path)

    def set_ipsec_site_to_site_peer_auth_srv_cert_file(self, peer_node, path):
        self.ipsec.site_to_site.set_peer_auth_srv_cert_file(peer_node, path)

    def set_ipsec_site_to_site_peer_auth_srv_key_file(self, peer_node, path):
        self.ipsec.site_to_site.set_peer_auth_srv_key_file(peer_node, path)

    def set_ipsec_site_to_site_peer_auth_srv_key_pswd(self, peer_node, pswd):
        self.ipsec.site_to_site.set_peer_auth_srv_key_pswd(peer_node, pswd)

    def set_ipsec_site_to_site_peer_local_address(self, peer_node,
                                                  local_address):
        self.ipsec.site_to_site.set_peer_local_address(peer_node,
                                                       local_address)

    def set_ipsec_site_to_site_peer_default_esp_group(self, peer_node,
                                                      esp_group):
        self.ipsec.site_to_site.set_peer_default_esp_group(peer_node,
                                                           esp_group)

    def set_ipsec_site_to_site_peer_ike_group(self, peer_node, ike_group):
        self.ipsec.site_to_site.set_peer_ike_group(peer_node, ike_group)

    def set_ipsec_site_to_site_peer_tunnel_local_prefix(self, peer_node,
                                                        tunnel,
                                                        local_prefix):
        self.ipsec.site_to_site.set_peer_tunnel_local_prefix(peer_node,
                                                             tunnel,
                                                             local_prefix)

    def set_ipsec_site_to_site_peer_tunnel_remote_prefix(self, peer_node,
                                                         tunnel,
                                                         remote_prefix):
        self.ipsec.site_to_site.set_peer_tunnel_remote_prefix(peer_node,
                                                              tunnel,
                                                              remote_prefix)


class Ipsec(Vpn):
    ''' Class representing VPN IP security (IPsec) configuration
        Helper sub-class of the 'Vpn' class '''

    def __init__(self):
        ''' Auto update interval for IPsec daemon (must be between 30 and
            65535) '''
        self.auto_update = None
        ''' Option to disable requirement for unique IDs in the Security
            Database '''
        self.disable_uniqreqids = None
        ''' Encapsulating Security Payload (ESP) groups
            (list of 'EspGroup' class instances) '''
        self.esp_group = []
        ''' Internet Key Exchange (IKE) groups
            (list of 'IkeGroup' class instances) '''
        self.ike_group = []
        ''' IPsec logging
           'enumeration: raw', 'crypt', 'parsing', 'emitting', 'control',
           'private', 'all' '''
        self.logging = None
        ''' Network Address Translation (NAT) networks '''
        self.nat_networks = None
        ''' Network Address Translation (NAT) traversal
           enumeration: 'enable', 'disable' '''
        self.nat_traversal = None
        ''' VPN IPSec Profiles
            (list of IpSecProfile class instances) '''
        self.profile = []
        ''' Site to site VPN
            (instance of 'SiteToSite' class)'''
        self.site_to_site = SiteToSite()

    def set_auto_update(self, interval):
        self.auto_update = interval

    def set_disable_uniqreqids(self):
        self.disable_uniqreqids = ""

    def set_nat_traversal(self, value):
        assert(isinstance(value, bool))
        self.nat_traversal = "enable" if (value) else "disable"

    def set_nat_allow_network(self, ipnet):
        if (self.nat_networks is None):
            self.nat_networks = {'allowed_network': []}
        d = {'tagnode': ipnet}
        self.nat_networks['allowed_network'].append(d)


class EspGroup(Ipsec):
    ''' Helper sub-class for 'Ipsec' class '''

    def __init__(self, esp_grp_name):
        self.tagnode = esp_grp_name
        self.lifetime = None
        self.proposal = []

    def set_lifetime(self, lifetime):
        self.lifetime = lifetime

    def set_proposal_encryption(self, proposal_num, encryption_cipher):
        proposal = self._find_create_proposal(proposal_num)
        assert (isinstance(proposal, EspProposal))
        proposal._set_encryption(encryption_cipher)

    def set_proposal_hash(self, proposal_num, hash_algorith):
        proposal = self._find_create_proposal(proposal_num)
        assert (isinstance(proposal, EspProposal))
        proposal._set_hash(hash_algorith)

    def _find_create_proposal(self, proposal_num):
        proposal = None
        for item in self.proposal:
            if (item.tagnode == proposal_num):
                proposal = item
                break
        if (proposal is None):
            proposal = EspProposal(proposal_num)
            self.proposal.append(proposal)
        return proposal


class EspProposal(EspGroup):
    ''' Helper sub-class for 'EspGroup' class '''

    def __init__(self, proposal_num):
        self.tagnode = proposal_num
        self.encryption = None
        self.hash = None

    def _set_encryption(self, encryption_cipher):
        self.encryption = encryption_cipher

    def _set_hash(self, hash_algorith):
        self.hash = hash_algorith


class IkeGroup(Ipsec):
    ''' Helper sub-class for 'Ipsec' class '''

    def __init__(self, ike_grp_name):
        self.tagnode = ike_grp_name
        self.lifetime = None
        self.proposal = []

    def set_lifetime(self, lifetime):
        self.lifetime = lifetime

    def set_proposal_encryption(self, proposal_num, encryption_cipher):
        proposal = self._find_create_proposal(proposal_num)
        assert (isinstance(proposal, IkeProposal))
        proposal._set_encryption(encryption_cipher)

    def set_proposal_hash(self, proposal_num, hash_algorith):
        proposal = self._find_create_proposal(proposal_num)
        assert (isinstance(proposal, IkeProposal))
        proposal._set_hash(hash_algorith)

    def set_proposal_dh_group(self, proposal_num, dh_group):
        proposal = self._find_create_proposal(proposal_num)
        assert (isinstance(proposal, IkeProposal))
        proposal._set_dh_group(dh_group)

    def _find_create_proposal(self, proposal_num):
        proposal = None
        for item in self.proposal:
            if (item.tagnode == proposal_num):
                proposal = item
                break
        if (proposal is None):
            proposal = IkeProposal(proposal_num)
            self.proposal.append(proposal)
        return proposal


class IkeProposal(IkeGroup):
    ''' Helper sub-class for 'IkeGroup' class '''

    def __init__(self, proposal_num):
        self.tagnode = proposal_num
        self.encryption = None
        self.hash = None
        self.dh_group = None

    def _set_encryption(self, encryption_cipher):
        self.encryption = encryption_cipher

    def _set_hash(self, hash_algorith):
        self.hash = hash_algorith

    def _set_dh_group(self, dh_group):
        self.dh_group = dh_group


class SiteToSite(Ipsec):
    ''' Helper sub-class of the 'Ipsec' class '''

    def __init__(self):
        self.peer = []

    def set_peer_description(self, peer_node, description):
        peer = self._find_create_peer(peer_node)
        assert (isinstance(peer, Peer))
        peer.set_description(description)

    def set_peer_auth_mode(self, peer_node, mode):
        peer = self._find_create_peer(peer_node)
        assert (isinstance(peer, Peer))
        peer.set_auth_mode(mode)

    def set_peer_auth_preshared_secret(self, peer_node, secret):
        peer = self._find_create_peer(peer_node)
        assert (isinstance(peer, Peer))
        peer.set_auth_pre_shared_secret(secret)

    def set_peer_auth_rsa_key_name(self, peer_node, rsa_key_name):
        peer = self._find_create_peer(peer_node)
        assert (isinstance(peer, Peer))
        peer.set_auth_rsa_key_name(rsa_key_name)

    def set_peer_auth_remote_id(self, peer_node, remote_id):
        peer = self._find_create_peer(peer_node)
        assert (isinstance(peer, Peer))
        peer.set_auth_remote_id(remote_id)

    def set_peer_auth_ca_cert_file(self, peer_node, path):
        peer = self._find_create_peer(peer_node)
        assert (isinstance(peer, Peer))
        peer.set_auth_ca_cert_file(path)

    def set_peer_auth_srv_cert_file(self, peer_node, path):
        peer = self._find_create_peer(peer_node)
        assert (isinstance(peer, Peer))
        peer.set_auth_srv_cert_file(path)

    def set_peer_auth_srv_key_file(self, peer_node, path):
        peer = self._find_create_peer(peer_node)
        assert (isinstance(peer, Peer))
        peer.set_auth_srv_key_file(path)

    def set_peer_auth_srv_key_pswd(self, peer_node, pswd):
        peer = self._find_create_peer(peer_node)
        assert (isinstance(peer, Peer))
        peer.set_auth_srv_key_pswd(pswd)

    def set_peer_local_address(self, peer_node, local_address):
        peer = self._find_create_peer(peer_node)
        assert (isinstance(peer, Peer))
        peer.set_local_address(local_address)

    def set_peer_default_esp_group(self, peer_node, esp_group):
        peer = self._find_create_peer(peer_node)
        assert (isinstance(peer, Peer))
        peer.set_default_esp_group(esp_group)

    def set_peer_ike_group(self, peer_node, ike_group):
        peer = self._find_create_peer(peer_node)
        assert (isinstance(peer, Peer))
        peer.set_ike_group(ike_group)

    def set_peer_tunnel_local_prefix(self, peer_node, tunnel_id, local_prefix):
        peer = self._find_create_peer(peer_node)
        assert (isinstance(peer, Peer))
        peer.set_tunnel_local_prefix(tunnel_id, local_prefix)

    def set_peer_tunnel_remote_prefix(self, peer_node, tunnel_id,
                                      remote_prefix):
        peer = self._find_create_peer(peer_node)
        assert (isinstance(peer, Peer))
        peer.set_tunnel_remote_prefix(tunnel_id, remote_prefix)

    def _find_create_peer(self, peer_node):
        peer = None
        for item in self.peer:
            if (item.tagnode == peer_node):
                peer = item
                break
        if (peer is None):
            peer = Peer(peer_node)
            self.peer.append(peer)
        return peer


class Peer():
    ''' Helper sub-class of the 'SiteToSite' class'''

    def __init__(self, peer_node):
        self.tagnode = peer_node
        self.description = None
        self.authentication = PeerAuthentication()
        self.default_esp_group = None
        self.ike_group = None
        self.local_address = None
        self.tunnel = []

    def set_description(self, description):
        self.description = description

    def set_auth_mode(self, mode):
        self.authentication.set_auth_mode(mode)

    def set_auth_pre_shared_secret(self, secret):
        self.authentication.set_pre_shared_secret(secret)

    def set_auth_rsa_key_name(self, rsa_key_name):
        self.authentication.set_rsa_key_name(rsa_key_name)

    def set_auth_remote_id(self, remote_id):
        self.authentication.set_remote_id(remote_id)

    def set_auth_ca_cert_file(self, path):
        self.authentication.set_ca_cert_file(path)

    def set_auth_srv_cert_file(self, path):
        self.authentication.set_srv_cert_file(path)

    def set_auth_srv_key_file(self, path):
        self.authentication.set_srv_key_file(path)

    def set_auth_srv_key_pswd(self, pswd):
        self.authentication.set_srv_key_pswd(pswd)

    def set_local_address(self, local_address):
        self.local_address = local_address

    def set_default_esp_group(self, esp_group):
        self.default_esp_group = esp_group

    def set_ike_group(self, ike_group):
        self.ike_group = ike_group

    def set_tunnel_local_prefix(self, tunnel_id, local_prefix):
        tunnel = self._find_create_tunnel(tunnel_id)
        assert (isinstance(tunnel, Tunnel))
        tunnel.set_local(local_prefix)

    def set_tunnel_remote_prefix(self, tunnel_id, remote_prefix):
        tunnel = self._find_create_tunnel(tunnel_id)
        assert (isinstance(tunnel, Tunnel))
        tunnel.set_remote(remote_prefix)

    def _find_create_tunnel(self, tunnel_id):
        tunnel = None
        for item in self.tunnel:
            if (item.tagnode == tunnel_id):
                tunnel = item
                break
        if (tunnel is None):
            tunnel = Tunnel(tunnel_id)
            self.tunnel.append(tunnel)
        return tunnel


class PeerAuthentication(Peer):
    ''' Helper sub-class of the 'Peer' class'''

    def __init__(self):
        self.mode = None
        self.pre_shared_secret = None
        self.rsa_key_name = None
        self.remote_id = None
        self.x509 = PeerCertificate()

    def set_auth_mode(self, mode):
        self.mode = mode

    def set_pre_shared_secret(self, secret):
        self.pre_shared_secret = secret

    def set_rsa_key_name(self, rsa_key_name):
        self.rsa_key_name = rsa_key_name

    def set_remote_id(self, remote_id):
        self.remote_id = remote_id

    def set_ca_cert_file(self, path):
        self.x509.set_ca_cert_file(path)

    def set_srv_cert_file(self, path):
        self.x509.set_srv_cert_file(path)

    def set_srv_key_file(self, path):
        self.x509.set_srv_key_file(path)

    def set_srv_key_pswd(self, pswd):
        self.x509.set_srv_key_pswd(pswd)


class PeerCertificate(PeerAuthentication):
    ''' Helper sub-class of the 'PeerAuthentication' class '''

    def __init__(self):
        ''' File containing the X.509 certificate for the Certificate
            Authority (CA) '''
        self.ca_cert_file = None
        ''' Server key file and password to open it '''
        self.key = {'file': None, 'password': None}
        ''' File containing the X.509 certificate for this host '''
        self.cert_file = None
        ''' File containing the X.509 Certificate Revocation List (CRL) '''
        self.crl_file = None

    def set_ca_cert_file(self, path):
        self.ca_cert_file = path

    def set_srv_key_file(self, path):
        self.key['file'] = path

    def set_srv_key_pswd(self, pswd):
        self.key['password'] = pswd

    def set_srv_cert_file(self, path):
        self.cert_file = path

    def set_crl_file(self, path):
        self.crl_file = path


class Tunnel(Peer):
    ''' Helper sub-class of the 'Peer' class'''

    def __init__(self, tunnel_id):
        self.tagnode = tunnel_id
        self.local = {'prefix': None}
        self.remote = {'prefix': None}

    def set_local(self, local):
        self.local['prefix'] = local

    def set_remote(self, remote):
        self.remote['prefix'] = remote


class L2tp(Vpn):
    ''' Class representing VPN Layer 2 Tunneling Protocol (L2TP) configuration
        Helper sub-class of the 'Vpn' class '''

    def __init__(self):
        self.remote_access = RemoteAccess()


class RemoteAccess(L2tp):
    ''' Helper sub-class of the 'L2tp' class '''

    def __init__(self):
        self.authentication = RemoteAccessAuthentication()
        self.client_ip_pool = None
        self.description = None
        self.dhcp_interface = None
        self.dns_servers = {'server_1': None, 'server_2': None}
        self.ipsec_settings = IpSecSettings()
        self.mtu = None
        self.outside_address = None
        self.outside_nexthop = None
        self.server_ip_pool = None
        self.wins_servers = {'server_1': None, 'server_2': None}

    def set_auth_mode(self, mode):
        self.authentication.set_mode(mode)

    def set_local_user(self, name, pswd):
        self.authentication.set_user(name, pswd)

    def set_ipsec_mode(self, mode):
        self.ipsec_settings.set_mode(mode)

    def set_ipsec_pre_shared_secret(self, secret):
        self.ipsec_settings.set_pre_shared_secret(secret)

    def set_ipsec_ca_cert_file(self, path):
        self.ipsec_settings.authentication.set_ca_cert_file(path)

    def set_ipsec_srv_cert_file(self, path):
        self.ipsec_settings.authentication.set_srv_cert_file(path)

    def set_ipsec_crl_file(self, path):
        self.ipsec_settings.authentication.set_crl_file(path)

    def set_ipsec_srv_key_file(self, path):
        self.ipsec_settings.authentication.set_srv_key_file(path)

    def set_ipsec_srv_key_pswd(self, pswd):
        self.ipsec_settings.authentication.set_srv_key_pswd(pswd)

    def set_client_ip_pool(self, start, end):
        self.client_ip_pool = {'start': start, 'stop': end}

    def set_outside_address(self, ipaddr):
        self.outside_address = ipaddr

    def set_outside_nexthop(self, ipaddr):
        self.outside_nexthop = ipaddr

    def set_description(self, description):
        self.description = description

    def set_server_ip_pool(self, start, end):
        self.server_ip_pool = {'start': start, 'stop': end}

    def set_dhcp_interface(self, interface):
        self.dhcp_interface = interface

    def set_primary_dns_server(self, ipaddr):
        self.dns_servers['server_1'] = ipaddr

    def set_secondary_dns_server(self, ipaddr):
        self.dns_servers['server_2'] = ipaddr

    def set_primary_wins_server(self, ipaddr):
        self.wins_servers['server_1'] = ipaddr

    def set_secondary_wins_server(self, ipaddr):
        self.wins_servers['server_2'] = ipaddr

    def set_mtu(self, mtu):
        self.mtu = mtu


class RemoteAccessAuthentication(RemoteAccess):
    ''' Helper sub-class of the 'RemoteAccess' class '''

    def __init__(self):
        self.local_users = {'username': []}
        self.mode = None

    def set_mode(self, mode):
        self.mode = mode

    def set_user(self, name, pswd):
        d = {'tagnode': name, 'password': pswd}
        self.local_users['username'].append(d)


class IpSecSettings(RemoteAccess):
    ''' Helper sub-class of the 'RemoteAccess' class '''

    def __init__(self):
        self.authentication = IpSecAuthentication()

    def set_mode(self, mode):
        self.authentication.set_mode(mode)

    def set_pre_shared_secret(self, secret):
        self.authentication.set_secret(secret)


class IpSecAuthentication(IpSecSettings):
    ''' Helper sub-class of the 'IpSecSettings' class '''

    def __init__(self):
        self.mode = None
        self.pre_shared_secret = None
        self.x509 = IpSecCertificate()

    def set_mode(self, mode):
        self.mode = mode

    def set_secret(self, secret):
        self.pre_shared_secret = secret

    def set_ca_cert_file(self, path):
        self.x509.set_ca_cert_file(path)

    def set_srv_cert_file(self, path):
        self.x509.set_srv_cert_file(path)

    def set_crl_file(self, path):
        self.x509.set_crl_file(path)

    def set_srv_key_file(self, path):
        self.x509.set_srv_key_file(path)

    def set_srv_key_pswd(self, pswd):
        self.x509.set_srv_key_pswd(pswd)


class IpSecCertificate(IpSecAuthentication):
    ''' Helper sub-class of the 'IpSecAuthentication' class '''

    def __init__(self):
        ''' File containing the X.509 certificate for the Certificate
            Authority (CA) '''
        self.ca_cert_file = None
        ''' File containing the X.509 Certificate Revocation List (CRL) '''
        self.crl_file = None
        ''' File containing the X.509 certificate for the remote access VPN
            server '''
        self.server_cert_file = None
        ''' File containing the private key for the X.509 certificate for the
            remote access VPN server '''
        self.server_key_file = None
        ''' Password that protects the private key '''
        self.server_key_password = None

    def set_ca_cert_file(self, path):
        self.ca_cert_file = path

    def set_crl_file(self, path):
        self.crl_file = path

    def set_srv_cert_file(self, path):
        self.server_cert_file = path

    def set_srv_key_file(self, path):
        self.server_key_file = path

    def set_srv_key_pswd(self, pswd):
        self.server_key_password = pswd


class RsaKeys(Vpn):
    ''' Class representing RSA keys for VPN configuration
        Helper sub-class of the 'Vpn' class '''

    def __init__(self):
        self.local_key = {'file': None}
        self.rsa_key_name = []

    def set_local_key(self, path):
        self.local_key['file'] = path

    def set_rsa_key(self, name, value):
        d = {'rsa_key': value, 'tagnode': name}
        self.rsa_key_name.append(d)
