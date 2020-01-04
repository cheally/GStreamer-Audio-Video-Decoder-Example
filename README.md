# GStreamer-Video-Decoder-Example
This is an example audio-video decoder implementation in GStreamer 1.0 (Python).

I changed the code from http://stackoverflow.com/questions/8187257/play-audio-and-video-with-a-pipeline-in-gstreamer-python/8197837 created by Joan Wandborg that previously implemented in GStreamer in 0.10.

## How To Use
You can use the code like this:
```
python3 main.py
    --input='<path to video file>'
```
For example:
```
python3 main.py
    --input='/home/jefflgaol/Dokumen/GStreamer/video.mp4'
```

## Structure
```
filesrc --> decodebin --> (1) ..
                      --> (2) ..
(1) --> queue --> autovideoconvert --> gtksink (previously is autovideosink)
(2) --> queue --> audioconvert --> autoaudiosink
```
Note: I modified from ```autovideosink``` to ```gtksink``` for better compatibility for most computers.

## Short Explanation
Our input comes from filesrc. Then, the file will be decoded using decodebin. From decodebin, it will demux the filesrc into two streams: video and audio. Then, for both streams we add a buffer. See https://gstreamer.freedesktop.org/documentation/tutorials/basic/multithreading-and-pad-availability.html?gi-language=c for a more clear explanation about buffer. After buffer, the video stream will go to autovideosink, but to have the same capabilities, we added autovideoconvert so capabilities negotiation can be performed. See https://gstreamer.freedesktop.org/documentation/tutorials/basic/media-formats-and-pad-capabilities.html?gi-language=c for a more clear explanation about pad capabilities. The same thing also happens to the music stream.

## Result
![alt text](https://github.com/jefflgaol/GStreamer-Video-Decoder-Example/blob/master/test.gif)
