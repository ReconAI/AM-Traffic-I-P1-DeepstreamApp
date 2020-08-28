import numpy as np
from datetime import datetime, timedelta
import random

print("INSERT INTO 'RelevantData'")
print("('id','deviceInstanceId','projectId','edgeNodeId','featureModelId','sensorGpsLat','sensorGpsLong','locationX','locationY','locationZ','orientTheta','orientPhi')")
print("VALUES")

coordinates_dict = {
    1: (65.0132, 25.4857),
    2: (64.9863, 25.5092),
    3: (65.0206, 25.4958),
    4: (65.0383, 25.4429),
    5: (65.0269, 25.5066),
    6: (64.9965, 25.4641),
    7: (64.9898, 25.4334),
    8: (64.984, 25.4724),
    9: (64.9744, 25.4884),
    10: (65.0383, 25.4429),
    11: (65.0269, 25.5066),
    12: (64.9965, 25.4641),
    13: (64.9898, 25.4334)
}

orientation_dict = {
    1: (0, 0.785),
    2: (0.785, 0.785),
    3: (2.26, 0.785),
    4: (0.26, 0.61),
    5: (0.26, 2.26),
    6: (0.785, 2.26),
    7: (0.785, 0),
    8: (0.26, 2.26),
    9: (0.785, 0.785),
    10: (0.785, 0),
    11: (0.26, 0.61),
    12: (0.785, 0.785),
    13: (0.26, 2.26)
}

for i in range(1,13):

    device_id = random.randint(1,13)
    projectId = random.randint(1,3)
    edgeNode_id = random.randint(1,4)
    featureModelId = random.randint(1,4)
    gps_lat, gps_long =coordinates_dict[device_id] 
    loc_x = random.randint(10,40)
    loc_y = random.randint(0,60)
    loc_z = random.randint(2000,3000)
    phi, theta = orientation_dict[device_id]

    print(f"({i},{i},{projectId},{edgeNode_id},{featureModelId},{gps_lat},{gps_long},{loc_x},{loc_y},{loc_z},{phi},{theta}),")


print(";")


