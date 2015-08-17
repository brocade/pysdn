# pybvc
Python library to program your network via the Brocade SDN Controller

## Other Brocade SDN Controller Libraries
* rubybvc - Ruby gem for Brocade SDN Controller:  https://github.com/BRCDcomm/rubybvc
* perlbsc - Perl library for Brocade SDN Controller:  https://github.com/BRCDcomm/perlbsc

## Current Version:
1.3.2

## Prerequisites
   - Python 2.7.x: 
       - Test if your system already has it

         ```bash
         python --version
         ```
          - If it is installed you should see a response like this (the last digit may be different):

          ```
          Python 2.7.5
          ```
          - If it is not installed, then download and install: https://www.python.org/downloads/
   - pip:  
       - Test if your system already has it:

         ```bash
         pip --version
         ```
         - If it is installed you should see a response similar to this (as long as it is not an error response):

         ```bash
         pip 6.0.8 from /Library/Python/2.7/site-packages/pip-6.0.8-py2.7.egg (python 2.7)
         ```
         - If it is not installed, then download and install:  https://pip.pypa.io/en/stable/installing.html#install-pip

## Installation:
```bash
sudo pip install pybvc
```

## Upgrade:
```bash
sudo pip install pybvc --upgrade
```

## Check installed version:
```bash
pip show pybvc
```

## Contribute:
If you want to contribute to this project, fantastic!  Please check out our CONTRIBUTE.md file for how to do this:
   - [Contribute](https://github.com/BRCDcomm/pybvc/blob/master/CONTRIBUTE.md)

## Documentation:
   - [Introduction Video](http://brcdcomm.github.io/BVC/jekyll/update/devops/netdev/appdev/2015/03/01/restconf-app-2.html)
   - [Programmer's Reference](http://brcdcomm.github.io/pybvc/)

## Sample Applications:
   - [pybvcsamples](https://github.com/brcdcomm/pybvcsamples)
   - To install samples:

     ```bash
     git clone https://github.com/brcdcomm/pybvcsamples.git
     ```
## Twitter:
If you use twitter, then follow [@jebpublic](http://twitter.com/intent/user?screen_name=jebpublic).  This is where announcements about updates are sent.

## Example 1:  Add and remove firewall on Vyatta vrouter5600 via Brocade SDN Controller:

```python
import pybvc

from pybvc.netconfdev.vrouter.vrouter5600 import VRouter5600, Firewall, Rules, Rule
from pybvc.common.status import STATUS
from pybvc.controller.controller import Controller

print (">>> Create Brocade SDN  controller instance")
ctrl = Controller("172.22.18.186", "8181" , "admin" , "admin") 

print (">>> Create Vyatta Router 5600 instance")
vrouter = VRouter5600(ctrl, "vRouter", "172.22.17.107", 830, "vyatta", "vyatta")


print (">>> Connect Vyatta Router 5600 to Brocade SDN Controller via NETCONF")
result = ctrl.add_netconf_node(vrouter)

print (">>> Define new firewall instance ACCEPT-SRC-IPADDR") 
firewall1 = Firewall()    
rules = Rules("ACCEPT-SRC-IPADDR")    
rule = Rule(30)
rule.add_action("accept")
rule.add_source_address("172.22.17.108")    
rules.add_rule(rule)
firewall1.add_rules(rules)


print (">>> Create ACCEPT-SRC-IPADDR on vrouter 5600") 
result = vrouter.create_firewall_instance(firewall1)


print (">>> Define new firewall instance DROP-ICMP") 
firewall2 = Firewall()    
rules = Rules("DROP-ICMP")    
rule = Rule(40)
rule.add_action("drop")
rule.add_icmp_typename("ping")
rules.add_rule(rule)
firewall2.add_rules(rules)   

print (">>> Create DROP-ICMP on vrouter 5600")  
result = vrouter.create_firewall_instance(firewall2)

print ("<<< Apply ACCEPT-SRC-IPADDR to inbound traffic and DROP-ICMP to outbound traffic on the dp0p1p7 dataplane interface" ) 
result = vrouter.set_dataplane_interface_firewall("dp0p1p7", "ACCEPT-SRC-IPADDR", "DROP-ICMP")

print (">>> Remove firewalls from dp0p1p7 dataplane interface")  
result = vrouter.delete_dataplane_interface_firewall("dp0p1p7")

print (">>> Remove firewall definitions from vrouter 5600")
result = vrouter.delete_firewall_instance(firewall1)
result = vrouter.delete_firewall_instance(firewall2)
```



### Example 2:  Add a flow that drops packets that match in-port, Ethernet src/dest addr, ip src/dest/dscp/ecn/protocol and tcp src/dest ports

```python
import time
import json
import pybvc


from pybvc.controller.controller import Controller
from pybvc.openflowdev.ofswitch import OFSwitch
from pybvc.openflowdev.ofswitch import FlowEntry
from pybvc.openflowdev.ofswitch import Instruction
from pybvc.openflowdev.ofswitch import DropAction
from pybvc.openflowdev.ofswitch import Match

from pybvc.common.status import STATUS
from pybvc.common.utils import load_dict_from_file

ctrl = Controller("192.168.56.101", "8181", "admin", "admin")
node = "openflow:1" # (name:DPID)
ofswitch = OFSwitch(ctrl, node)

# --- Flow
flow_entry = FlowEntry()
table_id = 0
flow_entry.set_flow_table_id(table_id)
flow_id = 16
flow_entry.set_flow_id(flow_id)
flow_entry.set_flow_priority(flow_priority = 1007)
flow_entry.set_flow_cookie(cookie=101)
flow_entry.set_flow_cookie_mask(cookie_mask=255)

# --- Instruction: 'Apply-action'
#     Action:      'Output' NORMAL
instruction = Instruction(instruction_order = 0)
action = DropAction(action_order = 0)
instruction.add_apply_action(action)
flow_entry.add_instruction(instruction)

# --- Match Fields: 
match = Match()    
match.set_eth_type(2048)
match.set_eth_src("00:00:00:11:23:ae")
match.set_eth_dst("ff:ff:29:01:19:61")
match.set_ipv4_src("17.1.2.3/8")
match.set_ipv4_dst("172.168.5.6/16")
match.set_ip_proto(6)
match.set_ip_dscp(2)
match.set_ip_ecn(2)    
match.set_tcp_src_port(25364)
match.set_tcp_dst_port(8080)
match.set_in_port(10)    
flow_entry.add_match(match)

# --- Program The Flow:
result = ofswitch.add_modify_flow(flow_entry)
status = result[0]    

# --- Retrieve The Flow:
print ("\n")    
print ("<<< Get configured flow from the Controller")    
result = ofswitch.get_configured_flow(table_id, flow_id)
flow = result[1]
print json.dumps(flow, indent=4)

 ```
