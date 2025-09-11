# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime
from typing_extensions import Literal

from ..._models import BaseModel
from ..file_info import FileInfo
from ..version_info import VersionInfo
from ..extract_configuration import ExtractConfiguration
from ..extract_output_response import ExtractOutputResponse

__all__ = ["ExtractCreateResponse"]


class ExtractCreateResponse(BaseModel):
    configuration: ExtractConfiguration

    created_at: datetime
    """The date and time when the task was created and queued."""

    file_info: FileInfo
    """Information about the input file."""

    message: str
    """A message describing the task's status or any errors that occurred."""

    status: Literal["Starting", "Processing", "Succeeded", "Failed", "Cancelled"]
    """The status of the task."""

    task_id: str
    """The unique identifier for the task."""

    task_type: Literal["Parse", "Extract"]

    version_info: VersionInfo
    """Version information for the task."""

    expires_at: Optional[datetime] = None
    """The date and time when the task will expire."""

    finished_at: Optional[datetime] = None
    """The date and time when the task was finished."""

    input_file_url: Optional[str] = None
    """The presigned URL of the input file. Deprecated use `file_info.url` instead."""

    output: Optional[ExtractOutputResponse] = None
    """The processed results of a document extraction task.

    Shapes:

    - `results`: JSON matching the user-provided schema.
    - `citations`: mirror of `results`; only leaf positions (primitive or
      array-of-primitives) contain a `Vec<Citation>` supporting that field.
    - `metrics`: mirror of `results`; only leaf positions contain a `Metrics` object
      for that field.
    """

    source_task_id: Optional[str] = None
    """The ID of the source `parse` task that was used for extraction"""

    started_at: Optional[datetime] = None
    """The date and time when the task was started."""

    task_url: Optional[str] = None
    """The presigned URL of the task."""
