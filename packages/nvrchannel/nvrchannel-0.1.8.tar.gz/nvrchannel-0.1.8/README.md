# NVRChannel
Network video recorder for iot_devices compatible apps.
Requires GStreamer to be installed on the system.

Split into a separate lib due to the large model file.


## Changes
### 0.1.7 

* setup.py file include fix

### 0.1.6

* Use cv2.dnn because tflite keeps breaking on python version updates.
* Switch to MobileNetSSD
