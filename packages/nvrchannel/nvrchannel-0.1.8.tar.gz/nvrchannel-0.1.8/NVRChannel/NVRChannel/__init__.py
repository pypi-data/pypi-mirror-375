from __future__ import annotations
import os
import time
import threading
import logging
import weakref
import traceback
import shutil
import re
import io
import socket
import random
from typing import Optional
from datetime import datetime
from datetime import timezone
from zeroconf import ServiceBrowser, ServiceStateChange
import numpy as np
import iot_devices.device as devices
from scullery import workers
from icemedia import iceflow
import cv2
import PIL.Image
import PIL.ImageOps
import PIL.ImageFilter
from NVRChannel.onvif import ONVIFCamera


logger = logging.Logger("plugins.nvr")


path = os.path.dirname(os.path.abspath(__file__))


def get_rtsp_from_onvif(c: ONVIFCamera):
    "Choose a URI to read from the discovered camera"
    c.create_devicemgmt_service()
    c.create_media_service()

    selection = None
    cw = 0
    for p in c.media.GetProfiles():
        # We want to find a profile that has H264/AAC
        if "VideoEncoderConfiguration" not in p:
            continue
        if "Encoding" not in p["VideoEncoderConfiguration"]:
            continue

        if not p["VideoEncoderConfiguration"]["Encoding"] == "H264":
            continue

        if "AudioEncoderConfiguration" in p:
            if not p["AudioEncoderConfiguration"]["Encoding"] == "AAC":
                continue

        # We want the best available quality so we are going to look for the widest.
        if "Resolution" in p["VideoEncoderConfiguration"]:
            if p["VideoEncoderConfiguration"]["Resolution"]["Width"] < cw:
                continue

            cw = p["VideoEncoderConfiguration"]["Resolution"]["Width"]
        selection = p

    if not selection:
        raise RuntimeError("Could not select profile from discovered camera")

    # Only do the net request after we know what we want to connect with.
    resp = c.media.GetStreamUri(
        {
            "StreamSetup": {"Stream": "RTP-Unicast", "Transport": {"Protocol": "RTSP"}},
            "ProfileToken": selection.token,
        }
    )

    return resp.Uri


# Model source: https://github.com/chuanqi305/MobileNet-SSD/

# MIT License

# Copyright (c) 2018 chuanqi305

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.




net = None

def getCaffeModel(device: NVRChannel):
    global net

    try:
        device.print("Loading MobileNet-SSD model")
        import huggingface_hub

        cm = huggingface_hub.hf_hub_download(
            repo_id="Imran606/cds", filename="MobileNetSSD_deploy.caffemodel",
                repo_type="space"
        )
        prototext = huggingface_hub.hf_hub_download(
            repo_id="Imran606/cds", filename="MobileNetSSD_deploy.prototxt",
            repo_type="space"
        )

        net = cv2.dnn.readNetFromCaffe(prototext, cm)
    except Exception:
        device.handle_exception()

    device.print("Loaded MobileNet-SSD model")



# Only one of these should happpen at a time. Because we need to limit how much CPU it can burn.
object_detection_lock = threading.RLock()

# Labels of Network.
classNames = {
    0: "background",
    1: "aeroplane",
    2: "bicycle",
    3: "bird",
    4: "boat",
    5: "bottle",
    6: "bus",
    7: "car",
    8: "cat",
    9: "chair",
    10: "cow",
    11: "diningtable",
    12: "dog",
    13: "horse",
    14: "motorbike",
    15: "person",
    16: "pottedplant",
    17: "sheep",
    18: "sofa",
    19: "train",
    20: "tvmonitor",
}


def toImgOpenCV(imgPIL):  # Conver imgPIL to imgOpenCV
    i = np.array(imgPIL)  # After mapping from PIL to np : [R,G,B,A]
    # np Image Channel system: [B,G,R,A]
    red = i[:, :, 0].copy()
    i[:, :, 0] = i[:, :, 2].copy()
    i[:, :, 2] = red
    return i


def letterbox_image(image, size):
    """resize image with unchanged aspect ratio using padding"""
    iw, ih = image.shape[0:2][::-1]
    w, h = size
    scale = min(w / iw, h / ih)
    nw = int(iw * scale)
    nh = int(ih * scale)
    image = cv2.resize(image, (nw, nh), interpolation=cv2.INTER_CUBIC)
    new_image = np.zeros((size[1], size[0], 3), np.uint8)
    new_image.fill(0)
    dx = (w - nw) // 2
    dy = (h - nh) // 2
    new_image[dy : dy + nh, dx : dx + nw, :] = image
    return new_image


def recognize_objects(img: bytes | bytearray):
    global net
    if not net:
        return {
            "objects": [],
            "x_inferencetime": 0,
            "x_imagesize": [0,0],
            "x_net_not_loaded": True
        }


    invoke_time = time.time()

    pil_img = PIL.Image.open(io.BytesIO(img))
    filtered = PIL.ImageOps.autocontrast(pil_img, cutoff=5)
    frame = toImgOpenCV(filtered)

    frame_resized = letterbox_image(frame, (300, 300))
    frame_resized = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)

    blob = cv2.dnn.blobFromImage(
        frame_resized, 0.007843, (300, 300), (127.5, 127.5, 127.5), False
    )
    net.setInput(blob)
    detections = net.forward()

    cols = frame.shape[1]
    rows = frame.shape[0]
    t = time.time() - invoke_time
    retval = []

    # For get the class and location of object detected,
    # There is a fix index for class, location and confidence
    # value in @detections array .
    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]  # Confidence of prediction
        if confidence > 0.1:  # Filter prediction
            class_id = int(detections[0, 0, i, 1])  # Class label

            # Object location
            xLeftBottom = int(detections[0, 0, i, 3] * cols)
            yLeftBottom = int(detections[0, 0, i, 4] * rows)
            xRightTop = int(detections[0, 0, i, 5] * cols)
            yRightTop = int(detections[0, 0, i, 6] * rows)

            # Factor for scale to original size of frame
            heightFactor = frame.shape[0] / 300.0
            widthFactor = frame.shape[1] / 300.0
            # Scale object detection to frame
            xLeftBottom = int(widthFactor * xLeftBottom)
            yLeftBottom = int(heightFactor * yLeftBottom)
            xRightTop = int(widthFactor * xRightTop)
            yRightTop = int(heightFactor * yRightTop)

            x = min(xRightTop, xLeftBottom)
            w = max(xRightTop, xLeftBottom) - x
            y = min(yRightTop, yLeftBottom)
            h = max(yRightTop, yLeftBottom) - y

            v = {
                "x": float(x),
                "y": float(y),
                "w": float(w),
                "h": float(h),
                "class": classNames[class_id],
                "confidence": float(confidence),
            }

            if xRightTop > (frame.shape[0] - 20) and confidence < 0.7:
                continue
            if yLeftBottom > (frame.shape[1] - 10) and confidence < 0.7:
                continue
            # For some reason I am consistently getting false positive people detections
            #  with y values in the -6 to 15 range
            # Could just be my input data.  But, things are usually not that high up unless
            #  they are big and big means a clear view which means
            # you probably would have a higher confidence
            if (x > 1 and y > 24) or confidence > 0.33:
                # If something takes up a very large amount of the frame, we probably have a clear view of it.
                # If we are still not confident the ANN
                # Is probably making stuff up.  Very large things are going to be uncommon since most cameras like
                # this aren't doing extreme close ups
                # and the ones that are probably have good lighting
                if ((w < frame.shape[0] / 4) or (confidence > 0.7)) and (
                    (h < (frame.shape[1] / 3)) or (confidence > 0.7)
                ):
                    if (w < (frame.shape[0] / 2.5) or (confidence > 0.5)) and (
                        h < (frame.shape[1] / 1.8) or (confidence > 0.5)
                    ):
                        # If the width of this object is such that more than 2/3d is off of the frame, we had better be very confident
                        # because that seems to be a common pattern of false positives.
                        if ((frame.shape[0] - x) > w / 3) or confidence > 0.4:
                            retval.append(v)
                        else:
                            pass  # print(v, "reject large offscreen")
                    else:
                        pass  # print(v, "reject to large for confidence 2")
                else:
                    pass  # print(v, "reject too large for confidence")
            else:
                pass  # print(v,"reject low xy")

    return {
        "objects": retval,
        "x_inferencetime": t,
        "x_imagesize": [frame.shape[0], frame.shape[1]],
    }


