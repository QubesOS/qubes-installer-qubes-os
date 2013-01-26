#
# pwcheck.py
#
# Copyright (C) 2010  Red Hat, Inc.
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

import re
import pwquality

import pygtk
pygtk.require("2.0")
import gtk

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pwcheck")

import gettext
_ = lambda x: gettext.ldgettext("firstboot", x)


def clamp(value, lowerbound, upperbound):
    return min(max(value, lowerbound), upperbound)


class Password(object):

    MIN_STRENGTH = 0
    MAX_STRENGTH = 100

    STRENGTH_STRINGS = [ _("Very weak"),
                         _("Weak"),
                         _("Fairly strong"),
                         _("Strong"),
                         _("Very strong") ]

    def __init__(self, password, username=None):
        self.password = password
        self.username = username
        self.pwq_settings = pwquality.PWQSettings()
        self.pwq_settings.read_config()

        self.strength = self.MIN_STRENGTH
        self.pwq_msg = ''
        try:
            self.strength = self.pwq_settings.check(self.password, None, self.username)
        except pwquality.PWQError as (e, msg):
            self.pwq_msg = msg

        self.strength = clamp(self.strength, self.MIN_STRENGTH, self.MAX_STRENGTH)

    @property
    def strength_frac(self):
        return float(self.strength) / self.MAX_STRENGTH

    @property
    def strength_string(self):
        strings_count = len(self.STRENGTH_STRINGS)
        index = int(self.strength / (self.MAX_STRENGTH / strings_count))

        try:
            return self.STRENGTH_STRINGS[index]
        except IndexError:
            return self.STRENGTH_STRINGS[-1]

    def __str__(self):
        return "%s" % self.password


class StrengthMeter(gtk.DrawingArea):

    COLORS = [(213.0/255.0, 4.0/255.0, 4.0/255.0),
              (234.0/255.0, 236.0/255.0, 31.0/255.0),
              (141.0/255.0, 133.0/255.0, 241.0/255.0),
              (99.0/255.0, 251.0/255.0, 107.0/255.0)]

    def __init__(self):
        super(StrengthMeter, self).__init__()
        self.connect("expose_event", self.expose)

        self._fraction = 0.0

    def curved_rectangle(self, context, x0, y0, width, height, radius):
        if not width or not height:
            return

        x1 = x0 + width
        y1 = y0 + height

        if width / 2 < radius:
            if height / 2 < radius:
                context.move_to (x0, (y0 + y1) / 2)
                context.curve_to(x0 ,y0, x0, y0, (x0 + x1) / 2, y0)
                context.curve_to(x1, y0, x1, y0, x1, (y0 + y1) / 2)
                context.curve_to(x1, y1, x1, y1, (x1 + x0) / 2, y1)
                context.curve_to(x0, y1, x0, y1, x0, (y0 + y1) / 2)
            else:
                context.move_to (x0, y0 + radius)
                context.curve_to(x0, y0, x0, y0, (x0 + x1) / 2, y0)
                context.curve_to(x1, y0, x1, y0, x1, y0 + radius)
                context.line_to (x1, y1 - radius)
                context.curve_to(x1, y1, x1, y1, (x1 + x0) / 2, y1)
                context.curve_to(x0, y1, x0, y1, x0, y1 - radius)
        else:
            if height / 2 < radius:
                context.move_to (x0, (y0 + y1) / 2)
                context.curve_to(x0, y0, x0 , y0, x0 + radius, y0)
                context.line_to (x1 - radius, y0)
                context.curve_to(x1, y0, x1, y0, x1, (y0 + y1) / 2)
                context.curve_to(x1, y1, x1, y1, x1 - radius, y1)
                context.line_to (x0 + radius, y1)
                context.curve_to(x0, y1, x0, y1, x0, (y0 + y1) / 2)
            else:
                context.move_to (x0, y0 + radius)
                context.curve_to(x0 , y0, x0 , y0, x0 + radius, y0)
                context.line_to (x1 - radius, y0)
                context.curve_to(x1, y0, x1, y0, x1, y0 + radius)
                context.line_to (x1, y1 - radius)
                context.curve_to(x1, y1, x1, y1, x1 - radius, y1)
                context.line_to (x0 + radius, y1)
                context.curve_to(x0, y1, x0, y1, x0, y1 - radius)

        context.close_path()

    def expose(self, widget, event):
        # Create the cairo context
        context = widget.window.cairo_create()

        # Restrict cairo to the exposed area
        context.rectangle(event.area.x, event.area.y,
                          event.area.width, event.area.height)
        context.clip()

        # Draw the widget
        self.draw(context)

        return False

    def draw(self, context):
        alloc = self.get_allocation()
        context.translate(-alloc.x, -alloc.y)

        context.save()
        context.set_source_rgb(0.0, 0.0, 0.0)
        context.set_line_width(1)
        self.curved_rectangle(context, alloc.x + 0.5, alloc.y + 0.5,
                              alloc.width - 1, alloc.height - 1,
                              4)
        context.stroke()
        context.restore()

        context.save()
        r, g, b = self.get_color()
        context.set_source_rgb(r, g, b)
        context.rectangle(alloc.x + 1, alloc.y + 1,
                          self.fraction * (alloc.width - 2), alloc.height - 2)
        context.fill_preserve()
        context.restore()

    def redraw(self):
        if self.window:
            alloc = self.get_allocation()

            rect = gtk.gdk.Rectangle(0, 0, alloc.width, alloc.height)
            self.window.invalidate_rect(rect, True)

            self.queue_draw_area(alloc.x, alloc.y, alloc.width, alloc.height)
            self.window.process_updates(True)

    @property
    def fraction(self):
        return self._fraction

    @fraction.setter
    def fraction(self, fraction):
        self._fraction = fraction
        self.redraw()

    def get_color(self):
        if self.fraction < 0.5:
            return self.COLORS[0]
        elif self.fraction < 0.75:
            return self.COLORS[1]
        elif self.fraction < 0.90:
            return self.COLORS[2]
        else:
            return self.COLORS[3]


class StrengthMeterWithLabel(gtk.HBox):

    def __init__(self):
        super(StrengthMeterWithLabel, self).__init__()

        self.meter = StrengthMeter()
        self.meter.set_size_request(120, 8)
        self.alignment = gtk.Alignment(0.0, 0.5)
        self.alignment.add(self.meter)

        self.label = gtk.Label()
        self.label.set_alignment(0.0, 0.5)

        self.pack_start(self.alignment, expand=False)
        self.pack_start(self.label)
        self.set_spacing(10)

    def set_fraction(self, fraction):
        self.meter.fraction = fraction

    def set_text(self, text):
        self.label.set_text(text)
