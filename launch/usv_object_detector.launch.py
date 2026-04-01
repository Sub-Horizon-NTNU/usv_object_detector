import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    publish_image_arg = DeclareLaunchArgument('publish_image',default_value='false',description='Publish images to topic selene/object_detector/image | <true/false>')
    model_arg = DeclareLaunchArgument('model',default_value='best.onnx',description='Select which model to use. e.g: best.onnx')
    usv_object_detector = Node(
                            package='usv_object_detector',
                            executable='usv_object_detector',
                            name='usv_object_detector',
                            output='screen',
                            parameters= [
                                {"publish_image":LaunchConfiguration("publish_image")},
                                {"model":LaunchConfiguration("model")}
                            ]
                        )

    return LaunchDescription([
        publish_image_arg,
        model_arg,
        usv_object_detector
    ])
