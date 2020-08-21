#Traffic stats test

import sys
sys.path.insert(0,'..')

import numpy as np

from detection_accounting import *

def CreateDetectionObject(key_id, pgie, sgie, x1,y1,x2,y2):
    a = DetectionObject(key_id,pgie,sgie)
    a.update_location(x1,y1,x2,y2)
    return a

DETECTION_OBJECT_ARRAY = [
    [1,0,1,1,1,1,1],
    [2,0,2,1,1,1,1],
    [3,0,3,1,1,1,1],
    [4,0,1,1,3,3,3],
    [5,0,2,1,1,1,1],
    [6,0,3,3,3,3,3],
    [7,0,1,1,1,1,1],
    [8,0,2,1,1,1,1],
    [9,0,3,1,1,1,1],
    [10,0,1,1,3,3,3],
    [11,0,2,1,1,1,1],
    [12,0,3,3,3,3,3],
    [13,0,1,1,3,3,3],
    [14,0,2,1,1,1,1],
    [15,0,3,3,3,3,3],
    [16,0,1,1,3,3,3],
    [17,0,2,1,1,1,1],
    [18,0,3,3,3,3,3],
    [19,0,1,1,3,3,3],
    [20,0,2,1,1,1,1],
    [21,0,3,3,3,3,3],
    [22,0,4,1,3,3,3],
    [23,0,5,1,1,1,1],
    [24,0,1,3,3,3,3]
]

DETECTION_ACCOUNTANT = DetectionAccountant(3)

for v_object in DETECTION_OBJECT_ARRAY:
    b = CreateDetectionObject(v_object[0],v_object[1],v_object[2],v_object[3],v_object[4],v_object[5],v_object[6])
    DETECTION_ACCOUNTANT.archive_buffer.append(b)

DETECTION_ACCOUNTANT.print_archve_buffer()

traffic_stats = DETECTION_ACCOUNTANT.calculate_traffic_stats()

traffic_stats.printStats()

for v_object in DETECTION_OBJECT_ARRAY:
    b = CreateDetectionObject(v_object[0],v_object[1],v_object[2],v_object[3],v_object[4],v_object[5],v_object[6])
    DETECTION_ACCOUNTANT.archive_buffer.append(b)

DETECTION_ACCOUNTANT.print_archve_buffer()

traffic_stats = DETECTION_ACCOUNTANT.calculate_traffic_stats()

traffic_stats.printStats()