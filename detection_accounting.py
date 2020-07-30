import numpy as np
from collections import Counter

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
            else:
                if (not v_char.isalpha()):
                    char_candidate = v_char
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

class DetectionObject():

    def __init__(self, key_id, pgie_id, sgie_ids):
        self.key_id = key_id
        self.pgie_id = pgie_id
        self.sgie_ids = sgie_ids
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

    #Top, bottom, left, right
    def update_location(self,p_X1, p_X2, p_Y1, p_Y2):
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
        if ((not self.LP_recognized) and len(p_measurement)>0):
            self.LP_measurements = self.LP_measurements + p_measurement
            self.LP_measurement_samples = self.LP_measurement_samples + 1

            if (self.LP_measurement_samples>=3):
                
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
        
    def process_next_frame(self, frame_detections):
        '''
        Updates buffer

        Params:
        object detected in this frame - frame_detections(dict): {key_id(=tracker_id): [[x1,y1,x2,y2], [lp_x1,lp_y1,lp_x2,lp_y2], ,['ZLV275','ZLY275','ZLY27S'],class,[secondary_class_list]]}
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

        for detection in frame_detections:
            self.objects_buffers[detection] = DetectionObject(detection, 0, 0)
            self.update_present_object(detection, frame_detections)

        for obj_id in objs_to_archive:
            self.archive_buffer.append(self.objects_buffers[obj_id])
            del self.objects_buffers[obj_id]
        
    def update_missing_object(self, obj_id, objs_to_archive):
        '''increment missing counters, drop objects that are away for long'''
        self.absence_count[obj_id] += 1
        if self.absence_count[obj_id] == self.absense_interval:
            # been missing for long, forget it
            objs_to_archive.append(obj_id)
        return objs_to_archive

    def update_present_object(self, obj_id, frame_detections):
        '''Drop abscense counter, '''
        if obj_id in self.absence_count:
            # was missing, reset its missing counter
            self.absence_count[obj_id] = 0

        location_array = frame_detections[obj_id][0]
        lp_location_array = frame_detections[obj_id][1]
        
        # update location information
        self.objects_buffers[obj_id].update_location(location_array[0],location_array[1],location_array[2],location_array[3])

        # update license plate location information
        self.objects_buffers[obj_id].update_lp_location(lp_location_array[0],lp_location_array[1],lp_location_array[2],lp_location_array[3])
        
        # update license plate information
        lp_array = frame_detections[obj_id][2]
        #lp_json = json.loads(frame_detections[obj_id][2])
        self.objects_buffers[obj_id].update_LP(lp_array)

    def get_objects_buffers(self):
        return list(self.objects_buffers.values())

    def print_objects_buffers(self):
        print('Objects buffer:')
        for key in self.objects_buffers:
            v_buffer_object = self.objects_buffers[key]

            lp_data = ''
            if (v_buffer_object.LP_recognized):
                lp_data = v_buffer_object.LP_record

            print("{0}:[{1},{2},{3},{4}],[{5},{6},{7},{8}]:{9}".format(key,v_buffer_object.last_location_x1,v_buffer_object.last_location_y1,v_buffer_object.last_location_x2,v_buffer_object.last_location_y2,
                v_buffer_object.last_lp_location_x1,v_buffer_object.last_lp_location_y1,v_buffer_object.last_lp_location_x2,v_buffer_object.last_lp_location_y2,lp_data))
            
    def get_archive_buffer(self):
        return self.archive_buffer

    def clear_archive_buffer(self):
        self.archive_buffer = []


        

