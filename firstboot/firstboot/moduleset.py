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
from firstboot.module import *
import logging

import gettext
_ = lambda x: gettext.ldgettext("firstboot", x)

class ModuleSet:
    """The base class for a set of firstboot modules.  A set of modules is
       a group of several related modules that are all loaded out of some
       common directory.  This class is useful for custom environments that
       need to ask a variety of questions of the user.  Important things to
       note about ModuleSet:

       -- A ModuleSet has its own priority for where it will be sorted in the
          main module list.  Within the ModuleSet, modules have their own
          priorities that specifies how they will be sorted within the set.
       -- A ModuleSet has a sidebarTitle that will be displayed for all modules
          in the set.  The contained modules' sidebarTitles will be ignored.
       -- Besides the sidebarTitle, nothing is displayed for a ModuleSet.  It
          is almost entirely just a container.
       -- Modules in a set may call interface.moveToPage(), but only to other
          modules within the same set.

       This is an abstract class.  All ModuleSets should subclass this one and
       define the following attributes and methods below.
    """
    def __init__(self):
        """Create a new ModuleSet instance.  This method must be provided by
           all subclasses.  Of the following instance attributes, all are
           required.  The module loader will check that all required attibutes
           are present and defined.  Instance attributes:

           mode         -- The mode of firstboot operation that this set should
                           appear in.  MODE_REGULAR means the set will appear
                           only in the regular running mode.  MODE_RECONFIG
                           means the set will appear in both regular mode and
                           reconfig mode.
           moduleList   -- The list of modules contained in this set.  This
                           list will be populated automatically.  It is for
                           read-only use here.
           path         -- The directory containing the modules within this
                           set.
           priority     -- An integer specifying the order in which this module
                           should be loaded and appear in firstboot.  The lower
                           the priority number, the earlier this module will
                           be loaded and run.  All modules with the same
                           priority will then be ordered alphabetically by
                           title.  This priority is for sorting the set within
                           the overall module list.
           sidebarTitle -- A brief word or phrase that will appear on the
                           firstboot sidebar on the left side of the screen.
        """

        if self.__class__ is ModuleSet:
            raise TypeError, "ModuleSet is an abstract class."

        self.mode = MODE_REGULAR
        self.moduleList = []
        self.path = None
        self.priority = 0
        self.sidebarTitle = None

    def createScreen(self):
        """A convenience method for running createScreen on all the modules
           contained within this set.  Subclasses should not need to override
           this method.
        """
        for module in self.moduleList:
            module.createScreen()

            if isinstance(module, Module) and module.vbox is None:
                logging.error(_("Module %s did not set up its UI; removing.") % module.title)
                self.moduleList.remove(module)

    def initializeUI(self):
        """A convenience method for running initializeUI on all the modules
           contained within this set.  Subclasses should not need to override
           this method.
        """
        for module in self.moduleList:
            module.initializeUI()

    def loadModules(self, mode=MODE_REGULAR):
        """Load all the modules contained by this module set.  Subclasses
           should not need to override this method.  Arguments:

           mode -- The mode of operation firstboot is running under.
        """
        if self.path is not None:
            # XXX
            reconfig = True if mode == MODE_RECONFIG else False

            from firstboot.loader import load_modules
            self.moduleList = load_modules(self.path, reconfig)

    def needsNetwork(self):
        """Does this module set require the network to be active in order to
           run?  By default, no module sets need networking.  If the set
           requires networking which is not available, the set will not be
           presented.  Note that within a ModuleSet, individual modules can
           still specify their own needsNetwork() method to take further
           action, so some modules may not be present even if the ModuleSet
           is loaded.  Sets that require networking should override this
           method.
        """
        return False

    def needsReboot(self):
        """A convenience method for running needsReboot on all the modules
           contained within this set.  Subclasses should not need to override
           this method.
        """
        for module in self.moduleList:
            if module.needsReboot():
                return True

        return False

    def renderModule(self, interface):
        """A convenience method for running renderModule on all the modules
           contained within this set.  Subclasses should not need to override
           this method.  Arguments:

           interface -- A reference to the running Interface class.
        """
        for module in self.moduleList:
            module.renderModule(interface)

    def shouldAppear(self):
        """Should this module set appear in firstboot?  This method will be
           called after the setis loaded, but before any UI work is performed.
           If False, no screens will be created and the set will not be
           displayed.  Note that within a ModuleSet, individual modules can
           still specify their own shouldAppear() method to take further action
           so some modules may not be present even if the ModuleSet is loaded.
           By default, all sets will be displayed.  Sets that need other
           behavior should override this method.
        """
        return True

    @property
    def reconfig(self):
        return self.mode == MODE_RECONFIG
