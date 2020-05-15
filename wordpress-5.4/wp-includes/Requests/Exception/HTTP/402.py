#!/usr/bin/env python3
# coding: utf-8
if '__PHP2PY_LOADED__' not in globals():
    import cgi
    import os
    import os.path
    import copy
    import sys
    from goto import with_goto
    with open(os.getenv('PHP2PY_COMPAT', 'php_compat.py')) as f:
        exec(compile(f.read(), '<string>', 'exec'))
    # end with
    globals()['__PHP2PY_LOADED__'] = True
# end if
#// 
#// Exception for 402 Payment Required responses
#// 
#// @package Requests
#// 
#// 
#// Exception for 402 Payment Required responses
#// 
#// @package Requests
#//
class Requests_Exception_HTTP_402(Requests_Exception_HTTP):
    code = 402
    reason = "Payment Required"
# end class Requests_Exception_HTTP_402