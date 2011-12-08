#!/usr/bin/env python
# =============================================================================
# SourceMod Plug-ins Search
# Copyright (C) 2008,2011 Zach "theY4Kman" Kanzler
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

from supybot.test import *

class SMPluginsTestCase(PluginTestCase):
    plugins = ('SMPlugins',)

    def test_plugin_search(self):
        # Base test search
        self.assertNotError('plugins test')
        # Base exact test search
        self.assertNotError('plugins "test"')

    def test_plugin_author_search(self):
        # Base test search
        self.assertNotError('pluginsauthor they4kman')
        # Base exact test search
        self.assertNotError('pluginsauthor "they4kman"')

# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
