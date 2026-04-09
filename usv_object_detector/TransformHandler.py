import numpy as np
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
import tf_transformations as tf
from numpy import pi

class TransformHandler:
    def __init__(self,*, node : Node):
        self.node = node
        self.position_subscriber = self.node.create_subscription(PoseStamped, "/ap/pose/filtered" , self.update_position,10)
        
    def update_position(self, pose_stamped_msg : PoseStamped) -> None:
        pose_stamped = pose_stamped_msg
        orientation_q = pose_stamped_msg.pose.orientation
        quat = [
            orientation_q.x,
            orientation_q.y,
            orientation_q.z,
            orientation_q.w
        ]

        self.rot_matrix = tf.quaternion_matrix(quat)

    def set_camera_orientation(self,*,qx,qy,qz,qw) -> None:
        # Mainly for testing without the usv.
        self.orientation = [
            qx,
            qy,
            qz,
            qw
        ]

    def transform_to_usv_2D(self,*,x, y, z) -> np.ndarray:
        # The goal of this function is to transform the detected object into the objects 2D position relative to the object.
        #q = tf.quaternion_from_euler(30*pi/180,20*pi/180,0)  
        self.rot_matrix = tf.quaternion_matrix(self.orientation)   

        position = np.array([[x],
                             [y],
                             [z],
                             [1]]
        )
        
        position_transformed = np.dot(self.rot_matrix,position)
        return position_transformed