
#Number of frames to run License Plate detection and recognition algorithms
ALPR_FRAME_RATE = 10
#Number of frames to send messages
MSQ_FRAME_RATE = 100
#Minimum age of an object to consider it a proper detection
MIN_DETECTION_AGE = 5
#Minimal number of LP samples to run license plate recognition
MIN_NUMBER_OF_LP_SAMPLES = 3

#Grouping algorithm settings
DBSCAN_EPSILON = 0.5
DBSCAN_SAMPLES = 10


#Object detector (TrafficCamNet) classes
PGIE1_UNIQUE_ID = 1
PGIE_CLASS_ID_VEHICLE = 0
PGIE_CLASS_ID_BICYCLE = 1
PGIE_CLASS_ID_PERSON = 2
PGIE_CLASS_ID_ROADSIGN = 3

PGIE1_LABELS_DICT = {
    -1: 'None',
    0: 'Car',
    1: 'TwoWheeler',
    2: 'Person',
    3: 'RoadSign',
}

#Secondary detector (Vehicle Type) classes
SGIE_UNIQUE_ID = 2
SGIE_CLASS_ID_COUPE = 0
SGIE_CLASS_ID_LARGE = 1
SGIE_CLASS_ID_SEDAN = 2
SGIE_CLASS_ID_SUV = 3
SGIE_CLASS_ID_TRUCK = 4
SGIE_CLASS_ID_VAN = 5

SGIE_LABELS_DICT = {
    -1: 'None',
    0: 'Coupe',
    1: 'LargeVehicle',
    2: 'Sedan',
    3: 'SUV',
    4: 'Truck',
    5: 'Van',
}

#Object detector (FaceLicensePlates) classes
PGIE2_UNIQUE_ID = 3
