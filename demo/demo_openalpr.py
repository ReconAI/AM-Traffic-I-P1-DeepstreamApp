# test openalpr speed on full-size images
# $ python3 demo_openalpr.py

import numpy as np
import cv2
from openalpr import Alpr
import os

global_alpr_engine = Alpr("eu", "/etc/openalpr/openalpr.conf", "/usr/share/openalpr/runtime_data")

global_alpr_engine.set_top_n(10)
global_alpr_engine.set_default_region("fi")

images_list = ['lp_test_image_1.png','lp_test_image_2.png','lp_test_image_3.png','lp_test_image_4.png']
images_path = '../data'

for v_img in images_list:
    img_path = os.path.join(images_path, v_img)
    image = cv2.imread(img_path)
    print(f"Image:{v_img}")
    print(global_alpr_engine.recognize_ndarray(image))
