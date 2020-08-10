SAVE_IMAGES = False
SAVE_LICENSE_PLATES_TO_FILE = True

LICENSE_PLATES_FILENAME = 'licensePlatesDetections.txt'

SAVE_ARCHIVE_TO_FILE = True
ARCHIVE_FILENAME = 'archiveDetections.txt'

SAVE_STATISTICS_TO_FILE = True
STATISTICS_FILENAME = 'statisticsDetections.txt'

SEND_IOT_MESSAGES = False

PRINT_DEBUG = False


#Number of frames to run License Plate detection and recognition algorithms
ALPR_FRAME_RATE = 5
#Number of frames to send messages
MSQ_FRAME_RATE = 3600
#Minimum age of an object to consider it a proper detection
MIN_DETECTION_AGE = 15 #15 frames = 1 second
#For how long object can be considered missing
ABSENSE_INTERVAL = 15
#Minimal number of LP samples to run license plate recognition
MIN_NUMBER_OF_LP_SAMPLES = 6

ALRP_CONFIDENCE_THRESHOLD = 70

#Grouping algorithm settings
DBSCAN_EPSILON = 0.5
DBSCAN_SAMPLES = 10

PGIE_CONFIG_FILE = "dstest2_pgie1_config.txt"
SGIE_CONFIG_FILE = "dstest2_sgie_config.txt"
MSCONV_CONFIG_FILE="dstest4_msgconv_config.txt"

TRACKER_KLT_CONFIG = 'tracker_klt_config.txt'
TRACKER_NVDCF_CONFIG = 'tracker_nvdcf_config.txt'
TRACKER_IOU_CONFIG = 'tracker_iou_config.txt'
TRACKER_CONFIG = TRACKER_KLT_CONFIG

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
