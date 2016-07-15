#
# Copyright (C) 2016  M. Vefa Bicakci <m.v.b@runbox.com>
# Copyright (C) 2016  Qubes OS Developers
# Copyright (C) 2013  Red Hat, Inc.
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# the GNU General Public License v.2, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY expressed or implied, including the implied warranties of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.  You should have received a copy of the
# GNU General Public License along with this program; if not, write to the
# Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.  Any Red Hat trademarks that are incorporated in the
# source code or documentation are not subject to the GNU General Public
# License and may only be used or replicated with the express permission of
# Red Hat, Inc.
#
# Red Hat Author(s): Vratislav Podzimek <vpodzime@redhat.com>
#

"""Module with the QubesOsSpoke class."""

# import gettext
# _ = lambda x: gettext.ldgettext("qubes-os-anaconda-plugin", x)

# will never be translated
_ = lambda x: x
N_ = lambda x: x

import functools
import grp
import logging
import os
import os.path
import pyudev
import subprocess
import threading

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GLib', '2.0')

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib

from pyanaconda import iutil
from pyanaconda.ui.categories.system import SystemCategory
from pyanaconda.ui.gui.spokes import NormalSpoke
from pyanaconda.ui.common import FirstbootOnlySpokeMixIn

# export only the spoke, no helper functions, classes or constants
__all__ = ["QubesOsSpoke"]

def is_package_installed(pkgname):
    return not subprocess.call(['rpm', '-q', pkgname],
        stdout=open(os.devnull, 'w'), stderr=open(os.devnull, 'w'))

def usb_keyboard_present():
    context = pyudev.Context()
    keyboards = context.list_devices(subsystem='input', ID_INPUT_KEYBOARD='1')
    return any([d.get('ID_USB_INTERFACES', False) for d in keyboards])

def started_from_usb():
    def get_all_used_devices(dev):
        stat = os.stat(dev)
        if stat.st_rdev:
            # XXX any better idea how to handle device-mapper?
            sysfs_slaves = '/sys/dev/block/{}:{}/slaves'.format(
                os.major(stat.st_rdev), os.minor(stat.st_rdev))
            if os.path.exists(sysfs_slaves):
                for slave_dev in os.listdir(sysfs_slaves):
                    for d in get_all_used_devices('/dev/{}'.format(slave_dev)):
                        yield d
            else:
                yield dev

    context = pyudev.Context()
    mounts = open('/proc/mounts').readlines()
    for mount in mounts:
        device = mount.split(' ')[0]
        if not os.path.exists(device):
            continue
        for dev in get_all_used_devices(device):
            udev_info = pyudev.Device.from_device_file(context, dev)
            if udev_info.get('ID_USB_INTERFACES', False):
                return True

    return False

class QubesChoice(object):
    instances = []

    def __init__(self, label, states, depend=None, extra_check=None,
                 replace=None, indent=False):
        self.widget = Gtk.CheckButton(label=label)
        self.states = states
        self.depend = depend
        self.extra_check = extra_check
        self.selected = None
        self.replace = replace

        self._can_be_sensitive = True

        if indent:
            self.outer_widget = Gtk.Alignment()
            self.outer_widget.add(self.widget)
            self.outer_widget.set_padding(0, 0, 20, 0)
        else:
            self.outer_widget = self.widget

        if self.depend is not None:
            self.depend.widget.connect('toggled', self.friend_on_toggled)
            self.depend.widget.connect('notify::sensitive', self.friend_on_toggled)
            self.friend_on_toggled(self.depend.widget)

        self.instances.append(self)

    def friend_on_toggled(self, other_widget, param_string=''):
        self.set_sensitive(other_widget.get_active())

    def get_selected(self):
        return (self.selected
                if self.selected is not None
                else self.widget.get_sensitive() and self.widget.get_active())

    def store_selected(self):
        self.selected = self.get_selected()

    def set_sensitive(self, sensitive):
        if self._can_be_sensitive:
            self.widget.set_sensitive(sensitive)

    @classmethod
    def on_check_advanced_toggled(cls, widget):
        selected = widget.get_active()

        # this works, because you cannot instantiate the choices in wrong order
        # (cls.instances is a list and have deterministic ordering)
        for choice in cls.instances:
            choice.set_sensitive(not selected and
                (choice.depend is None or choice.depend.get_selected()))

    @classmethod
    def get_states(cls):
        replaced = functools.reduce(
            lambda x, y: x+y if y else x,
            (choice.replace for choice in cls.instances if
             choice.get_selected()),
            ()
        )
        for choice in cls.instances:
            if choice.get_selected():
                for state in choice.states:
                    if state not in replaced:
                        yield state


