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
from firstboot.config import *
from firstboot.constants import *
import logging

import gettext
_ = lambda x: gettext.ldgettext("firstboot", x)

class Module:
    """The base class for all firstboot modules.  A firstboot module is a
       single screen that is presented during the first bootup of the system.
       A single module is used for asking a single question or several related
       questions, or for configuring one individual system component.

       This is an abstract class.  All firstboot modules should subclass this
       one and define the following attributes and methods as described below.
    """
    def __init__(self):
        """Create a new Module instance.  This method must be provided by
           all subclasses.  Of the following instance attributes, only icon
           is not required.  The module loader will check that all required
           attributes are present and defined.  Instance attributes;

           icon         -- No longer used.
           mode         -- The mode of firstboot operation that this module
                           should appear in.  MODE_REGULAR means the module
                           will appear only in the regular running mode.
                           MODE_RECONFIG means the module will appear in both
                           regular mode and reconfig mode.
           priority     -- An integer specifying the order in which this module
                           should be loaded and appear in firstboot.  The lower
                           the priority number, the earlier this module will
                           be loaded and run.  All modules with the same
                           priority will then be ordered alphabetically by
                           title.
           sidebarTitle -- A brief word or phrase that will appear on the
                           firstboot sidebar on the left side of the screen.
           title        -- The title of the module that will appear on the
                           right side of the screen above the module when it
                           is displayed.  The title is shown in large bold
                           letters.
           vbox         -- A gtk.VBox that contains all the widgets for this
                           module.  The vbox will be wrapped in various other
                           widgets to present a consistent look and placed
                           on the right side of the screen when the module is
                           displayed.
        """

        if self.__class__ is Module:
            raise TypeError, "Module is an abstract class."

        self.icon = None
        self.mode = MODE_REGULAR
        self.priority = 0
        self.sidebarTitle = None
        self.title = None
        self.vbox = None

    def apply(self, interface, testing=False):
        """Called when the Next button is clicked on the interface.  This
           method takes whatever action is appropriate based on the state
           of the UI.  This can include writing things to disk or running
           programs.  apply should return one of the following values:

           RESULT_FAILURE -- Return this value if firstboot should not move
                             to the next screen.  This is commonly used when
                             a module displays a yes/no question, and the user
                             selects no so the module must present its screen
                             again.
           RESULT_SUCCESS -- Return this value if everything worked.  This
                             tells firstboot that it should advance to the
                             next module.
           RESULT_JUMP    -- Return this value if the module called
                             interface.moveToPage.  This tells firstboot to
                             not automatically advance to the next module.
                             Otherwise, the page your module advanced to will
                             be skipped.

           This method must be provided by all subclasses.  Arguments:

           interface -- A reference to the running Interface class.
           testing   -- If True, this method must not make any permanent
                        changes to disk.
        """
        raise NotImplementedError, "apply() not implemented for Module."

    def createScreen(self):
        """Create a new instance of gtk.VBox, the UI elements required for
           this module, and pack them into self.vbox.  Do not take any action
           to initialize the UI elements or write anything to disk.  This
           method does not return any value, and is the first method called on
           a module after it is loaded.  This method must be provided by all
           subclasses.
        """
        raise NotImplementedError, "createScreen() not implemented for Module."

    def focus(self):
        """Focus some initial UI element on the page.  This method is called
           immediately after the UI is initialized and before it is displayed
           on the screen.  If the module requires that some UI element besides
           the Next button be focused by default, the module should override
           this method.  Otherwise, nothing will be done.
       """
        pass

    def initializeUI(self):
        """Synchronize the state of the UI with whatever's present on disk
           or wherever else the module looks for its default values.  This
           method will be called immediately before the module is displayed,
           both when moving forwards and backwards through the module list.
           It should be designed to be called multiple times.  This method
           must be provided by all subclasses.
        """
        raise NotImplementedError, "initializeUI() not implemented for Module."

    def needsNetwork(self):
        """Does this module require the network to be active in order to run?
           By default, no modules need networking.  If the module requires
           networking which is not available, the module will not be presented.
           Modules that require networking should override this method.
        """
        return False

    def needsReboot(self):
        """Does whatever action happened in this module's apply() method
           require rebooting the computer?  By default, no modules require
           rebooting.  Modules that require the system to be rebooted for
           their changes to take effect should override this method.
        """
        return False

    def renderModule(self, interface):
        """Wrap the module's top-level UI element in the other elements
           required to make sure all modules have the same common look.  This
           method is called immediately after createScreen() and requires that
           self.vbox be initialized.  Modules should not override this method.
           Arguments:

           interface -- A reference to the running Interface class.
        """
        if self.vbox is None:
            logging.error("Module %s has not initialized its UI" % self.title)
            raise SystemError, "Module %s has not initializes its UI" % self.title

        import gtk
        from firstboot.functions import loadToImage

        # Create the large label that goes at the top of the right side.
        label = gtk.Label("")
        label.set_alignment(0.0, 0.5)
        label.set_markup("<span foreground='#000000' size='30000' font_family='Helvetica'><b>%s</b></span>" % _(self.title))

        titleBox = gtk.HBox()

        titleBox.pack_start(label, True)
        titleBox.set_spacing(8)

        self.vbox.pack_start(titleBox, False)
        self.vbox.reorder_child(titleBox, 0)

    def shouldAppear(self):
        """Should this module appear in firstboot?  This method will be called
           after the module is loaded, but before any UI work is performed.
           If False, the screen will not be created and the module will not
           be displayed.  By default, all modules will be displayed.  Modules
           that need other behavior should override this method.
        """
        return True

    @property
    def reconfig(self):
        return self.mode == MODE_RECONFIG
