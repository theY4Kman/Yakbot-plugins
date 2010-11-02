#!/usr/bin/env python
# =============================================================================
# SourceMod API Viewer
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
from urllib2 import urlopen

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks


class SMAPI(callbacks.Plugin):
    """
    !api FunctionNameHere
    !smapi FunctionNameHere
    """
    threaded = True
    
    rgx_search_results = re.compile("<a onclick=\"ShowFunction\((\d+)\)\"[^>]*>([^<]+)")
    rgx_notes = re.compile("<b>Notes\s*</b>: <div style=\"padding-left: 25px;\">(.+?)</div>", re.DOTALL)
    rgx_prototype = re.compile(r"(\([^)]*\))\s*;?\s*(?:</span>|\r|<br />)")
    rgx_whitespace = re.compile("\\s+")
    
    def smapi(self, irc, msg, args, text):
        """<function>"""
        exact = False
        
        if str(msg).strip().endswith('"' + text + '"'):
            exact = True
        
        irc.reply(self.DO_LOOKUP(text, exact))
    smapi = wrap(smapi, ["text"])
    
    def DO_LOOKUP(self, args, exact=False):
        url = "http://docs.sourcemod.net/api/index.php?action=gethint&id=" + args.replace(" ", "%20")
        page = urlopen(url)
        if not page:
            return "error opening " + url
        
        contents = page.read()
        
        matches = self.rgx_search_results.findall(contents)
        length = len(matches)
        
        if exact is True:
            lowered = args.lower()
            for match in matches:
                if match[1].lower() == lowered:
                    matches[0] = match
                    length = 1
        
        if length == 0:
            # No results found
            if contents.endswith("0 results found."):
                return "No results found for \x02%s\x02" % (args)
            
            # Too many results (over 100)
            elif contents.endswith("smaller"):
                return "More than 100 results found for \x02%s\x02. Try a larger query." % (args)
            
            # Something bad happened if we get here.
            else:
                return "error finding \x02%s\x02" % (args)
        elif length == 1:
            func = matches[0][1]
            func_id = matches[0][0]
            
            url = "http://docs.sourcemod.net/api/index.php?action=show&id=" + func_id
            page = urlopen(url)
            
            if not page:
                return "error opening " + url
            
            contents = page.read()
            notes_match = self.rgx_notes.search(contents)
            proto_match = self.rgx_prototype.search(contents)
            
            fastload_url = "http://docs.sourcemod.net/api/index.php?fastload=show&id=" + func_id
            
            if notes_match is None:
                notes = "<no notes>"
            else:
                notes = notes_match.group(1).strip()
                notes = notes.replace("\n", " ").replace("<br />", " ")
                notes = notes.replace('\\"', '"').replace("  ", " ")
            
            if proto_match is None:
                prototype = "()"
            else:
                prototype = proto_match.group(1).replace("&nbsp;", " ")
                prototype = prototype.replace("<br />", "").replace("&amp;", "&")
                prototype = self.rgx_whitespace.sub(" ", prototype)
            
            return "\x02%s\x02%s: %s (%s)" % (func, prototype, notes, fastload_url)
        else:
            answer = ""
            
            # Append up to six results.
            results_limit = ((length <= 6) and length) or 6
            
            func_list = ""
            for i in range(results_limit):
                func_list += matches[i][1] + ", "
            
            if length > 6:
                answer = "First \x026\x02 results of \x02%d\x02: %s\x02...\x02" % (length, func_list)
            else:
                # func_list has a trailing ", " that has to be removed
                answer = "\x02%s\x02 results: %s" % (length, func_list[:-2])
            
            return answer + " ( http://docs.sourcemod.net/api/index.php?query=%s )" % (args)


Class = SMAPI


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
