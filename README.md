# AM-Traffic-I Phase 1 Deepstream SDK Application (Python)

Deepstream 5.0 Python application<br>
Application can read one RTSP Stream/Video file, perform traffic statistics calculation and license plate recognition, output rtsp stream, save metadata to a file and send AWS IoT Messages<br>

[Project documentation](https://docs.google.com/document/d/1AmKgb2SDzw7zBTJU8LNko5U9y1sy1nP9aKoB9-h3jLU/edit#heading=h.iwpwcwbb2cso)

## Pipeline

- One input source (rtsp/file[mp4])
- TrafficCamNet detector and classifier (Vehicle, Person, TwoWheeler, TrafficSign)
- KLT tracker
- Secondary network - car type classifier (Car, Coupe, LargeVehicle,Sedan,SUV,Truck,Van)
- OpenALPR license plate recognizer
- rtsp output + Metadata save + AWS IoT Messages

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
Hardware: Jetson Nano<br>
Input: 720p video<br>
FPS: 5.9 - 20<br>

## Feature metrics

### License Plate recognition
Accuracy: 52.63%<br>
Precision: 0.76<br>
Recall: 0.53<br>

### Traffic Statistics
Precision: 0.87<br>
Recall: 1.00<br>

## Installation

- Install Deepstream SDK 5.0
- Put project into folder '/opt/nvidia/deepstream/deepstream-5.0/sources/python/apps/deepstream-amtraffic'
- Install requirements
- Make sure that TrafficCamNet, fd_pld, VehicleTypeNet networks are placed into models folder
- Install OpenALPR

## Configurations

Configuration parameters can be found in 'deepstream_config.py' file. Parameters purpose and description can be found in the same file.

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
python3 deepstream_amtraffic_msq.py file:///opt/nvidia/deepstream/deepstream-5.0/samples/streams/18_LPs_1280_Trim.mp4

python3 deepstream_amtraffic_msq.py rtsp://192.168.100.2:8554
```

### Expected result

1. Command line output with metadata

2. Three text files in application folder:
- file_licensePlatesDetections.txt - list of recognized license plates
- file_archiveDetections.txt - list of detected objects
- file_statisticsDetections.txt - traffic statistics
*actual filenames can be seen in deepstream_config.py under LICENSE_PLATES_FILENAME, ARCHIVE_FILENAME, STATISTICS_FILENAME variables

## Results validation

### License plate recognition

Run following commands:
```sh
cd /opt/nvidia/deepstream/deepstream-5.0/sources/python/apps/deepstream-amtraffic
python3 test/test_lpcomparison.py --gtLP=data/laneALL.txt --recLP=file_licensePlatesDetections.txt
```

### Traffic statistics

Run following commands
```sh
cd /opt/nvidia/deepstream/deepstream-5.0/sources/python/apps/deepstream-amtraffic
python3 test/test_trafficstatistics.py --stats=file_statisticsDetections.txt --gtVehicles=102
```

## Instruction

[Final Report](https://docs.google.com/document/d/1AmKgb2SDzw7zBTJU8LNko5U9y1sy1nP9aKoB9-h3jLU/edit#)
[Edge device setup](https://github.com/ReconAI/EdgeDeviceSetup)
[Testing preparation and Perm Nano connection](https://docs.google.com/document/d/1hDoDEHMTkMPDQZCvGM-OgKTn2EXkXXvS0UaDlJ75vEw/edit)
