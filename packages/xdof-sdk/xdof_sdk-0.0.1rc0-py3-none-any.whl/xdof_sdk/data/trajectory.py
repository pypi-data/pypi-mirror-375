import abc
import json
import os
from functools import cache
from pathlib import Path
from typing import Dict, List

import cv2
import numpy as np
from numpy.typing import NDArray

from xdof_sdk.data.constants import ArmSide, CameraPerspective, FrameConvention
from xdof_sdk.data.fk import RobotFK
from xdof_sdk.data.schema.keys import DataKeys, key_filename
from xdof_sdk.data.schema.metadata import Metadata
from xdof_sdk.data.schema.types import ArmType, DataVersion
from xdof_sdk.data.xmi_helper import XmiHelper

GRIPPER_FLU_T_GRIPPER_RDF = np.array(
    [
        [0, -1, 0, 0],
        [0, 0, -1, 0],
        [1, 0, 0, 0],
        [0, 0, 0, 1],
    ]
).T

GRIPPER_FLU_T_GRIPPER_URF = np.array(
    [
        [0, 0, 1, 0],
        [0, -1, 0, 0],
        [1, 0, 0, 0],
        [0, 0, 0, 1],
    ]
).T


def _load_video(path: Path):
    """Load video frames as RGB arrays."""
    cap = cv2.VideoCapture(str(path))
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            yield frame[:, :, ::-1]  # BGR to RGB
    finally:
        cap.release()


class SegmentAnnotations:
    """Simple lookup for segment annotations."""

    def __init__(self, segments: List[tuple[int, int, str]]):
        self.segments = segments  # List of (start, end, label) tuples

    def __getitem__(self, frame: int) -> List[str]:
        """Get labels for a frame."""
        return [label for start, end, label in self.segments if start <= frame < end]


def load_per_frame_segment_annotation(path: Path) -> SegmentAnnotations:
    """Load frame annotations from JSON as simple segments."""
    if not path.exists():
        return SegmentAnnotations([])

    with open(path) as f:
        data = json.load(f)

    if not data:
        return SegmentAnnotations([])

    segments = []
    for ann in data["annotations"]:
        if ann["type"] == "segment":
            segments.append((ann["from_frame"], ann["to_frame"], ann["label"]))

    return SegmentAnnotations(segments)


