# License plate comparison script
# Input:
# CorrectLicensePlates.txt - list of ground truth license plates from a video
## 
# RecognizedLicensePlates.txt - list of recognized license plates after a video processing
# Output:
# Detection statistics

#Usage:
# python test_trafficstatistics.py --gtLP=../data/validLPs.txt --recLP=../data/testLPs_tracker1.txt

import os
import argparse

def compareLPs(plate1, plate2):
    if (len(plate1) != len(plate2)):
        return -1

    n_matches = 0
    for a,b in zip(plate1,plate2):
        if a == b:
            n_matches += 1
    
    return n_matches

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='License plate comparison script')
    parser.add_argument('--gtLP', dest='file_gtLP', help='Path to a file with correct license plates')
    parser.add_argument('--recLP', dest='file_recLP', help='Path to a file with license plate recognitions')

    args = parser.parse_args()

    file_gtLP = args.file_gtLP
    file_recLP = args.file_recLP

    print(f"Comparing GT data: {file_gtLP} with recognitions: {file_recLP}")
    
    f = open(file_gtLP, "r")
    list_gtLPs = f.read().splitlines()
    f.close() 

    f = open(file_recLP, "r")
    list_recLPs = f.read().splitlines()
    f.close() 
