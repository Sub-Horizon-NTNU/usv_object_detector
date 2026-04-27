import pyzed.sl as sl
import os

zed = sl.Camera()

init_params = sl.InitParameters()
init_params.set_from_svo_file("capture.svo2")
init_params.svo_real_time_mode = False  

err = zed.open(init_params)
if err != sl.ERROR_CODE.SUCCESS:
    exit(1)

os.makedirs("datasets/frames", exist_ok=True)

image = sl.Mat()
runtime = sl.RuntimeParameters()
i = 0

while True:
    if zed.grab(runtime) == sl.ERROR_CODE.SUCCESS:
        zed.retrieve_image(image, sl.VIEW.LEFT)
        image.write(f"datasets/frames/outdoor_test_{i:05d}.jpg", compression_level=0)
        i += 1
        print(f"Extracted frame {i}")
    else:
        break 

print(f"Done — {i} frames extracted")
zed.close()
