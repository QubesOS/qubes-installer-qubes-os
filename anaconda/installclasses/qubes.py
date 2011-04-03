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

from installclass import BaseInstallClass
from constants import *
from product import *
from meh.filer import *
from flags import flags
import os
import types
import iutil

import gettext
_ = lambda x: gettext.ldgettext("anaconda", x)

import installmethod
import yuminstall

import rpmUtils.arch

class InstallClass(BaseInstallClass):
    # name has underscore used for mnemonics, strip if you dont need it
    id = "qubes"
    name = N_("Qubes")
    _description = N_("The default installation of %s is a minimal install. "
                      "You can optionally select a different set of software "
                      "now.")
    _descriptionFields = (productName,)
    sortPriority = 20000
    if not productName.startswith("Red Hat Enterprise"):
        hidden = 1

    bootloaderTimeoutDefault = 5

    tasks = [(N_("Minimal"), ["core", "qubes"]),
             (N_("Desktop"),
              ["backup-client", "base", "compat-libraries", "fonts",
               "core", "qubes", "basic-desktop", "desktop-platform",
               "general-desktop", "graphical-admin-tools", "input-methods",
               "legacy-x", "x11"]),
              ]

    bugFiler = BugzillaFiler("http://qubes-os.org/trac/",
                             "http://qubes-os.org/",
                             product.productVersion, product.productName)

    def getPackagePaths(self, uri):
        if not type(uri) == types.ListType:
            uri = [uri,]

        return {'Installation Repo': uri}

    def configure(self, anaconda):
        BaseInstallClass.configure(self, anaconda)
        BaseInstallClass.setDefaultPartitioning(self,
                                                anaconda.storage,
                                                anaconda.platform)

    def setGroupSelection(self, anaconda):
        BaseInstallClass.setGroupSelection(self, anaconda)
        map(lambda x: anaconda.backend.selectGroup(x), ["core"])

    def setSteps(self, anaconda):
        BaseInstallClass.setSteps(self, anaconda)
        anaconda.dispatch.skipStep("partition")
        anaconda.dispatch.skipStep("language")
        anaconda.dispatch.skipStep("reposetup")
        anaconda.dispatch.skipStep("tasksel")
        anaconda.dispatch.skipStep("basepkgsel")
        anaconda.dispatch.skipStep("group-selection")
        anaconda.dispatch.skipStep("postselection")

    def getBackend(self):
        if flags.livecdInstall:
            import livecd
            return livecd.LiveCDCopyBackend
        else:
            return yuminstall.YumBackend

    def productMatches(self, oldprod):
        return False

    def versionMatches(self, oldver):
        return True

    def __init__(self):
        BaseInstallClass.__init__(self)
