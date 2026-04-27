import pyzed.sl as sl

zed = sl.Camera()

init_params = sl.InitParameters()
init_params.camera_resolution = sl.RESOLUTION.HD720
init_params.camera_fps = 60

err = zed.open(init_params)
if err != sl.ERROR_CODE.SUCCESS:
    exit(1)

recording_param = sl.RecordingParameters()
recording_param.compression_mode = sl.SVO_COMPRESSION_MODE.LOSSLESS
recording_param.video_filename = "capture.svo"

err = zed.enable_recording(recording_param)

if err != sl.ERROR_CODE.SUCCESS:
    print("Recording failed:", err)
    exit(1)

print("Recording... Press ENTER to stop.")
runtime = sl.RuntimeParameters()

try:
    while True:
        zed.grab(runtime)
finally:
    zed.disable_recording()
    zed.close()