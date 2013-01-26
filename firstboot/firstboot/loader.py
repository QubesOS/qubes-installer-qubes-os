#
# loader.py
#
# Copyright (C) 2011  Red Hat, Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Red Hat Author(s):  Martin Gracik <mgracik@redhat.com>
#

import operator
import os
import sys

from .constants import *
from .module import Module
from .moduleset import ModuleSet

import ethtool


# set up logging
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('firstboot.loader')


class Loader:

    def __init__(self):
        self.modlist = []

    def _check_module(self, module):
        # XXX this does not work as expected
        if isinstance(module, Module):
            attrs = ('mode', 'priority', 'sidebarTitle', 'title')
        elif isinstance(module, ModuleSet):
            attrs = ('mode', 'path', 'priority', 'sidebarTitle')
        else:
            return []

        return [a for a in attrs if getattr(module, a, None) is None]

    def _has_network(self):
        return [i for i in ethtool.get_active_devices() if i != 'lo']

    def load_modules(self, module_dir, reconfig=False):
        if not module_dir in sys.path:
            sys.path.append(module_dir)

        modules = [os.path.splitext(f)[0] for f in os.listdir(module_dir)
                   if f.endswith('.py')]

        for module in modules:
            log.info('loading module %s', module)
            try:
                imported = __import__(module)
            except ImportError as e:
                log.error('module could not be imported: %s', e)
                continue

            clsobj = getattr(imported, MODCLASS, None)
            if clsobj is None:
                log.error('module does not implement the required class')
                continue

            modobj = clsobj()

            # module sanity check
            missing = self._check_module(modobj)
            if missing:
                log.error('module has missing attributes: %s', str(missing))
                continue

            # skip modules that require network if it's not active
            if not self._has_network and modobj.needsNetwork():
                log.error('module requires active network connection')
                continue

            # skip modules that should only appear in reconfig mode
            if not reconfig and modobj.reconfig:
                log.info('module only available in reconfig mode')
                continue

            # skip hidden modules
            if not modobj.shouldAppear():
                log.info('module is hidden')
                continue

            # skip empty module sets
            if isinstance(modobj, ModuleSet):
                modobj.loadModules(mode=reconfig)
                if not obj.moduleList:
                    log.error('module set is empty')
                    continue

            # add the module to the list
            self.modlist.append(modobj)

        # sort modules
        self.modlist.sort(key=operator.attrgetter('priority'))

        return self.modlist
