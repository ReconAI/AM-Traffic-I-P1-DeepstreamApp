# AM-Traffic-I Phase 1 Deepstream SDK Application (Python)

Deepstream 5.0 Python application<br>
Application can read one RTSP Stream, perform vehicle detection and license plate recognition, output rtsp stream and print metadata in console

## Pipeline

- One input source (rtsp/file[mp4])
- TrafficCamNet 
- Default tracker
- Secondary network - car type
- OpenALPR license plate recognition
- rtsp output

## Stats
10-15 FPS on Jetson Nano (720p video).

## Installation

Put project folder into '/opt/nvidia/deepstream/deepstream-5.0/sources/python/apps/deepstream-amtraffic'

## How to run

To run production sample:

```sh
cd /opt/nvidia/deepstream/deepstream-5.0/sources/python/apps/deepstream-test12-helloworld8
python3 deepstream-amtraffic.py file:///opt/nvidia/deepstream/deepstream-5.0/samples/streams/StreamRecord_cam2_test.mp4
or
python3 deepstream-amtraffic.py rtsp://192.168.100.2:8554
```

RTSP output can be checked as rtps stream:
```sh
rtsp://<device-ip-address>:8554/ds-test
for example
rtsp://192.168.1.132:8554/ds-test
```

To run demo sample:

```sh
cd /opt/nvidia/deepstream/deepstream-5.0/sources/python/apps/deepstream-test12-helloworld8
python3 deepstream-amtraffic_demo.py file:///opt/nvidia/deepstream/deepstream-5.0/samples/streams/StreamRecord_cam2_test3.mp4
or
python3 deepstream-amtraffic_demo.py rtsp://192.168.100.2:8554
```


RTSP output can be checked as rtps stream:
```sh
rtsp://<device-ip-address>:8554/ds-test
for example
rtsp://192.168.1.132:8554/ds-test
```