class DisabledChoice(QubesChoice):
    def __init__(self, label):
        super(DisabledChoice, self).__init__(label, ())
        self.widget.set_sensitive(False)
        self._can_be_sensitive = False

class QubesOsSpoke(FirstbootOnlySpokeMixIn, NormalSpoke):
    """
    Since this class inherits from the FirstbootOnlySpokeMixIn, it will
    only appear in the Initial Setup (successor of the Firstboot tool).

    :see: pyanaconda.ui.common.UIObject
    :see: pyanaconda.ui.common.Spoke
    :see: pyanaconda.ui.gui.GUIObject
    :see: pyanaconda.ui.common.FirstbootSpokeMixIn
    :see: pyanaconda.ui.gui.spokes.NormalSpoke

    """

    ### class attributes defined by API ###

    # list all top-level objects from the .glade file that should be exposed
    # to the spoke or leave empty to extract everything
    builderObjects = ["qubesOsSpokeWindow"]

    # the name of the main window widget
    mainWidgetName = "qubesOsSpokeWindow"

    # name of the .glade file in the same directory as this source
    uiFile = "qubes_os.glade"

    # category this spoke belongs to
    category = SystemCategory

    # spoke icon (will be displayed on the hub)
    # preferred are the -symbolic icons as these are used in Anaconda's spokes
    icon = "qubes-logo-icon"

    # title of the spoke (will be displayed on the hub)
    title = N_("_QUBES OS")

    ### methods defined by API ###
    def __init__(self, data, storage, payload, instclass):
        """
        :see: pyanaconda.ui.common.Spoke.__init__
        :param data: data object passed to every spoke to load/store data
                     from/to it
        :type data: pykickstart.base.BaseHandler
        :param storage: object storing storage-related information
                        (disks, partitioning, bootloader, etc.)
        :type storage: blivet.Blivet
        :param payload: object storing packaging-related information
        :type payload: pyanaconda.packaging.Payload
        :param instclass: distribution-specific information
        :type instclass: pyanaconda.installclass.BaseInstallClass

        """

        NormalSpoke.__init__(self, data, storage, payload, instclass)

        self.logger = logging.getLogger("anaconda")

        self.main_box = self.builder.get_object("mainBox")
        self.thread_dialog = None

        self.qubes_user = None
        self.qubes_gid = None
        self.default_template = 'fedora-23'

        self.set_stage("Start-up")
        self.done = False

        self.__init_qubes_choices()

    def __init_qubes_choices(self):
        self.choice_network = QubesChoice(
            _('Create default system qubes (sys-net, sys-firewall)'),
            ('qvm.sys-net', 'qvm.sys-firewall'))

        self.choice_default = QubesChoice(
            _('Create default application qubes '
                '(personal, work, untrusted, vault)'),
            ('qvm.personal', 'qvm.work', 'qvm.untrusted', 'qvm.vault'),
            depend=self.choice_network)

        if (is_package_installed('qubes-template-whonix-gw') and
                is_package_installed('qubes-template-whonix-ws')):
            self.choice_whonix = QubesChoice(
                _('Create Whonix Gateway and Workstation qubes '
                    '(sys-whonix, anon-whonix)'),
                ('qvm.sys-whonix', 'qvm.anon-whonix'),
                depend=self.choice_network)
        else:
            self.choice_whonix = DisabledChoice(_("Whonix not installed"))

        self.choice_whonix_default = QubesChoice(
            _('Route applications traffic and updates through Tor anonymity '
              'network [experimental]'),
            (),
            depend=self.choice_whonix,
            indent=True)

        if not usb_keyboard_present() and not started_from_usb():
            self.choice_usb = QubesChoice(
                _('Create USB qube holding all USB controllers (sys-usb) '
                    '[experimental]'),
                ('qvm.sys-usb',))
        else:
            self.choice_usb = DisabledChoice(
                _('USB qube configuration disabled - you are using USB '
                  'keyboard or USB disk'))

        self.choice_usb_with_net = QubesChoice(
            _("Use sys-net qube for both networking and USB devices"),
            ('qvm.sys-net-with-usb',),
            depend=self.choice_usb,
            replace=('qvm.sys-usb',),
            indent=True
        )

        self.check_advanced = Gtk.CheckButton(label=_('Do not configure anything (for advanced users)'))
        self.check_advanced.connect('toggled', QubesChoice.on_check_advanced_toggled)

        for choice in QubesChoice.instances:
            self.main_box.pack_start(choice.outer_widget, False, True, 0)

        self.main_box.pack_end(self.check_advanced, False, True, 0)

        self.check_advanced.set_active(False)

        self.choice_network.widget.set_active(True)
        self.choice_default.widget.set_active(True)
        if self.choice_whonix.widget.get_sensitive():
            self.choice_whonix.widget.set_active(True)

    def initialize(self):
        """
        The initialize method that is called after the instance is created.
        The difference between __init__ and this method is that this may take
        a long time and thus could be called in a separated thread.

        :see: pyanaconda.ui.common.UIObject.initialize

        """

        NormalSpoke.initialize(self)

    def refresh(self):
        """
        The refresh method that is called every time the spoke is displayed.
        It should update the UI elements according to the contents of
        self.data.

        :see: pyanaconda.ui.common.UIObject.refresh

        """

        # nothing to do here
        pass

    def apply(self):
        """
        The apply method that is called when the spoke is left. It should
        update the contents of self.data with values set in the GUI elements.

        """

        # nothing to do here
        pass

    @property
    def ready(self):
        """
        The ready property that tells whether the spoke is ready (can be visited)
        or not. The spoke is made (in)sensitive based on the returned value.

        :rtype: bool

        """

        return True

    @property
    def completed(self):
        """
        The completed property that tells whether all mandatory items on the
        spoke are set, or not. The spoke will be marked on the hub as completed
        or uncompleted acording to the returned value.

        :rtype: bool

        """

        return self.done

    @property
    def mandatory(self):
        """
        The mandatory property that tells whether the spoke is mandatory to be
        completed to continue in the installation process.

        :rtype: bool

        """
        return True

    @property
    def status(self):
        """
        The status property that is a brief string describing the state of the
        spoke. It should describe whether all values are set and if possible
        also the values themselves. The returned value will appear on the hub
        below the spoke's title.

        :rtype: str

        """

        return ""

    def execute(self):
        """
        The execute method that is called when the spoke is left. It is
        supposed to do all changes to the runtime environment according to
        the values set in the GUI elements.

        """
        for choice in QubesChoice.instances:
            choice.store_selected()

        self.thread_dialog = ThreadDialog("Qubes OS Setup", self.do_setup, (), transient_for=self.main_window)
        self.thread_dialog.run()
        self.thread_dialog.destroy()

    def do_setup(self, *args):
        try:
            self.qubes_gid = grp.getgrnam('qubes').gr_gid

            qubes_users = grp.getgrnam('qubes').gr_mem

            if len(qubes_users) < 1:
                self.showErrorMessage(_("You must create a user account to create default VMs."))
                return
            else:
                self.qubes_user = qubes_users[0]

            if self.check_advanced.get_active():
                return

            errors = []

            os.setgid(self.qubes_gid)
            os.umask(0o0007)

            # Finish template(s) installation, because it wasn't fully possible
            # from anaconda (it isn't possible to start a VM there).
            # This is specific to firstboot, not general configuration.
            for template in os.listdir('/var/lib/qubes/vm-templates'):
                try:
                    self.configure_template(template)
                except Exception as e:
                    errors.append((self.stage, str(e)))

            self.configure_dom0()
            self.configure_default_template()
            self.configure_qubes()
            if self.choice_network.get_selected():
                self.configure_network()
            if self.choice_usb.get_selected() and not self.choice_usb_with_net.get_selected():
                # Workaround for #1464 (so qvm.start from salt can't be used)
                self.run_command(['systemctl', 'start', 'qubes-vm@sys-usb.service'])

            try:
                self.configure_default_dvm()
            except Exception as e:
                errors.append((self.stage, str(e)))

            if errors:
                msg = ""
                for (stage, error) in errors:
                    msg += "{} failed:\n{}\n\n".format(stage, error)

                raise Exception(msg)

        except Exception as e:
            self.showErrorMessage(str(e))

        finally:
            self.thread_dialog.done()
            self.done = True

    def set_stage(self, stage):
        self.stage = stage

        if self.thread_dialog != None:
            self.thread_dialog.set_text(stage)

    def run_command(self, command, stdin=None, ignore_failure=False):
        process_error = None

        try:
            sys_root = iutil.getSysroot()

            cmd = iutil.startProgram(command, stderr=subprocess.PIPE, stdin=stdin, root=sys_root)

            (stdout, stderr) = cmd.communicate()

            stdout = stdout.decode("utf-8")
            stderr = stderr.decode("utf-8")

            if not ignore_failure and cmd.returncode != 0:
                process_error = "{} failed:\nstdout: \"{}\"\nstderr: \"{}\"".format(command, stdout, stderr)

        except Exception as e:
            process_error = str(e)

        if process_error:
            self.logger.error(process_error)
            raise Exception(process_error)

        return (stdout, stderr)

    def configure_dom0(self):
        self.set_stage("Setting up administration VM (dom0)")

        for service in [ 'rdisc', 'kdump', 'libvirt-guests', 'salt-minion' ]:
            self.run_command(['systemctl', 'disable', '{}.service'.format(service) ], ignore_failure=True)
            self.run_command(['systemctl', 'stop',    '{}.service'.format(service) ], ignore_failure=True)

    def configure_qubes(self):
        self.set_stage('Executing qubes configuration')

        try:
            # get rid of initial entries (from package installation time)
            os.rename('/var/log/salt/minion', '/var/log/salt/minion.install')
        except OSError:
            pass

        # Refresh minion configuration to make sure all installed formulas are included
        self.run_command(['qubesctl', 'saltutil.sync_all'])

        for state in QubesChoice.get_states():
            print("Setting up state: {}".format(state))
            self.run_command(['qubesctl', 'top.enable', state])

        try:
            self.run_command(['qubesctl', 'state.highstate'])
        except Exception:
            raise Exception(
                    ("Qubes initial configuration failed. Login to the system and " +
                     "check /var/log/salt/minion for details. " +
                     "You can retry configuration by calling " +
                     "'sudo qubesctl state.highstate' in dom0 (you will get " +
                     "detailed state there)."))

    def configure_default_template(self):
        self.set_stage('Setting default template')
        self.run_command(['/usr/bin/qubes-prefs', '--set', 'default-template', self.default_template])

    def configure_default_dvm(self):
        self.set_stage("Creating default DisposableVM")

        try:
            self.run_command(['su', '-c', '/usr/bin/qvm-create-default-dvm --default-template --default-script', self.qubes_user])
        except Exception:
            # Kill DispVM template if still running
            # Do not use self.run_command to not clobber process output
            subprocess.call(['qvm-kill', '{}-dvm'.format(self.default_template)])
            raise

    def configure_network(self):
        self.set_stage('Setting up networking')

        default_netvm = 'sys-firewall'
        if self.choice_whonix_default.get_selected():
            default_netvm = 'sys-whonix'

        self.run_command(['/usr/bin/qvm-prefs', '--force-root', '--set', 'sys-firewall', 'netvm', 'sys-net'])
        self.run_command(['/usr/bin/qubes-prefs', '--set', 'default-netvm', default_netvm])
        self.run_command(['/usr/bin/qubes-prefs', '--set', 'updatevm', default_netvm])
        self.run_command(['/usr/bin/qubes-prefs', '--set', 'clockvm', 'sys-net'])
        self.run_command(['/usr/sbin/service', 'qubes-netvm', 'start'])

    def configure_template(self, template):
        self.set_stage("Configuring TemplateVM {}".format(template))
        self.run_command(['qvm-start', '--no-guid', template])
        self.run_command(['su', '-c', 'qvm-sync-appmenus {}'.format(template), '-', self.qubes_user])
        self.run_command(['qvm-shutdown', '--wait', template])

    def showErrorMessage(self, text):
        self.thread_dialog.run_in_ui_thread(self.showErrorMessageHelper, text)

    def showErrorMessageHelper(self, text):
        dlg = Gtk.MessageDialog(title="Error", message_type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK, text=text)
        dlg.set_position(Gtk.WindowPosition.CENTER)
        dlg.set_modal(True)
        dlg.set_transient_for(self.thread_dialog)
        dlg.run()
        dlg.destroy()

