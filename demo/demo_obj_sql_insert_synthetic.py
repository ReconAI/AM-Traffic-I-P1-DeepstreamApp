import numpy as np
from datetime import datetime, timedelta
import random
import string

SGIE_LABELS_DICT = {
    0: 'CAR',
    1: 'VAN',
    2: 'TRK',
    3: 'COU',
    4: 'SUV',
    5: 'LRG',
    6: 'SED',
}

date_time_obj = datetime.strptime('2020-08-12T20:15:45.085Z', '%Y-%m-%dT%H:%M:%S.%fZ')
key_id = 811

with open("../testdata/syntheticDetections.txt","w+") as fp:

    fp.write("INSERT INTO 'DetectedObjects'" + '\n')
    fp.write("('id','edgeNodeId','objectType','created_dt','fileId','parametersJSON')" + '\n')
    fp.write("VALUES" + '\n')

    for i in range(0,50000):
    
        date_time_obj = date_time_obj + timedelta(milliseconds=random.randint(100,1500))
        key_id = key_id + random.randint(1,5)
        obj_class = SGIE_LABELS_DICT[random.randint(0,6)]
        rand_lp = random.choice(string.ascii_letters).upper() + random.choice(string.ascii_letters).upper() + random.choice(string.ascii_letters).upper() + str(random.randint(0,9)) + str(random.randint(0,9)) + str(random.randint(0,9))

        fp.write(f"('{key_id}','1','{obj_class}','{str(date_time_obj)}', '', '{{ licenseplate: '{rand_lp}' }}'),\n" )

    fp.write(";\n" )
        


