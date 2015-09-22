#!/usr/bin/python

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


"""

import time

from pybvc.controller.controller import Controller
from pybvc.common.status import STATUS
from pybvc.controller.inventory import NetconfConfigModule
from pybvc.common.utils import load_dict_from_file


def nc_demo_12():

    f = "cfg1.yml"
    d = {}
    if(load_dict_from_file(f, d) is False):
        print("Config file '%s' read error: " % f)
        exit()

    try:
        ctrlIpAddr = d['ctrlIpAddr']
        ctrlPortNum = d['ctrlPortNum']
        ctrlUname = d['ctrlUname']
        ctrlPswd = d['ctrlPswd']
        rundelay = d['rundelay']
    except:
        print ("Failed to get Controller device attributes")
        exit(0)

    print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    print ("<<< Demo Start")
    print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    print "\n"
    ctrl = Controller(ctrlIpAddr, ctrlPortNum, ctrlUname, ctrlPswd)
    print ("<<< Controller '%s:%s'" % (ctrlIpAddr, ctrlPortNum))
    time.sleep(rundelay)

    print "\n"
    print ("<<< Get NETCONF Configuration Information")
    time.sleep(rundelay)

    netconf_cfg_modules = []
    result = ctrl.build_netconf_config_objects()
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        netconf_cfg_modules = result.get_data()
    else:
        print ("\n")
        print ("!!!Error, failed to obtain NETCONF configuration information, "
               "reason: %s"
               % status.brief().lower())
        exit(0)

    print "\n"
    print ("<<< NETCONF devices")
    s1 = 'Name'
    s2 = 'IP Address:Port Num'
    sym = '-'
    print "\n".strip()
    print "         {0:<25}  {1:<21}".format(s1, s2)
    print "         {0:<25}  {1:<21}".format(sym * 25, sym * 21)

    assert(netconf_cfg_modules)
    for item in netconf_cfg_modules:
        assert(isinstance(item, NetconfConfigModule))
        name = item.get_name()
        addr = item.get_ip_address()
        port = item.get_tcp_port()
        print "         {0:<25}  {1:<21}".format(name, addr + ":" + str(port))

    assert(netconf_cfg_modules)
    for item in netconf_cfg_modules:
        assert(isinstance(item, NetconfConfigModule))
        time.sleep(rundelay)
        print "\n".strip()
        print "<<< Information for '%s' device\n" % item.get_name()
        print ("         IP Address                    : %s"
               % item.get_ip_address())
        print ("         TCP Port                      : %s"
               % item.get_tcp_port())
        print ("         Connection timeout (ms)       : %s"
               % item.get_conn_timeout())
        print ("         Retry connection timeout (ms) : %s"
               % item.get_retry_conn_timeout())
        print ("         Max connection attempts       : %s"
               % item.get_max_conn_attempts())
        print ("         Admin user name               : %s"
               % item.get_admin_name())
        print ("         Admin password                : %s"
               % item.get_admin_pswd())

    print ("\n")
    print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print (">>> Demo End")
    print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")


if __name__ == "__main__":
    nc_demo_12()
