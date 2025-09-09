class DataKeys:
    class ACTION:
        class JOINT:
            class POS:
                LEFT = "action-left-pos"
                RIGHT = "action-right-pos"

        class GRIPPER:
            class POS:
                LEFT = "action-left-gripper_pos"
                RIGHT = "action-right-gripper_pos"

        class EE_POSE:
            LEFT = "action-left-pose"
            RIGHT = "action-right-pose"

    class OBS:
        class JOINT:
            class POS:
                LEFT = "left-joint_pos"
                RIGHT = "right-joint_pos"

            class VEL:
                LEFT = "left-joint_vel"
                RIGHT = "right-joint_vel"

            class EFFORT:
                LEFT = "left-joint_eff"
                RIGHT = "right-joint_eff"

            class POSE:  # EE pose observations
                LEFT = "left-joint_pose"
                RIGHT = "right-joint_pose"

        class GRIPPER:
            class POS:
                LEFT = "left-gripper_pos"
                RIGHT = "right-gripper_pos"

        class FORCE:
            LEFT = "left-force"
            RIGHT = "right-force"

        class SPEED:
            LEFT = "left-speed"
            RIGHT = "right-speed"

        class OBJECT_DETECTED:
            LEFT = "left-object_detected"
            RIGHT = "right-object_detected"

    class CAMERA:
        class IMAGES:
            TOP = "top_camera-images-rgb"
            # we might have stereo camera, so we need to have left and right camera images when concat_image=False
            TOP_LEFT = "top_camera-images-left_rgb"
            TOP_RIGHT = "top_camera-images-right_rgb"
            RIGHT = "right_camera-images-rgb"
            LEFT = "left_camera-images-rgb"

        class TIMESTAMP:
            TOP = "top_camera-timestamp"
            RIGHT = "right_camera-timestamp"
            LEFT = "left_camera-timestamp"

    class TRAJECTORY:
        GLOBAL_TIMESTAMP = "timestamp"
        METADATA = "metadata.json"
        ANNOTATIONS = "top_camera-images-rgb_annotation.json"


# Create the camera to timestamp mapping
CAMERA_TO_TIMESTAMP_KEY = {
    DataKeys.CAMERA.IMAGES.TOP: DataKeys.CAMERA.TIMESTAMP.TOP,
    DataKeys.CAMERA.IMAGES.RIGHT: DataKeys.CAMERA.TIMESTAMP.RIGHT,
    DataKeys.CAMERA.IMAGES.LEFT: DataKeys.CAMERA.TIMESTAMP.LEFT,
}


# If it's a camera image key, return .mp4 instead of .npy
_camera_image_keys = [
    getattr(DataKeys.CAMERA.IMAGES, attr)
    for attr in dir(DataKeys.CAMERA.IMAGES)
    if not attr.startswith("_")
]


def key_filename(key: str) -> str:
    if key in _camera_image_keys:
        return str(key) + ".mp4"
    return str(key) + ".npy"
