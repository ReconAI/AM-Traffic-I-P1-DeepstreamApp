# AM-Traffic-I Phase 1 Deepstream SDK Application (Python)

Deepstream 5.0 Python application<br>
Application can read one RTSP Stream, perform traffic statistics calculation and license plate recognition, output rtsp stream and AWS IoT Messages<br>

## Pipeline

- One input source (rtsp/file[mp4])
- TrafficCamNet detector and classifier (Vehicle, Person, TwoWheeler, TrafficSign)
- KLT tracker
- Secondary network - car type classifier (Car, Coupe, LargeVehicle,Sedan,SUV,Truck,Van)
- OpenALPR license plate recognizer
- rtsp output + AWS IoT Messages

## Performance
Hardware: Jetson Nano
Input: 720p video
FPS: 5.8 - 18

## Installation

Put project folder into '/opt/nvidia/deepstream/deepstream-5.0/sources/python/apps/deepstream-amtraffic'

## Configurations

Configuration parameters can be found in 'deepstream_config.py' file

## How to run

```sh
cd /opt/nvidia/deepstream/deepstream-5.0/sources/python/apps/deepstream-amtraffic
python3 deepstream_amtraffic_msq.py file://<PATH_TO_A_FILE>
or 
python3 deepstream_amtraffic_msq.py rtsp://<PATH_TO_A_FILE>
```

Check 'rtsp://<IP>:8554/ds-test' for RTSP stream

Examples:
```sh
cd /opt/nvidia/deepstream/deepstream-5.0/sources/python/apps/deepstream-amtraffic
python3 deepstream_amtraffic_msq.py file:///opt/nvidia/deepstream/deepstream-5.0/samples/streams/StreamRecord_cam2_test3.mp4

python3 deepstream_amtraffic_msq.py file:///opt/nvidia/deepstream/deepstream-5.0/samples/streams/sample_720p.mp4

python3 deepstream_amtraffic_msq.py file:///opt/nvidia/deepstream/deepstream-5.0/samples/streams/18_LPs_1280_Trim.mp4

python3 deepstream_amtraffic_msq.py rtsp://192.168.100.2:8554
```

## Testing Instruction

[Instruction](https://docs.google.com/document/d/1hDoDEHMTkMPDQZCvGM-OgKTn2EXkXXvS0UaDlJ75vEw/edit)

