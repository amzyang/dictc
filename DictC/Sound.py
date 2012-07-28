# -*- coding: utf-8 -*-
import sys
try:
    import gst
except ImportError:
    print """Python bindings for GStreamer is missing! Try install
gstreamer-python first"""
    raise
    # @TODO
    sys.exit(1)


class Sound():
    def __init__(self):
        self.player = gst.element_factory_make("playbin2", "player")
        fakesink = gst.element_factory_make("fakesink", "fakesink")
        self.player.set_property("video-sink", fakesink)
        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)

    def on_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)

    def do(self):
        self.player.set_property("uri", self.path)
        self.player.set_state(gst.STATE_PLAYING)


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 textwidth=79
