#!/usr/bin/env python3

import sys
sys.path.append('../')
import platform
from common.FPS import GETFPS
import configparser

import gi
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import GObject, Gst, GstRtspServer
from gi.repository import GLib
from common.is_aarch_64 import is_aarch64
from common.bus_call import bus_call
from common.utils import long_to_int
import math
import json

import pyds

import random
import numpy as np
import cv2
from openalpr import Alpr
import os
import os.path

from common.FPS import GETFPS

from detection_accounting import *

#CONSTANTS and GLOBALs
APPLICATION_PATH = '/opt/nvidia/deepstream/deepstream-5.0/sources/python/apps/deepstream-amtraffic'

SAVE_IMAGES = False
PRINT_DEBUG = False

fps_streams={}

TILED_OUTPUT_WIDTH=1920
TILED_OUTPUT_HEIGHT=1080

PGIE_CLASS_ID_VEHICLE = 0
PGIE_CLASS_ID_BICYCLE = 1
PGIE_CLASS_ID_PERSON = 2
PGIE_CLASS_ID_ROADSIGN = 3

ALPR_FRAME_RATE = 10
MSQ_FRAME_RATE = 10

frame_n = 0
global_alpr_engine=None
global_detection_accountant=None

## MSQ settings
MAX_DISPLAY_LEN=64
MAX_TIME_STAMP_LEN=32

proto_lib = '/opt/nvidia/deepstream/deepstream/sources/libs/aws_protocol_adaptor/device_client/libnvds_aws_proto.so'
conn_str = 'a3qtghj8wcrl9r-ats.iot.eu-west-2.amazonaws.com;443;ds_app'
cfg_file = '/opt/nvidia/deepstream/deepstream/sources/libs/aws_protocol_adaptor/device_client/cfg_aws.txt'
topic = None
no_display = True
MSCONV_CONFIG_FILE="dstest4_msgconv_config.txt"
schema_type = 0


# Callback function for deep-copying an NvDsEventMsgMeta struct
def meta_copy_func(data,user_data):
    # Cast data to pyds.NvDsUserMeta
    user_meta=pyds.NvDsUserMeta.cast(data)
    src_meta_data=user_meta.user_meta_data
    # Cast src_meta_data to pyds.NvDsEventMsgMeta
    srcmeta=pyds.NvDsEventMsgMeta.cast(src_meta_data)
    # Duplicate the memory contents of srcmeta to dstmeta
    # First use pyds.get_ptr() to get the C address of srcmeta, then
    # use pyds.memdup() to allocate dstmeta and copy srcmeta into it.
    # pyds.memdup returns C address of the allocated duplicate.
    dstmeta_ptr=pyds.memdup(pyds.get_ptr(srcmeta), sys.getsizeof(pyds.NvDsEventMsgMeta))
    # Cast the duplicated memory to pyds.NvDsEventMsgMeta
    dstmeta=pyds.NvDsEventMsgMeta.cast(dstmeta_ptr)

    # Duplicate contents of ts field. Note that reading srcmeat.ts
    # returns its C address. This allows to memory operations to be
    # performed on it.
    dstmeta.ts=pyds.memdup(srcmeta.ts, MAX_TIME_STAMP_LEN+1)

    # Copy the sensorStr. This field is a string property.
    # The getter (read) returns its C address. The setter (write)
    # takes string as input, allocates a string buffer and copies
    # the input string into it.
    # pyds.get_string() takes C address of a string and returns
    # the reference to a string object and the assignment inside the binder copies content.
    dstmeta.sensorStr=pyds.get_string(srcmeta.sensorStr)

    if(srcmeta.objSignature.size>0):
        dstmeta.objSignature.signature=pyds.memdup(srcmeta.objSignature.signature,srcMeta.objSignature.size)
        dstmeta.objSignature.size = srcmeta.objSignature.size;

    if(srcmeta.extMsgSize>0):
        if(srcmeta.objType==pyds.NvDsObjectType.NVDS_OBJECT_TYPE_VEHICLE):
            srcobj = pyds.NvDsVehicleObject.cast(srcmeta.extMsg);
            obj = pyds.alloc_nvds_vehicle_object();
            obj.type=pyds.get_string(srcobj.type)
            obj.make=pyds.get_string(srcobj.make)
            obj.model=pyds.get_string(srcobj.model)
            obj.color=pyds.get_string(srcobj.color)
            obj.license = pyds.get_string(srcobj.license)
            obj.region = pyds.get_string(srcobj.region)
            dstmeta.extMsg = obj;
            dstmeta.extMsgSize = sys.getsizeof(pyds.NvDsVehicleObject)
        if(srcmeta.objType==pyds.NvDsObjectType.NVDS_OBJECT_TYPE_PERSON):
            srcobj = pyds.NvDsPersonObject.cast(srcmeta.extMsg);
            obj = pyds.alloc_nvds_person_object()
            obj.age = srcobj.age
            obj.gender = pyds.get_string(srcobj.gender);
            obj.cap = pyds.get_string(srcobj.cap)
            obj.hair = pyds.get_string(srcobj.hair)
            obj.apparel = pyds.get_string(srcobj.apparel);
            dstmeta.extMsg = obj;
            dstmeta.extMsgSize = sys.getsizeof(pyds.NvDsVehicleObject);

    return dstmeta

# Callback function for freeing an NvDsEventMsgMeta instance
def meta_free_func(data,user_data):
    user_meta=pyds.NvDsUserMeta.cast(data)
    srcmeta=pyds.NvDsEventMsgMeta.cast(user_meta.user_meta_data)

    # pyds.free_buffer takes C address of a buffer and frees the memory
    # It's a NOP if the address is NULL
    pyds.free_buffer(srcmeta.ts)
    pyds.free_buffer(srcmeta.sensorStr)

    if(srcmeta.objSignature.size > 0):
        pyds.free_buffer(srcmeta.objSignature.signature);
        srcmeta.objSignature.size = 0

    if(srcmeta.extMsgSize > 0):
        if(srcmeta.objType == pyds.NvDsObjectType.NVDS_OBJECT_TYPE_VEHICLE):
            obj =pyds.NvDsVehicleObject.cast(srcmeta.extMsg)
            pyds.free_buffer(obj.type);
            pyds.free_buffer(obj.color);
            pyds.free_buffer(obj.make);
            pyds.free_buffer(obj.model);
            pyds.free_buffer(obj.license);
            pyds.free_buffer(obj.region);
        if(srcmeta.objType == pyds.NvDsObjectType.NVDS_OBJECT_TYPE_PERSON):
            obj = pyds.NvDsPersonObject.cast(srcmeta.extMsg);
            pyds.free_buffer(obj.gender);
            pyds.free_buffer(obj.cap);
            pyds.free_buffer(obj.hair);
            pyds.free_buffer(obj.apparel);
        pyds.free_gbuffer(srcmeta.extMsg);
        srcmeta.extMsgSize = 0;

def generate_vehicle_meta(data):
    obj = pyds.NvDsVehicleObject.cast(data);
    obj.type ="sedan"
    obj.color="blue"
    obj.make ="Bugatti"
    obj.model = "M"
    obj.license ="XX1234"
    obj.region ="CA"
    return obj

def generate_person_meta(data):
    obj = pyds.NvDsPersonObject.cast(data)
    obj.age = 45
    obj.cap = "none"
    obj.hair = "black"
    obj.gender = "male"
    obj.apparel= "formal"
    return obj

def generate_event_msg_meta(data, class_id):
    meta =pyds.NvDsEventMsgMeta.cast(data)
    meta.sensorId = 0
    meta.placeId = 0
    meta.moduleId = 0
    meta.sensorStr = "sensor-0"
    meta.ts = pyds.alloc_buffer(MAX_TIME_STAMP_LEN + 1)
    pyds.generate_ts_rfc3339(meta.ts, MAX_TIME_STAMP_LEN)

    # This demonstrates how to attach custom objects.
    # Any custom object as per requirement can be generated and attached
    # like NvDsVehicleObject / NvDsPersonObject. Then that object should
    # be handled in payload generator library (nvmsgconv.cpp) accordingly.
    if(class_id==PGIE_CLASS_ID_VEHICLE):
        meta.type = pyds.NvDsEventType.NVDS_EVENT_MOVING
        meta.objType = pyds.NvDsObjectType.NVDS_OBJECT_TYPE_VEHICLE
        meta.objClassId = PGIE_CLASS_ID_VEHICLE
        obj = pyds.alloc_nvds_vehicle_object()
        obj = generate_vehicle_meta(obj)
        meta.extMsg = obj
        meta.extMsgSize = sys.getsizeof(pyds.NvDsVehicleObject);
    if(class_id == PGIE_CLASS_ID_PERSON):
        meta.type =pyds.NvDsEventType.NVDS_EVENT_ENTRY
        meta.objType = pyds.NvDsObjectType.NVDS_OBJECT_TYPE_PERSON;
        meta.objClassId = PGIE_CLASS_ID_PERSON
        obj = pyds.alloc_nvds_person_object()
        obj=generate_person_meta(obj)
        meta.extMsg = obj
        meta.extMsgSize = sys.getsizeof(pyds.NvDsPersonObject)
    return meta

# Frame processing method
def osd_sink_pad_buffer_probe(pad,info,u_data):
    frame_number=0
    
    #Intiallizing object counter with 0.
    obj_counter = {
        PGIE_CLASS_ID_VEHICLE:0,
        PGIE_CLASS_ID_PERSON:0,
        PGIE_CLASS_ID_BICYCLE:0,
        PGIE_CLASS_ID_ROADSIGN:0
    }
    num_rects=0
    gst_buffer = info.get_buffer()
    if not gst_buffer:
        print("Unable to get GstBuffer ")
        return

    # Retrieve batch metadata from the gst_buffer
    # Note that pyds.gst_buffer_get_nvds_batch_meta() expects the
    # C address of gst_buffer as input, which is obtained with hash(gst_buffer)
    batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
    l_frame = batch_meta.frame_meta_list
    while l_frame is not None:
        try:
            # Note that l_frame.data needs a cast to pyds.NvDsFrameMeta
            # The casting is done by pyds.NvDsFrameMeta.cast()
            # The casting also keeps ownership of the underlying memory
            # in the C code, so the Python garbage collector will leave
            # it alone.
            frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
        except StopIteration:
            break

        frame_number=frame_meta.frame_num
        print("===")
        global frame_n
        frame_n = frame_n + 1
        num_rects = frame_meta.num_obj_meta
        l_obj=frame_meta.obj_meta_list
        is_first_obj = True
        
        detected_objects = {}

        while l_obj is not None:
            try:
                # Casting l_obj.data to pyds.NvDsObjectMeta
                obj_meta=pyds.NvDsObjectMeta.cast(l_obj.data)
            except StopIteration:
                break

            #get secondary classifier data
            l_classifier= obj_meta.classifier_meta_list
            classifier_class = ''
            if l_classifier is not None: # and class_id==XXX #apply classifier for a specific class
                classifier_meta=pyds.glist_get_nvds_classifier_meta(l_classifier.data)
                l_label=classifier_meta.label_info_list
                label_info=pyds.glist_get_nvds_label_info(l_label.data)
                classifier_class = label_info.result_class_id
                print("sgie class={0}".format(classifier_class))

            obj_counter[obj_meta.class_id] += 1
        
            if (frame_n % ALPR_FRAME_RATE == 0):
                print("obj_meta: object_id={0}; class_id={1}; classifier_class={2}".format(obj_meta.object_id,obj_meta.class_id,classifier_class))

                # Cv2 stuff
                if is_first_obj:
                    is_first_obj = False
                    # Getting Image data using nvbufsurface
                    # the input should be address of buffer and batch_id
                    n_frame=pyds.get_nvds_buf_surface(hash(gst_buffer),frame_meta.batch_id)
                    #convert python array into numy array format.
                    frame_image=np.array(n_frame,copy=True,order='C')
                    #covert the array into cv2 default color format
                    frame_image=cv2.cvtColor(frame_image,cv2.COLOR_RGBA2BGRA)

                    if (frame_n % MSQ_FRAME_RATE == 0):
                        msg_meta=pyds.alloc_nvds_event_msg_meta()
                        msg_meta.bbox.top =  obj_meta.rect_params.top
                        msg_meta.bbox.left =  obj_meta.rect_params.left
                        msg_meta.bbox.width = obj_meta.rect_params.width
                        msg_meta.bbox.height = obj_meta.rect_params.height
                        msg_meta.frameId = frame_number
                        msg_meta.trackingId = long_to_int(obj_meta.object_id)
                        msg_meta.confidence = obj_meta.confidence
                        msg_meta = generate_event_msg_meta(msg_meta, obj_meta.class_id)
                        user_event_meta = pyds.nvds_acquire_user_meta_from_pool(batch_meta)
                        if(user_event_meta):
                            user_event_meta.user_meta_data = msg_meta;
                            user_event_meta.base_meta.meta_type = pyds.NvDsMetaType.NVDS_EVENT_MSG_META
                            # Setting callbacks in the event msg meta. The bindings layer
                            # will wrap these callables in C functions. Currently only one
                            # set of callbacks is supported.
                            pyds.set_user_copyfunc(user_event_meta, meta_copy_func)
                            pyds.set_user_releasefunc(user_event_meta, meta_free_func)
                            pyds.nvds_add_user_meta_to_frame(frame_meta, user_event_meta)
                            print("Message attached")
                        else:
                            print("Error in attaching event meta to buffer\n")

                #recognize license plate data
                detected_objects[obj_meta.object_id] = recognize_license_plate(frame_image,obj_meta,obj_meta.confidence,frame_n)
                
            else:
                rect_params=obj_meta.rect_params
                top=int(rect_params.top)
                left=int(rect_params.left)
                width=int(rect_params.width)
                height=int(rect_params.height)

                detected_objects[obj_meta.object_id] = [[top,top+height,left,left+width], [], obj_meta.class_id]
            try: 
                l_obj=l_obj.next
            except StopIteration:
                break
        
        global global_detection_accountant
        print('Detected objects:')
        global_detection_accountant.process_next_frame(detected_objects)
        global_detection_accountant.print_objects_buffers()

        # Acquiring a display meta object. The memory ownership remains in
        # the C code so downstream plugins can still access it. Otherwise
        # the garbage collector will claim it when this probe function exits.
        display_meta=pyds.nvds_acquire_display_meta_from_pool(batch_meta)
        display_meta.num_labels = 1
        py_nvosd_text_params = display_meta.text_params[0]
        # Setting display text to be shown on screen
        # Note that the pyds module allocates a buffer for the string, and the
        # memory will not be claimed by the garbage collector.
        # Reading the display_text field here will return the C address of the
        # allocated string. Use pyds.get_string() to get the string content.
        py_nvosd_text_params.display_text = "Frame Number={} Number of Objects={}".format(frame_n, num_rects)

        # Now set the offsets where the string should appear
        py_nvosd_text_params.x_offset = 10
        py_nvosd_text_params.y_offset = 12

        # Font , font-color and font-size
        py_nvosd_text_params.font_params.font_name = "Serif"
        py_nvosd_text_params.font_params.font_size = 10
        # set(red, green, blue, alpha); set to White
        py_nvosd_text_params.font_params.font_color.set(1.0, 1.0, 1.0, 1.0)

        # Text background color
        py_nvosd_text_params.set_bg_clr = 1
        # set(red, green, blue, alpha); set to Black
        py_nvosd_text_params.text_bg_clr.set(0.0, 0.0, 0.0, 1.0)


        # Using pyds.get_string() to get display_text as string
        print(pyds.get_string(py_nvosd_text_params.display_text))

        pyds.nvds_add_display_meta_to_frame(frame_meta, display_meta)

        fps_streams["stream{0}".format(frame_meta.pad_index)].get_fps()

        try:
            l_frame=l_frame.next
        except StopIteration:
            break
    return Gst.PadProbeReturn.OK	

# RECOGNIZE LICENSE PLATES V1.0
def recognize_license_plate(image,obj_meta,confidence,p_frame_n):
    
    #Importing openalpr
    global global_alpr_engine
    
    #frame_number = random.randint(0, 100)
    rect_params=obj_meta.rect_params
    top=int(rect_params.top)
    left=int(rect_params.left)
    width=int(rect_params.width)
    height=int(rect_params.height)
    car_cutout = image[top:top+height,left:left+width,:]

    if (SAVE_IMAGES):
        cv2.imwrite("{0}/{1}_{2}_image.jpg".format(APPLICATION_PATH,p_frame_n,obj_meta.object_id),car_cutout)


    alrp_output = global_alpr_engine.recognize_ndarray(car_cutout)

    if ('results' in alrp_output and len(alrp_output['results'])>0):
        out_LP_array = []
        lp_detection = alrp_output['results'][0]

        if (PRINT_DEBUG):
            print('Main candidate:')
            print('{0}:{1}'.format(lp_detection['plate'],lp_detection['confidence']))
        
        if (len(lp_detection['plate'])==6):
            out_LP_array.append(lp_detection['plate'])

        lp_candidates = lp_detection['candidates']
        template_match = [x for x in lp_candidates if x['matches_template'] == 1]
        if (len(template_match)>0):
            if (PRINT_DEBUG):
                print('Match candidates:')

            for v_item in template_match[:2]:
                out_LP_array.append(v_item['plate'])
                
                if (PRINT_DEBUG):
                    print('{0}:{1}'.format(v_item['plate'],v_item['confidence']))

        else:
            template_no_match = [x for x in lp_candidates if (x['matches_template'] == 0 and len(x['plate'])==6)]
            if (len(template_no_match)>0):
                if (PRINT_DEBUG):
                    print('Unmatch candidates:')

                for v_item in template_no_match[:2]:
                    out_LP_array.append(v_item['plate'])

                    if (PRINT_DEBUG):
                        print('{0}:{1}'.format(v_item['plate'],v_item['confidence']))

        return [[top,top+height,left,left+width], out_LP_array, obj_meta.class_id]
    else:
        return [[top,top+height,left,left+width], [], -1]


def draw_bounding_boxes(image,obj_meta,confidence):
    confidence='{0:.2f}'.format(confidence)
    rect_params=obj_meta.rect_params
    top=int(rect_params.top)
    left=int(rect_params.left)
    width=int(rect_params.width)
    height=int(rect_params.height)
    obj_name = str(obj_meta.class_id)
    #obj_name=pgie_classes_str[obj_meta.class_id]
    image=cv2.rectangle(image,(left,top),(left+width,top+height),(0,0,255,0),2)
    # Note that on some systems cv2.putText erroneously draws horizontal lines across the image
    image=cv2.putText(image,obj_name+',C='+str(confidence),(left-10,top-10),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255,0),2)
    return image

def cb_newpad(decodebin, decoder_src_pad,data):
    print("In cb_newpad\n")
    caps=decoder_src_pad.get_current_caps()
    gststruct=caps.get_structure(0)
    gstname=gststruct.get_name()
    source_bin=data
    features=caps.get_features(0)

    # Need to check if the pad created by the decodebin is for video and not
    # audio.
    print("gstname=",gstname)
    if(gstname.find("video")!=-1):
        # Link the decodebin pad only if decodebin has picked nvidia
        # decoder plugin nvdec_*. We do this by checking if the pad caps contain
        # NVMM memory features.
        print("features=",features)
        if features.contains("memory:NVMM"):
            # Get the source bin ghost pad
            bin_ghost_pad=source_bin.get_static_pad("src")
            if not bin_ghost_pad.set_target(decoder_src_pad):
                sys.stderr.write("Failed to link decoder src pad to source bin ghost pad\n")
        else:
            sys.stderr.write(" Error: Decodebin did not pick nvidia decoder plugin.\n")

def decodebin_child_added(child_proxy,Object,name,user_data):
    print("Decodebin child added:", name, "\n")
    if(name.find("decodebin") != -1):
        Object.connect("child-added",decodebin_child_added,user_data)   
    if(is_aarch64() and name.find("nvv4l2decoder") != -1):
        print("Seting bufapi_version\n")
        Object.set_property("bufapi-version",True)

def create_source_bin(index,uri):
    print("Creating source bin")

    # Create a source GstBin to abstract this bin's content from the rest of the
    # pipeline
    bin_name="source-bin-%02d" %index
    print(bin_name)
    nbin=Gst.Bin.new(bin_name)
    if not nbin:
        sys.stderr.write(" Unable to create source bin \n")

    # Source element for reading from the uri.
    # We will use decodebin and let it figure out the container format of the
    # stream and the codec and plug the appropriate demux and decode plugins.
    uri_decode_bin=Gst.ElementFactory.make("uridecodebin", "uri-decode-bin")
    if not uri_decode_bin:
        sys.stderr.write(" Unable to create uri decode bin \n")
    # We set the input uri to the source element
    uri_decode_bin.set_property("uri",uri)
    # Connect to the "pad-added" signal of the decodebin which generates a
    # callback once a new pad for raw data has beed created by the decodebin
    uri_decode_bin.connect("pad-added",cb_newpad,nbin)
    uri_decode_bin.connect("child-added",decodebin_child_added,nbin)

    # We need to create a ghost pad for the source bin which will act as a proxy
    # for the video decoder src pad. The ghost pad will not have a target right
    # now. Once the decode bin creates the video decoder and generates the
    # cb_newpad callback, we will set the ghost pad target to the video decoder
    # src pad.
    Gst.Bin.add(nbin,uri_decode_bin)
    bin_pad=nbin.add_pad(Gst.GhostPad.new_no_target("src",Gst.PadDirection.SRC))
    if not bin_pad:
        sys.stderr.write(" Failed to add ghost pad in source bin \n")
        return None
    return nbin

# Main method
def main(args):
    # Check input arguments
    if len(args) < 2:
        sys.stderr.write("usage: %s <uri1> [uri2] ... [uriN]\n" % args[0])
        sys.exit(1)

    
    global global_detection_accountant
    global_detection_accountant=DetectionAccountant(15)

    global global_alpr_engine
    global_alpr_engine = Alpr("eu", "/etc/openalpr/openalpr.conf", "/usr/share/openalpr/runtime_data")

    if not global_alpr_engine.is_loaded():
        print("Error loading OpenALPR")
        sys.exit(1)

    global_alpr_engine.set_top_n(10)
    global_alpr_engine.set_default_region("fi")

    for i in range(0,len(args)-1):
        fps_streams["stream{0}".format(i)]=GETFPS(i)
    number_sources=len(args)-1

    # Standard GStreamer initialization
    GObject.threads_init()
    Gst.init(None)

    # Create gstreamer elements
    # Create Pipeline element that will form a connection of other elements
    print("Creating Pipeline \n ")
    pipeline = Gst.Pipeline()
    is_live = False

    if not pipeline:
        sys.stderr.write(" Unable to create Pipeline \n")
    print("Creating streamux \n ")

    #READ RTSP/MP4 STREAM
    # Create nvstreammux instance to form batches from one or more sources.
    streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
    if not streammux:
        sys.stderr.write(" Unable to create NvStreamMux \n")

    pipeline.add(streammux)
    #NOTE: number_sources is important!!!
    for i in range(number_sources):
        print("Creating source_bin ",i," \n ")
        uri_name=args[i+1]
        if uri_name.find("rtsp://") == 0 :
            is_live = True
        source_bin=create_source_bin(i, uri_name)
        if not source_bin:
            sys.stderr.write("Unable to create source bin \n")
        pipeline.add(source_bin)
        padname="sink_%u" %i
        sinkpad= streammux.get_request_pad(padname) 
        if not sinkpad:
            sys.stderr.write("Unable to create sink pad bin \n")
        srcpad=source_bin.get_static_pad("src")
        if not srcpad:
            sys.stderr.write("Unable to create src pad bin \n")
        srcpad.link(sinkpad)
    print("Creating Pgie \n ")

    #PRIMARY NEURAL NETWORK
    # Use nvinfer to run inferencing on decoder's output,
    # behaviour of inferencing is set through config file
    pgie1 = Gst.ElementFactory.make("nvinfer", "primary-inference-1")
    if not pgie1:
        sys.stderr.write(" Unable to create pgie1 \n")

    #TRACKER
    tracker = Gst.ElementFactory.make("nvtracker", "tracker")
    if not tracker:
        sys.stderr.write(" Unable to create tracker \n")

    #SECONDARY NEURAL NETWORK
    sgie = Gst.ElementFactory.make("nvinfer", "secondary1-nvinference-engine")
    if not sgie:
        sys.stderr.write(" Unable to make sgie \n")

    tiler=Gst.ElementFactory.make("nvmultistreamtiler", "nvtiler")
    if not tiler:
        sys.stderr.write(" Unable to create tiler \n")
    print("Creating nvvidconv \n ")

    nvvidconv = Gst.ElementFactory.make("nvvideoconvert", "convertor")
    if not nvvidconv:
        sys.stderr.write(" Unable to create nvvidconv \n")

    # Create OSD to draw on the converted RGBA buffer
    nvosd = Gst.ElementFactory.make("nvdsosd", "onscreendisplay")
    if not nvosd:
        sys.stderr.write(" Unable to create nvosd \n")

    tee=Gst.ElementFactory.make("tee", "nvsink-tee")
    if not tee:
        sys.stderr.write(" Unable to create tee \n")

    queue1=Gst.ElementFactory.make("queue", "nvtee-que1")
    if not queue1:
        sys.stderr.write(" Unable to create queue1 \n")

    queue2=Gst.ElementFactory.make("queue", "nvtee-que2")
    if not queue2:
        sys.stderr.write(" Unable to create queue2 \n")

    nvvidconv_postosd = Gst.ElementFactory.make("nvvideoconvert", "convertor_postosd")
    if not nvvidconv_postosd:
        sys.stderr.write(" Unable to create nvvidconv_postosd \n")

    # Create a caps filter
    caps = Gst.ElementFactory.make("capsfilter", "filter")
    caps.set_property("caps", Gst.Caps.from_string("video/x-raw(memory:NVMM), format=I420"))
    
    # Make the encoder
    if codec == "H264":
        encoder = Gst.ElementFactory.make("nvv4l2h264enc", "encoder")
        print("Creating H264 Encoder")
    elif codec == "H265":
        encoder = Gst.ElementFactory.make("nvv4l2h265enc", "encoder")
        print("Creating H265 Encoder")
    if not encoder:
        sys.stderr.write(" Unable to create encoder")
    encoder.set_property('bitrate', bitrate)
    if is_aarch64():
        encoder.set_property('preset-level', 1)
        encoder.set_property('insert-sps-pps', 1)
        encoder.set_property('bufapi-version', 1)
    
    # Make the payload-encode video into RTP packets
    if codec == "H264":
        rtppay = Gst.ElementFactory.make("rtph264pay", "rtppay")
        print("Creating H264 rtppay")
    elif codec == "H265":
        rtppay = Gst.ElementFactory.make("rtph265pay", "rtppay")
        print("Creating H265 rtppay")
    if not rtppay:
        sys.stderr.write(" Unable to create rtppay")

    msgconv=Gst.ElementFactory.make("nvmsgconv", "nvmsg-converter")
    if not msgconv:
        sys.stderr.write(" Unable to create msgconv \n")

    msgbroker=Gst.ElementFactory.make("nvmsgbroker", "nvmsg-broker")
    if not msgbroker:
        sys.stderr.write(" Unable to create msgbroker \n")

    #RTSP SINK
    # Make the UDP sink
    updsink_port_num = 5400
    sink = Gst.ElementFactory.make("udpsink", "udpsink")
    if not sink:
        sys.stderr.write(" Unable to create udpsink")
    
    sink.set_property('host', '224.224.255.255')
    sink.set_property('port', updsink_port_num)
    sink.set_property('async', False)
    sink.set_property('sync', 1)
    
    if is_live:
        print("Atleast one of the sources is live")
        streammux.set_property('live-source', 1)

    streammux.set_property('width', 1920)
    streammux.set_property('height', 1080)
    streammux.set_property('batch-size', 1)
    streammux.set_property('batched-push-timeout', 4000000)
    
    #IK: set config file for each network
    #Set properties of pgie and sgie
    pgie1.set_property('config-file-path', "dstest2_pgie1_config.txt")
    sgie.set_property('config-file-path', "dstest2_sgie_config.txt")

    tiler.set_property("rows",1)
    tiler.set_property("columns",1)
    tiler.set_property("width", TILED_OUTPUT_WIDTH)
    tiler.set_property("height", TILED_OUTPUT_HEIGHT)

    #Set properties of tracker
    config = configparser.ConfigParser()
    config.read('dstest2_tracker_config.txt')
    config.sections()

    for key in config['tracker']:
        if key == 'tracker-width' :
            tracker_width = config.getint('tracker', key)
            tracker.set_property('tracker-width', tracker_width)
        if key == 'tracker-height' :
            tracker_height = config.getint('tracker', key)
            tracker.set_property('tracker-height', tracker_height)
        if key == 'gpu-id' :
            tracker_gpu_id = config.getint('tracker', key)
            tracker.set_property('gpu_id', tracker_gpu_id)
        if key == 'll-lib-file' :
            tracker_ll_lib_file = config.get('tracker', key)
            tracker.set_property('ll-lib-file', tracker_ll_lib_file)
        if key == 'll-config-file' :
            tracker_ll_config_file = config.get('tracker', key)
            tracker.set_property('ll-config-file', tracker_ll_config_file)
        if key == 'enable-batch-process' :
            tracker_enable_batch_process = config.getint('tracker', key)
            tracker.set_property('enable_batch_process', tracker_enable_batch_process)
    
    # Set message pipeline settings
    msgconv.set_property('config',MSCONV_CONFIG_FILE)
    msgconv.set_property('payload-type', schema_type)
    msgbroker.set_property('proto-lib', proto_lib)
    msgbroker.set_property('conn-str', conn_str)
    if cfg_file is not None:
        msgbroker.set_property('config', cfg_file)
    if topic is not None:
        msgbroker.set_property('topic', topic)
    msgbroker.set_property('sync', False)

    #PIPELINE POPULATION
    print("Adding elements to Pipeline \n")
    pipeline.add(streammux)
    pipeline.add(pgie1)
    pipeline.add(tracker)
    pipeline.add(sgie)
    pipeline.add(tiler)
    pipeline.add(nvvidconv)
    pipeline.add(nvosd)

    #Split pipeline on two queues using tee
    pipeline.add(tee)
    pipeline.add(queue1)
    pipeline.add(queue2)

    #RTPS Part
    pipeline.add(nvvidconv_postosd)
    pipeline.add(caps)
    pipeline.add(encoder)
    pipeline.add(rtppay)
    pipeline.add(sink)

    #Msg broker Part
    pipeline.add(msgconv)
    pipeline.add(msgbroker)

    #PIPELINE LINKAGE
    # we link the elements together
    # file-source -> h264-parser -> nvh264-decoder ->
    # nvinfer -> nvvidconv -> nvosd -> video-renderer
    print("Linking elements in the Pipeline \n")
    streammux.link(pgie1)
    pgie1.link(tracker)
    tracker.link(sgie)
    sgie.link(tiler)
    tiler.link(nvvidconv)
    nvvidconv.link(nvosd)
    nvosd.link(tee) #pipeline separation linkage pt.1
    
    #RTPS linkage
    queue2.link(nvvidconv_postosd)
    nvvidconv_postosd.link(caps)
    caps.link(encoder)
    encoder.link(rtppay)
    rtppay.link(sink)

    #Msg broker linkage
    queue1.link(msgconv)
    msgconv.link(msgbroker)

    #pipeline separation linkage pt.2

    sink_pad=queue1.get_static_pad("sink")

    tee_msg_pad=tee.get_request_pad('src_%u')
    tee_rtsp_pad=tee.get_request_pad("src_%u")
    if not tee_msg_pad or not tee_rtsp_pad:
        sys.stderr.write("Unable to get request pads\n")
    
    tee_msg_pad.link(sink_pad)

    sink_pad=queue2.get_static_pad("sink")
    tee_rtsp_pad.link(sink_pad)

    # create and event loop and feed gstreamer bus mesages to it
    loop = GObject.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect ("message", bus_call, loop)
    
    # Start streaming
    rtsp_port_num = 8554
    
    server = GstRtspServer.RTSPServer.new()
    server.props.service = "%d" % rtsp_port_num
    server.attach(None)

    factory = GstRtspServer.RTSPMediaFactory.new()
    factory.set_launch( "( udpsrc name=pay0 port=%d buffer-size=524288 caps=\"application/x-rtp, media=video, clock-rate=90000, encoding-name=(string)%s, payload=96 \" )" % (updsink_port_num, codec))
    factory.set_shared(True)
    server.get_mount_points().add_factory("/ds-test", factory)
    
    print("\n *** DeepStream: Launched RTSP Streaming at rtsp://localhost:%d/ds-test ***\n\n" % rtsp_port_num)
    
    # ASSIGN PROBE METHOD
    # Lets add probe to get informed of the meta data generated, we add probe to
    # the sink pad of the osd element, since by that time, the buffer would have
    # had got all the metadata.
    osdsink_pad = nvosd.get_static_pad("sink")
    if not osdsink_pad:
        sys.stderr.write(" Unable to get osd sink pad \n")
    else:
        #IK: Custom method call to display data on screen
        osdsink_pad.add_probe(Gst.PadProbeType.BUFFER, osd_sink_pad_buffer_probe, 0)

    print("Starting pipeline \n")
    
    # start play back and listed to events
    pipeline.set_state(Gst.State.PLAYING)
    try:
      loop.run()
    except:
      pass

    # cleanup
    pipeline.set_state(Gst.State.NULL)

def parse_args():
    global codec
    global bitrate
    codec = "H264"
    bitrate = 4000000
    return 0

if __name__ == '__main__':
    parse_args()
    sys.exit(main(sys.argv))

