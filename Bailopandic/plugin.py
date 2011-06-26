#!/usr/bin/env python
# =============================================================================
# Bailopandic Phrases
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

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

class SqliteBailopandicDB(object):
    """Provides functions to lookup phrases in the database"""
    
    def __init__(self, filename):
        import sqlite3
        
        self.filename = filename
        try:
            self.db = sqlite3.connect(self.filename)
        except sqlite.DatabaseError, e:
            e = dbi.InvalidDBError(e)
            e.filename = self.filename
            raise e
        
        cur = self.db.cursor()
        cur.executescript("""
        CREATE TABLE IF NOT EXISTS phrases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phrase TEXT
        );
        """)
        
        self.db.commit()
    
    def close(self):
        self.db.close()
    
    def add(self, phrase):
        """
        Adds a question to the database and links it to the supplied answer.
        The answer is also added if it does not exist.
        
        @type   phrase: string
        @param  phrase: A Bailopandic phrase
        """
        cur = self.db.cursor()
        cur.execute("INSERT INTO phrases (phrase) VALUES (?)", (phrase,))
        self.db.commit()
    
    def random_phrase(self):
        """
        Retrieves a random Bailopandic phrase
        
        @rtype: string
        @return: A Bailopandic phrase
        """
        cur = self.db.cursor()
        
        # See if there is an exact term for the question
        cur.execute("SELECT phrase FROM phrases ORDER BY RANDOM() LIMIT 1")
        
        # If not, see if there is a question like it.
        if cur.rowcount == 0:
            return None
        
        return cur.fetchone()[0]


BailopandicDB = plugins.DB("Bailopandic", {'sqlite': SqliteBailopandicDB})

class Bailopandic(callbacks.Plugin):
    """
    !phrase
    !add
    """
    
    def __init__(self, irc):
        self.__parent = super(Bailopandic, self)
        self.__parent.__init__(irc)
        
        try:
            self.db = BailopandicDB()
        except dbi.InvalidDBError, e:
            self.log.exception('Error loading %s: %s', e.filename, str(e))
            raise # So it doesn't get loaded without its database.
    
    def phrase(self, irc, msg, args):
      '''- Prints a random Bailopandic phrase'''
      irc.reply(self.db.random_phrase())
    phrase = wrap(phrase, [])
    
    def add(self, irc, msg, args, text):
      '''<phrase> - Add a Bailopandic phrase to the database.'''
      self.db.add(text)
      irc.replySuccess()
    add = wrap(add, ['text'])


Class = Bailopandic


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
