from enum import Enum
from functools import total_ordering
from typing import Annotated, Literal

import numpy as np
import quaternion
from numpy.typing import NDArray
from pydantic import AliasChoices, BaseModel, Field, field_validator

Position3D = Annotated[
    list[float], Field(min_length=3, max_length=3, description="3D position [x, y, z]")
]
Quaternion = Annotated[
    list[float],
    Field(min_length=4, max_length=4, description="Quaternion [w, x, y, z]"),
]

TransformMatrix = Annotated[NDArray[np.float64], Literal[4, 4]]


class Transform3D(BaseModel):
    """Represents a 3D transformation with position and rotation."""

    position: Position3D = [0.0, 0.0, 0.0]
    quaternion_wxyz: Annotated[
        Quaternion, Field(validation_alias=AliasChoices("quaternion_wxyz", "rotation"))
    ] = [1.0, 0.0, 0.0, 0.0]

    @field_validator("quaternion_wxyz")
    @classmethod
    def validate_quaternion_normalization(cls, v: list[float]) -> list[float]:
        """Normalize quaternion to unit length."""
        quat_array = np.array(v)
        quat_norm = np.linalg.norm(quat_array)

        # Check for zero quaternion (invalid)
        if quat_norm < 1e-8:
            raise ValueError("Quaternion cannot be zero vector")

        # Normalize the quaternion
        normalized_quat = quat_array / quat_norm
        return normalized_quat.tolist()

    def to_transform_matrix(self) -> TransformMatrix:
        """Convert Transform3D to a 4x4 transformation matrix."""
        matrix = np.eye(4)
        matrix[:3, 3] = self.position

        # Convert quaternion to rotation matrix
        quat = quaternion.from_float_array(self.quaternion_wxyz)
        matrix[:3, :3] = quaternion.as_rotation_matrix(quat)
        return matrix

    @classmethod
    def from_transform_matrix(cls, matrix: TransformMatrix) -> "Transform3D":
        """Create Transform3D from a 4x4 transformation matrix.

        Args:
            matrix: 4x4 homogeneous transformation matrix

        Returns:
            Transform3D object with position and quaternion from the matrix
        """
        if matrix.shape != (4, 4):
            raise ValueError(f"Expected 4x4 matrix, got {matrix.shape}")

        # Extract position from translation part
        position = matrix[:3, 3].tolist()

        # Extract rotation matrix and convert to quaternion
        rotation_matrix = matrix[:3, :3]
        quat = quaternion.from_rotation_matrix(rotation_matrix)

        # Convert to wxyz format (quaternion library uses wxyz by default)
        quaternion_wxyz = [quat.w, quat.x, quat.y, quat.z]

        return cls(position=position, quaternion_wxyz=quaternion_wxyz)

    def __matmul__(self, other: "Transform3D") -> "Transform3D":
        if not isinstance(other, Transform3D):
            return NotImplemented

        # Rotation
        q_self = quaternion.from_float_array(self.quaternion_wxyz)
        q_other = quaternion.from_float_array(other.quaternion_wxyz)
        q_comp = q_self * q_other

        # Position
        R_self = quaternion.as_rotation_matrix(q_self)
        p_self = np.asarray(self.position, dtype=float)
        p_other = np.asarray(other.position, dtype=float)
        p_comp = p_self + R_self @ p_other

        return Transform3D(
            position=p_comp.tolist(),
            quaternion_wxyz=[q_comp.w, q_comp.x, q_comp.y, q_comp.z],
        )


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
