#!/usr/bin/env python
# =============================================================================
# JoinChannels
#   Join the channels yakbot should be in.
# Copyright (C) 2011 Zach "theY4Kman" Kanzler
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

from supybot.commands import *
import supybot.plugins as plugins
import supybot.conf as conf
import supybot.callbacks as callbacks

class JoinChannels(callbacks.Plugin):
  """A command to join all the channels yakbot should be in."""
  threaded = True
  
  def whatchannels(self, irc, msg, args):
    """Displays the channels `joinchannels` will join"""
    irc.reply(','.join(self.registryValue('channels')))
  
  def joinchannels(self, irc, msg, args):
    """Joins all the channels yakbot should be in. See `whatchannels` to
    see the channels this command will make yakbot join."""
    
    networkGroup = conf.supybot.networks.get(irc.network)
    
    for channel in self.registryValue('channels'):
      if irc.isChannel(channel):
        irc.queueMsg(networkGroup.channels.join(channel))


Class = JoinChannels


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
