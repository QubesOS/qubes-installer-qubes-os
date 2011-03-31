import gtk
import os

def loadPixbuf(fn):
    return gtk.gdk.pixbuf_new_from_file(fn)

def loadToImage(fn):
    pix = loadPixbuf(fn)

    pixWidget = gtk.Image()
    pixWidget.set_from_pixbuf(pix)
    return pixWidget

def start_process(path, args = None):
    if args == None:
        args = [path]
    else:
        args = [path, args]

    child = os.fork()

    if not child:
        os.execvp(path, args)
        os._exit(1)

    return child
