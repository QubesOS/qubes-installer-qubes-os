#
# Chris Lumens <clumens@redhat.com>
#
# Copyright 2008 Red Hat, Inc.
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
import gtk
import os, string, sys, time

from firstboot.config import *
from firstboot.constants import *
from firstboot.functions import *
from firstboot.module import *

import gettext
_ = lambda x: gettext.ldgettext("firstboot", x)
N_ = lambda x: x

sys.path.append("/usr/share/system-config-date")
from scdMainWindow import scdMainWindow

class moduleClass(Module):
    def __init__(self):
        Module.__init__(self)
        self.priority = 100
        self.sidebarTitle = N_("Date and Time")
        self.title = N_("Date and Time")
        self.icon = "system-config-date.png"

	self.scd = None

    def apply(self, interface, testing=False):
        if testing:
            return RESULT_SUCCESS

        try:
            rc = self.scd.firstboot_apply()
            if rc == 0 and self.scd.closeParent:
                return RESULT_SUCCESS
            else:
                return RESULT_FAILURE
        except:
            return RESULT_FAILURE

    def createScreen(self):
        self.vbox = gtk.VBox(spacing=5)

	label = gtk.Label(_("Please set the date and time for the system."))
	label.set_line_wrap(True)
	label.set_alignment(0.0, 0.5)
	label.set_size_request(500, -1)
	self.vbox.pack_start(label, False, True, padding=20)

	self.scd = scdMainWindow(firstboot=True, showPages=["datetime"])
	self.vbox.pack_start(self.scd.firstboot_widget(), False, False)

    def initializeUI(self):
        pass
