from rclpy.node import Node
from ament_index_python.packages import get_package_share_directory

import pyzed.sl as sl
import cv2
import os


class CameraHandler:
    def __init__(self):#,*, node : Node):
        #self.node = node
        self.init_camera_params()
        self.enable_positional_tracking()
        self.enable_object_detection(onnx_model_path="Bogus")
        self.objects = []
        self.set_runtime_parameters()

    def init_camera_params(self) -> None:

        # Init camera
        self.zed = sl.Camera()

        self.init_params = sl.InitParameters()
        self.init_params.coordinate_units = sl.UNIT.METER
        self.init_params.camera_resolution = sl.RESOLUTION.HD1080
        self.init_params.depth_mode = sl.DEPTH_MODE.NEURAL
        self.init_params.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Z_UP_X_FWD
        self.init_params.depth_maximum_distance = 50

        status = self.zed.open(self.init_params)
        if status != sl.ERROR_CODE.SUCCESS:
            #self.node.get_logger.error("Camera Open: %s. Exit program.",{repr(status)})
            exit()

        self.camera_configuration = self.zed.get_camera_information().camera_configuration
        #self.node.get_logger().info("Camera initialized")

    def enable_object_detection(self,*, onnx_model_path : str) -> None:

        current_dir = os.path.dirname(__file__)
        self.main_directory = os.path.dirname(current_dir)

        self.onnx_model_path = os.path.join(self.main_directory,"models","best.onnx")
        print("PATH IS:", self.onnx_model_path)

        # Enable object detection module
        print("Enabling Object Detection...")
        self.obj_param = sl.ObjectDetectionParameters()
        self.obj_param.detection_model = sl.OBJECT_DETECTION_MODEL.CUSTOM_YOLOLIKE_BOX_OBJECTS
        self.obj_param.custom_onnx_file = self.onnx_model_path
        self.obj_param.enable_tracking = True
        self.obj_param.enable_segmentation = False
        status = self.zed.enable_object_detection(self.obj_param)
        if status != sl.ERROR_CODE.SUCCESS:
            #self.node.get_logger().info("Object Detection enable : %s. Exit program.",{repr(status)})
            self.zed.close()
            exit()
        #self.node.get_logger().info("Enabling Object Detection... DONE")

        self.objects = sl.Objects()


    def enable_positional_tracking(self)-> None:
        positional_tracking_parameters = sl.PositionalTrackingParameters()
        status = self.zed.enable_positional_tracking(positional_tracking_parameters)
        if status > sl.ERROR_CODE.SUCCESS:
            print(f"Positional Tracking enable : {repr(status)}. Exit program.")
            self.zed.close()
            exit()
        print("Enabling Positional Tracking... DONE")


    def set_runtime_parameters(self):

        self.runtime_parameters = sl.RuntimeParameters()
        self.runtime_parameters.confidence_threshold = 50

        self.detection_parameters_rt = sl.CustomObjectDetectionRuntimeParameters()

        self.props_dict = {
            1: sl.CustomObjectDetectionProperties(),
        }

        self.props_dict[1].native_mapped_class = sl.OBJECT_SUBCLASS.SPORTSBALL
        self.props_dict[1].object_acceleration_preset = sl.OBJECT_ACCELERATION_PRESET.LOW
        self.props_dict[1].detection_confidence_threshold = 40
        self.detection_parameters_rt.object_class_detection_properties = self.props_dict
        #

    def run_object_detection(self)-> None:
        self.image = sl.Mat()
        self.depth_map = sl.Mat()
        self.objects = sl.Objects()
        while self.zed.grab(self.runtime_parameters) <= sl.ERROR_CODE.SUCCESS :

            status = self.zed.retrieve_custom_objects(self.objects, self.detection_parameters_rt)
            if status <= sl.ERROR_CODE.SUCCESS:
                self.zed.retrieve_image(self.image, sl.VIEW.LEFT) # Retrieve left image
                self.zed.retrieve_measure(self.depth_map, sl.MEASURE.DEPTH) # Retrieve depth
                image_opencv = self.image.get_data()

                if(self.objects.is_new):
                    obj_array = self.objects.object_list
                    for new_object in obj_array:
                        if True:
                            class_label = new_object.raw_label
                            position = new_object.position
                            dimensions =  new_object.dimensions

                            b_box = new_object.bounding_box_2d
                            cv2.rectangle(image_opencv,(int(b_box[0][0]), int(b_box[0][1])),(int(b_box[2][0]), int(b_box[2][1])),(0,0,255),2) # bgr

                            cv2.putText(image_opencv,
                                        str(new_object.raw_label),
                                        (int(b_box[0][0]), int(b_box[0][1])), 
                                        cv2.FONT_HERSHEY_DUPLEX,
                                        1,
                                        (255,0,0), 
                                        2
                                        )
            cv2.imshow("Zed2i stream", image_opencv)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    print("Object detection stopped")





def main(args=None):
    camera_handler = CameraHandler()
    camera_handler.run_object_detection()



if __name__ == "__main__":
    main()
