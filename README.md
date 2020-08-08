# AM-Traffic-I Phase 1 Deepstream SDK Application (Python)

Deepstream 5.0 Python application<br>
Application can read one RTSP Stream/Video file, perform traffic statistics calculation and license plate recognition, output rtsp stream and AWS IoT Messages<br>

## Pipeline

- One input source (rtsp/file[mp4])
- TrafficCamNet detector and classifier (Vehicle, Person, TwoWheeler, TrafficSign)
- KLT tracker
- Secondary network - car type classifier (Car, Coupe, LargeVehicle,Sedan,SUV,Truck,Van)
- OpenALPR license plate recognizer
- rtsp output + AWS IoT Messages

## How application works

1. Application is processing each frame of video with TrafficCamNet, Tracker and Secondary network and gather list of possible detections
2. If possible detection is alive for more than 'N' frames (MIN_DETECTION_AGE) it will be added in detections list
3. Object exist in detection list while system is able to track it, last object position is saved each frame.
4. Once in M frames (ALPR_FRAME_RATE), license plate recognition algorithm is running for each detected object. It detects License plate location and tries to recognize it's text. This data is saved to object properties
5. If object has enough license plate recognition samples, averaging algorithm is triggered, it would find 'average' value of a license plate. Result value will be saved to an object properties
6. License plate last position is used to cover license plate location with green (color cannot be picked in this version of Deepstream) boudning box
7. Object might dissapear from the frame, in this case algorithm will track how long it was missing and if it's value is bigger than K frames (ABSENSE_INTERVAL) it will be deleted from detections list and put into Archive
8. Once in O frames (MSQ_FRAME_RATE) pointer goes over Archive, composes individual Vehicle messages and one Traffic Statistics message and sends them to the AWS

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

## License plate detection single-network application test
```sh
cd /opt/nvidia/deepstream/deepstream-5.0/sources/python/apps/deepstream-amtraffic
python3 deepstream_lpdetection.py file:///opt/nvidia/deepstream/deepstream-5.0/samples/streams/StreamRecord_cam2_test3.mp4
```

https://github.com/ReconAI/AMTrafficPhase2-face-licenseplate-detection/tree/master/Detectnet_resnet10
