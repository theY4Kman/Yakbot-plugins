#!/usr/bin/env python
# =============================================================================
# SourceMod Plug-ins Search
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

import json
from urllib import urlencode
from urllib2 import urlopen

class SearchPluginsError(Exception):
    pass


def search(title=None, author=None, approved=None):
    args = dict([('title', title)] if title else [] + [('author', author)] if author else [])
    if approved is not None:
        args['approved'] = int(approved)
    url_args = urlencode(args)

    page = urlopen('http://users.alliedmods.net/~they4kman/plugin_search.php?' + url_args)
    if not page:
        raise SearchPluginsError('Could not reach plug-in search.')

    return json.loads(page.read())
