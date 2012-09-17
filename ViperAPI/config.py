#!/usr/bin/env python
# =============================================================================
# Viper API Viewer
# Copyright (C) 2012 Zach "theY4Kman" Kanzler
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

import supybot.conf as conf
import supybot.registry as registry

def configure(advanced):
    # This will be called by supybot to configure this module.  advanced is
    # a bool that specifies whether the user identified himself as an advanced
    # user or not.  You should effect your configuration by manipulating the
    # registry as appropriate.
    from supybot.questions import expect, anything, something, yn
    conf.registerPlugin('ViperAPI', True)

ViperAPI = conf.registerPlugin('ViperAPI')
conf.registerGroup(ViperAPI, 'fullyQualified')
conf.registerGlobalValue(ViperAPI.fullyQualified, 'search',
    registry.Boolean(False, 'Whether to use the fully-qualified name in '
                           'result lists'))
conf.registerGlobalValue(ViperAPI.fullyQualified, 'single',
    registry.Boolean(True, 'Whether to use the fully-qualified name when '
                           'returning a single object.'))


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