class Trajectory(abc.ABC):
    def __init__(self, path: Path, metadata: Metadata, load_videos: bool = False):
        self.path = path
        self.metadata = metadata

        self._trajectory_data = self._load_data(path)
        self._annotations = load_per_frame_segment_annotation(
            path / "top_camera-images-rgb_annotation.json"
        )

        self._gripper_pos_in_joint_pos = True

        # Ensure we have station metadata
        if not metadata.station_metadata:
            raise ValueError("station_metadata is required")

        arm_type = metadata.station_metadata.arm_type
        if arm_type in (ArmType.YAM, ArmType.ARX):
            self._n_dof_arm = 6
        elif arm_type == ArmType.FRANKA:
            self._n_dof_arm = 7
        elif arm_type in [ArmType.XMI, ArmType.YAM_XMI]:
            self._n_dof_arm = 0
        else:
            raise ValueError(f"Arm type {arm_type} not supported")

        # Get data version
        if metadata.station_metadata.data_version:
            self.data_version = metadata.station_metadata.data_version
        else:
            self.data_version = DataVersion.V0

    def _load_data(
        self, path: Path, load_videos: bool = False
    ) -> Dict[str, NDArray[np.float64]]:
        """Load trajectory data from .npy and .mp4 files."""

        if not path.exists():
            print(f"Path {path} does not exist")
            return {}

        data = {}

        npy_files = path.glob("*.npy")
        for file in npy_files:
            key = os.path.basename(file).split(".")[0]
            loaded_data = np.load(file, allow_pickle=True)
            # Makes it easy to splice later if everything is 2D
            data[key] = (
                loaded_data[:, np.newaxis] if loaded_data.ndim == 1 else loaded_data
            )

        if load_videos:
            mp4_files = path.glob("*.mp4")
            for file in mp4_files:
                key = os.path.basename(file).split(".")[0]
                data[key] = np.array(list(_load_video(file)))

        return data

    @property
    def n_frames(self) -> int:
        return len(self._trajectory_data["timestamp"])

    def get_joint_pos_obs(self, arm_side: ArmSide) -> NDArray[np.float64]:
        raise NotImplementedError("Implement in subclass")

    def get_joint_pos_action(self, arm_side: ArmSide) -> NDArray[np.float64]:
        raise NotImplementedError("Implement in subclass")

    @abc.abstractmethod
    @cache
    def get_ee_pose_obs(
        self,
        arm_side: ArmSide,
        frame_convention: FrameConvention = FrameConvention.GRIPPER_RDF,
    ) -> NDArray[np.float64]:
        raise NotImplementedError("Implement in subclass")

    @abc.abstractmethod
    @cache
    def get_ee_pose_action(
        self,
        arm_side: ArmSide,
        frame_convention: FrameConvention = FrameConvention.GRIPPER_RDF,
    ) -> NDArray[np.float64]:
        raise NotImplementedError("Implement in subclass")

    def get_gripper_pos_obs(self, arm_side: ArmSide) -> NDArray[np.float64]:
        """Returns the gripper position where 0 is closed, 1 is open."""
        if f"{arm_side.value}-gripper_pos" in self._trajectory_data:
            return self._trajectory_data[f"{arm_side.value}-gripper_pos"]
        else:
            return self._trajectory_data[f"{arm_side.value}-joint_pos"][
                :, self._n_dof_arm :
            ]

    def get_gripper_pos_action(self, arm_side: ArmSide) -> NDArray[np.float64]:
        return self._trajectory_data[f"action-{arm_side.value}-pos"][
            :, self._n_dof_arm :
        ]

    def get_video(self, camera_perspective: CameraPerspective) -> NDArray[np.float64]:
        if f"{camera_perspective.value}_camera-images-rgb" in self._trajectory_data:
            return self._trajectory_data[
                f"{camera_perspective.value}_camera-images-rgb"
            ]
        else:
            raise ValueError(f"Video {camera_perspective.value} not loaded")

    def get_video_path(self, camera_perspective: CameraPerspective) -> Path:
        return self.path / f"{camera_perspective.value}_camera-images-rgb.mp4"

    @property
    def annotation_map(self) -> SegmentAnnotations:
        return self._annotations

    @cache
    def get_data_by_key(
        self, key: str, frame_convention: FrameConvention = FrameConvention.GRIPPER_RDF
    ) -> NDArray[np.float64]:
        """Get data by key, using existing methods when available, otherwise loading from file."""
        # Check if data is already loaded in trajectory_data
        if key in self._trajectory_data:
            return self._trajectory_data[key]

        # Dictionary dispatch for specialized methods
        key_handlers = {
            # Joint position observations
            DataKeys.OBS.JOINT.POS.LEFT: lambda: self.get_joint_pos_obs(ArmSide.LEFT),
            DataKeys.OBS.JOINT.POS.RIGHT: lambda: self.get_joint_pos_obs(ArmSide.RIGHT),
            # Joint position actions
            DataKeys.ACTION.JOINT.POS.LEFT: lambda: self.get_joint_pos_action(
                ArmSide.LEFT
            ),
            DataKeys.ACTION.JOINT.POS.RIGHT: lambda: self.get_joint_pos_action(
                ArmSide.RIGHT
            ),
            # Gripper position observations
            DataKeys.OBS.GRIPPER.POS.LEFT: lambda: self.get_gripper_pos_obs(
                ArmSide.LEFT
            ),
            DataKeys.OBS.GRIPPER.POS.RIGHT: lambda: self.get_gripper_pos_obs(
                ArmSide.RIGHT
            ),
            # Gripper position actions
            DataKeys.ACTION.GRIPPER.POS.LEFT: lambda: self.get_gripper_pos_action(
                ArmSide.LEFT
            ),
            DataKeys.ACTION.GRIPPER.POS.RIGHT: lambda: self.get_gripper_pos_action(
                ArmSide.RIGHT
            ),
            # EE pose methods need frame_convention parameter
            DataKeys.OBS.JOINT.POSE.LEFT: lambda: self.get_ee_pose_obs(
                ArmSide.LEFT, frame_convention
            ),
            DataKeys.OBS.JOINT.POSE.RIGHT: lambda: self.get_ee_pose_obs(
                ArmSide.RIGHT, frame_convention
            ),
            DataKeys.ACTION.EE_POSE.LEFT: lambda: self.get_ee_pose_action(
                ArmSide.LEFT, frame_convention
            ),
            DataKeys.ACTION.EE_POSE.RIGHT: lambda: self.get_ee_pose_action(
                ArmSide.RIGHT, frame_convention
            ),
            # Video data
            DataKeys.CAMERA.IMAGES.TOP: lambda: self.get_video(CameraPerspective.TOP),
            DataKeys.CAMERA.IMAGES.LEFT: lambda: self.get_video(CameraPerspective.LEFT),
            DataKeys.CAMERA.IMAGES.RIGHT: lambda: self.get_video(
                CameraPerspective.RIGHT
            ),
        }

        # Try to use specialized method
        try:
            if key in key_handlers:
                return key_handlers[key]()
        except (NotImplementedError, ValueError, KeyError):
            # If specialized method fails, fall through to file loading
            pass

        file_path = self.path / key_filename(key)
        if file_path.exists():
            if file_path.suffix == ".mp4":
                # Handle video files (would need cv2 or similar)
                raise NotImplementedError(
                    "Video loading from get_data_by_key not implemented yet"
                )
            else:
                # Load numpy file
                return np.load(file_path)
        else:
            raise FileNotFoundError(
                f"No data found for key '{key}' - file {file_path} does not exist"
            )


