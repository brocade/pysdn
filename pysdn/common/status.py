
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

status.py: Operational Status of a performed HTTP communication session


"""


def enum(*args):
    enums = dict(zip(args, range(len(args))))
    return type('Enum', (), enums)

#
# Status codes to be set in result of HTTP communication session
#
STATUS = enum('OK', 'CONN_ERROR',
              'DATA_NOT_FOUND', 'BAD_REQUEST',
              'UNAUTHORIZED_ACCESS', 'INTERNAL_ERROR',
              'NODE_CONNECTED', 'NODE_DISONNECTED',
              'NODE_NOT_FOUND', 'NODE_CONFIGURED',
              'HTTP_ERROR', 'MALFORM_DATA', 'UNKNOWN')


class OperStatus(object):
    """Operational status of completed HTTP session"""
    """and methods for easy parsing of the status data."""

    def __init__(self, status_code=None, http_resp=None):
        """Initializes this object properties."""
        self.status_code = status_code
        self.http_resp = http_resp

    def set_status(self, status_code, http_resp=None):
        self.status_code = status_code
        self.http_resp = http_resp

    def set_status_code(self, status_code):
        self.status_code = status_code

    def get_status_code(self):
        return self.status_code

    def set_status_response(self, http_resp):
        self.http_resp = http_resp

    def get_status_response(self):
        return self.http_resp

    def to_string(self):
        return self.__status_code_string()

    def brief(self):
        return self.__status_code_string()

    def detailed(self):
        s = self.brief()
        if(self.http_resp is not None and self.http_resp.content is not None):
            s += "\n" + self.http_resp.content
        return s

    def eq(self, status_code):
        if(self.status_code == status_code):
            return True
        else:
            return False

    def __status_code_string(self):
        if (self.status_code == STATUS.OK):
            return "Success"
        elif(self.status_code == STATUS.CONN_ERROR):
            return "Server connection error"
        elif(self.status_code == STATUS.DATA_NOT_FOUND):
            return "Requested data not found"
        elif(self.status_code == STATUS.BAD_REQUEST):
            return "Bad or invalid data in request"
        elif(self.status_code == STATUS.UNAUTHORIZED_ACCESS):
            return "Server unauthorized access"
        elif(self.status_code == STATUS.INTERNAL_ERROR):
            return "Internal Server Error"
        elif(self.status_code == STATUS.NODE_CONNECTED):
            return "Node is connected"
        elif(self.status_code == STATUS.NODE_DISONNECTED):
            return "Node is disconnected"
        elif(self.status_code == STATUS.NODE_NOT_FOUND):
            return "Node not found"
        elif(self.status_code == STATUS.NODE_CONFIGURED):
            return "Node is configured"
        elif(self.status_code == STATUS.HTTP_ERROR):
            errMsg = "HTTP error"
            if(self.http_resp is not None and
               self.http_resp.status_code and
               self.http_resp.reason is not None):
                errMsg += " %d - '%s'" % (self.http_resp.status_code,
                                          self.http_resp.reason)
            return errMsg
        elif(self.status_code == STATUS.MALFORM_DATA):
            return "Malformed data"
        elif(self.status_code == STATUS.UNKNOWN):
            return "Unknown error"
        else:
            print ("Error: undefined status code %s" % self.status_code)
            raise ValueError('!!!undefined status code')
