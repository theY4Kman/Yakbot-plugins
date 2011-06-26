#!/usr/bin/env python
# =============================================================================
# Wikipedia
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

import sys
import re
import urllib2

# reload mwclient
#if 'mwclient' in globals():
#  reload(mwclient)
if sys.modules.has_key('mwclient'):
  del sys.modules['mwclient']
  del mwclient
import mwclient

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

rgx_first_title = re.compile(r'(=+)[^=]+?\1')
rgx_tags = re.compile(r'<[^>]*?>')
rgx_sup_tag = re.compile(r'<sup.*?</sup>')
rgx_redirect = re.compile(r'^\s*#REDIRECT (\[\[)?(?P<page>[^\]]+)(\]\])?\s*$')
rgx_braces = re.compile(r'{{[^}]*}}')
rgx_link = re.compile(r'\[([^\]]+)\]')
rgx_int_link = re.compile(r'\[\[([^\]]+)\]\]')

def irc_clean_text(value):
  "Cleans up HTML to an acceptable IRC message"
  
  value = value.replace("'''", "\x02").replace("''", "/")
  value = rgx_sup_tag.sub('', value)
  value = rgx_tags.sub('', value)
  return value

def internallinkrepl(match):
  text = match.group(1).split('|', 1)
  return text[len(text)-1]

def linkrepl(match):
  text = match.group(1).split(' ', 1)
  if len(text) is 1:
    return text[0]
  else:
    return '%s (%s)' % (text[1], text[0])
    
def get_summary(page):
  text = page.edit()
  match = rgx_redirect.match(text.strip())
  if match is not None:
    return get_summary(page.site.Pages[match.group('page')])
  
  text = rgx_tags.sub('', text)
  text = rgx_braces.sub('', text).strip()
  text = rgx_int_link.sub(internallinkrepl, text)
  text = rgx_link.sub(linkrepl, text)
  match = rgx_first_title.search(text)
  if not match:
    return text
  else:
    text = text[:match.span()[0]].strip()
    return text


class Wikipedia(callbacks.Plugin):
    """Use the wiki command to see the short description of the Wikipedia
    article."""
    threaded = True
    
    def __init__(self, *args, **kwargs):
      callbacks.Plugin.__init__(self, *args, **kwargs)
      
      self._smwiki = mwclient.Site('wiki.alliedmods.net', path='/')
      self._wiki = mwclient.Site('en.wikipedia.org', do_init=False)
      self._wiki.version = (1,7,'alpha')
    
    def wiki(self, irc, msg, args, text):
      page = self._wiki.Pages[text]
      if not page.exists:
        irc.reply('page "%s" does not exist in en.wikipedia.org' % text)
      else:
        irc.reply(unicode(irc_clean_text(get_summary(page))))
    wiki = wrap(wiki, ["text"])
    
    def smwiki(self, irc, msg, args, text):
      page = self._smwiki.Pages[text]
      if not page.exists:
        irc.reply('page "%s" does not exist in wiki.alliedmods.net' % text)
      else:
        irc.reply(unicode(irc_clean_text(get_summary(page))))
    smwiki = wrap(smwiki, ["text"])


Class = Wikipedia


# vim:set shiftwidth=2 tabstop=2 expandtab textwidth=79:
