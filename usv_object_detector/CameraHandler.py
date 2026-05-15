from rclpy.node import Node
from ament_index_python.packages import get_package_share_path
from object_msgs.msg import Object
from sensor_msgs.msg import Image
from sensor_msgs.msg import CompressedImage

import pyzed.sl as sl
import cv2
from cv_bridge import CvBridge

class CameraHandler:
    def __init__(self,*, node : Node, enable_display : bool, model : str):

        self.GREEN_BUOY_ID  = 0
        self.BOAT_ID        = 1
        self.RED_BUOY_ID    = 2
        self.YELLOW_BUOY_ID = 3
        
        self.LABEL_NAMES = {
        self.GREEN_BUOY_ID:  "Green Buoy",
        self.BOAT_ID:        "Boat",
        self.RED_BUOY_ID:    "Red Buoy",
        self.YELLOW_BUOY_ID: "Yellow Buoy"
    }
    
        self.node = node
        self.model = model
        self.display_enabled = enable_display
        self.init_camera_params()
        self.enable_positional_tracking()
        self.enable_object_detection()
        self.objects = []
        self.set_runtime_parameters()
        
        self.object_publisher = self.node.create_publisher(Object, "selene/object_detector/object", 10)

        if(self.display_enabled):
            self.node.get_logger().info("Image publisher is activated")
            self.image_publisher= self.node.create_publisher(CompressedImage,"selene/object_detector/image/compressed",10)
            self.bridge = CvBridge()

    
    def init_camera_params(self) -> None:

        # Init camera
        self.node.get_logger().info("Initializing camera parameters")
        self.zed = sl.Camera()
        self.init_params = sl.InitParameters()
        self.init_params.coordinate_units = sl.UNIT.METER
        self.init_params.camera_resolution = sl.RESOLUTION.HD720
        self.init_params.depth_mode = sl.DEPTH_MODE.NEURAL
        self.init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Z_UP_X_FWD
        self.init_params.depth_maximum_distance = 20

        self.node.get_logger().info("Opening camera")

        status = self.zed.open(self.init_params)

        if status != sl.ERROR_CODE.SUCCESS:
            self.node.get_logger().error("Camera Open: %s. Exit program.",{repr(status)})
            exit()

        self.camera_configuration = self.zed.get_camera_information().camera_configuration
        self.node.get_logger().info("Camera initialized")

    def enable_object_detection(self) -> None:
        self.model_path = get_package_share_path("usv_object_detector")/'models'/str(self.model)

        # Enable object detection module
        self.obj_param = sl.ObjectDetectionParameters()
        self.obj_param.detection_model = sl.OBJECT_DETECTION_MODEL.CUSTOM_YOLOLIKE_BOX_OBJECTS
        self.obj_param.custom_onnx_file = str(self.model_path)
        self.obj_param.enable_tracking = True
        self.obj_param.enable_segmentation = False
        status = self.zed.enable_object_detection(self.obj_param)
        if status != sl.ERROR_CODE.SUCCESS:
            #self.node.get_logger().error("Object Detection enable : %s. Exit program.",{repr(status)})
            self.zed.close()
            exit()
        self.node.get_logger().info("Enabling Object Detection... DONE")

        self.objects = sl.Objects()

    def enable_positional_tracking(self)-> None:
        positional_tracking_parameters = sl.PositionalTrackingParameters()
        status = self.zed.enable_positional_tracking(positional_tracking_parameters)
        if status > sl.ERROR_CODE.SUCCESS:
            print(f"Positional Tracking enable : {repr(status)}. Exit program.")
            self.zed.close()
            exit()
        self.node.get_logger().info("Enabling Positional Tracking... DONE")
        


    def set_runtime_parameters(self):
        self.runtime_parameters = sl.RuntimeParameters()
        self.runtime_parameters.confidence_threshold = 40
        self.detection_parameters_rt = sl.CustomObjectDetectionRuntimeParameters()

        self.props_dict = {
            self.GREEN_BUOY_ID: sl.CustomObjectDetectionProperties(),
            self.BOAT_ID: sl.CustomObjectDetectionProperties(),
            self.RED_BUOY_ID : sl.CustomObjectDetectionProperties(),
            self.YELLOW_BUOY_ID : sl.CustomObjectDetectionProperties()
        }

        #self.props_dict[self.GREEN_BUOY_ID].native_mapped_class = sl.OBJECT_SUBCLASS.SPORTSBALL
        #self.props_dict[self.GREEN_BUOY_ID].object_acceleration_preset = sl.OBJECT_ACCELERATION_PRESET.LOW
        self.props_dict[self.GREEN_BUOY_ID].detection_confidence_threshold = 60

        #self.props_dict[self.BOAT_ID].native_mapped_class = sl.OBJECT_SUBCLASS.BOAT
        #self.props_dict[self.BOAT_ID].object_acceleration_preset = sl.OBJECT_ACCELERATION_PRESET.MEDIUM
        self.props_dict[self.BOAT_ID].detection_confidence_threshold = 60

        #self.props_dict[self.RED_BUOY_ID].native_mapped_class = sl.OBJECT_SUBCLASS.SPORTSBALL
        #self.props_dict[self.RED_BUOY_ID].object_acceleration_preset = sl.OBJECT_ACCELERATION_PRESET.LOW
        self.props_dict[self.RED_BUOY_ID].detection_confidence_threshold = 60

        #self.props_dict[self.YELLOW_BUOY_ID].native_mapped_class = sl.OBJECT_SUBCLASS.SPORTSBALL
        #self.props_dict[self.YELLOW_BUOY_ID].object_acceleration_preset = sl.OBJECT_ACCELERATION_PRESET.LOW
        self.props_dict[self.YELLOW_BUOY_ID].detection_confidence_threshold = 60

        self.detection_parameters_rt.object_class_detection_properties = self.props_dict

    def run_object_detection(self)-> None:
        self.image = sl.Mat()
        self.depth_map = sl.Mat()
        self.objects = sl.Objects()
        while self.zed.grab(self.runtime_parameters) <= sl.ERROR_CODE.SUCCESS:
            status = self.zed.retrieve_custom_objects(self.objects, self.detection_parameters_rt)
            if status <= sl.ERROR_CODE.SUCCESS:
                self.zed.retrieve_image(self.image, sl.VIEW.LEFT) # Retrieve left image
                self.zed.retrieve_measure(self.depth_map, sl.MEASURE.DEPTH) # Retrieve depth

                image_opencv = self.image.get_data()
                if(self.objects.is_new):
                    obj_array = self.objects.object_list
                    for new_object in obj_array:
                        self.publish_object(
                            class_label=new_object.raw_label, 
                            pos_x=new_object.position[0],
                            pos_y=new_object.position[1],
                            pos_z=new_object.position[2]
                        )
                        
                        b_box = new_object.bounding_box_2d
                        cv2.rectangle(image_opencv,(int(b_box[0][0]), int(b_box[0][1])),(int(b_box[2][0]), int(b_box[2][1])),(0,0,255),2) # bgr
                        label_text = self.LABEL_NAMES.get(new_object.raw_label, "Unknown") + " ID:" + str(new_object.id) + " C:"+ str(round(new_object.confidence))
                        cv2.putText(image_opencv, label_text ,(int(b_box[0][0]), int(b_box[0][1])), cv2.FONT_HERSHEY_DUPLEX,1,(255,0,0),2)
                            
                if(self.display_enabled):
                    image_bgr = cv2.cvtColor(image_opencv, cv2.COLOR_BGRA2BGR)
                    _, encoded = cv2.imencode('.jpg', image_bgr, [cv2.IMWRITE_JPEG_QUALITY, 50])
            
                
                    msg = CompressedImage()
                    msg.header.stamp = self.node.get_clock().now().to_msg()
                    msg.format = "jpeg"
                    msg.data = encoded.tobytes()
                    self.image_publisher.publish(msg)

    def publish_object(self, *, class_label : int,  pos_x, pos_y , pos_z):
        match class_label:
            case self.GREEN_BUOY_ID:
                buoy = Object()
                buoy.type = "static"
                buoy.color = "green"
                buoy.header.stamp = self.node.get_clock().now().to_msg()
                buoy.position_x = pos_x; buoy.position_y = pos_y; buoy.position_z = pos_z;
                self.object_publisher.publish(buoy)

            case self.BOAT_ID:
                boat = Object()
                boat.type = "dynamic"
                boat.color = "unknown"
                boat.header.stamp = self.node.get_clock().now().to_msg()      
                boat.position_x = pos_x; boat.position_y = pos_y; boat.position_z = pos_z;
                self.object_publisher.publish(boat)

            case self.RED_BUOY_ID:
                buoy = Object()
                buoy.type = "static"
                buoy.color = "red"
                buoy.header.stamp = self.node.get_clock().now().to_msg()
                buoy.position_x = pos_x; buoy.position_y = pos_y; buoy.position_z = pos_z;
                self.object_publisher.publish(buoy)

            case self.YELLOW_BUOY_ID:
                buoy = Object()
                buoy.type = "static"
                buoy.color = "yellow"
                buoy.header.stamp = self.node.get_clock().now().to_msg()
                buoy.position_x = pos_x; buoy.position_y = pos_y; buoy.position_z = pos_z;
                self.object_publisher.publish(buoy)

def main(args=None):
    camera_handler = CameraHandler(enable_display=False)
    camera_handler.run_object_detection()

if __name__ == "__main__":
    main()
