from ultralytics import YOLO

model = YOLO('yolo12n.pt')
 
results = model.train(data=f'src/object_detector/autodrone/data.yaml', epochs=100,cache=False, batch=2)
