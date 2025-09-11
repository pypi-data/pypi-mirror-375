from typing import Any, Optional

from pydantic import BaseModel, EmailStr

from ncmi_idc_extract_interfaces.models import ParameterCodes, SurveyNames
from ncmi_idc_extract_interfaces.query_models import CTDExportQuery

###########################################
# REQUESTS
###########################################


class CTDExportRequest(BaseModel):
    """
    Request model for exporting CTD data.

    Parameters
    ----------
    email : EmailStr
        Email address to send the export to (the requesting user too)

    query : CTDExportQuery
        Query parameters for filtering the CTD data
    """

    email: EmailStr
    query: CTDExportQuery

    class Config:
        extra = "forbid"


###########################################
# RESPONSES
###########################################


class BaseResponse(BaseModel):
    """
    Base response model that defines common fields for API responses.

    Parameters
    ----------
    status_code : int
        HTTP status code for the response
    details : str
        Description or details about the response
    """

    status_code: int
    details: str


class HealthCheckResponse(BaseResponse):
    """
    Response model for health check endpoints.

    Inherits all fields from BaseResponse.
    """

    pass


class TaskStatusResponseBaseModel:
    """
    Response model for checking the status of an asynchronous task.

    Parameters
    ----------
    task_id : str
        Unique identifier for the task
    status : str
        Current status of the task (e.g., "pending", "processing", "completed", "failed")
    result : Optional[Any]
        Result of the task, if completed
    """

    task_id: str
    status: str
    result: Optional[Any] = None


class CreateTaskResponse(BaseResponse):
    """
    Response model for creating a new asynchronous task.

    Parameters
    ----------
    details : str
        Description or details about the task creation
    task_id : str
        Unique identifier for the newly created task
    status_code : int
        API response status code
    """

    task_id: str
    


class DownloadResponse(BaseModel):
    """
    Response model for file download operations.

    Parameters
    ----------
    file_path : str
        Path to the file on the server
    filename : str
        Name of the file to be downloaded
    status_code : int
        HTTP status code for the response
    headers : dict
        HTTP headers for the download response
    """

    file_path: str
    filename: str
    status_code: int
    headers: dict


class PresignedURLResponse(BaseResponse):
    """
    Response model for providing a pre-signed URL.

    Parameters
    ----------
    signed_url : str
        The pre-signed URL for accessing a resource

    Notes
    -----
    Inherits status_code and details from BaseResponse.
    """

    signed_url: str


class CreateExportTaskResponse(CreateTaskResponse, PresignedURLResponse):
    pass


class ParameterCodesResponse(BaseResponse, ParameterCodes):
    """
    Response model for providing valid parameter codes.

    Parameters
    ----------
    parameter_codes : list[str]
        List of valid parameter codes

    Notes
    -----
    Inherits status_code and details from BaseResponse and adds parameter_codes.
    """


class SurveyNamesResponse(BaseResponse, SurveyNames):
    """
    Response model for providing valid survey names.

    Parameters
    ----------
    survey_names : list[str]
        List of valid survey names

    Notes
    -----
    Inherits status_code and details from BaseResponse and adds survey_names.
    """
