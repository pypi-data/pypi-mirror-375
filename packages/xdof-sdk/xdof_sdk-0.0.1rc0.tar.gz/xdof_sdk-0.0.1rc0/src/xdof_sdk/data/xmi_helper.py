import numpy as np
import numpy.typing as npt

from xdof_sdk.data.constants import ArmSide
from xdof_sdk.data.schema.metadata import Metadata
from xdof_sdk.data.schema.station_metadata import XMIExtrinsicsConfig
from xdof_sdk.data.schema.types import Transform3D

# --- Constants and Helper Functions

# see from the back of the camera lens                     / z
#       z                                                 /
#       ^    x                                            /
#       |   ^                                            |------> x
#       |  /   -> pin whole camera convention            |
#       | /                                              |
#    y--|/                                               |y
CAMERA_LOCAL_FRAME_WORLD_TO_CAMERA_CONVENTION = np.array(
    [[0, -1, 0, 0], [0, 0, -1, 0], [1, 0, 0, 0], [0, 0, 0, 1]]
)
CALIB_FRAME_TO_WORLD_FRAME = np.array(
    [[0, 0, 1, 0], [-1, 0, 0, 0], [0, -1, 0, 0], [0, 0, 0, 1]]
)


def convert_left_handed_to_right_handed(
    quest_matrix: npt.NDArray[np.float64],
) -> npt.NDArray[np.float64]:
    y_flip_transform = np.array(
        [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, -1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ],
        dtype=np.float64,
    )
    intermediate_result = y_flip_transform @ quest_matrix
    final_result = intermediate_result @ y_flip_transform.T
    return final_result


def load_pose_from_transform3d(transform: Transform3D) -> np.ndarray:
    """Convert Transform3D object to 4x4 transformation matrix."""
    return transform.to_transform_matrix()


def movement_calib_frame_to_plot_world_frame(
    pose_in_calib_frame: np.ndarray,
) -> np.ndarray:
    return (
        CALIB_FRAME_TO_WORLD_FRAME @ pose_in_calib_frame @ CALIB_FRAME_TO_WORLD_FRAME.T
    )


def get_average_head_pose_collapose_to_z_up(head_poses_mat: np.ndarray) -> np.ndarray:
    Z_AXIS_OFFSET = -1.7
    head_poses_mat_in_calibration_frame = convert_left_handed_to_right_handed(
        head_poses_mat
    )
    head_poses_mat_in_world_frame = movement_calib_frame_to_plot_world_frame(
        head_poses_mat_in_calibration_frame
    )
    head_poses_mat_in_world_frame_average = np.mean(
        head_poses_mat_in_world_frame, axis=0
    )
    plot_world_frame = head_poses_mat_in_world_frame_average.copy()
    plot_world_frame[:3, 3] += np.array([0, 0, Z_AXIS_OFFSET])
    plot_world_frame[:3, 2] = np.array([0, 0, 1])
    x_axis = plot_world_frame[:3, 0]
    x_axis[2] = 0
    x_axis = x_axis / np.linalg.norm(x_axis)
    y_axis = -np.cross(x_axis, np.array([0, 0, 1]))
    plot_world_frame[:3, 1] = y_axis
    plot_world_frame[:3, 0] = x_axis
    return plot_world_frame


