# Object Detection System
This package uses the Zed SDK python API along with YOLO in order to detect buoys and boats. The goal is to identify objects and publish the objects detected.

## Setup
It is recommended to create a virtual environment for installing the dependencies.
```console
python -m venv venv_z 
source venv_z/bin/activate
```
Make sure the Zed SDK is installed, this is done by following the steps at: (https://www.stereolabs.com/docs/development/zed-sdk/linux)
The Zed Python API can be installed after the Zed SDK is downloaded, to install the dependencies run the following commands:
```console 
python -m pip install cython numpy opencv-python pyopengl catkin_pkg lark pyyaml requests empy==3.3.4
python /usr/local/zed/get_python_api.py
touch venv_z/COLCON_IGNORE
```

### Launch the node
Launch the node using the following command:
```console
ros2 launch usv_object_detector usv_object_detector.launch.py
```

### Parameters
The parameter **publish_image** specifies is images should be published to the topic: **selene/object_detector/image**. The parameter **model** specifies which ONNX model to use.


###  Model
Each model trained must be exported to *.onnx. The zed sdk supports YOLO v5, v6, v7, v8, v9, v10, v11 and v12.

Export a model to onnx:
```console
yolo export model=yolo12n.pt format=onnx simplify=True dynamic=False imgsz=608
```


### View vision system detections
In order to view the output frames with the detected objects you must start with the following launch command:
```console
ros2 launch usv_object_detector usv_object_detector.launch.py publish_image:=true
```

Then the image published to the topic **selene/object_detector/image** view using:
```console
ros2 run rqt_image_view rqt_image_view                 
```


### venv install scheme on jetson (tested):
```console
python3 -m venv venv
source venv/bin/activate
touch venv/COLCON_IGNORE

pip install --upgrade pip setuptools wheel 
pip install colcon-common-extensions
pip install catkin_pkg empy==3.3.4 lark pyyaml packaging numpy==1.26.4 opencv-python-headless==4.9.0.80 requests pyopengl cython

python /usr/local/zed/get_python_api.py

```
The zed sdk has probably upgraded numpy making it incompatible with opencv:

```console
pip install numpy==1.26.4 --force-reinstall
``` 




