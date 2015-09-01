# Sample Applications for PyBVC
Sample applications demonstrating use of [pybvc](https://github.com/BRCDcomm/pybvc) (a python support library for Brocade Vyatta Controller) to monitor/configure network via Brocade Vyatta Controller (BVC).

## Pre-requisites:
* [pybvc](https://github.com/BRCDcomm/pybvc)

## Installation
```bash
git clone https://github.com/BRCDcomm/pybvc.git
cd pybvc
cd samples
```

## BVC Version Support:
* 1.1.1 folder has been tested with BVC 1.1.1
* 1.2.0 folder has been tested with BVC 1.2.0
* 1.3.0 folder is being tested with BVC 1.3.0 

## Sample Apps

* samples/sampleopenflow/apps/
    * _oftool/oftool_*: A command line tool for obtaining topology, inventory info as well as flow info.  Also provides ability to delete flows.
* samples/sampleopenflow/demos/
    * _demo1_: Get list of OpenFlow nodes and provide generic info for each.
    * _demo2_: Get detailed info about node with specific name (default node name is openflow:1).
    * _demo3_: Get detailed info about ports on a node with specific name (default node name is openflow:1).
    * _demo4_: Add/remove flow to openflow:1 node that Match: Ethernet Type 0x800, IPv4 destination 10.11.12.13/24 Action: Drop
    * _demo5_: Add/remove flow to openflow:1 node that Match: Ethernet Type 0x800, IPv4 source 10.11.12.13/24 Action: Drop
    * _demo6_: Add/remove flow to openflow:1 node that Match: Ethernet Type 0x2d, Ethernet source 00:00:00:00:23:ae, Ethernet destination ff:ff:ff:ff:ff:ff Action: drop
    * _demo7_:  Add/remove flow to openflow:1 node that Match: Ethernet Type 0x800, Ethernet source 00:1a:1b:00:22:aa, Ethernet destination 00:2b:00:60:ff:f1, IPv4 source 44.44.44.1/24, IPv4 destination 55.55.55.1/16, Input Port 13 Action: Output (controller)
    * _demo8_: Add/remove flow to openflow:1 node that Match: Ethernet Type 0x800, Ethernet source 00:1c:01:00:23:aa, Ethernet destination 00:02:02:60:ff:fe, IPv4 source 10.0.245.1/24, IPv4 destination 192.168.1.123/16, IP Protocol Number 56, IP DSCP 15, Input Port 1 Action: Output (controller)
    * _demo9_: Add/remove flow to openflow:1 node that Match: Ethernet Type 0x800, Ethernet source 00:00:00:11:23:ae, Ethernet destination ff:ff:29:01:19:61, IPv4 source 17.1.2.3/8, IPv4 destination 172.168.5.6/16, IP Protocol Number 6, IP DSCP 2, TCP Source Port 25364, TCP Destination Port 8080, Input Port 13 Action: Output (normal)
    * _demo10_: Add/remove flow to openflow:1 node that Match: Ethernet Type 0x800, Ethernet source 00:00:00:11:23:ae, Ethernet destination 20:14:29:01:19:61, IPv4 source 192.1.2.3/10, IPv4 destination 172.168.5.6/18, IP Protocol Number 17, IP DSCP 8, IP ECN 3, UDP Source Port 25364, UDP Destination Port 8080, Input Port 13 Action: Output (normal)
    * _demo11_: Add/remove flow to openflow:1 node that Match: Ethernet Type 0x800, Ethernet source 00:00:00:11:23:ae, Ethernet destination 00:ff:20:01:1a:3d, IPv4 source 17.1.2.3/8, IPv4 destination 172.168.5.6/18, IP Protocol Number 1, IP DSCP 27, IP ECN 3, ICMPv4 Type 6, ICMPv4 Code 3, Input Port 10 Action: Output (normal)
    * _demo12_: Add/remove flow to openflow:1 node that Match: Ethernet Type 0x806, Ethernet source 11:ab:fe:01:03:31,Ethernet destination ff:ff:ff:ff:ff:ff, ARP Operation 1,ARP source IPv4 192.168.4.1, ARP target IPv4 10.21.22.23ARP source hardware address 12:34:56:78:98:ab,ARP target hardware address fe:dc:ba:98:76:54 Action: Output (controller)
    * _demo13_: Add/remove flow to openflow:1 node that Match: Ethernet Type 0x800, Ethernet source 00:00:00:11:23:ad,Ethernet destination 00:ff:29:01:19:61, VLAN ID 100, VLAN PCP 3 Action: Output (controller)
    * _demo14_: Add/remove flow to openflow:1 node that Match: Ethernet Type 0x800, Ethernet source 00:00:00:AA:BB:CC, Ethernet destination FF:FF:AA:BC:ED:FE, Input port 5 Action: Push VLAN / Set Field (VLAN ID 100) / Output (physical port)
    * _demo15_: Add/remove flow to openflow:1 node that pushes ethernet type VLAN traffic to a particular VLAN ID and port 
    * _demo16_: Add/remove flow to openflow:1 node that Match: Ethernet Type 0x86dd, IPv6 Source fe08::2acf:e9ff:fe21:6431/128, IPv6 Destination aabb:1234:2acf:e9ff::fe21:6431/64 Action: Output (controller)
    * _demo17_: Add/remove flow to openflow:1 node that Match: Ethernet Type 0x86dd, IPv6 Source fe80::2acf:e9ff:fe21:6431/128, IPv6 Destination aabb:1234:2acf:e9ff::fe21:6431/64, IP DSCP 8, UDP Source Port 25364, UDP Destination Port 7777 Action: Output (controller)
    * _demo18_: Add/remove flow to openflow:1 node that Match: Ethernet Type 0x86dd, IPv6 Source 2001::2acf:e9ff:fe21:6431/80, IPv6 Destination 2004:1234:2acf:e9ff::fe21:6431/64, IP DSCP 8, TCP Source Port 12345, TCP Destination Port 54321 Action: Output (controller)
    * _demo19_: Add/remove flow to openflow:1 node that Match: Ethernet Type 0x86dd, IPv6 Source 4321::3210:3210:3210:3210/80, IPv6 Destination 1234:1234:1234:1234::5678:5678/64, IPv6 Flow Label 33, IP DSCP 60, TCP Source Port 11111, TCP Destination Port 22222 Action: Output (controller)
    * _demo20_: Add/remove flow to openflow:1 node that Match: Ethernet Type 0x86dd, IPv6 Source 1234:5678:9ABC:DEF0:FDCD:A987:6543:210F/76, IPv6 Destination 2000:2abc:edff:fe00::3456/94, IPv6 Flow Label 15, IP DSCP 60, IP ECN 3, ICMPv6 Type 6, ICPMv6 Code 3, Metadata: 0x0123456789ABCDEF Action: Output (controller)
    * _demo21_: Add/remove flow to openflow:1 node that Match: Ethernet Type 0x86dd, IPv6 Source 1234:5678:9ABC:DEF0:FDCD:A987:6543:210F/76, IPv6 Destination 2000:2abc:edff:fe00::3456/94, IPv6 Flow Label 7, IP DSCP 60, IP ECN 3, TCP Source 1831, TCP Destination 100610, Metadata: 123456789 Action: Output (controller)
    * _demo23_: Add/remove flow to openflow:1 node that Match: Ethernet Type 0x8847, MPLS Label 0x1b In port 13 Action: Set Field (MPLS Label 44, Output (Physical Port Number 14)
    * _demo24_: Add/remove flow to openflow:1 node that Match: Ethernet Type 0x8847, MPLS Label 0x2c In port 14 Action: Pop MPLS (Ethernet Type 34887, Output (Physical Port Number 13)
    * _demo25_: Add/retrieve/remove four flow entries to controller
    * _demo26_: Add/retrieve/remove seven flow entries to controller, display using compressed oxm format (similar to open vswitch).
    * _demo27_: Retrieve and display topology information about network seen by controller.
    * _demo28_: Retrieve and display inventory information about network seen by controller.
    * _demo29_: Notification service example.  Subscribes to controller and receives notifications of any changes to topology and outputs those changes to the screen.  You will need to connect some switches to your controller or
use mininet.
    * _demo30_: Another notifcation service example.  Same as demo29, but it is for changes to inventory instead of topology. 
    * _demo31_: Add/remove flow to openflow:1 node that Match: In port 10, Ethernet Type 0x800, IPv4 dest addr 10.1.2.3/32 Action: Set IPv4 ToS (tos 8), Output (Physical Port Number 15)
    * _demo32_: For each openflow capable switch it lists the group table support.  The switch must support OpenFlow's GroupTable to work otherwise the demo will exit with an error.  Mininet 2.2.0 does not support GroupTable.
    * _demo33_: Creates/Removes an example of multicast/broadcast group table.  The switch must support OpenFlow's GroupTable to work otherwise the demo will show that the group table is not in the operational table (but is in config table).  Mininet 2.2.0 does not support GroupTable.
    * _demo34_: Creates/Removes an example of load balancing group table.  The switch must support OpenFlow's GroupTable to work otherwise the demo will show that the group table is not in the operational table (but is in config table).  Mininet 2.2.0 does not support GroupTable.
    * _demo35_: Creates/Removes an example of 'set of common actions' group table.  The switch must support OpenFlow's GroupTable to work otherwise the demo will show that the group table is not in the operational table (but is in config table).  Mininet 2.2.0 does not support GroupTable.
    * _demo36_: Creates/Removes an example of 'link fast failover' group table.  The switch must support OpenFlow's GroupTable to work otherwise the demo will show that the group table is not in the operational table (but is in config table).  Mininet 2.2.0 does not support GroupTable.
* samples/samplenetconf/demos
    * _ctrl_demo1_: List of YANG models supported by the Controller.
    * _ctrl_demo2_: Retrieve specific YANG model definition from the Controller.
    * _ctrl_demo3_: List of service provider applications on the controller.
    * _ctrl_demo4_: Retrieve specific service provider info.
    * _ctrl_demo5_: List of all NETCONF operations supported by the Controller.
    * _ctrl_demo6_: Show operational state of all configuration modules on the Controller.
    * _ctrl_demo7_: Show operational state of a particular configuration module.
    * _ctrl_demo8_: Show active sessions on the Controller.
    * _ctrl_demo9_: Show notification event streams registered on the Controller.
    * _ctrl_demo10_: Add/remove a NETCONF node to the controller.
    * _ctrl_demo11_: Another example of Add/remove a NETCONF node to the controller.
    * _ctrl_demo12_: Retrieve and display the configured NETCONF nodes.
    * _ctrl_demo13_: Retrieve and display the connection status of NETCONF nodes to the controller.
    * _vr_demo1_: Get supported models of vRouter connected to Controller.
    * _vr_demo2_: Get definition of specific model of vRouter connected.
    * _vr_demo3_: Get vRouter configuration.
    * _vr_demo4_: Get firewall configuration for vRouter.
    * _vr_demo5_: Get information on dataplane interfaces configured on vRouter.
    * _vr_demo6_: Get information on loopback interfaces configured on vRouter".
    * _vr_demo7_: Create complex firewalls for vRouter
    * _vr_demo8_: adds and removes a VPN configuration for Remote Access VPN Configuration Example - L2TP/IPsec with Pre-Shared Key
    * _vr_demo9_: adds and removes a VPN configuration for Remote Access VPN Configuration Example - L2TP/IPsec with X.509 Certificates
    * _vr_demo10_: adds and removes a VPN configuration for site-to-site VPN with pre-shared key (PSK) authentication
    * _vr_demo11_: adds and removes a VPN configuration for site-to-site VPN with RSA Digital Signature authentication
    * _vr_demo12_: adds and removes a VPN configuration for Site-to-Site VPN Configuration - X.509 Certificate Authentication
    * _vr_demo13_: adds and removes a vtun0 OpenVPN tunnel for Site-to-Site Mode with Preshared Secret
    * _vr_demo14_: adds and removes a vtun0 OpenVPN tunnel for Site-to-Site Mode with TLS
* samples/samplenetconf/cmds
    * _mount_: Mount the vRouter onto Controller.
    * _show_cfg_: Show config of vRouter.
    * _show_ctrl_yangmodel_: Return a specified YANG model.
    * _show_ctrl_yangmodels_: Display a list of available YANG models in Controller..
    * _show_dpifcfg_: List configuration of each dataplane interface in vRouter.
    * _show_dpiflist_: List dataplane interfaces of vRouter.
    * _show_firewallcfg_: Show firewall configuration of vRouter.
    * _show_iflist_: List interfaces of vRouter.
    * _show_lbifcfg_: List configuration of each loopback interface in vRouter.
    * _show_lbiflist_: List loopback interfaces of vRouter.
    * _show_mount_: List NETCONF nodes mounted on controller and their connection status.
    * _show_nodeinfo_: List info about node specified in config.yml file.
    * _show_nodelist_: List all nodes known by the Controller.
    * _show_yangmodel_: Return a specified YANG model from vRouter device.
    * _show_yangmodels_: Display a list of available YANG models in vRouter device.
    * _unmount_: Unmount the vRouter specified in config.yml file.


