#!/usr/bin/env python
# =============================================================================
# SourceMod Bugs
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

import time
from urllib2 import urlopen, unquote
from threading import Timer

import icalendar
icalendar = reload(icalendar)
import xml.dom.minidom as dom

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.ircmsgs as ircmsgs
import supybot.callbacks as callbacks
import supybot.registry as registry
import supybot.conf as conf


class SMBugs(callbacks.Plugin):
    """
    Checks for new bugs every two minutes. Use !bug to see a specific bug
    """
    threaded = True
    
    TIME_CST = 60 * 60 * 6
    HG_ENTRY_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S-05:00"
    
    def __init__(self, irc):
        self.__parent = super(SMBugs, self)
        self.__parent.__init__(irc)
        
        try:
            self.registryValue("refreshTime")
        except registry.NonExistentRegistryEntry:
            plugin = conf.registerPlugin('SMBugs')
            conf.registerGlobalValue(plugin, "refreshTime",
                registry.PositiveInteger(60 * 2,
                    "Time in seconds to refresh bugs list."))
        
        self.BugCheck(irc, time.localtime())
        self.MercurialCheck(irc, time.localtime())
    
    def BugCheck(self, irc, last_checked):
        """
        Downloads the list of bugs since the day it was last checked. Bugzilla
        only allows you to retrieve bugs from a date, not a time, so we must
        manually filter out results that have already been seen.
        """
        page = urlopen("https://bugs.alliedmods.net/buglist.cgi?chfieldfrom=%s"
            "&product=SourceMod&order=bugs.bug_id%%20desc&ctype=ics"
            % time.strftime("%Y-%m-%d", last_checked))
        contents = page.read()
        cal = icalendar.Calendar.from_string(contents)
        
        for comp in cal.walk("VTODO"):
            comptime = comp["DTSTART"].dt.utctimetuple()
            if comptime < last_checked:
                break
            
            bug_id = comp["UID"].split("%40", 2)[0]
            irc.queueMsg(ircmsgs.privmsg("#sourcemod", "New bug #%s: %s (%s)" %
                (bug_id, comp["SUMMARY"].replace('\"', '"'), unquote(comp["URL"]))))
        
        self.timer = Timer(self.registryValue("refreshTime"), 
            self.BugCheck, [irc, time.localtime()])
        self.timer.start()
    
    def check(self, irc, msg, args, now, expiry=None):
        if expiry is not None:
            last_checked = time.gmtime(now - (expiry - now))
        else:
            last_checked = time.gmtime(now)
        
        self.timer.cancel()
        self.BugCheck(irc, last_checked)
    check = wrap(check, ["now", optional("expiry")])
    
    def MercurialCheck(self, irc, last_checked):
        atom_log = dom.parse(urlopen("http://hg.alliedmods.net/sourcemod-central/atom-log"))
        
        for elem in atom_log.getElementsByTagName("entry"):
            if time.strptime(elem.getElementsByTagName("updated")[0].firstChild.data,
                self.HG_ENTRY_TIME_FORMAT) < last_checked:
                break
            irc.queueMsg(ircmsgs.privmsg("#sourcemod", "Check-in: %s - by \x02"
                "%s\x02 - %s" %
                (elem.childNodes[5].getAttribute("href"),
                 elem.childNodes[7].childNodes[1].firstChild.data,
                 elem.childNodes[1].firstChild.data)))
        
        Timer(self.registryValue("refreshTime"), self.MercurialCheck,
            [irc, time.localtime()]).start()
    

Class = SMBugs

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
