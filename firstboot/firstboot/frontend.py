#
# frontend.py
#
# Copyright (C) 2011  Red Hat, Inc.
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
# Red Hat Author(s):  Martin Gracik <mgracik@redhat.com>
#

import logging
import os
import shlex
import signal
import subprocess

from .constants import *

from system_config_keyboard import keyboard


# set up logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger('firstboot.frontend')


class Frontend:

    def __init__(self):
        self.x = None
        self.wm_pid = None

    def set_lang(self):
        try:
            i18n = shlex.split(open(I18N).read())
            i18n = dict(item.split('=') for item in i18n)
            if 'LANG' in i18n:
                log.info('setting LANG to %s', i18n['LANG'])
                os.environ['LANG'] = i18n['LANG']
        except:
            os.environ.setdefault("LANG", "en_US.UTF-8")

    def startx(self):
        def sigusr1_handler(num, frame):
            pass

        def sigchld_handler(num, frame):
            raise OSError

        def preexec_fn():
            signal.signal(signal.SIGUSR1, signal.SIG_IGN)

        old_sigusr1 = signal.signal(signal.SIGUSR1, sigusr1_handler)
        old_sigchld = signal.signal(signal.SIGCHLD, sigchld_handler)

        os.environ['DISPLAY'] = DISPLAY
        cmd = ['Xorg', os.environ['DISPLAY'],
               '-ac', '-nolisten', 'tcp', VT]

        devnull = os.open('/dev/null', os.O_RDWR)

        try:
            log.info('starting the Xorg server')
            self.x = subprocess.Popen(cmd, stdout=devnull, stderr=devnull,
                                      preexec_fn=preexec_fn)

        except OSError as e:
            err = 'Xorg server failed to start: %s' % e
            log.critical(err)
            raise RuntimeError(err)

        signal.pause()
        signal.signal(signal.SIGUSR1, old_sigusr1)
        signal.signal(signal.SIGCHLD, old_sigchld)

        log.info('Xorg server started successfully')

        # XXX no need to close devnull?

    def init_gtk(self):
        rd, wr = os.pipe()
        pid = os.fork()
        if not pid:
            import gtk
            os.write(wr, '#')

            gtk.main()
            os._exit(0)

        os.read(rd, 1)
        os.close(rd)
        os.close(wr)

    def start_wm(self):
        path = os.environ['PATH'].split(':')
        wms = [os.path.join(p, wm) for wm in WMS for p in path]
        available = [wm for wm in wms if os.access(wm, os.X_OK)]
        if not available:
            err = 'no window manager available'
            log.critical(err)
            raise RuntimeError(err)

        wm = available[0]
        cmd = [wm, '--display', os.environ['DISPLAY']]

        self.wm_pid = os.fork()
        if not self.wm_pid:
            log.info('starting the window manager')
            os.execvp(wm, cmd)

        try:
            pid, status = os.waitpid(self.wm_pid, os.WNOHANG)
        except OSError as e:
            err = 'window manager failed to start: %s' % e
            log.critical(err)
            raise RuntimeError(err)

        log.info('window manager started successfully')

    def merge_xres(self):
        if os.access(XRES, os.R_OK):
            log.info('merging the Xresources')
            p = subprocess.Popen(['xrdb', '-merge', XRES])
            p.wait()

    def kill(self):
        if self.wm_pid:
            log.info('killing the window manager')
            os.kill(self.wm_pid, 15)

        if self.x:
            log.info('killing the Xorg server')
            os.kill(self.x.pid, 15)
            self.x.wait()