class ArmTrajectory(Trajectory):
    def __init__(self, path: Path, metadata: Metadata, load_videos: bool = False):
        super().__init__(path, metadata, load_videos)

        # We know station_metadata exists from parent validation
        assert metadata.station_metadata is not None
        arm_type = metadata.station_metadata.arm_type
        if arm_type in (ArmType.YAM, ArmType.ARX):
            self._ROBOT_CONVENTION_T_GRIPPER_FLU = np.array(
                [
                    [0, 0, 1, 0],
                    [0, 1, 0, 0],
                    [-1, 0, 0, 0],
                    [0, 0, 0, 1],
                ]
            ).T

        elif arm_type == ArmType.FRANKA:
            self._ROBOT_CONVENTION_T_GRIPPER_FLU = np.array(
                [
                    [0, 0, 1, 0],
                    [0, -1, 0, 0],
                    [1, 0, 0, 0],
                    [0, 0, 0, 1],
                ]
            ).T

        self._robot_fk = RobotFK(metadata)
        self._ee_left_action = self._robot_fk.fk(
            self.get_joint_pos_action(ArmSide.LEFT)
        )
        self._ee_right_action = self._robot_fk.fk(
            self.get_joint_pos_action(ArmSide.RIGHT),
            extrinsics=self._robot_fk.right_T_left,
        )
        self._ee_left_obs = self._robot_fk.fk(self.get_joint_pos_obs(ArmSide.LEFT))
        self._ee_right_obs = self._robot_fk.fk(
            self.get_joint_pos_obs(ArmSide.RIGHT),
            extrinsics=self._robot_fk.right_T_left,
        )

    def get_joint_pos_obs(self, arm_side: ArmSide) -> NDArray[np.float64]:
        return self._trajectory_data[f"{arm_side.value}-joint_pos"][
            :, : self._n_dof_arm
        ]

    def get_joint_pos_action(self, arm_side: ArmSide) -> NDArray[np.float64]:
        return self._trajectory_data[f"action-{arm_side.value}-pos"][
            :, : self._n_dof_arm
        ]

    @cache
    def get_ee_pose_obs(
        self,
        arm_side: ArmSide,
        frame_convention: FrameConvention = FrameConvention.GRIPPER_RDF,
    ) -> NDArray[np.float64]:
        base_obs = self._ee_left_obs if arm_side == ArmSide.LEFT else self._ee_right_obs

        base_obs = base_obs @ self._ROBOT_CONVENTION_T_GRIPPER_FLU

        if frame_convention == FrameConvention.GRIPPER_RDF:
            return base_obs @ GRIPPER_FLU_T_GRIPPER_RDF
        elif frame_convention == FrameConvention.GRIPPER_URF:
            return base_obs @ GRIPPER_FLU_T_GRIPPER_URF

        return base_obs

    @cache
    def get_ee_pose_action(
        self,
        arm_side: ArmSide,
        frame_convention: FrameConvention = FrameConvention.GRIPPER_RDF,
    ) -> NDArray[np.float64]:
        base_action = (
            self._ee_left_action if arm_side == ArmSide.LEFT else self._ee_right_action
        )

        base_action = base_action @ self._ROBOT_CONVENTION_T_GRIPPER_FLU

        if frame_convention == FrameConvention.GRIPPER_RDF:
            return base_action @ GRIPPER_FLU_T_GRIPPER_RDF
        elif frame_convention == FrameConvention.GRIPPER_URF:
            return base_action @ GRIPPER_FLU_T_GRIPPER_URF

        return base_action

    @cache
    def fk_for_arm(
        self,
        arm_side: ArmSide,
        extrinsics: NDArray[np.float64] | None = None,
        site_name: str | None = None,
        body_name: str | None = None,
    ):
        q = self.get_joint_pos_obs(arm_side)
        return self._robot_fk.fk(
            q, extrinsics=extrinsics, site_name=site_name, body_name=body_name
        )


