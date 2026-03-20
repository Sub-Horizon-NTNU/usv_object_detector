# Object Detection System
This package uses the Zed SDK python API along with YOLO in order to detect buoys and boats. The goal is to identify objects and publish the



Export a model to onnx:
```console
yolo export model=yolo12n.pt format=onnx simplify=True dynamic=False imgsz=608
```

##### https://colab.research.google.com/github/roboflow-ai/notebooks/blob/main/notebooks/train-yolov12-object-detection-model.ipynb?ref=blog.roboflow.com#scrollTo=jdS8xtWOFblv