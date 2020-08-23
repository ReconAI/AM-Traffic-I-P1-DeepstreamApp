# Traffic Statistics comarison script
# Input:
# - stats_data.txt - statistical output
# - Ground truth number of vehicles
## 
# Output:
# Traffic Statistics quality metrics

#Usage:
# python test_trafficstatistics.py --stats=../data/stats_data.txt --gtVehicles=102

import os
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='License plate comparison script')
    parser.add_argument('--gtVehicles', dest='gtVehiclesNum', help='Ground Truth Number of vehicles')
    parser.add_argument('--stats', dest='file_stats', help='Path to a file with license plate recognitions')

    args = parser.parse_args()

    file_stats = args.file_stats
    gtVehiclesNum = int(args.gtVehiclesNum)

    print(f"Checking Traffic stats from file: {file_stats}. Ground truth number of vehicles provided: {gtVehiclesNum}")
    
    f = open(file_stats, "r")
    list_recLPs = f.read().splitlines()
    f.close() 

    recVehicleNum = 0

    for v_line in list_recLPs:
        if "Timeframe" not in v_line:
            numVehicles = int(v_line.split(':')[3])
            recVehicleNum += numVehicles

    if (recVehicleNum>gtVehiclesNum):
        precision = gtVehiclesNum/recVehicleNum
        recall = 1
    else:
        precision = 1
        recall = recVehicleNum/gtVehiclesNum
    
    print(f'Precision:{precision}')
    print(f'Recall:{recall}')
    print(f"Number of vehicles on the video:{gtVehiclesNum}")
    print(f"Number of vehicles detected by algorithm:{recVehicleNum}")