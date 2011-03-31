#
# additional_cds.py - firstboot module for add-on CDs
#
# Copyright 2002, 2003, 2007 Red Hat, Inc.
# Copyright 2002, 2003 Brent Fox <bfox@redhat.com>
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
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
import gtk
import kudzu
import os, time
import subprocess

from firstboot.config import *
from firstboot.constants import *
from firstboot.functions import *
from firstboot.module import *

##
## I18N
##
import gettext
_ = lambda x: gettext.ldgettext("firstboot", x)
N_ = lambda x: x

class moduleClass(Module):
    def __init__(self):
        Module.__init__(self)
        self.icon = "lacd.png"
        self.priority = 1000
        self.sidebarTitle = N_("Additional CDs")
        self.title = N_("Additional CDs")

    def shouldAppear(self):
        return False

    def apply(self, interface, testing=False):
        return RESULT_SUCCESS

    def createScreen(self):
        self.vbox = gtk.VBox(spacing=5)

        cd_label_rhel = _("""Please insert the disc labeled "Red Hat Enterprise Linux """
                          """Extras" to allow for installation of third-party plug-ins and """
                          """applications.  You may also insert the Documentation disc, or """
                          """other Red Hat-provided discs to install additional software at """
                          """this time.""")

        cd_label = _("""Please insert any additional software install cds """
                     """at this time.""")

        if os.uname()[4] == "ia64":
            cd_label += _("""\n\nTo enable runtime support of 32-bit applications on the Intel """
                          """Itanium2 architecture you must install the Intel Execution """
                          """Layer package from the Extras disc now.""")

        label = gtk.Label(cd_label)
        label.set_line_wrap(True)
        label.set_alignment(0.0, 0.5)

        button = gtk.Button(_("Install..."))
        button.set_size_request(100, -1)
        button.connect("clicked", self.autorun)

        tempHBox = gtk.HBox()
        tempHBox.pack_start(button, False, False)

        self.vbox.pack_start(label, False, True)
        self.vbox.pack_start(tempHBox, False, padding=20)

    def autorun(self, *args):
        def getCDDev():
            drives = kudzu.probe(kudzu.CLASS_CDROM,
                                 kudzu.BUS_UNSPEC, kudzu.PROBE_ALL)
            return map (lambda d: d.device, drives)

        #Create a gtkInvisible widget to block until the autorun is complete
        i = gtk.Invisible ()
        i.grab_add ()

        dev = None
        mounted = False

        while not mounted:
            for device in getCDDev():
                if device is None:
                    continue

                try:
                    subprocess.call(["mount", "-o", "ro", "/dev/%s" % device, "/mnt"])
                    dev = device
                    break
                except:
                    continue

            if dev is None:
                dlg = gtk.MessageDialog(None, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_NONE,
                                        (_("A CD-ROM has not been detected.  Please insert "
                                           "a CD-ROM in the drive and click \"OK\" to continue.")))
                dlg.set_position(gtk.WIN_POS_CENTER)
                dlg.set_modal(True)
                cancelButton = dlg.add_button('gtk-cancel', 0)
                okButton = dlg.add_button('gtk-ok', 1)
                rc = dlg.run()
                dlg.destroy()

                if rc == 0:
                    #Be sure to remove the focus grab if we have to return here.
                    #Otherwise, the user is stuck
                    i.grab_remove ()
                    return
            else:
                mounted = True

        if os.access("/mnt/autorun", os.R_OK):
            #If there's an autorun file on the cd, run it
            pid = start_process("/mnt/autorun")

            flag = None
            while not flag:
                while gtk.events_pending():
                    gtk.main_iteration_do()

                child_pid, status = os.waitpid(pid, os.WNOHANG)

                if child_pid == pid:
                    flag = 1
                else:
                    time.sleep(0.1)

        else:
            #There's no autorun on the disc, so complain
            dlg = gtk.MessageDialog(None, 0, gtk.MESSAGE_ERROR, gtk.BUTTONS_NONE,
                                    (_("The autorun program cannot be found on the CD. "
                                       "Click \"OK\" to continue.")))
            dlg.set_position(gtk.WIN_POS_CENTER)
            dlg.set_modal(True)
            okButton = dlg.add_button('gtk-ok', 0)
            rc = dlg.run()
            dlg.destroy()

            if rc == 0:
                #Be sure to remove the focus grab if we have to return here.
                #Otherwise, the user is stuck
                i.grab_remove ()

        #I think system-config-packages will do a umount, but just in case it doesn't...
        try:
            subprocess.call(["umount", "/mnt"])
        except:
            #Yep, system-config-packages has already umounted the disc, so fall through and go on
            pass

        #Remove the focus grab of the gtkInvisible widget
        i.grab_remove ()

    def initializeUI(self):
        pass
