#!/usr/bin/env python
# =============================================================================
# Answers Database
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

import supybot.utils as utils
import supybot.dbi as dbi
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

class SqliteAnswersDB(object):
    """Provides functions to lookup questions and answers in the database"""
    
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
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            answer TEXT UNIQUE
        );
        
        CREATE TABLE IF NOT EXISTS terms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            term TEXT UNIQUE,
            answer_id INTEGER NOT NULL,
            FOREIGN KEY (answer_id) REFERENCES answers(id)
        );
        
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer_id INTEGER NOT NULL,
            FOREIGN KEY (answer_id) REFERENCES answers(id)
        );
        """)
        
        self.db.commit()
    
    def close(self):
        self.db.close()
    
    def add(self, answer, terms, questions=[]):
        """
        Adds a question to the database and links it to the supplied answer.
        The answer is also added if it does not exist.
        
        @type   answer: string
        @param  answer: An answer
        @type   terms: list
        @param  terms: A list of terms to add to the database and link to the
            answer.
        @type   questions: list
        @param  questions: A list of questions to add to the database and link
            to the answer.
        """
        cur = self.db.cursor()
        
        cur.execute("INSERT OR IGNORE INTO answers (answer) VALUES (?)",
            (answer,))
        answer_id = cur.lastrowid
        
        # Add the terms and questions
        for q_type in ["term", "question"]:
            qs = locals()[q_type + 's']
            
            for q in qs:
                if q is None: continue
                cur.execute("INSERT OR IGNORE INTO %s (%s, answer_id) VALUES"
                    " (?, ?)" % (q_type + 's', q_type), (q, answer_id))
        
        self.db.commit()
    
    def find_answers(self, question):
        """
        Searches through the database of questions for an answer.
        
        @type   question: string
        @param  question: The question/term to lookup
        @rtype: list
        @return: A list of tuple(id, answer) where `id` is the ID number of the
            answer in the database, and `answer` is the text of the answer.
            If there are no suitable answers, it returns None.
        """
        cur = self.db.cursor()
        
        # See if there is an exact term for the question
        cur.execute("SELECT answers.id,answers.answer FROM answers"
            " JOIN terms ON answers.id = terms.answer_id"
            " WHERE terms.term LIKE ?", (question,))
        
        # If not, see if there is a question like it.
        if cur.rowcount == 0:
            cur.execute("SELECT answers.id,answers.answer FROM answers"
                " JOIN questions ON answers.id = questions.answer_id"
                " WHERE questions.question LIKE ?", ('%' + question + '%',))
            if cur.rowcount == 0:
                return None
        
        return [(row[0], row[1]) for row in cur]

    def random_answer(self):
        """
        Returns a random (term, answer) tuple.

        @rtype: tuple(str, str)
        @return: A random term/answer pair retrieved from the database.
        """
        cur = self.db.cursor()

        cur.execute("SELECT terms.term,answers.answer FROM answers"
                    " JOIN terms ON terms.answer_id = answers.id"
                    " ORDER BY RANDOM() LIMIT 1;")

        if cur.rowcount == 0:
            return ('Empty', 'There ain\'t a darned thing in this database!')

        row = cur.fetchone()
        return (row[0], row[1])


AnswersDB = plugins.DB("Answers", {'sqlite': SqliteAnswersDB})

class Answers(callbacks.Plugin):
    """Add the help for "@plugin help Answers" here
    This should describe *how* to use this plugin."""
    #threaded = True
    
    def __init__(self, irc):
        self.__parent = super(Answers, self)
        self.__parent.__init__(irc)
        
        try:
            self.db = AnswersDB()
        except dbi.InvalidDBError, e:
            self.log.exception('Error loading %s: %s', e.filename, str(e))
            raise # So it doesn't get loaded without its database.
    
    def die(self):
        self.db.close()
    
    def add(self, irc, msg, args, answer, term, questions):
        """<answer> <term> [question]
        
        Adds the `answer` to the database and connects the `term` and
        `question` to the `answer`. A term is a direct way to access an answer:
        the term must be fully matched, unlike the questions, which can be
        partially matched.
        """
        
        try:
            self.db.add(answer, [term.lower()],
                questions is None and [] or [questions])
            irc.replySuccess()
        except Exception,e:
            irc.error('Error adding to the database.')
            raise
    add = wrap(add, ['anything', 'anything', optional('text')])
    
    def find(self, irc, msg, args, search):
        """<term|question>
        
        Finds the answer matching the term or question. When a conflict arises, 
        a matching term has a higher priority over a question on conflict.
        """
        answers = self.db.find_answers(search.lower())
        answers_cnt = len(answers)
        
        if answers is None or answers_cnt == 0:
            irc.reply("No answer found")
            return
        if answers_cnt == 1:
            irc.reply(answers[0][1])
        else:
            irc.reply("(1 of \x02%d\x02) %s" % (answers_cnt, answers[0]))
    find = wrap(find, ['text'])

    def random(self, irc, msg, args):
        """
        Returns a random term/answer.
        """
        term,answer = self.db.random_answer()
        irc.reply('%s: %s' % (term, answer))


Class = Answers


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
