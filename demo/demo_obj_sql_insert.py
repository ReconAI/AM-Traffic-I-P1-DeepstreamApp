import numpy as np
from datetime import datetime, timedelta
import random

FILEPATH = '../testdata/file_klt_archiveDetections.txt'

PGIE1_LABELS_DICT = {
    -1: 'None',
    0: 'Car',
    1: 'TwoWheeler',
    2: 'Person',
    3: 'RoadSign',
}

SGIE_LABELS_DICT = {
    -1: 'None',
    0: 'Coupe',
    1: 'LargeVehicle',
    2: 'Sedan',
    3: 'SUV',
    4: 'Truck',
    5: 'Van',
}

DB_Type_Code_Convertor = {
'Car':'CAR',
'Van':'VAN',
'Truck':'TRK',
'Coupe':'COU',
'SUV':'SUV',
'LargeVehicle':'LRG',
'Sedan':'SED'
}

print("INSERT INTO 'DetectedObjects'")
print("('id','edgeNodeId','objectType','created_dt','fileId','parametersJSON')")
print("VALUES")

date_time_obj = datetime.strptime('2020-08-11T22:37:31.025Z', '%Y-%m-%dT%H:%M:%S.%fZ')

with open(FILEPATH,'r') as fp:
    for cnt, line in enumerate(fp):
        line_split = line.split(';')
        
        row_id = line_split[0].split(':')[1]
        row_pgie = PGIE1_LABELS_DICT[int(line_split[1].split(':')[1])]
        row_sgie = SGIE_LABELS_DICT[int(line_split[2].split(':')[1])]

        row_class = row_pgie
        if (row_sgie != 'None'):
            row_class = row_sgie

        row_lp = line_split[12].split(':')[1]
        date_time_obj = date_time_obj + timedelta(milliseconds=random.randint(100,1500))
            
        print (f"('{row_id}','1','{DB_Type_Code_Convertor[row_class]}','{str(date_time_obj)}', '', '{{ licenseplate: '{row_lp}' }}'),")
print(";")


