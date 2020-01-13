#
# The Qubes OS Project, https://www.qubes-os.org/
#
# Copyright (C) 2019 Marek Marczykowski-Górecki
#                           <marmarek@invisiblethingslab.com>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU General Public
# License along with this library; if not, see <https://www.gnu.org/licenses/>.
#
import grp
import os

import distutils.version
import pyudev
import subprocess

from pyanaconda import iutil
from pyanaconda.addons import AddonData
from pykickstart.errors import KickstartValueError
from pyanaconda.progress import progress_message

import logging
log = logging.getLogger("anaconda")

__all__ = ['QubesData']


def is_package_installed(pkgname):
    pkglist = subprocess.check_output(['rpm', '-qa', pkgname])
    return bool(pkglist)

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


class QubesData(AddonData):
    """
    Class providing and storing data for the Qubes initial setup addon
    """

    bool_options = (
        'system_vms', 'default_vms', 'whonix_vms', 'whonix_default', 'usbvm',
        'usbvm_with_netvm', 'skip')

    def __init__(self, name):
        """

        :param name: name of the addon
        :type name: str
        """

        super(QubesData, self).__init__(name)

        self.whonix_available = (
                is_package_installed('qubes-template-whonix-gw*') and
                is_package_installed('qubes-template-whonix-ws*'))
        self.usbvm_available = (
                not usb_keyboard_present() and not started_from_usb())
        self.system_vms = True
        self.default_vms = True

        self.whonix_vms = self.whonix_available
        self.whonix_default = False

        self.usbvm = self.usbvm_available
        self.usbvm_with_netvm = False

        self.skip = False

        # this is a hack, but initial-setup do not have progress hub or similar
        # provision for handling lengthy self.execute() call, so we must do it
        # ourselves
        self.gui_mode = False
        self.thread_dialog = None

        # choose latest fedora template
        fedora_tpls = sorted(
            name for name in os.listdir('/var/lib/qubes/vm-templates')
            if 'fedora' in name)
        if fedora_tpls:
            self.default_template = fedora_tpls[-1]
        else:
            print(
                'ERROR: No Fedora template is installed, '
                'cannot set default template!')
            self.default_template = None

        self.qubes_user = None

        self.seen = False

    def handle_header(self, lineno, args):
        pass

    def handle_line(self, line):
        """

        :param line:
        :return:
        """

        try:
            (param, value) = line.strip().split(maxsplit=1)
        except ValueError:
            raise KickstartValueError('invalid line: %s' % line)
        if param in self.bool_options:
            if value.lower() not in ('true', 'false'):
                raise KickstartValueError(
                    'invalid value for bool property: %s' % line)
            bool_value = value.lower() == 'true'
            setattr(self, param, bool_value)
        elif param == 'default_template':
            self.default_template = value
        else:
            raise KickstartValueError('invalid parameter: %s' % param)
        self.seen = True

    def __str__(self):
        section = "%addon {}\n".format(self.name)

        for param in self.bool_options:
            section += "{} {!s}\n".format(param, getattr(self, param))

        section += 'default_template {}\n'.format(self.default_template)

        section += '%end\n'
        return section

    def execute(self, storage, ksdata, instClass, users, payload):
        if self.gui_mode:
            from ..gui import ThreadDialog
            self.thread_dialog = ThreadDialog(
                "Qubes OS Setup", self.do_setup, ())
            self.thread_dialog.run()
            self.thread_dialog.destroy()
        else:
            self.do_setup()

    def set_stage(self, stage):
        if self.thread_dialog is not None:
            self.thread_dialog.set_text(stage)
        else:
            print(stage)

    def do_setup(self):
        qubes_gid = grp.getgrnam('qubes').gr_gid

        qubes_users = grp.getgrnam('qubes').gr_mem

        if len(qubes_users) < 1:
            raise Exception(
                  "You must create a user account to create default VMs.")
        else:
            self.qubes_user = qubes_users[0]

        if self.skip:
            return

        errors = []

        os.setgid(qubes_gid)
        os.umask(0o0007)

        self.configure_default_kernel()

        # Finish template(s) installation, because it wasn't fully possible
        # from anaconda (it isn't possible to start a VM there).
        # This is specific to firstboot, not general configuration.
        for template in os.listdir('/var/lib/qubes/vm-templates'):
            try:
                self.configure_template(template,
                    '/var/lib/qubes/vm-templates/' + template)
            except Exception as e:
                errors.append(('Templates', str(e)))

        self.configure_dom0()
        self.configure_default_template()
        self.configure_qubes()
        if self.system_vms:
            self.configure_network()
        if self.usbvm and not self.usbvm_with_netvm:
            # Workaround for #1464 (so qvm.start from salt can't be used)
            self.run_command(['systemctl', 'start', 'qubes-vm@sys-usb.service'])

        try:
            self.configure_default_dvm()
        except Exception as e:
            errors.append(('Default DVM', str(e)))

        if errors:
            msg = ""
            for (stage, error) in errors:
                msg += "{} failed:\n{}\n\n".format(stage, error)

            raise Exception(msg)

    def run_command(self, command, stdin=None, ignore_failure=False):
        process_error = None

        try:
            sys_root = iutil.getSysroot()

            cmd = iutil.startProgram(command,
                stderr=subprocess.PIPE,
                stdin=stdin,
                root=sys_root)

            (stdout, stderr) = cmd.communicate()

            stdout = stdout.decode("utf-8")
            stderr = stderr.decode("utf-8")

            if not ignore_failure and cmd.returncode != 0:
                process_error = "{} failed:\nstdout: \"{}\"\nstderr: \"{}\"".format(command, stdout, stderr)

        except Exception as e:
            process_error = str(e)

        if process_error:
            log.error(process_error)
            raise Exception(process_error)

        return (stdout, stderr)

    def configure_default_kernel(self):
        self.set_stage("Setting up default kernel")
        installed_kernels = os.listdir('/var/lib/qubes/vm-kernels')
        installed_kernels = [distutils.version.LooseVersion(x) for x in installed_kernels]
        default_kernel = str(sorted(installed_kernels)[-1])
        self.run_command([
            '/usr/bin/qubes-prefs', 'default-kernel', default_kernel])

    def configure_dom0(self):
        self.set_stage("Setting up administration VM (dom0)")

        for service in ['rdisc', 'kdump', 'libvirt-guests', 'salt-minion']:
            self.run_command(['systemctl', 'disable', '{}.service'.format(service) ], ignore_failure=True)
            self.run_command(['systemctl', 'stop',    '{}.service'.format(service) ], ignore_failure=True)

    def configure_qubes(self):
        self.set_stage('Executing qubes configuration')

        states = []
        if self.system_vms:
            states.extend(
                ('qvm.sys-net', 'qvm.sys-firewall', 'qvm.default-dispvm'))
        if self.default_vms:
            states.extend(
                ('qvm.personal', 'qvm.work', 'qvm.untrusted', 'qvm.vault'))
        if self.whonix_available and self.whonix_vms:
            states.extend(
                ('qvm.sys-whonix', 'qvm.anon-whonix'))
        if self.whonix_default:
            states.append('qvm.updates-via-whonix')
        if self.usbvm:
            states.append('qvm.sys-usb')
        if self.usbvm_with_netvm:
            states.append('pillar.qvm.sys-net-as-usbvm')

        try:
            # get rid of initial entries (from package installation time)
            os.rename('/var/log/salt/minion', '/var/log/salt/minion.install')
        except OSError:
            pass

        # Refresh minion configuration to make sure all installed formulas are included
        self.run_command(['qubesctl', 'saltutil.clear_cache'])
        self.run_command(['qubesctl', 'saltutil.sync_all'])

        for state in states:
            print("Setting up state: {}".format(state))
            if state.startswith('pillar.'):
                self.run_command(['qubesctl', 'top.enable',
                    state[len('pillar.'):], 'pillar=True'])
            else:
                self.run_command(['qubesctl', 'top.enable', state])

        try:
            self.run_command(['qubesctl', '--all', 'state.highstate'])
            # After successful call disable all the states to not leave them
            # enabled, to not interfere with later user changes (like assigning
            # additional PCI devices)
            for state in states:
                if not state.startswith('pillar.'):
                    self.run_command(['qubesctl', 'top.disable', state])
        except Exception:
            raise Exception(
                    ("Qubes initial configuration failed. Login to the system and " +
                     "check /var/log/salt/minion for details. " +
                     "You can retry configuration by calling " +
                     "'sudo qubesctl state.highstate' in dom0 (you will get " +
                     "detailed state there)."))

    def configure_default_template(self):
        self.set_stage('Setting default template')
        self.run_command(['/usr/bin/qubes-prefs', 'default-template', self.default_template])

    def configure_default_dvm(self):
        self.set_stage("Creating default DisposableVM")

        dispvm_name = self.default_template + '-dvm'
        self.run_command(['/usr/bin/qubes-prefs', 'default-dispvm',
            dispvm_name])

    def configure_network(self):
        self.set_stage('Setting up networking')

        default_netvm = 'sys-firewall'
        updatevm = default_netvm
        if self.whonix_default:
            updatevm = 'sys-whonix'

        self.run_command(['/usr/bin/qvm-prefs', 'sys-firewall', 'netvm', 'sys-net'])
        self.run_command(['/usr/bin/qubes-prefs', 'default-netvm', default_netvm])
        self.run_command(['/usr/bin/qubes-prefs', 'updatevm', updatevm])
        self.run_command(['/usr/bin/qubes-prefs', 'clockvm', 'sys-net'])
        self.run_command(['/usr/bin/qvm-start', default_netvm])

    def configure_template(self, template, path):
        self.set_stage("Configuring TemplateVM {}".format(template))
        self.run_command([
            'qvm-template-postprocess', '--really', 'post-install', template, path])

