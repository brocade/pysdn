
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

constants.py: Standardized (well known) numbers


"""

# flake8: noqa

# Ethernet Types for some notable protocols
ETH_TYPE_IPv4       = 2048   # (0x0800)
ETH_TYPE_IPv6       = 34525  # (0x86DD)
ETH_TYPE_ARP        = 2054   # (0x0806)
ETH_TYPE_MPLS_UCAST = 34887  # (0x8847)
ETH_TYPE_MPLS_MCAST = 34888  # (0x8848)
ETH_TYPE_LLDP       = 35020  # (0x88CC)

ETH_TYPE_QINQ       = 34984  # (0x88A8)
ETH_TYPE_DOT1AD     = 34984  # (0x88A8)
ETH_TYPE_STAG       = 34984  # (0x88A8)

ETH_TYPE_DOT1Q      = 33024  # (0x8100)
ETH_TYPE_CTAG       = 33024  # (0x8100)

# IP protocol numbers
IP_PROTO_ICMP   = 1     # (0x01) Internet Control Message Protocol
IP_PROTO_UDP    = 17    # (0x11) User Datagram Protocol
IP_PROTO_TCP    = 6     # (0x06) Transmission Control Protocol
IP_PROTO_TLSP   = 56    # (0x86) Transport Layer Security Protocol
IP_PROTO_ICMPv6 = 58    # (0x3A) ICMP for IPv6

# The IP Differentiated Services Code Points (DSCP)
# Class Selector (CS) are of the form 'xxx000'
# (higher value = higher priority)
IP_DSCP_CS0 = 0           # binary '000000' - equivalent IP precedence value 0 (Routine or Best Effort)
IP_DSCP_CS1 = 8           # binary '001000' - equivalent IP precedence value 1 (Priority)
IP_DSCP_CS2 = 16          # binary '010000' - equivalent IP precedence value 2 (Immediate)
IP_DSCP_CS3 = 24          # binary '011000' - equivalent IP precedence value 3 (Flash)
IP_DSCP_CS4 = 32          # binary '100000' - equivalent IP precedence value 4 (Flash Override)
IP_DSCP_CS5 = 40          # binary '101000' - equivalent IP precedence value 5 (Critical)
IP_DSCP_CS6 = 48          # binary '110000' - equivalent IP precedence value 6 (Internet)
IP_DSCP_CS7 = 56          # binary '111000' - equivalent IP precedence value 7 (Network)

# Assured Forwarding (AF) Per Hop Behavior (PHB) group
# The AF PHB group defines four separate classes
# Within each class, packets are given a drop precedence: high, medium or low
# Higher precedence means more dropping.
# AFxy (x=class, y=drop precedence)
# Class 1
IP_DSCP_AF11 = 10         # binary '001010' - equivalent IP precedence value 1
IP_DSCP_AF12 = 12         # binary '001100' - equivalent IP precedence value 1
IP_DSCP_AF13 = 14         # binary '001110' - equivalent IP precedence value 1
# Class 2
IP_DSCP_AF21 = 18         # binary '010010' - equivalent IP precedence value 2
IP_DSCP_AF22 = 20         # binary '010100' - equivalent IP precedence value 2
IP_DSCP_AF23 = 22         # binary '010110' - equivalent IP precedence value 2
# Class 3
IP_DSCP_AF31 = 26         # binary '011010' - equivalent IP precedence value 3
IP_DSCP_AF32 = 28         # binary '011100' - equivalent IP precedence value 3
IP_DSCP_AF33 = 30         # binary '011110' - equivalent IP precedence value 3
# Class 4
IP_DSCP_AF41 = 34         # binary '100010' - equivalent IP precedence value 4
IP_DSCP_AF42 = 36         # binary '100100' - equivalent IP precedence value 4
IP_DSCP_AF43 = 38         # binary '100110' - equivalent IP precedence value 4

# Expedited Forwarding
IP_DSCP_EF = 46           # binary '101110' - equivalent IP precedence value 5

# The Explicit Congestion Notification (ECN)
# ECN uses the two least significant (right-most) bits of the DiffServ field
# in the IPv4 or IPv6 header to encode four different code points
IP_ECN_NON_ECT = 0  # binary '00' - Non ECN-Capable Transport, NON-ECT
IP_ECN_ECT0    = 2  # binary '10' - ECN Capable Transport, ECT(0)
IP_ECN_ECT1    = 1  # binary '01' - ECN Capable Transport, ECT(1)
IP_ECN_CE      = 3  # binary '11' - Congestion Encountered, CE

# ARP Operation Codes
ARP_REQUEST = 1
ARP_REPLY   = 2

# Ethernet frame Priority Code Points (PCP)
PCP_BE = 1  # Best Effort            (priority 0, lowest)
PCP_BK = 0  # Background             (priority 1)
PCP_EE = 2  # Excellent Effort       (priority 2)
PCP_CA = 3  # Critical Applications  (priority 3)
PCP_VI = 4  # Video                  (priority 4)
PCP_VO = 5  # Voice                  (priority 5)
PCP_IC = 6  # Internetwork Control   (priority 6)
PCP_NC = 7  # Network Control        (priority 7, highest)

# OpenFlow Group types
OFPGT_ALL      = "group-all"      # All (multicast/broadcast) group
OFPGT_SELECT   = "group-select"   # Select group
OFPGT_INDIRECT = "group-indirect" # Indirect group
OFPGT_FF       = "group-ff"       # Fast failover group
