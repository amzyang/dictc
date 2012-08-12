# -*- coding: utf-8 -*-
try:
    import gst
except ImportError:
    print """Python binding for GStreamer is missing!"""
    raise


class Sound():
    def __init__(self):
        self.player = gst.element_factory_make("playbin2", "player")
        fakesink = gst.element_factory_make("fakesink", "fakesink")
        self.player.set_property("video-sink", fakesink)
        bus = self.player.get_bus()
        bus.connect("message", self.on_message)
        bus.add_signal_watch()

    def on_message(self, bus, message):
        t = message.type
        if t == gst.MESSAGE_EOS:
            self.player.set_state(gst.STATE_NULL)
        elif t == gst.MESSAGE_ERROR:
            self.player.set_state(gst.STATE_NULL)

    def do(self, uri):
        self.player.set_state(gst.STATE_NULL)
        self.player.set_property("uri", uri)
        self.player.set_state(gst.STATE_PLAYING)


# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4 textwidth=79
