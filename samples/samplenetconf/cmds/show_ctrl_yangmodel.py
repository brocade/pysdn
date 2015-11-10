#!/usr/bin/python

"""
Copyright (c) 2015,  BROCADE COMMUNICATIONS SYSTEMS, INC

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
contributors may be used to endorse or promote products derived from this
software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
THE POSSIBILITY OF SUCH DAMAGE.


@authors: Sergei Garbuzov
@status: Development
@version: 1.1.0


"""

import sys
import getopt

from pysdn.controller.controller import Controller
from pysdn.common.status import STATUS
from pysdn.common.utils import load_dict_from_file


def usage(myname):
    print('   Usage: %s -i <identifier> -v <version>' % myname)
    sys.exit()

if __name__ == "__main__":

    f = "cfg.yml"
    d = {}
    if(load_dict_from_file(f, d) is False):
        print("Config file '%s' read error: " % f)
        exit()

    try:
        ctrlIpAddr = d['ctrlIpAddr']
        ctrlPortNum = d['ctrlPortNum']
        ctrlUname = d['ctrlUname']
        ctrlPswd = d['ctrlPswd']
    except:
        print ("Failed to get Controller device attributes")
        exit(0)

    model_identifier = None
    model_version = None

    if(len(sys.argv) == 1):
        print("   Error: missing arguments")
        usage(sys.argv[0])

    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv,
                                   "i:v:h",
                                   ["identifier=", "version=", "help"])
    except getopt.GetoptError, e:
        print("   Error: %s" % e.msg)
        usage(sys.argv[0])

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage(sys.argv[0])
        elif opt in ("-i", "--identifier"):
            model_identifier = arg
        elif opt in ("-v", "--version"):
            model_version = arg
        else:
            print("Error: failed to parse option %s" % opt)
            usage(sys.argv[0])

    if(model_identifier is None) or (model_version is None):
        print("Error: incomplete command")
        usage(sys.argv[0])

    ctrl = Controller(ctrlIpAddr, ctrlPortNum, ctrlUname, ctrlPswd)
    print ("<<< 'Controller': %s" % (ctrlIpAddr))
    result = ctrl.get_schema("controller-config",
                             model_identifier, model_version)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print "YANG model definition:"
        schema = result.get_data()
        print schema.encode('utf-8', 'replace')
    else:
        print ("\n")
        print ("!!!Failed, reason: %s" % status.brief().lower())
        print ("%s" % status.detailed())
        exit(0)

    print ("\n")
