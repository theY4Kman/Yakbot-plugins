#!/usr/bin/env python
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
# =============================================================================
# Steam ID Converter
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

import profile
reload(profile)
from profile import SteamCommunityProfile, SteamIDError

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

class SteamID(callbacks.Plugin):
  """
  Converts Steam IDs, user IDs, and Community IDs.
  """
  threaded = True
  
  def steamid(self, irc, msg, args, text):
    try:
      profile = SteamCommunityProfile.input_to_profile(text)
    except SteamIDError,e:
      irc.error(unicode(e))
      return
    
    if profile is None:
      irc.error("could not recognize your input.")
    else:
      irc.reply(unicode(profile))
  steamid = wrap(steamid, ["text"])


Class = SteamID
