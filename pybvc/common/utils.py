"""
Copyright (c) 2015,  BROCADE COMMUNICATIONS SYSTEMS, INC

All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
 are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this 
list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, 
this list of conditions and the following disclaimer in the documentation and/or 
other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors 
may be used to endorse or promote products derived from this software without 
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE 
GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) 
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT 
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT 
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.





utils.py: Helper utilities




"""
import sys
import time
import string
import yaml

debug_count = 0

def remove_empty_from_dict(d):
    if type(d) is dict:
        return dict((k, remove_empty_from_dict(v)) for k, v in d.iteritems() if v and remove_empty_from_dict(v))
    elif type(d) is list:
        return [remove_empty_from_dict(v) for v in d if v and remove_empty_from_dict(v)]
    else:
        return d


def stripNone(data):
    if isinstance(data, dict):
        res = {k:stripNone(v) for k, v in data.items() if k != None and v != None}
        return res
    elif isinstance(data, list):
        res = [stripNone(item) for item in data if item != None]
        return res
    elif isinstance(data, tuple):
        res = tuple(stripNone(item) for item in data if item != None)
        return res
    elif isinstance(data, set):
        res = {stripNone(item) for item in data if item != None}
        return res
    else:
        return data

def load_dict_from_file(f, d):
    try:
        with open(f, 'r') as f:
            obj = yaml.load(f)
        for k, v in obj.iteritems():
            d[k] = v
        return True
    except IOError:
        print("Error: failed to read file '%s'" % f)
        return False

def find_key_values_in_dict(d, key):
    """
    Searches a dictionary (with nested lists and dictionaries)
    for all the values matching to the provided key.
    """
    values = []

    for k, v in d.iteritems():
        if k == key:
            values.append(v)
        elif isinstance(v, dict):
            results = find_key_values_in_dict(v, key)
            for result in results:
                values.append(result)
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    more_results = find_key_values_in_dict(item, key)
                    for another_result in more_results:
                        values.append(another_result)
    
    return values

def find_key_value_in_dict(d, key):
    """
    Searches a dictionary (with nested lists and dictionaries)
    for the first value matching to the provided key.
    """
    for k, v in d.iteritems():
        if k == key:
            return v
        elif isinstance(v, dict):
            results = find_key_values_in_dict(v, key)
            for result in results:
                return result
        elif isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    more_results = find_key_values_in_dict(item, key)
                    for another_result in more_results:
                        return another_result
    
    return None


def find_dict_in_list(slist, key):
    for item in slist:
        if (type(item) is dict and item.has_key(key)):
            return item
#            for k, v in item.items():
#                if (k == key):
#                    return {k, v}
#            return dict((k,v) for k,v in item.items() if k == key)    
    return None

def replace_str_value_in_dict(d, old, new):
    if type(d) is dict:
        return dict((k, replace_str_value_in_dict(v, old, new)) for k, v in d.iteritems() if v and replace_str_value_in_dict(v, old, new))
    elif type(d) is list:
        return [replace_str_value_in_dict(v, old, new) for v in d if v and replace_str_value_in_dict(v, old, new)]
    elif type(d) is unicode:
        d = string.replace(d, unicode(old), unicode(new))
        return d        
    elif type(d) is str:
        d = string.replace(d, old, new)
        return d
    else:
        return d    

def progress_wait_secs(msg=None, waitTime=None, sym="."):
    if (waitTime != None):
#        sys.stdout.write ("(waiting for %s seconds) " % waitTime)
#        sys.stdout.write ("waiting for %s seconds: " % waitTime)
#        sys.stdout.write ("waiting for %s seconds: " % waitTime)
        if (msg != None):
            sys.stdout.write ("%s" % msg)
        for i in range(0, waitTime, 1):
            print "%s" % sym, # <- no newline
            sys.stdout.flush() #<- makes python print it anyway
            time.sleep(1)
        sys.stdout.write ("\n")

'''        
def replace_underscores_with_dashes_in_dict(d):
    d1 = {}
    for k, v in d.iteritems():
        print type(k)
        if (type(k) is str):
            print "1)******"
            k1 = k.replace('_', '-')
        else:
            k1 = k
        
        print type(v)
        if (type(v) is str):
            print "1)******"
            v1 = v.replace('_','-')
        else:
            v1 = v
            
        d1[k1] = v1

    return d1
'''
