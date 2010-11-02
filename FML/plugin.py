#!/usr/bin/env python
# =============================================================================
# YakMyLife
#   Interact with the fmylife site
# Copyright (C) 2009 Zach "theY4Kman" Kanzler
# =============================================================================
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License, version 3.0, as published by the
# Free Software Foundation.
# 
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

import socket
import urllib2
import fmylife as fml
reload(fml)
import re
from htmlentitydefs import name2codepoint

socket.setdefaulttimeout(10)

def htmlentdecode(s):
    return re.sub('&(%s);' % '|'.join(name2codepoint), 
        lambda m: unichr(name2codepoint[m.group(1)]), s)

class FML(callbacks.Plugin):
    """Use the `fml` command"""
    threaded = True
    
    def fml(self, irc, msg, args, query):
        """[#id|category]"""
        options = {}
        cat = "random"
        if query is not None:
            try: cat = int(query)
            except ValueError:
                options["category"] = query
        
        try:
            code,doc = fml.fml_req("http://api.betacie.com/view/%s/nocomment"
                % cat, options)
        except urllib2.URLError, e:
            irc.error("Error retrieving FML: " + str(e.reason))
            return
        
        for id,item in fml.parse_items(doc).iteritems():
            irc.reply("%s - \x02#%d\x02 - \x02%s\x02 - \x02%d\x02 agree, "
                "their life is f***ed - \x02%d\x02 think they deserved that one"
                % (htmlentdecode(item["text"]), id, item["category"],
                   item["agree"], item["deserved"]))
    fml = wrap(fml, [optional("text")])


Class = FML


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