automated_record_uuid = "76241b9c-5b08-4828-9358-37c6a25dd823"


# very much not thread safe, doesn't matter, it's only for one UI page
httpservices = []
httplock = threading.Lock()


onvifCams = {}


def fixAddr(a):
    return a.split(".")[0] + ".local"


def on_service_state_change(zeroconf, service_type, name, state_change):
    with httplock:
        info = zeroconf.get_service_info(service_type, name)
        if not info:
            return
        if state_change is ServiceStateChange.Added:
            httpservices.append(
                (
                    tuple(sorted([socket.inet_ntoa(i) for i in info.addresses])),
                    service_type,
                    name,
                    info.port,
                )
            )
            if len(httpservices) > 2048:
                httpservices.pop(0)

            try:
                if name.startswith("AMC"):
                    # No username/pw yet, we cannot actually fill this in.
                    onvifCams[fixAddr(name)] = None
            except Exception:
                pass
        elif state_change is ServiceStateChange.Removed:
            try:
                httpservices.remove(
                    (
                        tuple(sorted([socket.inet_ntoa(i) for i in info.addresses])),
                        service_type,
                        name,
                        info.port,
                    )
                )

                if name.startswith("AMC"):
                    del onvifCams[fixAddr(name)]
            except Exception:
                logging.exception("???")


# Not common enough to waste CPU all the time on
# browser = ServiceBrowser(util.zeroconf, "_https._tcp.local.", handlers=[ on_service_state_change])
try:
    from kaithem.src.util import zeroconf as zcinstance
except Exception:
    import zeroconf

    zcinstance = zeroconf.Zeroconf()

browser2 = ServiceBrowser(
    zcinstance, "_http._tcp.local.", handlers=[on_service_state_change]
)


