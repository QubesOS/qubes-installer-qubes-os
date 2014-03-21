#
# The Qubes OS Project, http://www.qubes-os.org
#
# Copyright (C) 2011  Tomasz Sterna <tomek@xiaoka.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
#
import gtk
import libuser
import os, string, sys, time, re
import threading, subprocess, grp

from firstboot.config import *
from firstboot.constants import *
from firstboot.functions import *
from firstboot.module import *

import gettext
_ = lambda x: gettext.ldgettext("firstboot", x)
N_ = lambda x: x

class moduleClass(Module):
    netvm_name = "netvm"
    fwvm_name  = "firewallvm"

    def __init__(self):
        Module.__init__(self)
        self.priority = 10000
        self.sidebarTitle = N_("Create Service VMs")
        self.title = N_("Create Service VMs")
        self.icon = "qubes.png"
        self.admin = libuser.admin()

    def apply(self, interface, testing=False):
        try:

            qubes_users = self.admin.enumerateUsersByGroup('qubes')
            if self.radio_servicevms_and_appvms.get_active() and len(qubes_users) < 1:
                self._showErrorMessage(_("You must create a user account to create default AppVMs."))
                return RESULT_FAILURE
            else:
                self.qubes_user = qubes_users[0]

            self.radio_servicevms_and_appvms.set_sensitive(False)
            self.radio_onlyservicevms.set_sensitive(False)
            self.radio_dontdoanything.set_sensitive(False)

            if self.progress is None:
                self.progress = gtk.ProgressBar()
                self.progress.set_pulse_step(0.06)
                self.vbox.pack_start(self.progress, True, False)
            self.progress.show()

            if testing:
                return RESULT_SUCCESS

            if self.radio_dontdoanything.get_active():
                return RESULT_SUCCESS

            interface.nextButton.set_sensitive(False)

            self.create_default_netvm()
            self.create_default_fwvm()
            self.set_networking_type(netvm=True)
            self.start_qubes_networking()
            self.configure_template()
            self.create_default_dvm()

            if self.radio_servicevms_and_appvms.get_active():
                self.create_appvms()

            interface.nextButton.set_sensitive(True)
            return RESULT_SUCCESS
        except Exception as e:
            md = gtk.MessageDialog(interface.win, gtk.DIALOG_DESTROY_WITH_PARENT,
                    gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE,
                    self.stage + " failure!\n\n" + str(e))
            md.run()
            md.destroy()
            self.show_stage("Failure...")
            self.progress.hide()

            self.radio_dontdoanything.set_active(True)
            interface.nextButton.set_sensitive(True)

            return RESULT_FAILURE

    def show_stage(self, stage):
        self.stage = stage
        self.progress.set_text(stage)

    def configure_template(self):
        self.show_stage(_("Configuring default TemplateVM"))
        self.run_in_thread(self.do_configure_template)

    def run_in_thread(self, method):
        thread = threading.Thread(target=method)
        thread.start()
        count = 0
        while thread.is_alive():
            self.progress.pulse()
            while gtk.events_pending():
                gtk.main_iteration(False)
            time.sleep(0.1)
        if self.process_error is not None:
            raise Exception(self.process_error)

    def create_default_netvm(self):
        self.show_stage(_("Creating default NetworkVM"))
        self.run_in_thread(self.do_create_netvm)

    def create_default_fwvm(self):
        self.show_stage(_("Creating default FirewallVM"))
        self.run_in_thread(self.do_create_fwvm)

    def create_default_dvm(self):
        self.show_stage(_("Creating default DisposableVM"))
        self.run_in_thread(self.do_create_dvm)

    def set_networking_type(self, netvm):
        if netvm:
            self.show_stage(_("Setting FirewallVM + NetworkVM networking"))
            self.run_in_thread(self.do_set_netvm_networking)
        else:
            self.show_stage(_("Setting Dom0 networking"))
            self.run_in_thread(self.do_set_dom0_networking)

    def start_qubes_networking (self):
        self.show_stage(_("Starting Qubes networking"))
        self.run_in_thread(self.do_start_networking)

    def create_appvms (self):
        self.show_stage(_("Creating handy AppVMs"))
        self.run_in_thread(self.do_create_appvms)

    def run_command(self, command):
        try:
            os.setgid(self.qubes_gid)
            os.umask(0007)
            cmd = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            out = cmd.communicate()[0]
            if cmd.returncode == 0:
                self.process_error = None
            else:
                self.process_error = out
        except Exception as e:
            self.process_error = str(e)

    def find_net_devices(self):
        p = subprocess.Popen (["/sbin/lspci", "-mm", "-n"], stdout=subprocess.PIPE)
        result = p.communicate()
        retcode = p.returncode
        if (retcode != 0):
            print "ERROR when executing lspci!"
            raise IOError

        net_devices = set()
        rx_netdev = re.compile (r"^([0-9][0-9]:[0-9][0-9].[0-9]) \"02")
        for dev in str(result[0]).splitlines():
            match = rx_netdev.match (dev)
            if match is not None:
                dev_bdf = match.group(1)
                assert dev_bdf is not None
                net_devices.add (dev_bdf)

        return  net_devices

    def do_create_netvm(self):
        self.run_command(['su', '-c', '/usr/bin/qvm-create --net --label red %s' % self.netvm_name, self.qubes_user])
        for dev in self.find_net_devices():
            self.run_command(['/usr/bin/qvm-pci', '-a', self.netvm_name, dev])

    def do_create_fwvm(self):
        self.run_command(['su', '-c', '/usr/bin/qvm-create --proxy --label green %s' % self.fwvm_name, '-', self.qubes_user])

    def do_create_dvm(self):
        self.run_command(['su', '-c', '/usr/bin/qvm-create-default-dvm --default-template --default-script', self.qubes_user])

    def do_set_netvm_networking(self):
        self.run_command(['/usr/bin/qvm-prefs', '--force-root', '--set', self.fwvm_name, 'netvm', self.netvm_name])
        self.run_command(['/usr/bin/qubes-prefs', '--set', 'default-netvm', self.fwvm_name])

    def do_set_dom0_networking(self):
        self.run_command(['/usr/bin/qubes-prefs', '--set', 'default-netvm', 'dom0'])

    def do_start_networking(self):
        subprocess.check_call(['/usr/sbin/service', 'qubes_netvm', 'start'])

    def do_configure_template(self):
        subprocess.check_call(['/bin/mkdir', '-p', '/mnt/template-root'])
        for template in os.listdir('/var/lib/qubes/vm-templates'):
            subprocess.check_call(['/bin/mount', '-oloop',
                '/var/lib/qubes/vm-templates/%s/root.img' % template,
                '/mnt/template-root'])
            # Copy timezone setting from Dom0 to template
            subprocess.check_call(['cp', '/etc/localtime', '/mnt/template-root/etc'])
            subprocess.check_call(['cp', '/etc/ntp.conf', '/mnt/template-root/etc'])
            subprocess.check_call(['/bin/umount', '/mnt/template-root'])
            subprocess.check_call(['/bin/rmdir', '/mnt/template-root'])

    def do_create_appvms(self):
        self.run_command(['su', '-c', '/usr/bin/qvm-create work --label green', '-', self.qubes_user])
        self.run_command(['su', '-c', '/usr/bin/qvm-create banking --label green', '-', self.qubes_user])
        self.run_command(['su', '-c', '/usr/bin/qvm-create personal --label yellow', '-', self.qubes_user])
        self.run_command(['su', '-c', '/usr/bin/qvm-create untrusted --label red', '-', self.qubes_user])

    def createScreen(self):
        self.vbox = gtk.VBox(spacing=5)

        label = gtk.Label(_("Almost there! We just need to create a few system service VM.\n\n"
            "We can also create a few AppVMs that might be useful for most users, "
            "or you might prefer to do it yourself later.\n\n"
            "Choose an option below and click 'Finish'..."))

        label.set_line_wrap(True)
        label.set_alignment(0.0, 0.5)
        label.set_size_request(500, -1)
        self.vbox.pack_start(label, False, True, padding=20)

        self.radio_servicevms_and_appvms  = gtk.RadioButton(None, _("Create default service VMs, and pre-defined AppVMs (work, banking, personal, untrusted)"))
        self.vbox.pack_start(self.radio_servicevms_and_appvms, False, True)

        self.radio_onlyservicevms = gtk.RadioButton(self.radio_servicevms_and_appvms, _("Just create default service VMs"))
        self.vbox.pack_start(self.radio_onlyservicevms, False, True)

        self.radio_dontdoanything = gtk.RadioButton(self.radio_servicevms_and_appvms, _("Do not create any VMs right now (not recommended, for advanced users only)"))
        self.vbox.pack_start(self.radio_dontdoanything, False, True)

        self.progress = None

    def initializeUI(self):
        self.radio_servicevms_and_appvms.set_active(True)
        self.qubes_gid = grp.getgrnam('qubes').gr_gid
        self.stage = "Initialization"
        self.process_error = None
