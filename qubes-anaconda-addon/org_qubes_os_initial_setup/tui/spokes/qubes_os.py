#
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

"""Module with the class for the Qubes OS TUI spoke."""

# import gettext
# _ = lambda x: gettext.ldgettext("qubes-os-anaconda-plugin", x)

# will never be translated
_ = lambda x: x
N_ = lambda x: x

from pyanaconda.ui.categories.system import SystemCategory
from pyanaconda.ui.tui.spokes import NormalTUISpoke
from simpleline.render.containers import ListColumnContainer
from simpleline.render.widgets import CheckboxWidget
from simpleline.render.screen import InputState
from pyanaconda.ui.common import FirstbootOnlySpokeMixIn

# export only the HelloWorldSpoke and HelloWorldEditSpoke classes
__all__ = ["QubesOsSpoke"]

class QubesOsSpoke(FirstbootOnlySpokeMixIn, NormalTUISpoke):
    """
    Since this class inherits from the FirstbootOnlySpokeMixIn, it will
    only appear in the Initial Setup (successor of the Firstboot tool).

    :see: pyanaconda.ui.tui.TUISpoke
    :see: pyanaconda.ui.common.FirstbootSpokeMixIn
    :see: pyanaconda.ui.tui.tuiobject.TUIObject
    :see: pyaanconda.ui.tui.simpleline.Widget

    """

    ### class attributes defined by API ###


    # category this spoke belongs to
    category = SystemCategory

    def __init__(self, data, storage, payload, instclass):
        """
        :see: pyanaconda.ui.tui.base.UIScreen
        :see: pyanaconda.ui.tui.base.App
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

        NormalTUISpoke.__init__(self, data, storage, payload, instclass)

        self.initialize_start()

        # title of the spoke
        self.title = N_("Qubes OS")

        self._container = None

        self.qubes_data = self.data.addons.org_qubes_os_initial_setup

        for attr in self.qubes_data.bool_options:
            setattr(self, '_' + attr, getattr(self.qubes_data, attr))

        self.initialize_done()


    def initialize(self):
        """
        The initialize method that is called after the instance is created.
        The difference between __init__ and this method is that this may take
        a long time and thus could be called in a separated thread.

        :see: pyanaconda.ui.common.UIObject.initialize

        """

        NormalTUISpoke.initialize(self)

    def _add_checkbox(self, name, title):
        w = CheckboxWidget(title=title, completed=getattr(self, name))
        self._container.add(w, self._set_checkbox, name)

    def refresh(self, args=None):
        """
        The refresh method that is called every time the spoke is displayed.
        It should update the UI elements according to the contents of
        self.data.

        :see: pyanaconda.ui.common.UIObject.refresh
        :see: pyanaconda.ui.tui.base.UIScreen.refresh
        :param args: optional argument that may be used when the screen is
                     scheduled (passed to App.switch_screen* methods)
        :type args: anything
        :return: whether this screen requests input or not
        :rtype: bool

        """
        super(QubesOsSpoke, self).refresh()
        self._container = ListColumnContainer(1)

        w = CheckboxWidget(title=_('Create default system qubes '
                                   '(sys-net, sys-firewall, default DispVM)'),
                           completed=self._system_vms)
        self._container.add(w, self._set_checkbox, '_system_vms')
        w = CheckboxWidget(title=_('Create default application qubes '
                                   '(personal, work, untrusted, vault)'),
                           completed=self._default_vms)
        self._container.add(w, self._set_checkbox, '_default_vms')
        if self.qubes_data.whonix_available:
            w = CheckboxWidget(
                title=_('Create Whonix Gateway and Workstation qubes '
                        '(sys-whonix, anon-whonix)'),
                completed=self._whonix_vms)
            self._container.add(w, self._set_checkbox, '_whonix_vms')
        if self._whonix_vms:
            w = CheckboxWidget(
                title=_('Enable system and template updates over the Tor anonymity '
                        'network using Whonix'),
                completed=self._whonix_default)
            self._container.add(w, self._set_checkbox, '_whonix_default')
        if self.qubes_data.usbvm_available:
            w = CheckboxWidget(
                title=_('Create USB qube holding all USB controllers (sys-usb)'),
                completed=self._usbvm)
            self._container.add(w, self._set_checkbox, '_usbvm')
        if self._usbvm:
            w = CheckboxWidget(
                title=_('Use sys-net qube for both networking and USB devices'),
                completed=self._usbvm_with_netvm)
            self._container.add(w, self._set_checkbox, '_usbvm_with_netvm')

        self.window.add_with_separator(self._container)

    def _set_checkbox(self, name):
        setattr(self, name, not getattr(self, name))

    def apply(self):
        """
        The apply method that is called when the spoke is left. It should
        update the contents of self.data with values set in the spoke.

        """

        for attr in self.qubes_data.bool_options:
            setattr(self.qubes_data, attr, getattr(self, '_' + attr))

        self.qubes_data.seen = True

    def execute(self):
        """
        The excecute method that is called when the spoke is left. It is
        supposed to do all changes to the runtime environment according to
        the values set in the spoke.

        """

        # nothing to do here
        pass

    @property
    def completed(self):
        """
        The completed property that tells whether all mandatory items on the
        spoke are set, or not. The spoke will be marked on the hub as completed
        or uncompleted acording to the returned value.

        :rtype: bool

        """

        return self.qubes_data.seen

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

    def input(self, args, key):
        """
        The input method that is called by the main loop on user's input.

        :param args: optional argument that may be used when the screen is
                     scheduled (passed to App.switch_screen* methods)
        :type args: anything
        :param key: user's input
        :type key: unicode
        :return: if the input should not be handled here, return it, otherwise
                 return INPUT_PROCESSED or INPUT_DISCARDED if the input was
                 processed succesfully or not respectively
        :rtype: bool|unicode

        """

        if self._container.process_user_input(key):
            self.apply()
            return InputState.PROCESSED_AND_REDRAW

        return super().input(args, key)
