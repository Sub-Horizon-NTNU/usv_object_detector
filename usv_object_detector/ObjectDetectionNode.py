import rclpy
from rclpy.node import Node


class ObjectDetectionNode(Node):
    def __init__(self):
        super().__init__("object_detector")
        
        self.get_logger().info("[Object Detection Node] started")
        


def main(args=None):
    rclpy.init(args=args)
    object_detection_node = ObjectDetectionNode()
    rclpy.spin(object_detection_node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
