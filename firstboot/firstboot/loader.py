#
# Chris Lumens <clumens@redhat.com>
#
# Copyright 2007 Red Hat, Inc.
#
# This copyrighted material is made available to anyone wishing to use, modify,
# copy, or redistribute it subject to the terms and conditions of the GNU
# General Public License v.2.  This program is distributed in the hope that it
# will be useful, but WITHOUT ANY WARRANTY expressed or implied, including the
# implied warranties of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.  Any Red Hat
# trademarks that are incorporated in the source code or documentation are not
# subject to the GNU General Public License and may only be used or replicated
# with the express permission of Red Hat, Inc. 
#
from firstboot.constants import *
from firstboot.module import Module
from firstboot.moduleset import ModuleSet
import ethtool
import glob
import imputil
import logging
import os
import sys
import gettext
_ = lambda x: gettext.ldgettext("firstboot", x)

def _check(obj, attrLst):
    for attr in attrLst:
        if not hasattr(obj, attr) or getattr(obj, attr) is None:
            raise TypeError, attr

def _checkModule(obj):
    _check(obj, ["mode", "priority", "sidebarTitle", "title"])

def _checkModuleSet(obj):
    _check(obj, ["mode", "path", "priority", "sidebarTitle"])

def _haveNetwork():
    intfs = ethtool.get_active_devices()
    return len(filter(lambda i: i != "lo", intfs)) != 0

def _insertSorted(list, obj):
    _max = len(list)
    i = 0

    while i < _max:
        if obj.title > list[i].title:
            i += 1
        elif obj.title == list[i].title:
            list[i] = obj
            return
        elif obj.title < list[i].title:
            break

    if i >= _max:
        list.append(obj)
    else:
        list.insert(i, obj)

def loadModules(moduleDir, mode=MODE_REGULAR):
    # Make sure moduleDir is in the system path so imputil works.
    if not moduleDir in sys.path:
        sys.path.append(moduleDir)

    moduleList = []

    # A temporary dictionary of modules to run, keyed by priority.  This
    # will be flattened out into a single list after all modules have been
    # loaded.
    _tmpDict = {}

    lst = map(lambda x: os.path.splitext(os.path.basename(x))[0],
              glob.glob(moduleDir + "/*.py"))

    for module in lst:
        # Attempt to load the found module.
        try:
            found = imputil.imp.find_module(module)
            loaded = imputil.imp.load_module(module, found[0], found[1], found[2])
        except ImportError as e:
            if str(e).find("firstboot_module_window") != -1:
                logging.error(_("Skipping old module %s that has not been updated.") % module)

            logging.error(_("Error loading module %s:\n%s") % (module, str(e)))
            continue
        except Exception as e:
            logging.error(_("Error loading module %s:\n%s") % (module, str(e)))
            continue

        # If the module was loaded, check to see if there's a class named
        # moduleClass.  All firstboot modules must contain this class to be
        # executed.
        if loaded.__dict__.has_key("moduleClass"):
            obj = loaded.moduleClass()
        else:
            logging.error(_("Module %s does not contain a class named moduleClass; skipping.") % module)
            continue

        # Perform a bunch of sanity checks on the loaded module and skip if
        # it doesn't pass.
        try:
            if isinstance(obj, Module):
                _checkModule(obj)
            else:
                _checkModuleSet(obj)
        except TypeError, attr:
            logging.error(_("Module %s does not contain the required attribute %s; skipping.") % (module, attr))
            continue

        # If the loaded module requires networking which is unavailable, skip
        # the module.  We really should have a way to bring up the network if
        # it's not already up.
        if obj.needsNetwork() and not _haveNetwork():
            logging.info("skipping module %s because it requires networking" % module)
            continue

        # If the loaded module should not appear for some reason, don't
        # do anything else with it.
        if not obj.shouldAppear():
            logging.info("skipping module %s because shouldAppear returned false" % module)
            continue

        # Also, the module may not need to be run in this particular mode.
        # Skip those too.
        if (mode == MODE_REGULAR and not obj.mode & MODE_REGULAR) or \
           (mode == MODE_RECONFIG and not obj.mode & MODE_RECONFIG):
            logging.info("skipping module %s because it should not run in this mode" % module)
            continue

        # If we got here, the module should appear in firstboot.  Add it.
        if isinstance(obj, ModuleSet):
            logging.debug("Module %s is a ModuleSet, adding" % module)
            obj.loadModules(mode=mode)

            if len(obj.moduleList) == 0:
                logging.info("skipping module set %s because it has no modules" % module)
                continue
        else:
            logging.debug("Successfully loaded module %s, adding" % module)

        if _tmpDict.has_key(obj.priority):
            _insertSorted(_tmpDict[obj.priority], obj)
        else:
            _tmpDict[obj.priority] = [obj]

    # Now we've loaded all the modules.  Flatten the _tmpDict out into a
    # single list.
    keys = _tmpDict.keys()
    keys.sort()

    for i in keys:
        moduleList.extend(_tmpDict[i])

    return moduleList
