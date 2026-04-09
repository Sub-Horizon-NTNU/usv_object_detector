import rclpy
from rclpy.node import Node
from usv_object_detector.CameraHandler import CameraHandler


class ObjectDetectionNode(Node):
    def __init__(self):
        super().__init__("usv_object_detector")
        
        self.declare_parameter('publish_image',False)
        publish_image = self.get_parameter('publish_image').value

        self.declare_parameter('model','best.onnx')
        model = self.get_parameter('model').value
        
        
        self.get_logger().info("[Object Detection Node] started")
        self.camera_handler = CameraHandler(node=self, enable_display=publish_image,model=model)
        self.camera_handler.run_object_detection()
        
        

def main(args=None):
    rclpy.init(args=args)
    object_detection_node = ObjectDetectionNode()
    rclpy.spin(object_detection_node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
