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

result.py: Result of HTTP communication session (status and data)


"""

from pybvc.common.status import OperStatus

#-------------------------------------------------------------------------------
# Class 'Result'
#-------------------------------------------------------------------------------
class Result(object):
    """ Result of completed HTTP session (status and data) """

    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def __init__(self, status=None, data=None):
        """ Initializes this object properties. """
        if isinstance(status, OperStatus) == False:
            raise TypeError(status)
        self.status = status
        self.data = data
    
    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_status(self):
        assert (self.status != None)
        return self.status

    #---------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------
    def get_data(self):
        return self.data
    