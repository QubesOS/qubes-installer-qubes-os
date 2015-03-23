#
# qubes.py
#
# Copyright (C) 2011  Invisible Things Lab All rights reserved.
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


from pyanaconda.installclass import BaseInstallClass
from pyanaconda.constants import *
from pyanaconda.product import *
from pyanaconda import network
from pyanaconda.i18n import N_
import os, types

from decimal import Decimal

class InstallClass(BaseInstallClass):
    # name has underscore used for mnemonics, strip if you dont need it
    id = "qubes"
    name = N_("Qubes")
    _description = N_("The default installation of %s is a minimal install. "
                      "You can optionally select a different set of software "
                      "now.")
    _descriptionFields = (productName,)
    sortPriority = 20000
    hidden = 0
    efi_dir = 'qubes'

    _l10n_domain = "anaconda"

    installUpdates = False

    efi_dir = "qubes"

    bootloaderTimeoutDefault = 5

    tasks = [(N_("Minimal"), ["base", "base-x", "kde-desktop-qubes", "qubes" ]) ]

    help_placeholder = "QubesPlaceholder.html"
    help_placeholder_with_links = "QubesPlaceholderWithLinks.html"

    def getPackagePaths(self, uri):
        if not type(uri) == types.ListType:
            uri = [uri,]

        return {'Installation Repo': uri}

    def configure(self, anaconda):
        BaseInstallClass.configure(self, anaconda)

    def setDefaultPartitioning(self, storage):
        BaseInstallClass.setDefaultPartitioning(self,
                                                storage)
        for autoreq in storage.autoPartitionRequests:
            if autoreq.mountpoint == "/":
                autoreq.maxSize=None
                autoreq.requiredSpace=24*1024
            if autoreq.mountpoint == "/home":
                storage.autoPartitionRequests.remove(autoreq)

    def productMatches(self, oldprod):
        if oldprod is None:
            return False

        if oldprod.startswith(productName):
            return True

        return False

    def versionMatches(self, oldver):
        return True

    def __init__(self):
        BaseInstallClass.__init__(self)
