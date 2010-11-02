#!/usr/bin/env python
# =============================================================================
# SourceMod Plug-ins Search
# Copyright (C) 2008 Zach "theY4Kman" Kanzler
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

import re
from urllib import urlopen

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

rgx_search_results = re.compile(r"""
 <tr>
  <td><center><a href="http://[^"]+"><img src="[^"]+" border="0" title="(?P<mod>[^"]+)" alt="(?P=mod)"></a></center></td>
<td><center><img src="images/(?:approved|new3)\.gif" alt="(?P<status>Approved|New)" title="(?P=status)"></center></td>
  <td><a href="http://forums\.alliedmods\.net/showthread\.php\?p=(?P<threadnum>\d+)" title="(?P<title>[^"]*)">(?P<desc>[^<]*)</a></td>
  <td><a href="http://forums\.alliedmods\.net/member\.php\?u=(?P<authornum>\d+)">(?P<author>[^<]*)</a></td>
  <td>(?P<category>[^<]*)</td>
 </tr""")

class SMPlugins(callbacks.Plugin):
    """
    Queries the plug-in titles at sourcemod.net/plugins.php
    """
    threaded = True
    
    def plugins(self, irc, msg, args, search):
        """<plug-in title>"""
        exact = False
        
        if str(msg).strip().endswith('"' + search + '"'):
            exact = True
        
        irc.reply(self.DO_PLUGIN_SEARCH(search, "title", exact))
    plugins = wrap(plugins, ["text"])
    
    def pluginsauthor(self, irc, msg, args, search):
        """<plug-in author>"""
        exact = False
        
        if str(msg).strip().endswith('"' + search + '"'):
            exact = True
        
        irc.reply(self.DO_PLUGIN_SEARCH(search, "author", exact))
    pluginsauthor = wrap(pluginsauthor, ["text"])
    
    def DO_PLUGIN_SEARCH(self, args, criterion, exact):
        search = args.replace(" ", "+")
        url = "http://sourcemod.net/plugins.php?search=1&%s=%s" % (criterion, search)
        page = urlopen(url)
        
        if not page:
            return "Error opening " + url
        
        contents = page.read()
        
        matches = rgx_search_results.findall(contents)
        length = len(matches)
        
        if exact is True:
            lowered = args.lower()
            for match in matches:
                if match[rgx_search_results.groupindex[criterion]].lower() == lowered:
                    matches[0] = match
                    length = 1
        
        if length == 0:
            # No results found
            return "No results found for \x02%s\x02" % (args)
        elif length == 1:
            match = matches[0]
            return "\x02%s\x02, by %s: %s  "\
                "( http://forums.alliedmods.net/showthread.php?p=%s )" % \
                (self.UNESCAPE(match[4]), match[6], self.UNESCAPE(match[3]), match[2])
        elif length < 7:
            return "Displaying \x02%d\x02 results: %s ( %s )" % \
                (length, ", ".join((self.UNESCAPE(x[4]) for x in matches)), url)
        else:
            return "First \x026\x02 results of \x02%d\x02: %s ( %s )" % \
                (length, ", ".join((self.UNESCAPE(x[4]) for x in matches[:6])), url)

    def UNESCAPE(self, string):
        return string.replace("&quot;", '"').replace("&amp;", "&")


Class = SMPlugins


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
