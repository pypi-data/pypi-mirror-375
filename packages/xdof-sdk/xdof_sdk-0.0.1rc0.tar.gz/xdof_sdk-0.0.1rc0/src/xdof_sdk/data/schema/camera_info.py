from typing import Literal, Optional

import numpy as np
from numpy.typing import NDArray
from pydantic import (
    AliasChoices,
    AliasPath,
    BaseModel,
    ConfigDict,
    Field,
    field_serializer,
    field_validator,
)

from xdof_sdk.data.schema.types import TransformMatrix


class CameraExtrinsics(BaseModel):
    world: Literal["left_rgb"] = "left_rgb"

    right_rgb: TransformMatrix = Field(
        validation_alias=AliasChoices(
            "right_rgb",
            AliasPath("extrinsics", "right_rgb"),
        )
    )
    """ Transform of the right_rgb camera in the left_rgb frame. """

    @field_validator("right_rgb", mode="before")
    @classmethod
    def validate_right_rgb(cls, value):
        if isinstance(value, list):
            value = np.array(value, dtype=np.float64)

        if isinstance(value, np.ndarray):
            if value.shape != (4, 4):
                raise ValueError(f"Invalid shape for right_rgb: {value.shape}")
            return value

        raise ValueError(f"Invalid type for right_rgb: {type(value)}")

    @field_serializer("right_rgb")
    def serialize_right_rgb(self, value: NDArray[np.float64]) -> list[list[float]]:
        if value.shape != (4, 4):
            raise ValueError(f"Invalid shape for right_rgb: {value.shape}")
        return value.tolist()

    model_config = ConfigDict(extra="ignore", arbitrary_types_allowed=True)


class SingleCameraIntrinsicData(BaseModel):
    intrinsics_matrix: NDArray[np.float64]

    distortion_coefficients: list[float] = Field(
        validation_alias=AliasChoices(
            "distortion_coefficients",
            AliasPath("distortion", "distortion_coefficients"),
        )
    )

    distortion_model: Literal[
        "inverse_brown_conrady",  # Intel Realsense
        "zed_rectified",  # Zed
        "Perspective",  # Oak
        "plumb_bob",
    ] = Field(
        validation_alias=AliasChoices(
            "distortion_model",
            AliasPath("distortion", "distortion_model"),
        )
    )

    @field_validator("intrinsics_matrix", mode="before")
    @classmethod
    def validate_intrinsics_matrix(cls, value):
        if isinstance(value, list):
            value = np.array(value, dtype=np.float64)

        if isinstance(value, np.ndarray):
            if value.shape != (3, 3):
                raise ValueError(f"Invalid shape for intrinsics_matrix: {value.shape}")
            return value

        raise ValueError(f"Invalid type for intrinsics_matrix: {type(value)}")

    @field_serializer("intrinsics_matrix")
    def serialize_intrinsics_matrix(
        self, value: NDArray[np.float64]
    ) -> list[list[float]]:
        if value.shape != (3, 3):
            raise ValueError(f"Invalid shape for intrinsics_matrix: {value.shape}")
        return value.tolist()

    model_config = ConfigDict(extra="ignore", arbitrary_types_allowed=True)


class IntrinsicsList(BaseModel):
    rgb: Optional[SingleCameraIntrinsicData] = None
    """ Intrinsics for a single camera for a non-stereo camera. """

    left_rgb: Optional[SingleCameraIntrinsicData] = None
    """ Intrinsics for the left camera of a stereo camera. """

    right_rgb: Optional[SingleCameraIntrinsicData] = None
    """ Intrinsics for the right camera of a stereo camera. """


class CameraInfo(BaseModel):
    width: int
    height: int

    extrinsics: Optional[CameraExtrinsics] = None
    """ Extrinsics for the camera. Really only used for getting the right camera's extrinsics from left_rgb. """

    intrinsics: Optional[IntrinsicsList] = Field(
        default=None,
        validation_alias=AliasChoices(
            "intrinsics",
            AliasPath("intrinsic_data", "cameras"),
        ),
    )
    """ Intrinsics for the sensors(s) in this camera. """


class CameraInfoList(BaseModel):
    top_camera: CameraInfo
    left_camera: CameraInfo
    right_camera: CameraInfo
