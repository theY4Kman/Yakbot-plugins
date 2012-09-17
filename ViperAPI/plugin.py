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

import re
import json
from urllib2 import urlopen
from operator import itemgetter

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.conf as conf
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
import supybot.registry as registry


class ViperAPI(callbacks.Plugin):
    """
    !vapi ObjectNameHere
    """
    threaded = True


    class Function(object):
        def __init__(self, api, name, prototype):
            self.api = api
            self.name = name
            self.prototype = prototype

        def __str__(self):
            if self.api.registryValue('fullyQualified.single'):
                parts = self.name.rsplit('.', 1)
                name = base = '\x02%s\x02' % parts[-1]
                if len(parts) > 1:
                    name = '.'.join((parts[0], base))
            else:
                name = '\x02%s\x02' % self.name.rsplit('.', 1)[-1]
            return '%s(%s)' % (name, self.prototype)

    
    def vapi(self, irc, msg, args, text):
        """<object>"""
        exact = False
        
        if str(msg).strip().endswith('"' + text + '"'):
            exact = True
        
        irc.reply(self.DO_LOOKUP(text, exact))
    vapi = wrap(vapi, ["text"])

    @property
    def _names(self):
        """Retrieve and store the objects from the API JSON"""
        if not hasattr(self, '_api_cache'):
            url = 'http://viper.imkcreative.com/viperapi.php'
            page = urlopen(url)
            if not page:
                return False, 'error opening ' + url

            self._api_cache = json.load(page)

            self._names_cache = {}
            for name,module in self._api_cache.iteritems():
                self._names_cache.update(self._build_objects(name, module))
        return self._names_cache

    def _build_objects(self, name, obj):
        obj_desc = '<thing>'
        obj_name = name.rsplit('.')[-1]
        if 'parent_class' in obj:
            obj_desc = 'class %s(%s)' % (obj_name,
                                         ', '.join(obj['parent_class']))
        else:
            obj_desc = 'module %s' % obj_name
        yield (name, obj_desc)

        if 'classes' in obj and obj['classes']:
            for class_name,cls in obj['classes'].iteritems():
                for tup in self._build_objects(name + '.' + class_name, cls):
                    yield tup

        if 'functions' in obj and obj['functions']:
            for func in obj['functions']:
                func_name = func['name']
                abs_name = name + '.' + func_name
                yield (abs_name, self._get_function(func, abs_name))


    def _rebuild_api(self):
        if hasattr(self, '_api_cache'):
            del self._api_cache
        return self._api

    def _get_function(self, func, name=None):
        """Returns the prototype string of a function from its JSON object"""
        params = []
        if name is None:
            name = func['name']
        if 'params' in func and func['params']:
            for param in func['params']:
                out = param['name']
                if 'default' in param:
                    out += '=' + param['default']
                params.append(out)
        return ViperAPI.Function(self, name, ', '.join(params))
    
    def DO_LOOKUP(self, args, exact=False):
        matches = []
        search = args.lower()
        for name,desc in self._names.iteritems():
            if exact:
                if name.lower().rsplit('.')[-1] == search:
                    matches.append((name, desc))
            elif search in name.lower():
                matches.append((name, desc))

        length = len(matches)

        if length == 0:
            # No results found
            return "No results found for \x02%s\x02" % (args)
        elif length == 1:
            obj = matches[0]
            obj_abs,obj_desc = obj
            obj_name = obj_abs.rsplit('.')[-1]
            obj_url = 'http://viper.imkcreative.com/viperapi.html#%s' % obj_abs

            # TODO: docstrings
            obj_docs = '<docstrings not supported, yet>'

            return "%s: %s (%s)" % (obj_desc, obj_docs, obj_url)
        else:
            answer = ""
            
            # Append up to six results.
            if self.registryValue('fullyQualified.search'):
                names = map(itemgetter(0), matches)
            else:
                names = map(lambda n: n[0].rsplit('.')[-1], matches)

            obj_list = utils.str.commaAndify(names[:6])
            
            if length > 6:
                answer = "First \x026\x02 results of \x02%d\x02: %s\x02...\x02" % (length, obj_list)
            else:
                # func_list has a trailing ", " that has to be removed
                answer = "\x02%s\x02 results: %s" % (length, obj_list)
            
            return answer + " ( http://viper.imkcreative.com/viperapi.html#%s )" % (args)


Class = ViperAPI


# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:
