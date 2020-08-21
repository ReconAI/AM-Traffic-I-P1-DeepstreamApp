import numpy as np
from datetime import datetime, timedelta
import random

class WeatherRecord(object):
    pass

v_WeatherInstance = WeatherRecord()
v_isFirstRun = True


with open("../testdata/syntheticWeather.txt","w+") as wp:

    wp.write("INSERT INTO 'RoadConditions'\n")
    wp.write("('edgeNodeId','created_dt','parametersJSON')\n")
    wp.write("VALUES\n")

    with open("../testdata/sensor_data2.txt","r") as rp:
        for cnt, line in enumerate(rp):
            
            line_words = line.split('\t')
            if (line_words[0] == 'UNNAMED: 0'):
                if (not v_isFirstRun):
                    #Write data to a syntheticWeather.txt
                    wp.write(f"('{v_WeatherInstance.EdgeDeviceId}','{v_WeatherInstance.time}','{{\"{v_WeatherInstance.json_attr}\":\"{v_WeatherInstance.json_val}\"}}\n")
                else:
                    v_isFirstRun = False
                
                v_WeatherInstance = WeatherRecord()

            if (line_words[0] == 'WEATHERSTATIONID'):
                v_WeatherInstance.EdgeDeviceId = line_words[-1].replace('\n','')
            if (line_words[0] == 'MEASUREDTIME'):
                v_WeatherInstance.time = line_words[-1].replace('\n','')
            if (line_words[0] == 'OLDNAME'):
                v_WeatherInstance.json_attr = line_words[-1].replace('\n','')
            if (line_words[0] == 'SENSORVALUEDESCRIPTIONEN'):
                v_WeatherInstance.json_val = line_words[-1].replace('\n','')


            #.replace('\n','')

