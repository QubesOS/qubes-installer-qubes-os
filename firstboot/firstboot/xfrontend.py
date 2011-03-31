#
# Chris Lumens <clumens@redhat.com>
#
# Copyright 2007, 2008 Red Hat, Inc.
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
import logging
import os, string, subprocess, sys, signal

##
## I18N
##
import gettext
_ = lambda x: gettext.ldgettext("firstboot", x)

class XFrontEnd:
    def __init__(self):
        self._wm_pid = None
        self.x = None

    def _mergeXresources(self):
        path = "/etc/X11/Xresources"
        if os.access(path, os.R_OK):
            os.system("xrdb -merge %s" % path)

    # Attempt to start up the window manager.  Check the value of self.wm_pid
    # afterwards to see if this succeeded.
    def _startWindowManager(self):
        self._wm_pid = os.fork()

        if not self._wm_pid:
            path = "/usr/bin/metacity"
            args = [path, "--display", os.environ["DISPLAY"]]
            os.execvp(path, args)

        status = 0
        try:
            (pid, status) = os.waitpid (self._wm_pid, os.WNOHANG)
        except OSError, (errno, msg):
            logging.error ("starting window manager failed: %s" % msg)

        if status:
            raise RuntimeError, "Window manager failed to start."

    # Initializes the UI for firstboot by starting up an X server and
    # window manager, but returns control to the caller to proceed.
    def start(self):
        os.environ["DISPLAY"] = ":9"

        try:
            args = [":9", "-ac", "-nolisten", "tcp", "vt6", "-br"]
            noOutput = os.open("/dev/null", os.O_RDWR)

	    def sigchld_handler(num, frame):
		raise OSError

	    def sigusr1_handler(num, frame):
		pass

	    def preexec_fn():
		signal.signal(signal.SIGUSR1, signal.SIG_IGN)

	    old_sigusr1 = signal.signal(signal.SIGUSR1, sigusr1_handler)
	    old_sigchld = signal.signal(signal.SIGCHLD, sigchld_handler)
            self.x = subprocess.Popen(["/usr/bin/Xorg"] + args,
                                      stdout=noOutput, stderr=noOutput,
				      preexec_fn=preexec_fn)
	    signal.pause()
	    signal.signal(signal.SIGUSR1, old_sigusr1)
	    signal.signal(signal.SIGCHLD, old_sigchld)

        except OSError:
            logging.error("X server failed to start")
            raise RuntimeError, "X server failed to start"
        except:
            import traceback
            (ty, value, tb) = sys.exc_info()
            lst = traceback.format_exception (ty, value, tb)
            text = string.joinfields (lst, "")
            print text

            logging.error("X server failed to start")
            raise RuntimeError, "X server failed to start"

        logging.info("X server started successfully.")

        # Init GTK to connect to the X server, then write a token on a pipe to
        # tell our parent process that we're ready to start metacity.
        (rd, wr) = os.pipe()
        pid = os.fork()
        if not pid:
            import gtk
            os.write(wr, "#")

            # Set up the keyboard.
            import system_config_keyboard.keyboard as keyboard
            kbd = keyboard.Keyboard()
            kbd.read()
            kbd.activate()

            # Block until the X server is killed.
            gtk.main()
            os._exit(0)

        # Block on read of token
        os.read(rd, 1)
        os.close(rd)
        os.close(wr)

        self._wm_pid = self._startWindowManager()
        self._mergeXresources()

    def stop(self):
        if self._wm_pid:
            os.kill(self._wm_pid, 15)

        if self.x:
            os.kill(self.x.pid, 15)
            self.x.wait()
