import numpy as np
from datetime import datetime, timedelta
import random

FILEPATH = '../testdata/statisticsDetections.txt'

print("INSERT INTO 'DetectionsSummary'")
print("('edgeNodeId','observationDate','parametersJSON')")
print("VALUES")

with open(FILEPATH) as fp:
    for cnt, line in enumerate(fp):
        line_split = line.split(';')

        start_dt = line_split[0]
        end_dt = line_split[1]
        obj_num = line_split[2]
        dir_num = line_split[3]
        dir_json = line_split[4]
        print (f"('1','{str(end_dt)}','{{ ObservationStartDT: '{str(start_dt)}', ObservationEndDT: '{str(end_dt)}', NumberOfObjects: '{obj_num}', NumberOfDirections : '{dir_num}', DirectionsStatistics : {dir_json} }}'),")
print(";")


