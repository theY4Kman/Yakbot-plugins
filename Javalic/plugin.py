#!/usr/bin/env python
# =============================================================================
# Javalic Phrases
# Copyright (C) 2011 Zach "theY4Kman" Kanzler <they4kman@gmail.com>
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

import random

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

class SqliteJavalicDB(object):
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
        
        self.cache = []
        self.force_cache = False
    
    def close(self):
        self.db.close()
    
    def add(self, phrase):
        """
        Adds a question to the database and links it to the supplied answer.
        The answer is also added if it does not exist.
        
        @type   phrase: string
        @param  phrase: A Javalic phrase
        """
        cur = self.db.cursor()
        cur.execute("INSERT INTO phrases (phrase) VALUES (?)", (phrase,))
        self.cache.append(phrase)
        self.db.commit()
    
    def force_cache(self):
      self.force_cache = True
    
    def random_phrase(self, words=""):
        """
        Retrieves a random Javalic phrase containing `words`
        
        @type   words: str
        @param  words: Try to find a quote containing these words.
        @rtype: string
        @return: A Javalic phrase
        """
        cur = self.db.cursor()
        
        # Try to find quote with `words` in it
        if words is not None:
            cur.execute("SELECT phrase FROM phrases WHERE phrase LIKE (?)"
                " ORDER BY RANDOM() LIMIT 1", ("%%%s%%" % words,))
        
        row = cur.fetchone()
        if cur.rowcount == 0 or row is None:
            # Otherwise, just grab a random quote
            if len(self.cache) < 5 or self.force_cache:
                self.force_cache = False
                self.cache = [phrase[0] for phrase in cur.execute("SELECT"
                    " phrase FROM phrases ORDER BY RANDOM()")]
            
            quote = random.choice(self.cache)
            if quote is None:
                return "No quotes in database :("
            
            self.cache.remove(quote)
            return quote
        
        return row[0]


JavalicDB = plugins.DB("Javalic", {'sqlite': SqliteJavalicDB})

class Javalic(callbacks.Plugin):
    """
    !phrase
    !add
    """
    
    def __init__(self, irc):
        self.__parent = super(Javalic, self)
        self.__parent.__init__(irc)
        
        try:
            self.db = JavalicDB()
        except dbi.InvalidDBError, e:
            self.log.exception('Error loading %s: %s', e.filename, str(e))
            raise # So it doesn't get loaded without its database.
    
    def phrase(self, irc, msg, args, text=''):
      '''- Prints a random Javalic phrase'''
      irc.reply(self.db.random_phrase(text))
    phrase = wrap(phrase, [optional('text')])
    
    def add(self, irc, msg, args, text):
      '''<phrase> - Add a Javalic phrase to the database.'''
      self.db.add(text)
      irc.replySuccess()
    add = wrap(add, ['text'])


Class = Javalic


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
