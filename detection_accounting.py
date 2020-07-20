
import numpy as np

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
        self.LP_measurements = []
        self.LP_recognized = False

    def update_location(self,p_X1, p_Y1, p_X2, p_Y2):
        self.last_location_x1 = p_X1
        self.last_location_y1 = p_Y1
        self.last_location_x2 = p_X2
        self.last_location_y2 = p_Y2

    def update_LP(self,p_measurement):
        self.LP_measurements.append(p_measurement)

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
        object detected in this frame - frame_detections(dict): {key_id(=tracker_id): [x1,y1,x2,y2]   #######,[LicensePlateRecords],class,secondary_class]}
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

        # update location information
        self.objects_buffers[obj_id].update_location(frame_detections[obj_id][0],frame_detections[obj_id][1],frame_detections[obj_id][2],frame_detections[obj_id][3])
        # update location information
        #self.objects_buffer[obj_id].update_LP(frame_detections[obj_id][1])

    def print_objects_buffers(self):
        print('Objects buffer:')
        for key in self.objects_buffers:
            print("{0}:{1}".format(key,self.objects_buffers[key].last_location_x1))


        

