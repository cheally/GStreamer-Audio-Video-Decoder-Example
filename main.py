'''
Copyright (c) 2011 Joar Wandborg <http://wandborg.se>
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
---

A response to http://stackoverflow.com/questions/8187257/play-audio-and-video-with-a-pipeline-in-gstreamer-python/8197837
'''

'''
This code is originally created by Joar Wandborg for GStreamer 0.10 and I fitted it for GStreamer 1.0.
Jeff L Gaol - Instagram: @jefflgaol
'''

import sys, os
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject
import logging
import argparse

GObject.threads_init()
Gst.init(None)

logging.basicConfig()

_log = logging.getLogger(__name__)
_log.setLevel(logging.DEBUG)

class VideoPlayer(object):
    source_file = None

    def __init__(self, **kwargs):
        self.loop = GObject.MainLoop()
        if kwargs.get('src'):
            self.source_file = kwargs.get('src')
        self.__setup()

    def run(self):
        self.loop.run()

    def stop(self):
        self.loop.quit()

    def __setup(self):
        self.__setup_pipeline()

    def __setup_pipeline(self):
        self.pipeline = Gst.Pipeline()

        # Source element
        self.filesrc = Gst.ElementFactory.make('filesrc')
        self.filesrc.set_property('location', self.source_file)
        self.pipeline.add(self.filesrc)

        # Demuxer
        self.decoder = Gst.ElementFactory.make('decodebin')
        self.decoder.connect('pad-added', self.__on_decoded_pad)
        self.pipeline.add(self.decoder)

        # Video elements
        self.videoqueue = Gst.ElementFactory.make('queue', 'videoqueue')
        self.pipeline.add(self.videoqueue)

        self.autovideoconvert = Gst.ElementFactory.make('autovideoconvert')
        self.pipeline.add(self.autovideoconvert)

        self.autovideosink = Gst.ElementFactory.make('gtksink')
        self.pipeline.add(self.autovideosink)

        # Audio elements
        self.audioqueue = Gst.ElementFactory.make('queue', 'audioqueue')
        self.pipeline.add(self.audioqueue)

        self.audioconvert = Gst.ElementFactory.make('audioconvert')
        self.pipeline.add(self.audioconvert)

        self.autoaudiosink = Gst.ElementFactory.make('autoaudiosink')
        self.pipeline.add(self.autoaudiosink)

        self.progressreport = Gst.ElementFactory.make('progressreport')
        self.progressreport.set_property('update-freq', 1)
        self.pipeline.add(self.progressreport)

        # Link source and demuxer
        link1 = self.filesrc.link(self.decoder)
        if not link1:
            _log.error('Could not link filesrc & decoder!\n{0}'.format(
                    link1))

        # Link audio elements
        link2 = self.audioqueue.link(self.audioconvert)
        if not link2:
            _log.error('Could not link audioqueue & audioconvert!\n{0}'.format(
                    link2))        
        link3 = self.audioconvert.link(self.autoaudiosink)
        if not link3:
            _log.error('Could not link audioconvert & autoaudiosink!\n{0}'.format(
                    link3))

        # Link video elements
        link4 = self.videoqueue.link(self.progressreport)
        if not link4:
            _log.error('Could not link videoqueue & progressreport!\n{0}'.format(
                    link4))
        link5 = self.progressreport.link(self.autovideoconvert)
        if not link5:
            _log.error('Could not link progressreport & autovideoconvert!\n{0}'.format(
                    link5))
        link6 = self.autovideoconvert.link(self.autovideosink)
        if not link6:
            _log.error('Could not link autovideoconvert & gtksink!\n{0}'.format(
                    link6))

        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message', self.__on_message)

        self.pipeline.set_state(Gst.State.PLAYING)

    def __on_decoded_pad(self, element, pad):
        _log.debug('on_decoded_pad: {0}'.format(pad))
        string = pad.query_caps(None).to_string()
        if string.startswith('audio/'):
            pad.link(self.audioqueue.get_static_pad('sink'))
        else:
            pad.link(self.videoqueue.get_static_pad('sink'))
   
    def __on_message(self, bus, message):
        _log.debug(' - MESSAGE: {0}'.format(message))


def main():
    # Argument parser
    parser = argparse.ArgumentParser(description="GStreamer to display video.")
    parser.add_argument('-i', '--input', help="Path to video file", required=True)
    args = parser.parse_args()

    player = VideoPlayer(src=str(args.input))
    player.run()

if __name__ == '__main__':
    main()
