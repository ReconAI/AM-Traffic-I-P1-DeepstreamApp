# License plate comparison script
# Input:
# CorrectLicensePlates.txt - list of ground truth license plates from a video
## 
# RecognizedLicensePlates.txt - list of recognized license plates after a video processing
# Output:
# Detection statistics

#Usage:
# python test_lpcomparison.py --gtLP=testdata/validLPs.txt --recLP=testdata/testLPs_tracker1.txt
# python test_lpcomparison.py --gtLP=testdata/validLPs.txt --recLP=testdata/testLPs_tracker2.txt

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

    set_gtLPs = set(list_gtLPs)
    set_recLPs = set(list_recLPs)

    len_gtLPs = len(set_gtLPs)
    len_recLPs = len(set_recLPs)

    set_matchLPs = set_recLPs.intersection(set_gtLPs)
    len_matchLPs = len(set_matchLPs)

    print(f"Ground Truth Length:{len_gtLPs}; Recognition Length {len_recLPs};")

    print(f">>Full-Match recognitions: {len_matchLPs} ( {round((len_matchLPs/len_gtLPs*100),2)}% )")

    set_gtLPs = set_gtLPs-set_matchLPs
    set_recLPs = set_recLPs-set_matchLPs

    matchesDict = {}

    for v_groundTruthLP in set_gtLPs:
        max_match = -2
        max_recognition = ''
        for v_recognizedLPs in set_recLPs:
            match_distance = compareLPs(v_groundTruthLP,v_recognizedLPs)

            if (match_distance>max_match):
                max_match = match_distance
                max_recognition = v_recognizedLPs

        if (max_match not in matchesDict):
            matchesDict[max_match] = []
        #matchesDict[max_match].append(f"{v_groundTruthLP}:{max_recognition}")
        matchesDict[max_match].append(f"{v_groundTruthLP}")

    len_OneCharMatchLPs = 0
    if (5 in matchesDict):
        len_OneCharMatchLPs = len(matchesDict[5])
    print(f">>1-Symbol-Diff recognitions: {len_OneCharMatchLPs} ( {round((len_OneCharMatchLPs/len_gtLPs*100),2)}% )")
    
    len_TwoCharMatchLPs = 0
    if (4 in matchesDict):
        len_TwoCharMatchLPs = len(matchesDict[4])
    print(f">>2-Symbol-Diff recognitions: {len_TwoCharMatchLPs} ( {round((len_TwoCharMatchLPs/len_gtLPs*100),2)}% )")

    len_ThreeCharMatchLPs = 0
    if (3 in matchesDict):
        len_ThreeCharMatchLPs = len(matchesDict[3])
    print(f">>3-Symbol-Diff recognitions: {len_ThreeCharMatchLPs} ( {round((len_ThreeCharMatchLPs/len_gtLPs*100),2)}% )")

    print(f">>Not recognized: {len_gtLPs-len_matchLPs-len_OneCharMatchLPs-len_TwoCharMatchLPs-len_ThreeCharMatchLPs} ( {round(((len_gtLPs-len_matchLPs-len_OneCharMatchLPs-len_TwoCharMatchLPs-len_ThreeCharMatchLPs)/len_gtLPs*100),2)}% )")
    print(f"Not recognized examples: {set_gtLPs - set(matchesDict[5]+matchesDict[4]+matchesDict[3])}")

    if (len_recLPs > len_gtLPs):
        print(f">>Extra recognitions: {len_recLPs - len_gtLPs}")
