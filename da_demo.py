import numpy as np

from detection_accounting import *

DETECTION_FRAMES = [
{'1': [1,1,1,1],'2': [1,1,1,1],'3': [1,1,1,1] },
{'1': [2,2,2,2],'2': [2,2,2,2],'3': [2,2,2,2] },
{'4': [3,3,3,3],'2': [3,3,3,3],'3': [3,3,3,3] },
{'4': [3,3,3,3],'2': [3,3,3,3],'3': [3,3,3,3] },
{'4': [3,3,3,3],'2': [3,3,3,3],'3': [3,3,3,3] },
{'4': [3,3,3,3],'2': [3,3,3,3],'3': [3,3,3,3] },
{'4': [3,3,3,3],'2': [3,3,3,3],'3': [3,3,3,3] },
{'5': [3,3,3,3],'6': [3,3,3,3],'7': [3,3,3,3] }]

DETECTION_ACCOUNTANT = DetectionAccountant(3)

for idx,frame_dict in enumerate(DETECTION_FRAMES):
    print("frame num=",idx)
    DETECTION_ACCOUNTANT.process_next_frame(frame_dict)
    DETECTION_ACCOUNTANT.print_objects_buffers()