# Object detector
This package uses the Zed SDK python API along with YOLO in order to detect buoys and boats



Export a model to onnx:
```console
yolo export model=yolo12n.pt format=onnx simplify=True dynamic=False imgsz=608
```