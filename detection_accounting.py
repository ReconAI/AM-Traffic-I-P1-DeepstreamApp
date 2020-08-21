import datetime
import numpy as np

from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

from collections import Counter

from deepstream_config import *

def GetTrueLPRecord(p_LP_Array): #['ZLV275','ZLY275','ZLY27S']
    LP_char_Array = []
    
    for v_lp in p_LP_Array:
        LP_char_Array.append(list(v_lp))
    
    LP_char_Array_t = list(map(list, zip(*LP_char_Array)))
    
    output_LP = '' ##AAA000
    
    for idx,v_char_list in enumerate(LP_char_Array_t):
        cnt = Counter(v_char_list)
        
        most_common_list = cnt.most_common()
        
        char_candidate = ''
        
        for v_char,_ in most_common_list:
            if idx<3:
                if v_char.isalpha():
                    char_candidate = v_char
                    break
                else: #is numeric
                    if (v_char == '1'):
                        char_candidate = 'I'
                    elif (v_char == '5'):
                        char_candidate = 'S'
                    elif (v_char == '0'):
                        char_candidate = 'O'
                    else:
                         char_candidate = ''
                    break
            else:
                if (not v_char.isalpha()):
                    char_candidate = v_char
                    break
                else: #is alpha
                    if (v_char == 'I'):
                        char_candidate = '1'
                    elif (v_char == 'S'):
                        char_candidate = '5'
                    elif (v_char == 'O'):
                        char_candidate = '0'
                    elif (v_char == 'D'):
                        char_candidate = '0'
                    else:
                         char_candidate = ''
                    break
            
        if (char_candidate == ''):
            char_candidate,_ = most_common_list[0]
        
        output_LP += char_candidate
        
    return True, output_LP

class LicensePlateRecord():
    def __init__(self, text, matches_template, confidence):
        self.text = text
        self.matches_template = matches_template
        self.confidence = confidence

class ExitPoint():
    def __init__(self, label, X, Y, W, classes_stats):
        self.label = label # -1;0;1...
        self.X = X
        self.Y = Y
        self.W = W #number of objects
        self.classes_stats = classes_stats #dict with {obj_class:num_of_objects}

    def toString(self):
        return f"{self.label}:{self.X}:{self.Y}:{self.W}:{self.classes_stats}"

    def printExitPoint(self):
        print(self.toString())

class TrafficStats():

    def __init__(self, start_dt, end_dt, traffic_points):
        self.start_dt = start_dt
        self.end_dt = end_dt
        self.traffic_points = traffic_points #list of ExitPoint's
        
    def printStats(self):
        print('Traffic Stats:')
        print('Timeframe between: {0} and {1}'.format(self.start_dt,self.end_dt))
        
        for x in self.traffic_points:
            x.printExitPoint()

        print(f"Number of Exit points: {len(self.traffic_points)}")

class DetectionObject():

    def __init__(self, key_id, pgie_id, sgie_id):

        self.age = 0

        self.key_id = key_id

        self.pgie_id = pgie_id
        
        self.sgie_id_recognized = False
        self.sgie_id = sgie_id

        if (sgie_id != -1):
            self.sgie_id_recognized = True
        
        self.last_location_x1 = -1
        self.last_location_y1 = -1
        self.last_location_x2 = -1
        self.last_location_y2 = -1

        self.last_lp_location_x1 = -1
        self.last_lp_location_y1 = -1
        self.last_lp_location_x2 = -1
        self.last_lp_location_y2 = -1

        self.LP_measurements = []
        self.LP_measurement_samples = 0
        self.LP_recognized = False
        self.LP_record = None

    def update_primary_class(self, p_pgie_id):
        if (self.pgie_id == -1):
            self.pgie_id = p_pgie_id

    def update_secondary_class(self, p_sgie_id):
        if ((not self.sgie_id_recognized) and p_sgie_id != -1):
            self.sgie_id = p_sgie_id
            self.sgie_id_recognized = True
            
    #Top, bottom, left, right
    def update_location(self,p_X1, p_X2, p_Y1, p_Y2):
        self.age += 1

        self.last_location_x1 = p_X1
        self.last_location_y1 = p_Y1
        self.last_location_x2 = p_X2
        self.last_location_y2 = p_Y2

    def update_lp_location(self,p_X1, p_X2, p_Y1, p_Y2):
        if (min(p_X1, p_X2, p_Y1, p_Y2) != -1):
            self.last_lp_location_x1 = p_X1
            self.last_lp_location_y1 = p_Y1
            self.last_lp_location_x2 = p_X2
            self.last_lp_location_y2 = p_Y2

    def update_LP(self,p_measurement):
        if (len(p_measurement)>0):
            self.LP_measurements = self.LP_measurements + p_measurement
            self.LP_measurement_samples = self.LP_measurement_samples + 1

            if (self.LP_measurement_samples % MIN_NUMBER_OF_LP_SAMPLES == 0):
                self.getLPInfo()

    def getLPInfo(self):
        v_success, LP_rec = GetTrueLPRecord(self.LP_measurements)

        if (v_success):
            self.LP_record = LP_rec
            self.LP_recognized = True