class XmiTrajectory(Trajectory):
    def __init__(self, path: Path, metadata: Metadata, load_videos: bool = False):
        super().__init__(path, metadata, load_videos)

        self._xmi_helper = XmiHelper(
            metadata, self._trajectory_data["action-left-head"]
        )

    @cache
    def get_ee_pose_action(
        self,
        arm_side: ArmSide,
        frame_convention: FrameConvention = FrameConvention.GRIPPER_RDF,
    ) -> NDArray[np.float64]:
        if arm_side == ArmSide.LEFT:
            return (
                self.get_controller_pose_action(ArmSide.LEFT)
                @ self._xmi_helper.controller_T_left_gripper
            )
        else:
            return (
                self.get_controller_pose_action(ArmSide.RIGHT)
                @ self._xmi_helper.controller_T_right_gripper
            )

    @cache
    def get_controller_pose_action(self, arm_side: ArmSide) -> NDArray[np.float64]:
        hand_poses_mat = self._load_hand_poses_quest_world_frame(arm_side)
        return self._xmi_helper.get_controller_data(hand_poses_mat, arm_side)

    @cache
    def get_wrist_camera_pose_action(self, arm_side: ArmSide) -> NDArray[np.float64]:
        if arm_side == ArmSide.LEFT:
            return (
                self.get_controller_pose_action(ArmSide.LEFT)
                @ self._xmi_helper.controller_T_left_wrist_camera
            )
        else:
            return (
                self.get_controller_pose_action(ArmSide.RIGHT)
                @ self._xmi_helper.controller_T_right_wrist_camera
            )

    @cache
    def get_head_pose_action(self) -> NDArray[np.float64]:
        return self._xmi_helper.get_head_data(self._trajectory_data["action-left-head"])

    @cache
    def get_head_camera_pose_action(self) -> NDArray[np.float64]:
        return self.get_head_pose_action() @ self._xmi_helper.head_T_top_camera

    @cache
    def _load_hand_poses_quest_world_frame(self, arm_side: ArmSide) -> np.ndarray:
        if self.data_version == DataVersion.V1:
            return self._trajectory_data[f"action-{arm_side.value}-hand"]

        elif self.data_version == DataVersion.V0:
            moving_quest_world_frame = self._trajectory_data[
                f"action-{arm_side.value}-quest_world_frame"
            ]
            hand_pose_in_quest_moving_world_frame = self._trajectory_data[
                f"action-{arm_side.value}-hand_in_quest_world_frame"
            ]
            # in quest world frame
            return moving_quest_world_frame @ hand_pose_in_quest_moving_world_frame
        else:
            raise ValueError(f"Unknown data version: {self.data_version}")

    def get_joint_pos_obs(
        self, arm_side: ArmSide, include_gripper: bool = True
    ) -> NDArray[np.float64]:
        raise ValueError("XMI has no joint positions")

    def get_joint_pos_action(
        self, arm_side: ArmSide, include_gripper: bool = True
    ) -> NDArray[np.float64]:
        raise ValueError("XMI has no joint positions")

    @cache
    def get_ee_pose_obs(self, arm_side: ArmSide) -> NDArray[np.float64]:
        raise ValueError("XMI has no EE pose obs, use get_ee_pose_action()")


def load_trajectory(path: Path) -> Trajectory:
    metadata_dict = json.load(open(path / "metadata.json"))
    metadata = Metadata.model_validate(metadata_dict)

    if metadata.station_metadata and metadata.station_metadata.arm_type == ArmType.XMI:
        return XmiTrajectory(path, metadata)
    else:
        return ArmTrajectory(path, metadata)


if __name__ == "__main__":
    trajectory = load_trajectory(
        Path("standard/yam/fold_napkin_utensils/episode_64b69550")
    )
    print(trajectory._trajectory_data.keys())