class Pipeline(iceflow.GstreamerPipeline):
    def on_motion_begin(self, *a, **k):
        self.mcb(True)

    def on_motion_end(self, *a, **k):
        self.mcb(False)

    def on_presence_value(self, v):
        self.presenceval(v)

    def on_video_analyze(self, *a, **k):
        self.acb(*a)

    def on_barcode(self, *a, **k):
        self.bcb(*a, **k)

    def on_appsink_data(self, *a, **k):
        self.dev.on_appsink_data(*a, **k)

    def getGstreamerSourceData(self, s, cfg, un, pw, doJackAudio=False):
        self.config = cfg
        self.h264source = self.mp3src = False
        self.syncFile = False

        # The source is an HLS stream
        if s.endswith(".m3u8") and s.startswith("http"):
            self.add_element("souphttpsrc", location=s)
            self.add_element("hlsdemux")
            self.add_element("tsdemux")
            self.add_element("parsebin")
            self.h264source = self.add_element("tee")

        elif s.startswith("file://"):
            if s.endswith(".jpg"):
                self.add_element(
                    "multifilesrc",
                    location=s.split("://")[-1],
                    loop=True,
                    caps="image/jpeg,framerate="
                    + (self.config.get("device.fps", "1") or "1")
                    + "/1",
                    do_timestamp=True,
                )
                self.add_element("jpegdec")
                self.add_element("videoconvert")
                self.add_element("videorate")
                self.add_element("queue", max_size_time=10000000)
                self.add_element(
                    "x264enc",
                    tune="zerolatency",
                    rc_lookahead=0,
                    bitrate=int(self.dev.config["device.bitrate"]),
                    key_int_max=int((self.config.get("device.fps", "4") or "4")) * 2,
                )
                self.add_element("capsfilter", caps="video/x-h264, profile=main")
                self.add_element("h264parse")
                self.add_element("queue")

                self.h264source = self.add_element("tee")

            else:
                if not os.path.exists(s[len("file://") :]):
                    raise RuntimeError("Bad file: " + s)
                self.add_element(
                    "multifilesrc", location=s[len("file://") :], loop=True
                )
                if s.endswith(".mkv"):
                    dm = self.add_element("matroskademux")
                else:
                    dm = self.add_element("qtdemux")
                self.add_element("h264parse", connect_when_available="video/x-h264")
                # self.add_element('identity', sync=True)
                self.syncFile = True
                self.add_element("queue", max_size_time=10000000)

                self.h264source = self.add_element("tee")
                self.add_element(
                    "decodebin3", connectToOutput=dm, connect_when_available="audio"
                )
                self.add_element("audioconvert", connect_when_available="audio")

                self.add_element("audiorate")
                self.add_element("queue", max_size_time=10000000)
                self.add_element("voaacenc")
                self.add_element("aacparse")

                self.mp3src = self.add_element("queue", max_size_time=10000000)

        # Make a video test src just for this purpose
        elif not s:
            self.add_element("videotestsrc", is_live=True)
            self.add_element("videorate")
            self.add_element(
                "capsfilter",
                caps="video/x-raw,framerate="
                + (self.config.get("device.fps", "4") or "4")
                + "/1",
            )
            self.add_element(
                "capsfilter", caps="video/x-raw, format=I420, width=320, height=240"
            )

            self.add_element("videoconvert")
            self.add_element(
                "x264enc", tune="zerolatency", byte_stream=True, rc_lookahead=0
            )
            self.add_element("h264parse")
            self.h264source = self.add_element("tee")

        # Make a video test src just for this purpose
        elif s == "test":
            self.add_element("videotestsrc", is_live=True)
            self.add_element(
                "capsfilter",
                caps="video/x-raw,framerate="
                + (self.config.get("device.fps", "4") or "4")
                + "/1",
            )

            self.add_element(
                "capsfilter", caps="video/x-raw, format=I420, width=320, height=240"
            )
            self.add_element("videoconvert")
            self.add_element(
                "x264enc",
                tune="zerolatency",
                key_int_max=int((self.config.get("device.fps", "4") or "4")) * 2,
            )
            self.add_element("h264parse")
            self.h264source = self.add_element("tee")

        elif s in ("webcam", "webcam_pipewire", "webcam_audio"):
            self.add_element("v4l2src")
            self.add_element("videorate", drop_only=True)
            self.add_element(
                "capsfilter",
                caps="video/x-raw,framerate="
                + (self.config.get("device.fps", "4") or "4")
                + "/1",
            )
            self.add_element("videoconvert")
            self.add_element("queue", max_size_time=10000000)
            self.add_element(
                "x264enc",
                tune="zerolatency",
                rc_lookahead=0,
                bitrate=int(self.dev.config["device.bitrate"]),
                key_int_max=int((self.config.get("device.fps", "4") or "4")) * 2,
            )
            self.add_element("capsfilter", caps="video/x-h264, profile=main")
            self.add_element("h264parse", config_interval=1)
            self.h264source = self.add_element("tee")

            if s == "webcam_pipewire":
                self.add_element("pipewiresrc", connectToOutput=False)
            if s == "webcam_audio":
                self.add_element("autoaudiosrc", connectToOutput=False)
            else:
                self.add_element("audiotestsrc", wave=4)
            self.add_element("queue")
            self.add_element("audioconvert")

            self.add_element("voaacenc")
            self.add_element("aacparse")

            self.mp3src = self.add_element("queue", max_size_time=10000000)

        elif s.startswith("rtsp://") or self.dev.onvif:
            if self.dev.onvif:
                s = get_rtsp_from_onvif(self.dev.onvif)
                self.dev.metadata["device.discovered_rtsp_url"] = s

            rtsp = self.add_element(
                "rtspsrc",
                location=s,
                latency=100,
                async_handling=True,
                user_id=un or None,
                user_pw=pw or None,
            )
            self.add_element("rtph264depay", connect_when_available="video")

            self.add_element("h264parse", config_interval=1)
            self.add_element(
                "capsfilter", caps="video/x-h264,stream-format=byte-stream"
            )
            self.h264source = self.add_element("tee")

            self.add_element(
                "decodebin",
                connectToOutput=rtsp,
                connect_when_available="audio",
                async_handling=True,
            )

            if doJackAudio:
                rawaudiotee = self.add_element("tee", connect_when_available="audio")

            self.add_element("audioconvert")
            self.add_element("audiorate")
            self.add_element("voaacenc")
            self.add_element("aacparse")

            self.mp3src = self.add_element("queue", max_size_time=10000000)

            if doJackAudio:
                self.add_element(
                    "queue",
                    max_size_time=100_000_000,
                    leaky=2,
                    connect_when_available="audio",
                    connectToOutput=rawaudiotee,
                )
                self.sink = self.add_element(
                    "jackaudiosink",
                    buffer_time=10,
                    latency_time=10,
                    sync=False,
                    provide_clock=False,
                    slave_method=0,
                    port_pattern="ghjkcsrc",
                    client_name=self.dev.name + "_out",
                    connect=0,
                    blocksize=512,
                )

        elif s.startswith("srt://"):
            rtsp = self.add_element("srtsrc", mode=1, uri=s, passphrase=pw or "")

            demux = self.add_element("tsdemux")
            self.add_element(
                "h264parse", config_interval=2, connect_when_available="video"
            )
            self.add_element(
                "capsfilter", caps="video/x-h264,stream-format=byte-stream"
            )
            self.add_element("queue", max_size_time=100_000_000, leaky=2)

            self.h264source = self.add_element("tee")

            self.add_element(
                "aacparse", connectToOutput=demux, connect_when_available="audio"
            )
            self.mp3src = self.add_element("queue", max_size_time=100_000_000, leaky=2)

        elif s == "screen":
            self.add_element("ximagesrc")
            self.add_element(
                "capsfilter",
                caps="video/x-raw,framerate="
                + (self.config.get("device.fps", "4") or "4")
                + "/1",
            )
            self.add_element("videoconvert")
            self.add_element("queue", max_size_time=10000000)
            self.add_element(
                "x264enc",
                tune="zerolatency",
                rc_lookahead=0,
                bitrate=int(self.dev.config["device.bitrate"]),
                key_int_max=int((self.config.get("device.fps", "4") or "4")) * 2,
            )
            self.add_element("capsfilter", caps="video/x-h264, profile=main")
            self.add_element("h264parse")
            self.add_element(
                "capsfilter", caps="video/x-h264,stream-format=byte-stream"
            )
            self.h264source = self.add_element("tee")

        return s


class NVRChannelRegion(devices.Device):
    """
    Subdevice used to configure one sub-region of motion detection
    """

    device_type = "NVRChannelRegion"

    def __init__(self, name, data, **kw):
        devices.Device.__init__(self, name, data, **kw)


        self.numeric_data_point(
            "motion_detected", min=0, max=1, subtype="bool", writable=False
        )

        self.numeric_data_point("raw_motion_value", min=0, max=10, writable=False)

        self.object_data_point("contained_objects", writable=False)

        # self.object_data_point("overlapping_objects",
        #                             writable=False)

        self.set_config_default("device.motion_threshold", "0.08")

    def processImage(self, img):
        pass

    def onMotionValue(self, v):
        self.set_data_point("raw_motion_value", v)
        self.motion(v > float(self.config.get("device.motion_threshold", 0.08)))

    def isRectangleContained(self, d, overallsize):
        x = d["x"] / overallsize[0]
        y = d["y"] / overallsize[1]
        w = d["w"] / overallsize[0]
        h = d["h"] / overallsize[1]

        # Opper right corner in rectangle
        if self.x <= x <= self.x + self.width:
            if self.y <= y <= self.y + self.height:
                # Lower right corner
                if self.x <= x + w <= self.x + self.width:
                    if self.y <= y + h <= self.y + self.height:
                        return True

    def isRectangleOverlapping(self, d):
        R1 = [d["x"], d["y"], d["x"] + d["width"], d["y"] + d["width"]]
        R2 = [self.x, self.y, self.x + self.width, self.y + self.width]

        if (R1[0] >= R2[2]) or (R1[2] <= R2[0]) or (R1[3] <= R2[1]) or (R1[1] >= R2[3]):
            return False
        return True

    def onObjects(self, o):
        # Filter by the objects that are contained within the rectangle
        op = {"objects": []}
        # oop = {'objects': []}

        for i in o["objects"]:
            if "x" in i:
                if self.isRectangleContained(i, o["x_imagesize"]):
                    op["objects"].append(i)
        self.set_data_point("contained_objects", op)

        # for i in o['objects']:
        #     if 'x' in i:
        #         if self.isRectangleOverlapping(i):
        #             oop['objects'].append(i)

        # self.set_data_point('overlapping_objects', oop)

    def motion(self, v):
        self.set_data_point("motion_detected", v)


