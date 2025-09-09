from typing import Optional

from pydantic import BaseModel, ConfigDict

from xdof_sdk.data.schema.camera_info import CameraInfoList
from xdof_sdk.data.schema.station_metadata import (
    StationMetadata,
)


class Metadata(BaseModel):
    model_config = ConfigDict(extra="ignore")

    # Following fields are from the database, not written at save time.
    task_name: Optional[str] = None
    id: Optional[str] = None  # Delivered upon customer request
    operator_id: Optional[str] = None  # Delivered upon customer request

    duration: Optional[float] = None
    env_loop_frequency: Optional[float] = None

    station_metadata: Optional[StationMetadata] = None
    camera_info: Optional[CameraInfoList] = None

    start_datetime: Optional[str] = None
    """ E.g. 20250725_182559 """
    end_datetime: Optional[str] = None
    """ E.g. 20250725_182559 """
