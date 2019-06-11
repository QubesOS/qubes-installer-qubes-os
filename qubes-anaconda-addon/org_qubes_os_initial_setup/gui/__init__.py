"""
We need org_qubes_os_initial_setup/gui to be a package so that relative imports
work.

"""

import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GLib', '2.0')

from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib

import logging
import threading


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

        self.thread = threading.Thread(target=self.run_fun)

    def run_fun(self):
        try:
            self.fun(*self.args)
        except Exception as e:
            self.showErrorMessage(str(e))
        finally:
            self.done()

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

    def showErrorMessage(self, text):
        self.run_in_ui_thread(self.showErrorMessageHelper, text)

    def showErrorMessageHelper(self, text):
        dlg = Gtk.MessageDialog(title="Error", message_type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.OK, text=text)
        dlg.set_position(Gtk.WindowPosition.CENTER)
        dlg.set_modal(True)
        dlg.set_transient_for(self)
        dlg.run()
        dlg.destroy()