class XmiHelper:
    """
    This class manages the XMI episode: maintaining a fixed 'world frame' and converting the raw
    data stream and camera calibration data into that world frame.

    World frame: z-up, x-forward, y-left
    Camera/Gripper convention: z-forward, x-right, y-down
    """

    def __init__(self, metadata: Metadata, head_poses_quest_world_frame: np.ndarray):
        # Ensure we have XMI station metadata and extrinsics
        if not metadata.station_metadata:
            raise ValueError("station_metadata is required for XMI helper")

        if not isinstance(metadata.station_metadata.extrinsics, XMIExtrinsicsConfig):
            raise ValueError("XMI extrinsics configuration is required")

        extrinsics = metadata.station_metadata.extrinsics

        # Load raw extrinsic matrices from metadata
        top_camera_in_quest_head_raw = load_pose_from_transform3d(
            extrinsics.top_camera_in_quest_head
        )
        left_gripper_in_controller_raw = load_pose_from_transform3d(
            extrinsics.gripper_in_left_controller
        )
        right_gripper_in_controller_raw = load_pose_from_transform3d(
            extrinsics.gripper_in_right_controller
        )
        self.wrist_camera_in_gripper_flange = load_pose_from_transform3d(
            extrinsics.gripper_camera_in_gripper
        )

        # Get camera intrinsics
        if not metadata.camera_info or not metadata.camera_info.top_camera:
            raise ValueError("camera_info with top_camera is required for XMI helper")

        if (
            not metadata.camera_info.top_camera.intrinsics
            or not metadata.camera_info.top_camera.intrinsics.left_rgb
        ):
            raise ValueError(
                "top_camera left_rgb intrinsics are required for XMI helper"
            )

        self.left_intrinsics = (
            metadata.camera_info.top_camera.intrinsics.left_rgb.intrinsics_matrix
        )

        # Establish the final, stable world frame based on average head pose
        self.final_world_frame = get_average_head_pose_collapose_to_z_up(
            head_poses_quest_world_frame
        )
        self.to_final_world_frame = np.linalg.inv(self.final_world_frame)

        # 1. Head camera relative to the head
        self.head_T_top_camera = (
            movement_calib_frame_to_plot_world_frame(top_camera_in_quest_head_raw)
            @ CAMERA_LOCAL_FRAME_WORLD_TO_CAMERA_CONVENTION.T
        )

        # 2. Grippers relative to their controllers
        self.controller_T_left_gripper = (
            movement_calib_frame_to_plot_world_frame(left_gripper_in_controller_raw)
            @ CAMERA_LOCAL_FRAME_WORLD_TO_CAMERA_CONVENTION.T
        )
        self.controller_T_right_gripper = (
            movement_calib_frame_to_plot_world_frame(right_gripper_in_controller_raw)
            @ CAMERA_LOCAL_FRAME_WORLD_TO_CAMERA_CONVENTION.T
        )

        # 3. Wrist cameras relative to their controllers (Hand -> Gripper -> Camera)
        self.controller_T_left_wrist_camera = (
            self.controller_T_left_gripper @ self.wrist_camera_in_gripper_flange
        )
        self.controller_T_right_wrist_camera = (
            self.controller_T_right_gripper @ self.wrist_camera_in_gripper_flange
        )

    def get_head_data(
        self, head_poses_mat_quest_world_frame: np.ndarray
    ) -> npt.NDArray[np.float64]:
        """
        Gets the head pose in the final world frame and the constant transform from the
        head to its camera.

        Returns:
            head_poses_in_world_frame: Head poses in the final world frame. Shape (N, 4, 4).
        """
        head_poses_in_calibration_frame = convert_left_handed_to_right_handed(
            head_poses_mat_quest_world_frame
        )
        head_poses_in_plot_world_frame = movement_calib_frame_to_plot_world_frame(
            head_poses_in_calibration_frame
        )
        head_poses_in_world_frame = (
            self.to_final_world_frame @ head_poses_in_plot_world_frame
        )

        return head_poses_in_world_frame

    def get_controller_data(
        self, hand_poses_mat_quest_world_frame: np.ndarray, arm_side: ArmSide
    ) -> npt.NDArray[np.float64]:
        """
        Gets controller poses in the final world frame.

        Returns:
            controller_poses_in_world_frame: Controller poses in the final world frame. Shape (N, 4, 4).
        """
        hand_poses_in_calibration_frame = convert_left_handed_to_right_handed(
            hand_poses_mat_quest_world_frame
        )
        hand_poses_in_plot_world_frame = movement_calib_frame_to_plot_world_frame(
            hand_poses_in_calibration_frame
        )
        hand_poses_in_world_frame = (
            self.to_final_world_frame @ hand_poses_in_plot_world_frame
        )

        return hand_poses_in_world_frame