class DetectionAccountant():

    def __init__(self, absense_interval):
        '''
            Parameters:
            candidate_interval - min number of objects lifetime frames so it would be added to objects_buffer
            absense_interval - min number of object lifietime frames to be considered absent
        '''
        
        self.absense_interval = absense_interval

        self.objects_buffers = {} #dict of key_ids; list of DetectionObjects.key_ids (=tracker ids) for ease of access
        self.absence_count = {} #dict of ints; absense counter for objects_buffer #->absense_interval
        self.archive_buffer = [] #dict of DetectionObjects; buffer where we put all absent DetectionObjects

        self.archive_update_df = datetime.datetime.now()
        
        self.traffic_stats = None

    def process_next_frame(self, frame_detections):
        '''
        Updates buffer

        Params:
        object detected in this frame - frame_detections(dict): {key_id(=tracker_id): [[x1,y1,x2,y2], [lp_x1,lp_y1,lp_x2,lp_y2], ,['ZLV275','ZLY275','ZLY27S'],pgie_class,sgie_class]}
        '''

        objs_to_archive = []
        # go over current objects buffer
        for obj_id in self.objects_buffers:
            #if object doesn't exist in current detections
            if obj_id not in frame_detections:
                # if object is already missing
                if obj_id in self.absence_count:
                    objs_to_archive = self.update_missing_object(obj_id, objs_to_archive)
                # if object just missed
                else:
                    self.absence_count[obj_id] = 1
            # if object exist in current detection
            else:
                # update object status
                self.update_present_object(obj_id, frame_detections)
                # delete record from detections
                del frame_detections[obj_id]

        for v_detection in frame_detections:
            self.objects_buffers[v_detection] = DetectionObject(v_detection, -1, -1)
            self.update_present_object(v_detection, frame_detections)

        for obj_id in objs_to_archive:

            #if object has big enough lifetime (age)
            if (self.objects_buffers[obj_id].age >= MIN_DETECTION_AGE):
                if (self.objects_buffers[obj_id].LP_measurement_samples>0):
                    self.objects_buffers[obj_id].getLPInfo()
                self.archive_buffer.append(self.objects_buffers[obj_id])
            del self.objects_buffers[obj_id]
        
    def update_missing_object(self, obj_id, objs_to_archive):
        '''increment missing counters, drop objects that are away for long'''
        self.absence_count[obj_id] += 1
        if self.absence_count[obj_id] == self.absense_interval:
            # been missing for long, forget it
            objs_to_archive.append(obj_id)
        return objs_to_archive

    def update_present_object(self, obj_id, p_frame_detections):
        '''Drop abscense counter, '''
        if obj_id in self.absence_count:
            # was missing, reset its missing counter
            self.absence_count[obj_id] = 0

        location_array = p_frame_detections[obj_id][0]
        lp_location_array = p_frame_detections[obj_id][1]
        lp_array = p_frame_detections[obj_id][2]
        base_class = p_frame_detections[obj_id][3]
        secondary_class = p_frame_detections[obj_id][4]

        # update primary class
        self.objects_buffers[obj_id].update_primary_class(base_class)

        # update secondary class
        self.objects_buffers[obj_id].update_secondary_class(secondary_class)

        # update location information
        self.objects_buffers[obj_id].update_location(location_array[0],location_array[1],location_array[2],location_array[3])

        # update license plate location information
        self.objects_buffers[obj_id].update_lp_location(lp_location_array[0],lp_location_array[1],lp_location_array[2],lp_location_array[3])
        
        #lp_json = json.loads(p_frame_detections[obj_id][2])
        self.objects_buffers[obj_id].update_LP(lp_array)

    def archive_all_object_buffer(self):
        for key in self.objects_buffers:
            #if object has big enough lifetime (age)
            if (self.objects_buffers[key].age >= MIN_DETECTION_AGE):
                if (self.objects_buffers[key].LP_measurement_samples>0):
                    self.objects_buffers[key].getLPInfo()
                self.archive_buffer.append(self.objects_buffers[key])
            
        self.objects_buffers = {}

    def get_objects_buffers(self):
        return list(self.objects_buffers.values())

    def print_objects_buffers(self):
        print('Objects buffer:')
        for key in self.objects_buffers:
            v_buffer_object = self.objects_buffers[key]

            lp_data = ''
            if (v_buffer_object.LP_recognized):
                lp_data = v_buffer_object.LP_record

            print("{0}:[{1},{2},{3},{4}],[{5},{6},{7},{8}]:{9}:{10}:{11}".format(key,v_buffer_object.last_location_x1,v_buffer_object.last_location_y1,v_buffer_object.last_location_x2,v_buffer_object.last_location_y2,
                v_buffer_object.last_lp_location_x1,v_buffer_object.last_lp_location_y1,v_buffer_object.last_lp_location_x2,v_buffer_object.last_lp_location_y2,lp_data,
                PGIE1_LABELS_DICT[v_buffer_object.pgie_id],
                SGIE_LABELS_DICT[v_buffer_object.sgie_id]
                ))
            

    def print_archve_buffer(self):
        print('Archive Buffer:')
        print('Len: {0}'.format(len(self.archive_buffer)))
        if (len(self.archive_buffer)>0):
            v_buffer_object = self.archive_buffer[-1]

            lp_data = ''
            if (v_buffer_object.LP_recognized):
                lp_data = v_buffer_object.LP_record

            print("{0}:[{1},{2},{3},{4}],[{5},{6},{7},{8}]:{9}:{10}:{11}".format(v_buffer_object.key_id ,v_buffer_object.last_location_x1,v_buffer_object.last_location_y1,v_buffer_object.last_location_x2,v_buffer_object.last_location_y2,
                v_buffer_object.last_lp_location_x1,v_buffer_object.last_lp_location_y1,v_buffer_object.last_lp_location_x2,v_buffer_object.last_lp_location_y2,lp_data,
                PGIE1_LABELS_DICT[v_buffer_object.pgie_id],
                SGIE_LABELS_DICT[v_buffer_object.sgie_id]
                ))

    def calculate_traffic_stats(self, use_prev_traffic_stats=True):

        print('Clustering in progress')
        points = []
        obj_types = []
        
        if (use_prev_traffic_stats):
            current_traffic_points = []

            if (self.traffic_stats is not None):
                current_traffic_points = self.traffic_stats.traffic_points
            
            for v_ExitPoint in current_traffic_points:
                for v_key in v_ExitPoint.classes_stats:
                    for i in range(0,int(v_ExitPoint.classes_stats[v_key])):
                        points.append([v_ExitPoint.X,v_ExitPoint.Y])
                        obj_types.append(v_key)

        for v_archive_item in self.archive_buffer:
            X = int(v_archive_item.last_location_x1 + (v_archive_item.last_location_x2-v_archive_item.last_location_x1)/2)
            Y = int(v_archive_item.last_location_y1 + (v_archive_item.last_location_y2-v_archive_item.last_location_y1)/2)
            points.append([X,Y])

            if (v_archive_item.pgie_id == PGIE_CLASS_ID_VEHICLE and v_archive_item.sgie_id != -1) :
                obj_types.append(SGIE_LABELS_DICT[v_archive_item.sgie_id])
            else:
                obj_types.append(PGIE1_LABELS_DICT[v_archive_item.pgie_id])

        points_scaled = StandardScaler().fit_transform(points)

        print(f"Len points:{len(points)}")
        print(f"Len points:{len(points_scaled)}")
        
        db = DBSCAN(eps=DBSCAN_EPSILON, min_samples=DBSCAN_SAMPLES, p=2, metric='minkowski').fit(points_scaled)

        labels = db.labels_

        traffic_points = []

        points_dict = {}
        weights_dict = {}
        obj_types_dict = {}

        cnt_i = 0
        for label, obj_type in zip(labels, obj_types):
            if label == -1:
                x,y = points[cnt_i]
                traffic_points.append(ExitPoint(label,x,y,1,{obj_type:1}))
            else:
                #put x,y,obj_type in corresponding dict
                if label not in points_dict:
                    weights_dict[label] = 0
                    points_dict[label] = []
                    obj_types_dict[label] = []

                weights_dict[label] += 1
                points_dict[label].append(points[cnt_i])
                obj_types_dict[label].append(obj_type)

            cnt_i += 1

        for v_key in points_dict:
            points_arr = points_dict[v_key]
            weight = weights_dict[v_key]
            obj_types_arr = obj_types_dict[v_key]
            
            x = [p[0] for p in points_arr]
            y = [p[1] for p in points_arr]
            centroid = (int(sum(x) / len(points_arr)), int(sum(y) / len(points_arr)))

            #apply counter
            statistics_dict = Counter(obj_types_arr)

            traffic_points.append(ExitPoint(v_key,centroid[0],centroid[1],weight,statistics_dict))

        v_dt_now = datetime.datetime.now()
        arch_upd_dt = self.archive_update_df
        self.archive_update_df = v_dt_now
        
        self.traffic_stats = TrafficStats(arch_upd_dt,v_dt_now,traffic_points)

        return self.traffic_stats
        
    def clear_archive_buffer(self):
        self.archive_buffer = []

    def get_archive_buffer(self):
        return self.archive_buffer



        