class NVRChannel(devices.Device):
    device_type = "NVRChannel"
    readme = os.path.join(os.path.dirname(__file__), "README.md")

    def putTrashInBuffer(self):
        "Force a wake up of a thread sitting around waiting for the pipe"
        if os.path.exists(self.rawFeedPipe):
            import select

            try:
                f = os.open(self.rawFeedPipe, flags=os.O_NONBLOCK | os.O_APPEND)
                s = 0
                for i in range(188):
                    r, w, x = select.select([], [f], [], 0.2)
                    if w:
                        f.write(b"b" * 42)
                    else:
                        s += 1
                        if s > 15:
                            return

            except Exception:
                print(traceback.format_exc())

    def thread(self):
        # Has to be at top othherwise other threads wait and get same val.... and we have multiple...
        initialValue = self.runWidgetThread
        self.threadStarted = True
        self.threadExited = False

        b = b""
        while not os.path.exists(self.rawFeedPipe):
            time.sleep(1)

        f = open(self.rawFeedPipe, "rb")
        lp = time.time()

        while self.runWidgetThread and (self.runWidgetThread == initialValue):
            try:
                x = f.read(188 * 32)
                if x is None:
                    return
                b += x
            except OSError:
                time.sleep(0.2)
            except TypeError:
                time.sleep(1)
                try:
                    f = open(self.rawFeedPipe, "rb")
                except Exception:
                    print(traceback.format_exc())

            except Exception:
                time.sleep(0.5)
                print(traceback.format_exc())

            if self.runWidgetThread:
                if len(b) > (188 * 256) or (lp < (time.time() - 0.2) and b):
                    if self.runWidgetThread and (self.runWidgetThread == initialValue):
                        lp = time.time()
                        self.push_bytes("raw_feed", b)
                        self.lastPushedWSData = time.time()
                    b = b""
        self.threadExited = True

    def checkThread(self):
        # Has to be at top othherwise other threads wait and get same val.... and we have multiple...
        initialValue = self.runCheckThread

        while self.runCheckThread and (self.runCheckThread == initialValue):
            try:
                self.check()
            except Exception:
                self.handle_exception()
            time.sleep(3)

    def close(self):
        self.closed = True
        try:
            if self.process:
                self.process.stop()
        except Exception:
            print(traceback.format_exc())
        self.runCheckThread = False
        self.runWidgetThread = False
        try:
            self.putTrashInBuffer()
        except Exception:
            print(traceback.format_exc())

        try:
            if os.path.exists(self.rawFeedPipe):
                os.remove(self.rawFeedPipe)
        except Exception:
            print(traceback.format_exc())

        s = 10
        while s:
            s -= 1
            if self.threadExited:
                break
            time.sleep(0.1)

        devices.Device.close(self)

        try:
            shutil.rmtree("/dev/shm/knvr_buffer/" + self.name)
        except Exception:
            pass

    def __del__(self):
        self.close()

    def onRawTSData(self, data):
        pass

    def getSnapshot(self):
        if hasattr(self, "snapshotter"):
            with open("/dev/shm/knvr_buffer/" + self.name + ".bmp", "w") as f:
                os.chmod("/dev/shm/knvr_buffer/" + self.name + ".bmp", 0o700)
            if self.datapoints["running"]:
                try:
                    # Use a temp file to make it an atomic operation
                    fn = "/dev/shm/knvr_buffer/" + self.name + ".bmp"
                    tmpfn = (
                        "/dev/shm/knvr_buffer/" + self.name + str(time.time()) + ".bmp"
                    )

                    x = self.snapshotter.pull_to_file(tmpfn)

                    st = time.monotonic()
                    while not os.path.exists(tmpfn):
                        time.sleep(0.01)
                        if time.monotonic() - st > 0.2:
                            break

                    shutil.move(tmpfn, fn)

                except Exception:
                    self.set_data_point("running", 0)
                    if self.process:
                        try:
                            self.process.stop()
                        except Exception:
                            print(traceback.format_exc())
                    raise

                if x:
                    with open("/dev/shm/knvr_buffer/" + self.name + ".bmp", "rb") as f:
                        x = f.read()
                    os.remove("/dev/shm/knvr_buffer/" + self.name + ".bmp")

                return x

    def connect(self, config):
        if self.closed:
            return
        # Close the old thread
        self.runWidgetThread = time.time()

        self.config = config
        if time.time() - self.lastStart < 15:
            return

        # When we reconnect we stop the recording and motion
        self.set_data_point("record", False, None, automated_record_uuid)
        self.set_data_point("raw_motion_value", 0)
        self.set_data_point("motion_detected", 0)
        self.activeSegmentDir = self.segmentDir = None

        self.lastStart = time.time()

        if self.process:
            try:
                self.process.stop()
            except Exception:
                print(traceback.format_exc())

        # Used to check that things are actually still working.
        # Set them to prevent a loop.
        self.lastSegment = time.time()
        self.lastPushedWSData = time.time()

        # Can't stop as soon as they push stop, still need to capture
        # the currently being recorded segment
        self.stoprecordingafternextsegment = 0

        if os.path.exists("/dev/shm/knvr_buffer/" + self.name):
            # Race condition retry
            try:
                shutil.rmtree("/dev/shm/knvr_buffer/" + self.name)
            except Exception:
                shutil.rmtree("/dev/shm/knvr_buffer/" + self.name)

        os.makedirs("/dev/shm/knvr_buffer/" + self.name)

        try:
            # Make it so nobody else can read the files
            os.chmod("/dev/shm/knvr_buffer/" + self.name, 0o700)
        except Exception:
            pass

        # Close the old thread
        self.runWidgetThread = time.time()
        self.putTrashInBuffer()
        s = 100
        while s:
            s -= 1
            if self.threadExited:
                break
            time.sleep(0.1)
        else:
            self.print("COULD NOT STOP OLD THREAD")

        self.process = Pipeline()
        self.process.dev = self

        # self.config['device.jack_output'].lower() in ('yes', 'true', 'enable', 'enabled')
        j = False
        self.process.getGstreamerSourceData(
            self.config.get("device.source", ""),
            self.config,
            self.config.get("device.username", ""),
            self.config.get("device.password", ""),
            doJackAudio=j,
        )

        x = self.process.add_element(
            "queue", connectToOutput=self.process.h264source, max_size_time=10000000
        )

        self.process.add_element("mpegtsmux", connectToOutput=(x, self.process.mp3src))

        self.process.add_element("tsparse", set_timestamps=True)

        self.mpegtssrc = self.process.add_element("tee")

        # Path to be created
        path = self.rawFeedPipe

        # Get rid of the old one, it could be clogged
        try:
            os.remove(path)
        except OSError:
            pass

        try:
            os.mkfifo(path)
        except OSError:
            print("Failed to create FIFO")

        os.chmod(path, 0o700)

        self.process.add_element("queue", max_size_time=10000000)
        self.process.add_element(
            "filesink", location=path, buffer_mode=2, sync=self.process.syncFile
        )

        # # Motion detection part of the graph

        # # This flag discards every unit that cannot be handled individually
        self.process.add_element(
            "identity", drop_buffer_flags=8192, connectToOutput=self.process.h264source
        )
        self.process.add_element("queue", max_size_time=20000000, leaky=2)
        self.process.add_element("capsfilter", caps="video/x-h264")

        self.process.add_element("avdec_h264")
        # self.process.add_element("videorate",drop_only=True)
        # self.process.add_element("capsfilter", caps="video/x-raw,framerate=1/1")

        rawtee = self.process.add_element("tee")
        self.process.add_element("queue", max_size_buffers=1, leaky=2)

        self.snapshotter = self.process.add_pil_capture()

        self.process.add_element("videoanalyse", connectToOutput=rawtee)

        if self.config.get("device.barcodes", "").lower() in (
            "yes",
            "true",
            "detect",
            "enable",
            "on",
        ):
            self.process.add_element("zbar")

        # Not a real GST element. The iceflow backend hardcodes this motion/presense detection
        self.process.add_presence_detector((640, 480), regions=self.regions)

        self.process.mcb = self.motion
        self.process.bcb = self.barcode
        self.process.acb = self.analysis

        self.process.presenceval = self.presencevalue

        self.process.add_element(
            "hlssink",
            connectToOutput=self.mpegtssrc,
            message_forward=True,
            async_handling=True,
            max_files=0,
            location=os.path.join(
                "/dev/shm/knvr_buffer/", self.name, r"segment%08d.ts"
            ),
            playlist_root=os.path.join("/dev/shm/knvr_buffer/", self.name),
            playlist_location=os.path.join(
                "/dev/shm/knvr_buffer/", self.name, "playlist.m3u8"
            ),
            target_duration=5,
        )

        # We may want to have an SRT source.
        if int(self.config["device.srt_server_port"]) > 0:
            self.process.add_element(
                "queue",
                leaky=2,
                max_size_time=200000000,
                connectToOutput=self.mpegtssrc,
            )
            self.process.add_element(
                "srtsink",
                mode=2,
                localaddress="0.0.0.0",
                localport=int(self.config["device.srt_server_port"]),
                sync=False,
            )

        self.threadStarted = False

        self.datapusher = threading.Thread(
            target=self.thread, daemon=True, name="NVR " + self.name
        )
        self.datapusher.start()

        s = 25000
        while not self.threadStarted:
            time.sleep(0.001)
            s -= 1
        else:
            if not self.threadStarted:
                self.print("Thread not started within 25 seconds")

        self.process.start()
        # Used to check that things are actually still working.
        # Set them to prevent a loop.
        self.lastSegment = time.time()
        self.lastPushedWSData = time.time()

    def onRecordingChange(self, v, t, a):
        with self.recordlock:
            d = os.path.join(self.storageDir, self.name, "recordings")
            if os.path.exists(d):
                for i in os.listdir(d):
                    i2 = os.path.join(d, i)
                    try:
                        dt = datetime.fromisoformat(i)
                    except Exception:
                        continue

                    now = datetime.utcnow().replace(tzinfo=timezone.utc)

                    if dt < now:
                        dt = now - dt
                        # Sanity check
                        if dt.days > self.retainDays and dt.days < 10000:
                            shutil.rmtree(i2)

            if a == automated_record_uuid:
                self.canAutoStopRecord = True
            else:
                self.canAutoStopRecord = False

            if v:
                self.stoprecordingafternextsegment = 0
                if not self.segmentDir:
                    self.setsegmentDir()
            else:
                self.stoprecordingafternextsegment = 1

    def setsegmentDir(self, manual=False):
        with self.recordlock:
            # Manually triggered recordings should go in a different folder

            my_date = datetime.utcnow()
            date = (
                my_date.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
                + "+00:00"
            )
            t = my_date.isoformat() + "+00:00"

            d = os.path.join(self.storageDir, self.name, "recordings", date, t)
            os.makedirs(d)
            self.segmentDir = d

            with open(os.path.join(self.segmentDir, "playlist.m3u8"), "w") as f:
                f.write("#EXTM3U\r\n")
                f.write("#EXT-X-START:	TIME-OFFSET=0\r\n")
                f.write("#EXT-X-PLAYLIST-TYPE: VOD\r\n")
                f.write("#EXT-X-VERSION:3\r\n")
                f.write("#EXT-X-ALLOW-CACHE:NO\r\n")
                f.write("#EXT-X-TARGETDURATION:5\r\n")

                s = []
                x = self.datapoints["detected_objects"]
                if x and "objects" in x:
                    for i in x["objects"]:
                        if "class" in i:
                            if not i["class"] in s:
                                s.append(i["class"])

                f.write("#EXTALB:" + ",".join(s) + "\r\n")

        # Capture a tiny preview snapshot
        import PIL

        # todo make the bmp thing reliable
        try:
            x = PIL.Image.open(io.BytesIO(self.request_data_point("bmp_snapshot")))
            x.thumbnail((320, 240))
            x = PIL.ImageOps.autocontrast(x, cutoff=0.1)
            with open(os.path.join(self.segmentDir, "thumbnail.jpg"), "wb") as f:
                x.save(f, "jpeg")
        except Exception:
            print(traceback.format_exc())

    def on_multi_file_sink(self, fn, *a, **k):
        with self.recordlock:
            self.moveSegments()
            d = os.path.join("/dev/shm/knvr_buffer/", self.name)
            ls = os.listdir(d)
            ls = list(sorted([i for i in ls if i.endswith(".ts")]))

            n = max(
                1,
                int((float(self.config.get("device.loop_record_length", 5)) + 2.5) / 5),
            )

            s = 100
            while len(ls) > n:
                if s < 1:
                    break
                s -= 1
                os.remove(os.path.join(d, ls[0]))
                self.lastSegment = time.time()
                self.set_data_point("running", 1)

                ls = os.listdir(d)
                ls = list(sorted([i for i in ls if i.endswith(".ts")]))
                n = max(
                    1,
                    int(
                        (float(self.config.get("device.loop_record_length", 5)) + 2.5)
                        / 5
                    ),
                )

    def moveSegments(self):
        with self.recordlock:
            d = os.path.join("/dev/shm/knvr_buffer/", self.name)
            ls = os.listdir(d)
            ls = list(sorted([i for i in ls if i.endswith(".ts")]))

            if self.activeSegmentDir or self.segmentDir:
                # Ignore latest, that could still be recording
                for i in ls[:-1]:
                    self.lastSegment = time.time()
                    self.set_data_point("running", 1)

                    # Someone could delete a segment dir while it is being written to.
                    # Prevent that from locking everything up.
                    if os.path.exists(self.activeSegmentDir or self.segmentDir):
                        # Find the duration of the segment from the hlssink playlist file
                        with open(os.path.join(d, "playlist.m3u8")) as f:
                            x = f.read()
                        if not i in x:
                            return

                        x = x.split(i)[0]
                        x = float(re.findall(r"EXTINF:\s*([\d\.]*)", x)[-1])

                        # Assume the start time is mod time minus length
                        my_date = datetime.utcfromtimestamp(
                            os.stat(os.path.join(d, i)).st_mtime - x
                        )
                        t = my_date.isoformat() + "+00:00"

                        shutil.move(
                            os.path.join(d, i), self.activeSegmentDir or self.segmentDir
                        )
                        with open(
                            os.path.join(
                                self.activeSegmentDir or self.segmentDir,
                                "playlist.m3u8",
                            ),
                            "a+",
                        ) as f:
                            f.write("\r\n")
                            f.write("#EXTINF:" + str(x) + ",\r\n")
                            f.write("#EXT-X-PROGRAM-DATE-TIME:" + t + "\r\n")
                            f.write(i + "\r\n")

                        self.directorySegments += 1

                    if self.stoprecordingafternextsegment:
                        x = self.segmentDir
                        self.segmentDir = None
                        self.activeSegmentDir = None

                        with open(os.path.join(x, "playlist.m3u8"), "a+") as f:
                            f.write("\r\n#EXT-X-ENDLIST\r\n")

                        break
                    else:
                        # Don't make single directories with more than an hour of video.
                        if self.directorySegments > (3600 / 5):
                            self.setsegmentDir()

                # Now we can transition to the new one!
                self.activeSegmentDir = self.segmentDir
                self.directorySegments = 0

    def check(self):
        "Pretty mush all periodic tasks go here"

        # Make sure we are actually getting video frames. Otherwise we reconnect.
        if not self.lastSegment > (time.time() - 15):
            self.set_data_point("running", False)
            if self.datapoints.get("switch", 1):
                self.connect(self.config)
                return

        if not self.lastPushedWSData > (time.time() - 15):
            self.set_data_point("running", False)
            if self.datapoints.get("switch", 1):
                self.connect(self.config)
                return

        d = os.path.join("/dev/shm/knvr_buffer/", self.name)
        ls = os.listdir(d)

        # If there is a ton of files run the poller anyway, if could have stalled because it ran out of memory
        # because something caused things to block long enough for it all to fill up.
        if (not ls == self.lastshm) or len(ls) > 16:
            self.on_multi_file_sink("")
        self.lastshm = ls

    def commandState(self, v, t, a):
        with self.streamLock:
            if not v:
                if self.process:
                    self.process.stop()
                self.runWidgetThread = False
                try:
                    self.putTrashInBuffer()
                except Exception:
                    print(traceback.format_exc())

                s = 10
                while s:
                    s -= 1
                    if self.threadExited:
                        break
                    time.sleep(0.1)
            else:
                self.check()

    def motion(self, v):
        self.doMotionRecordControl(v)
        self.set_data_point("motion_detected", v)

    def doMotionRecordControl(self, v, forceMotionOnly=False):
        "forceMotionOnly records even if there is no object detection, for when the CPU can't keep up with how many motion requests there are"
        if self.config.get("device.motion_recording", "no").lower() in (
            "true",
            "yes",
            "on",
            "enable",
            "enabled",
        ):
            # If object recording is set up, and we have some object detection, only record if there is one of the objects
            # In frame
            lookfor = self.config.get("device.object_record", "").strip()
            if not self.config["device.object_detection"].lower() in (
                "yes",
                "true",
                "enable",
                "enabled",
            ):
                lookfor = None

            if v:
                # Do obj recognition. Accept recent object detection too in addition to current.
                #  We also rerun this after we successfully do the motion detection
                if (
                    lookfor
                    and (self.lastObjectSet is not None)
                    and (not forceMotionOnly)
                ):
                    for i in self.lastObjectSet["objects"]:
                        if i["class"] in lookfor:
                            self.lastRecordTrigger = time.time()
                            self.lastObjectDetectionHit = time.time()
                            if not self.datapoints["record"]:
                                self.print("Record started because of " + i["class"])

                            if (self.datapoints["auto_record"] or 1) > 0.5:
                                self.set_data_point(
                                    "record", True, None, automated_record_uuid
                                )

                else:
                    self.lastRecordTrigger = time.time()
                    if (self.datapoints["auto_record"] or 1) > 0.5:
                        self.set_data_point("record", True, None, automated_record_uuid)

            elif not v and self.canAutoStopRecord:
                if self.lastRecordTrigger < (time.time() - 12):
                    # Even if there is still motion, if we have object detection data coming in but have not seen the object recently, stop if we are in objetc detecting
                    # mode

                    # But after a while we just have to stop, because maybe the object detector failed for some reason.

                    # Our window is 3 sucessive runs with no object hits.  Our window never goes past 30 seconds.
                    window = min(
                        self.lastDidObjectRecognition
                        - ((time.time() - self.lastDidObjectRecognition) * 3),
                        30,
                    )
                    if (self.lastRecordTrigger < (time.time() - 60)) or (
                        (self.lastDidObjectRecognition > (time.time() - 15))
                        and lookfor
                        and (self.lastObjectDetectionHit < window)
                    ):
                        self.set_data_point(
                            "record", False, None, automated_record_uuid
                        )

        self.lastDidMotionRecordControl = time.time()

    def presencevalue(self, v):
        "Takes a raw presence value. Unfortunately it seems we need to do our own motion detection."

        if isinstance(v, dict):
            for i in v:
                # Empty string is entire image
                if i and i in self.subdevices:
                    self.subdevices[i].onMotionValue(v[i])

            # Get the overall motion number
            v = v[""]

        self.set_data_point("raw_motion_value", v)

        self.motion(v > float(self.config.get("device.motion_threshold", 0.08)))

        # We do object detection on one of two conditions. Either when there is motion or every N seconds no matter what.
        # Even when there is motion, however, we rate limit to once every 1 second.
        # On top of that we give up waiting for the one available slot to do the detection, after a random amount of time.
        # This ensures that under high CPU load we just gracefully fall back to not doing very much detection.

        # The value of N seconds should be very low if we detect that there is *really* nothing that could reasonably be seen as motion.
        detect_interval = 8 if v > 0.003 else 15

        objects = True
        if not self.config["device.object_detection"].lower() in (
            "yes",
            "true",
            "enable",
            "enabled",
        ):
            objects = False

        if objects and (
            (v > float(self.config.get("device.motion_threshold", 0.08)))
            or (self.lastDidObjectRecognition < time.time() - detect_interval)
        ):
            # Limit CPU usage. But don't limit so much we go more than 5s between detections
            if (
                self.lastDidObjectRecognition - min(self.lastInferenceTime * 1.1, 5)
            ) < time.time() - min(self.lastInferenceTime * 1.1, 5):
                self.obj_rec_wait_timestamp = time.time()
                obj_rec_wait = self.obj_rec_wait_timestamp

                def f():
                    # Wait longer if not already recording so that things that don't need to detect as much give up faster.
                    # prioritize reliable start of record!

                    # Cannot wait too long thogh because we nee to quickly fail back to motion only.

                    # This calculates our length in terms of how much loop recorded footage we have
                    # We have to detect within this window or it will dissapear before we capture it.

                    # Note
                    n = (
                        max(
                            1,
                            int(
                                (
                                    float(
                                        self.config.get("device.loop_record_length", 5)
                                    )
                                    + 2.5
                                )
                                / 5
                            ),
                        )
                        * 5
                    )

                    # If we have not seen any objects lately, better check more often because
                    # We might be about to stop the recording even if there is still motion, so it must be accurate.
                    if self.lastObjectDetectionHit > (time.time() - 15):
                        t = 3 if self.datapoints["record"] else (n * 0.75)
                    else:
                        t = n * 0.75

                    if object_detection_lock.acquire(True, t + (random.random() * 0.1)):
                        try:
                            # We have to make sure an older detection does not wait on a newer detection.
                            # Only the latest should get through, or we would queue up a problem.
                            if self.obj_rec_wait_timestamp > obj_rec_wait:
                                return

                            x = self.request_data_point("bmp_snapshot")
                            if not x:
                                return
                            o = recognize_objects(x)
                            self.lastInferenceTime = o["x_inferencetime"]
                            self.lastDidObjectRecognition = time.time()
                            self.lastObjectSet = o

                            lookfor = self.config.get(
                                "device.object_record", ""
                            ).strip()
                            # For some high-certainty things we can trigger motion even when there is no motion detected by
                            # the standard algorithm.
                            relevantObjects = 0
                            if lookfor and (self.lastObjectSet is not None):
                                for i in self.lastObjectSet["objects"]:
                                    if i["class"] in lookfor and i["confidence"] > 0.35:
                                        relevantObjects += 1

                            if self.oldRelevantObjectCount > -1 and not (
                                self.oldRelevantObjectCount == relevantObjects
                            ):
                                self.motion(True)

                            self.oldRelevantObjectCount = relevantObjects

                            self.set_data_point("detected_objects", o)
                            for i in self.subdevices:
                                self.subdevices[i].onObjects(o)
                            # We are going to redo this.
                            # We do it in both places.
                            # Imagine you detect a person but no motion, but then later see motion,
                            # but no person a few seconds later
                            # You probably want to catch that because a person was likely involved
                            self.doMotionRecordControl(
                                self.datapoints["motion_detected"]
                            )
                        finally:
                            object_detection_lock.release()

                    else:
                        self.doMotionRecordControl(
                            self.datapoints["motion_detected"], True
                        )

                workers.do(f)

        else:
            # We arent't even using obj detct at all
            self.doMotionRecordControl(self.datapoints["motion_detected"], True)

    def analysis(self, v):
        self.set_data_point("luma_average", v["luma_average"])
        self.set_data_point("luma_variance", v["luma_variance"])

    def barcode(self, t, d, q):
        self.set_data_point(
            "barcode",
            {
                "barcode_type": t,
                "barcode_data": d,
                "wallclock": time.time(),
                "quality": q,
            },
        )

    def __init__(self, name, data, **kw):
        devices.Device.__init__(self, name, data, **kw)
        try:
            self.runWidgetThread = True
            self.runCheckThread = time.time()

            self.lastInferenceTime = 0.0
            self.threadExited = True
            self.closed = False

            self.set_config_default("device.storage_dir", "~/NVR")

            self.set_config_default("device.loop_record_length", "5")

            self.set_config_default("device.srt_server_port", "0")

            self.set_config_default("device.source", "")
            self.set_config_default("device.username", "")
            self.set_config_default("device.password", "")
            # If this is true, we send the camera audio to JACK if possible
            # self.set_config_default("device.jack_output", 'no')

            # Region data is in the format like regionName=0.3,0.3,0.4,0.2;
            # X, Y, W, H as fraction of image dimension
            self.set_config_default("device.regions", "")

            # Handle region data of the form foo=x,y,w,h;
            regions = {}
            x = self.config["device.regions"]
            if x:
                x = x.split(";")

                for i in x:
                    if not "=" in i:
                        continue

                    n, d = i.split("=")
                    n = n.strip()
                    regions[n] = [float(i.strip()) for i in d.split(",")]

                for i in regions:
                    x = self.create_subdevice(NVRChannelRegion, i, {})
                    i = regions[i]
                    x.x = i[0]
                    x.y = i[1]
                    x.width = i[2]
                    x.height = i[3]

                    x.region = i

            self.regions = regions

            # Support ONVIF URLs
            self.onvif = None
            if self.config["device.username"] and self.config["device.password"]:
                try:
                    if (
                        self.config["device.source"]
                        and not self.config["device.source"].startswith("rtsp://")
                        and not self.config["device.source"].startswith("file://")
                        and not self.config["device.source"] in ("webcam", "screen")
                    ):
                        if not self.config["device.source"].startswith("srt://"):
                            p = self.config["device.source"].split("://")[-1]
                            if ":" in p:
                                port = int(p.split(":")[1])
                                p = p.split(":")[0]
                            else:
                                port = 80

                            self.onvif = ONVIFCamera(
                                p,
                                port,
                                self.config["device.username"],
                                self.config["device.password"],
                            )
                except Exception:
                    self.print(traceback.format_exc())

            self.process = None

            self.lastInferenceTime = 1

            self.lastDidObjectRecognition = 0

            # So we can tell if there is new object recogintion data since we last checked.
            self.lastDidMotionRecordControl = 0

            # Used to detect motion by looking at changes in the number of relevant objects.
            # Response time may be very low.
            self.oldRelevantObjectCount = -1

            # The most recent set of object detection results.
            self.lastObjectSet = None

            # We don't want to stop till a few seconds after an event that would cause motion
            self.lastRecordTrigger = 0

            # We also DO want to stop if we are in object record mode and have not seen the object in a long time

            self.lastObjectDetectionHit = 0

            # If this is true, record when there is motion
            self.set_config_default("device.motion_recording", "no")

            self.storageDir = os.path.expanduser(
                self.config["device.storage_dir"] or "~/NVR"
            )

            self.segmentDir = None

            # When changing segment dir, we can't do it instantly, we instead wait to be done with the current file.
            self.activeSegmentDir = None

            # How many segments in this dir. Must track so we can switch to a new directory if we need to.
            self.directorySegments = 0

            self.lastshm = None

            self.canAutoStopRecord = False

            if not os.path.exists(self.storageDir):
                os.makedirs(self.storageDir)
                # Secure it!
                os.chmod(self.storageDir, 0o700)

            self.tsQueue = b""

            self.recordlock = threading.RLock()

            self.rawFeedPipe = (
                "/dev/shm/knvr_buffer/"
                + self.name
                + "/"
                + str(time.time())
                + ".raw_feed.tspipe"
            )

            self.bytestream_data_point("raw_feed", subtype="mpegts", writable=False)

            # Give this a little bit of caching
            self.bytestream_data_point(
                "bmp_snapshot", subtype="bmp", writable=False, interval=0.3
            )

            self.set_data_point_getter("bmp_snapshot", self.getSnapshot)

            self.numeric_data_point(
                "switch",
                min=0,
                max=1,
                subtype="bool",
                default=1,
                handler=self.commandState,
                dashboard=False,
            )

            self.numeric_data_point(
                "auto_record",
                min=0,
                max=1,
                subtype="bool",
                default=1,
                handler=self.onRecordingChange,
                description="Set to 0 to disable automatic new recordings.",
                dashboard=False,
            )

            self.numeric_data_point(
                "record",
                min=0,
                max=1,
                subtype="bool",
                default=0,
                handler=self.onRecordingChange,
            )

            self.numeric_data_point(
                "running", min=0, max=1, subtype="bool", writable=False
            )

            self.numeric_data_point(
                "motion_detected", min=0, max=1, subtype="bool", writable=False
            )

            self.numeric_data_point(
                "raw_motion_value", min=0, max=10, writable=False, dashboard=False
            )

            self.numeric_data_point("luma_average", min=0, max=1, writable=False)

            self.numeric_data_point(
                "luma_variance", min=0, max=1, writable=False, dashboard=False
            )

            self.set_alarm(
                "Camera dark",
                "luma_average",
                "value < 0.095",
                trip_delay=10,
                auto_ack=True,
            )
            self.set_alarm(
                "Camera low varience",
                "luma_variance",
                "value < 0.004",
                release_condition="value > 0.008",
                trip_delay=60,
                auto_ack=True,
            )
            self.set_alarm(
                "Long_recording",
                "record",
                "value > 0.5",
                trip_delay=800,
                auto_ack=True,
                priority="debug",
            )

            self.set_alarm(
                "Not Running",
                "running",
                "value < 0.5",
                trip_delay=90,
                auto_ack=False,
                priority="warning",
            )

            self.set_config_default("device.fps", "4")
            self.set_config_default("device.barcodes", "no")
            self.set_config_default("device.object_detection", "no")

            if self.config["device.object_detection"].lower() in (
                "yes",
                "true",
                "enable",
                "enabled",
                "on"
            ):
                def f():
                    getCaffeModel(self)
                t = threading.Thread(target=f, name="getCaffeModel")
                t.daemon = True
                t.start()


            self.set_config_default(
                "device.object_record",
                "person, dog, cat, horse, sheep, cow, handbag, frisbee, bird, backpack, suitcase, sports ball",
            )

            self.set_config_default("device.motion_threshold", "0.08")
            self.set_config_default("device.bitrate", "386")

            self.set_config_default("device.retain_days", "90")

            self.config.pop("device.motion_sensitivity", 0)

            self.retainDays = int(self.config["device.retain_days"])

            if self.config["device.barcodes"].lower() in (
                "yes",
                "true",
                "enable",
                "enabled",
            ):
                self.object_data_point("barcode", writable=False)

            if self.config["device.object_detection"].lower() in (
                "yes",
                "true",
                "enable",
                "enabled",
            ):
                self.object_data_point("detected_objects", writable=False)

            self.config_properties["device.loop_record_length"] = {
                "description": "How many seconds to buffer at all times to allow recording things before motion events actually happen."
            }

            self.config_properties["device.barcodes"] = {"type": "bool"}

            self.config_properties["device.object_detection"] = {
                "type": "bool",
                "description": "Enable object detection.  See kaithem readme for where to put model files. ",
            }

            self.config_properties["device.object_record"] = {
                "description": "Does nothing without object detection and motion record enabled. Only record if there is both motion, and a recognized object on the list in the frame. If empty, always record. Can use any COCO item."
            }

            self.config_properties["device.password"] = {"secret": True}
            self.config_properties["device.motion_recording"] = {"type": "bool"}

            self.config_properties["device.storage_dir"] = {"type": "local_fs_dir"}

            self.config_properties["device.regions"] = {"type": "region_list"}

            self.streamLock = threading.RLock()
            self.lastStart = 0

            try:
                self.connect(self.config)
            except Exception:
                self.handleException()
                self.set_data_point("running", 0)

            self.set_data_point("switch", 1)

            # Used to check that things are actually still working.
            self.lastSegment = time.time()
            self.lastPushedWSData = time.time()

            self.check()
            self.checkthreadobj = threading.Thread(
                target=self.checkThread, daemon=True, name="NVR checker" + self.name
            )
            self.checkthreadobj.start()

        except Exception:
            self.handleException()

    @classmethod
    def discover_devices(cls, config={}, current_device=None, intent=None, **kw):
        # Discover based on the ONVIF cameras.  Let the user fill in username/password.
        l = {}
        for i in onvifCams:
            config2 = config.copy()

            config2.update({"type": cls.device_type, "device.source": i})

            config2["device.username"] = "admin"
            config2["device.password"] = ""
            l[i] = config2

        for i in os.listdir("/dev/"):
            if i.startswith("video"):
                config2 = config.copy()

                config2.update({"type": cls.device_type, "device.source": "/dev/" + i})

                config2["device.username"] = ""
                config2["device.password"] = ""
                l["Webcam " + i] = config2

        config2 = config.copy()
        config2.update({"type": cls.device_type, "device.source": "screen"})

        config2["device.username"] = ""
        config2["device.password"] = ""
        config2["device.fps"] = "4"
        l["Screen Recording"] = config2

        return l