class ThreadDialog(Gtk.Dialog):
    def __init__(self, title, fun, args, transient_for=None):
        Gtk.Dialog.__init__(self, title=title, transient_for=transient_for)

        self.set_modal(True)
        self.set_default_size(500, 100)

        self.connect('delete-event', self.on_delete_event)

        self.progress = Gtk.ProgressBar()
        self.progress.set_pulse_step(100)
        self.progress.set_text("")
        self.progress.set_show_text(False)

        self.label = Gtk.Label()
        self.label.set_line_wrap(True)
        self.label.set_text("")

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.box.pack_start(self.progress, True, True, 0)
        self.box.pack_start(self.label, True, True, 0)

        self.get_content_area().pack_start(self.box, True, True, 0)

        self.fun = fun
        self.args = args

        self.logger = logging.getLogger("anaconda")

        self.thread = threading.Thread(target=self.fun, args=self.args)

    def on_delete_event(self, widget=None, *args):
        # Ignore the clicks on the close button by returning True.
        self.logger.info("Caught delete-event")
        return True

    def set_text(self, text):
        Gdk.threads_add_timeout(GLib.PRIORITY_DEFAULT, 0, self.label.set_text, text)

    def done(self):
        Gdk.threads_add_timeout(GLib.PRIORITY_DEFAULT, 100, self.done_helper, ())

    def done_helper(self, *args):
        self.logger.info("Joining thread.")
        self.thread.join()

        self.logger.info("Stopping self.")
        self.response(Gtk.ResponseType.ACCEPT)

    def run_in_ui_thread(self, fun, *args):
        Gdk.threads_add_timeout(GLib.PRIORITY_DEFAULT, 0, fun, *args)

    def run(self):
        self.thread.start()
        self.progress.pulse()
        self.show_all()

        ret = None
        while ret in (None, Gtk.ResponseType.DELETE_EVENT):
            ret = super(ThreadDialog, self).run()

        return ret

if __name__ == "__main__":
    import time

    def hello_fun(*args):
        global thread_dialog
        thread_dialog.set_text("Hello, world! " * 30)
        time.sleep(2)
        thread_dialog.set_text("Goodbye, world!")
        time.sleep(1)
        thread_dialog.done()
        return

    logger = logging.getLogger("anaconda")
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    thread_dialog = ThreadDialog("Hello", hello_fun, ())
    thread_dialog.run()
