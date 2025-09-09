from enum import Enum
from functools import total_ordering
from typing import Annotated, Any, Literal, Optional

import numpy as np
import quaternion
from numpy.typing import NDArray
from pydantic import (
    AliasChoices,
    BaseModel,
    Field,
    field_validator,
    model_serializer,
    model_validator,
)

Position3D = Annotated[
    list[float], Field(min_length=3, max_length=3, description="3D position [x, y, z]")
]
Quaternion = Annotated[
    list[float],
    Field(min_length=4, max_length=4, description="Quaternion [w, x, y, z]"),
]


class LengthUnit(str, Enum):
    """Enumeration of supported length units for spatial transformations."""

    M = "m"
    CM = "cm"
    MM = "mm"


TransformMatrix = Annotated[NDArray[np.float64], Literal[4, 4]]


class Transform3D(BaseModel):
    """Represents a 3D transformation with position and rotation. By default, will transform all units to meters.
    Provide either position and quaternion_wxyz or 4x4 matrix.
    e.g.
    Transform3D(position=[1.0, 2.0, 3.0], quaternion_wxyz=[1.0, 0.0, 0.0, 0.0])
    Transform3D(matrix=np.array(
        [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ]))
    )
    """

    model_config = {"frozen": True, "arbitrary_types_allowed": True}

    position: Position3D = [0.0, 0.0, 0.0]
    quaternion_wxyz: Annotated[
        Quaternion, Field(validation_alias=AliasChoices("quaternion_wxyz", "rotation"))
    ] = [1.0, 0.0, 0.0, 0.0]
    matrix: TransformMatrix = Field(default=...)
    units: LengthUnit = LengthUnit.M
    was_matrix_input: bool = Field(default=False, exclude=True)

    @model_validator(mode="before")
    @classmethod
    def convert_inputs(cls, values):
        """Populate both representations from either input format and handle units conversion."""
        if not isinstance(values, dict):
            return values

        # Get units, default to meters
        units = values.get("units", LengthUnit.M)

        if "matrix" in values:
            # Matrix input - extract pos/quat and keep matrix
            matrix = values["matrix"]
            if isinstance(matrix, list):
                matrix = np.array(matrix, dtype=np.float64)

            if matrix.shape != (4, 4):
                raise ValueError(f"Expected 4x4 matrix, got {matrix.shape}")

            # Convert to meters if needed
            if units != LengthUnit.M:
                scale_factor = 1.0
                if units == LengthUnit.CM:
                    scale_factor = 0.01
                elif units == LengthUnit.MM:
                    scale_factor = 0.001
                matrix = matrix.copy()
                matrix[:3, 3] *= scale_factor

            values["position"] = matrix[:3, 3].tolist()
            rotation_matrix = matrix[:3, :3]
            quat = quaternion.from_rotation_matrix(rotation_matrix)
            values["quaternion_wxyz"] = [quat.w, quat.x, quat.y, quat.z]
            values["matrix"] = matrix
            values["was_matrix_input"] = True
        else:
            # Position/quaternion input - create matrix
            pos = values.get("position", [0.0, 0.0, 0.0])
            if "quaternion_wxyz" in values:
                quat_wxyz = values.get("quaternion_wxyz", [1.0, 0.0, 0.0, 0.0])
            else:
                quat_wxyz = values.get("rotation", [1.0, 0.0, 0.0, 0.0])

            # Convert position to meters if needed
            if units != LengthUnit.M:
                scale_factor = 1.0
                if units == LengthUnit.CM:
                    scale_factor = 0.01
                elif units == LengthUnit.MM:
                    scale_factor = 0.001
                pos = [p * scale_factor for p in pos]
                values["position"] = pos

            transform_matrix = np.eye(4)
            transform_matrix[:3, 3] = pos
            quat = quaternion.from_float_array(quat_wxyz)
            transform_matrix[:3, :3] = quaternion.as_rotation_matrix(quat)
            values["matrix"] = transform_matrix

        # Always store as meters
        values["units"] = LengthUnit.M
        return values

    @field_validator("quaternion_wxyz")
    @classmethod
    def validate_quaternion_normalization(
        cls, v: Optional[list[float]]
    ) -> Optional[list[float]]:
        """Normalize quaternion to unit length."""
        if v is None:
            return v

        quat_array = np.array(v)
        quat_norm = np.linalg.norm(quat_array)

        # Check for zero quaternion (invalid)
        if quat_norm < 1e-8:
            raise ValueError("Quaternion cannot be zero vector")

        # Normalize the quaternion
        normalized_quat = quat_array / quat_norm
        return normalized_quat.tolist()

    @model_serializer
    def serialize_model(self):
        """Serialize based on original input format to preserve precision."""
        if self.was_matrix_input:
            ret_dict = {"matrix": self.matrix.tolist()}
        else:
            ret_dict: dict[str, Any] = {
                "position": self.position,
                "quaternion_wxyz": self.quaternion_wxyz,
            }

        if self.units != LengthUnit.M:
            ret_dict["units"] = self.units.value

        return ret_dict

    def __eq__(self, other):
        return np.allclose(self.matrix, other.matrix) and self.units == other.units

    def __matmul__(self, other: "Transform3D") -> "Transform3D":
        if not isinstance(other, Transform3D):
            return NotImplemented

        return Transform3D(matrix=self.matrix @ other.matrix)


@total_ordering
class DataVersion(str, Enum):
    """Supported data versions for stations."""

    # Future versions should just start as V2 = "2", otherwise requires SemVer dependency
    # See CHANGELOG.md for details of changes

    V1 = "0.1"  # Version 0.1 - XMI stations running after https://github.com/xdofai/lab42/pull/662
    V0 = "0.0"  # Version 0.0 - supported by all stations


class ArmType(str, Enum):
    """Enumeration of supported arm types in the robotics system.

    This enum defines the different types of robotic arms that can be used
    within the system, including physical arms and simulated variants.
    """

    YAM = "yam"  # Yet Another Manipulator
    ARX = "arx"  # ARX series robotic arm
    XMI = "xmi"  # XMI robotic arm
    FRANKA = "franka"  # Franka Emika robotic arm
    PIPER = "piper"  # Piper robotic arm
    SIM_YAM = "sim_yam"  # Simulated YAM arm
    YAM_XMI = "yam_xmi"  # xmi with dm4310 linear gripper
    TEST = "test"  # Test arm for pytest purposes


class WorldFrame(Enum):
    """Enumeration of coordinate frame references in the world.

    This enum defines the different reference frames that can be used
    for coordinate transformations and spatial reasoning in the robotic system.
    """

    LEFT_ARM = "left_arm"  # Coordinate frame relative to the left arm base
    NA = "NA"  # Not applicable, this usually applies to VR stations where the world frame is dynamically changing
    BASE = "base"  # This usually applies to the mobile station or single arm stations
