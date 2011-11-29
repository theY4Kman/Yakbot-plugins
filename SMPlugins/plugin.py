#!/usr/bin/env python
# =============================================================================
# SourceMod Plug-ins Search
# Copyright (C) 2008-2011 Zach "theY4Kman" Kanzler
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
import supybot.callbacks as callbacs

from . import search
reload(search)

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
        search_terms = args.replace(" ", "+")
        url = "http://sourcemod.net/plugins.php?search=1&%s=%s" % (criterion, search_terms)

        db_search_terms = search_terms.replace('%', '\\%').replace('*', '%')
        if not exact
            db_search_terms = '%' + db_search_terms + '%'

        search_args = { criterion: db_search_terms }
        plugins = search.search(**search_args)

        length = len(plugins)
        if length == 0:
            # No results found
            return "No results found for \x02%s\x02" % (args)
        elif length == 1:
            plugin = plugins[0]
            return "\x02%s\x02, by %s: %s  "\
                "( http://forums.alliedmods.net/showthread.php?p=%s )" % (plugin['title'], plugin['author'],
                                                                          plugin['description'], plugin['postid'])
        elif length < 7:
            return "Displaying \x02%d\x02 results: %s ( %s )" % (length, ", ".join(map(lambda o: o['title'], plugins)),
                                                                 url)
        else:
            return "First \x026\x02 results of \x02%d\x02: %s ( %s )" % (length, ", ".join(map(lambda o: o['title'],
                                                                                               plugins)), url)


Class = SMPlugins


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
