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
#// Class ParagonIE_Sodium_Core_Base64
#// 
#// Copyright (c) 2016 - 2018 Paragon Initiative Enterprises.
#// Copyright (c) 2014 Steve "Sc00bz" Thomas (steve at tobtu dot com)
#// 
#// We have to copy/paste the contents into the variant files because PHP 5.2
#// doesn't support late static binding, and we have no better workaround
#// available that won't break PHP 7+. Therefore, we're forced to duplicate code.
#//
class ParagonIE_Sodium_Core_Base64_Common():
    #// 
    #// Encode into Base64
    #// 
    #// Base64 character set "[A-Z][a-z][0-9]+/"
    #// 
    #// @param string $src
    #// @return string
    #// @throws TypeError
    #//
    @classmethod
    def encode(self, src=None):
        
        return self.doencode(src, True)
    # end def encode
    #// 
    #// Encode into Base64, no = padding
    #// 
    #// Base64 character set "[A-Z][a-z][0-9]+/"
    #// 
    #// @param string $src
    #// @return string
    #// @throws TypeError
    #//
    @classmethod
    def encodeunpadded(self, src=None):
        
        return self.doencode(src, False)
    # end def encodeunpadded
    #// 
    #// @param string $src
    #// @param bool $pad   Include = padding?
    #// @return string
    #// @throws TypeError
    #//
    def doencode(self, src=None, pad=True):
        
        dest = ""
        srcLen = ParagonIE_Sodium_Core_Util.strlen(src)
        #// Main loop (no padding):
        i = 0
        while i + 3 <= srcLen:
            
            #// @var array<int, int> $chunk
            chunk = unpack("C*", ParagonIE_Sodium_Core_Util.substr(src, i, 3))
            b0 = chunk[1]
            b1 = chunk[2]
            b2 = chunk[3]
            dest += self.encode6bits(b0 >> 2) + self.encode6bits(b0 << 4 | b1 >> 4 & 63) + self.encode6bits(b1 << 2 | b2 >> 6 & 63) + self.encode6bits(b2 & 63)
            i += 3
        # end while
        #// The last chunk, which may have padding:
        if i < srcLen:
            #// @var array<int, int> $chunk
            chunk = unpack("C*", ParagonIE_Sodium_Core_Util.substr(src, i, srcLen - i))
            b0 = chunk[1]
            if i + 1 < srcLen:
                b1 = chunk[2]
                dest += self.encode6bits(b0 >> 2) + self.encode6bits(b0 << 4 | b1 >> 4 & 63) + self.encode6bits(b1 << 2 & 63)
                if pad:
                    dest += "="
                # end if
            else:
                dest += self.encode6bits(b0 >> 2) + self.encode6bits(b0 << 4 & 63)
                if pad:
                    dest += "=="
                # end if
            # end if
        # end if
        return dest
    # end def doencode
    #// 
    #// decode from base64 into binary
    #// 
    #// Base64 character set "./[A-Z][a-z][0-9]"
    #// 
    #// @param string $src
    #// @param bool $strictPadding
    #// @return string
    #// @throws RangeException
    #// @throws TypeError
    #// @psalm-suppress RedundantCondition
    #//
    @classmethod
    def decode(self, src=None, strictPadding=False):
        
        #// Remove padding
        srcLen = ParagonIE_Sodium_Core_Util.strlen(src)
        if srcLen == 0:
            return ""
        # end if
        if strictPadding:
            if srcLen & 3 == 0:
                if src[srcLen - 1] == "=":
                    srcLen -= 1
                    if src[srcLen - 1] == "=":
                        srcLen -= 1
                    # end if
                # end if
            # end if
            if srcLen & 3 == 1:
                raise php_new_class("RangeException", lambda : RangeException("Incorrect padding"))
            # end if
            if src[srcLen - 1] == "=":
                raise php_new_class("RangeException", lambda : RangeException("Incorrect padding"))
            # end if
        else:
            src = php_rtrim(src, "=")
            srcLen = ParagonIE_Sodium_Core_Util.strlen(src)
        # end if
        err = 0
        dest = ""
        #// Main loop (no padding):
        i = 0
        while i + 4 <= srcLen:
            
            #// @var array<int, int> $chunk
            chunk = unpack("C*", ParagonIE_Sodium_Core_Util.substr(src, i, 4))
            c0 = self.decode6bits(chunk[1])
            c1 = self.decode6bits(chunk[2])
            c2 = self.decode6bits(chunk[3])
            c3 = self.decode6bits(chunk[4])
            dest += pack("CCC", c0 << 2 | c1 >> 4 & 255, c1 << 4 | c2 >> 2 & 255, c2 << 6 | c3 & 255)
            err |= c0 | c1 | c2 | c3 >> 8
            i += 4
        # end while
        #// The last chunk, which may have padding:
        if i < srcLen:
            #// @var array<int, int> $chunk
            chunk = unpack("C*", ParagonIE_Sodium_Core_Util.substr(src, i, srcLen - i))
            c0 = self.decode6bits(chunk[1])
            if i + 2 < srcLen:
                c1 = self.decode6bits(chunk[2])
                c2 = self.decode6bits(chunk[3])
                dest += pack("CC", c0 << 2 | c1 >> 4 & 255, c1 << 4 | c2 >> 2 & 255)
                err |= c0 | c1 | c2 >> 8
            elif i + 1 < srcLen:
                c1 = self.decode6bits(chunk[2])
                dest += pack("C", c0 << 2 | c1 >> 4 & 255)
                err |= c0 | c1 >> 8
            elif i < srcLen and strictPadding:
                err |= 1
            # end if
        # end if
        #// @var bool $check
        check = err == 0
        if (not check):
            raise php_new_class("RangeException", lambda : RangeException("Base64::decode() only expects characters in the correct base64 alphabet"))
        # end if
        return dest
    # end def decode
    #// 
    #// Uses bitwise operators instead of table-lookups to turn 6-bit integers
    #// into 8-bit integers.
    #// 
    #// Base64 character set:
    #// [A-Z]      [a-z]      [0-9]      +
    #// 0x41-0x5a, 0x61-0x7a, 0x30-0x39, 0x2b, 0x2f
    #// 
    #// @param int $src
    #// @return int
    #//
    def decode6bits(self, src=None):
        
        pass
    # end def decode6bits
    #// 
    #// Uses bitwise operators instead of table-lookups to turn 8-bit integers
    #// into 6-bit integers.
    #// 
    #// @param int $src
    #// @return string
    #//
    def encode6bits(self, src=None):
        
        pass
    # end def encode6bits
# end class ParagonIE_Sodium_Core_Base64_Common