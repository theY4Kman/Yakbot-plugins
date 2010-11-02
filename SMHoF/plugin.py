#!/usr/bin/env python
# =============================================================================
# SourceMod Donor Hall of Fame
# Copyright (C) 2010 Zach "theY4Kman" Kanzler <they4kman@gmail.com>
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

import htmlentitydefs

def unescape(text):
   """Removes HTML or XML character references 
      and entities from a text string.
      keep &amp;, &gt;, &lt; in the source code.
   from Fredrik Lundh
   http://effbot.org/zone/re-sub.htm#unescape-html
   """
   def fixup(m):
      text = m.group(0)
      if text[:2] == "&#":
         # character reference
         try:
            if text[:3] == "&#x":
               return unichr(int(text[3:-1], 16))
            else:
               return unichr(int(text[2:-1]))
         except ValueError:
            pass
      else:
         # named entity
         try:
            if text[1:-1] == "amp":
               text = "&amp;amp;"
            elif text[1:-1] == "gt":
               text = "&amp;gt;"
            elif text[1:-1] == "lt":
               text = "&amp;lt;"
            else:
               print text[1:-1]
               text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
         except KeyError:
            pass
      return text # leave as is
   return re.sub("&#?\w+;", fixup, text)


class SMHoF(callbacks.Plugin):
    """
    !top
    !latest
    """
    threaded = True
    
    RGX_DONOR = re.compile('<td style="width: 45px;">\s*<i>(?P<date>[^<]+)</i>\s*</td>\s*<td>'
      '\s*\\$(?P<amount>\d+) - (<a href="http://forums\\.alliedmods\\.net/member\\.php'
      '\\?u=(?P<forum_uid>\d+)">)?(?P<name>[^<]+)(</a>)?\s*'
      '(\\(<a href="(?P<homepage>[^"]*)">homepage</a>\\))?\s*</td>', re.M)

    RGX_TOPDONOR = re.compile('<td style="width: 45px;">\s*\\$(?P<amount>\d+)'
      '\s*</td>\s*<td>\s*(<a href="http://forums\\.alliedmods\\.net/member\\.php'
      '\\?u=(?P<forum_uid>\d+)">)?(?P<name>[^<]+)(</a>)?\s*'
      '(\\(<a href="(?P<homepage>[^"]*)">homepage</a>\\))?\s*</td>', re.M)
    
    
    def top(self, irc, msg, args):
      donors = self.TOP_DONORS()
      r = ', '.join(['$%s - %s' % (d['amount'], d['name']) for d in donors])
      irc.reply('Top donors: ' + r)
    top = wrap(top, [])
    
    def latest(self, irc, msg, args):
      donors = self.LATEST_DONORS()[:10]
      r = ', '.join(['$%s - %s (%s)' % (d['amount'], d['name'], d['date']) for d in donors])
      irc.reply('Latest donors: ' + r)
    latest = wrap(latest, [])
    
    def TOP_DONORS(self):
      page = urlopen('http://www.sourcemod.net/halloffame.php')
      if page is None:
        raise HallOfFameError('could not access sourcemod.net/halloffame.php')
      
      contents = page.read()
      
      mtx = self.RGX_TOPDONOR.findall(contents)
      if len(mtx) == 0:
        raise HallOfFameError('no top donors. Get on the tippy top of the hall of fame!'
          ' http://www.sourcemod.net/donate.php')
      
      donors = []
      for amount,crumtussels,uid,name,sapcrangle,frizcramble,homepage in mtx[:10]:
        donors.append({
          'amount': amount,
          'uid': uid,
          'homepage': unescape(homepage),
          'name': unescape(name.strip()),
        })
      
      return donors

    def LATEST_DONORS(self):
      page = urlopen('http://www.sourcemod.net/halloffame.php')
      if page is None:
        raise HallOfFameError('could not access sourcemod.net/halloffame.php')
      
      contents = page.read()
      
      latest_idx = contents.find('Donors this month:')
      if latest_idx == -1:
        raise HallOfFameError('could not find latest donors on '
          'sourcemod.net/halloffame.php')
      
      goodbits = contents[latest_idx:]
      mtx = self.RGX_DONOR.findall(goodbits)
      if len(mtx) == 0:
        raise HallOfFameError('no recent donors. Get on the hall of fame!'
          ' http://www.sourcemod.net/donate.php')
      
      donors = []
      for date,amount,crumtussels,uid,name,sapcrangle,frizcramble,homepage in mtx:
        donors.append({
          'date': date,
          'amount': amount,
          'uid': uid,
          'homepage': unescape(homepage),
          'name': unescape(name.strip()),
        })
      
      return donors


Class = SMHoF


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
