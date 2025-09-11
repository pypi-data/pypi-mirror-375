from datetime import date
from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self


class BoundingBox(BaseModel):
    """
    Geographic bounding box defined by minimum and maximum longitude and latitude coordinates.

    Parameters
    ----------
    min_lon : float
        Minimum longitude, must be between -180 and 180 degrees
    max_lon : float
        Maximum longitude, must be between -180 and 180 degrees
    min_lat : float
        Minimum latitude, must be between -90 and 90 degrees
    max_lat : float
        Maximum latitude, must be between -90 and 90 degrees

    Notes
    -----
    The model includes validation to ensure min values are less than max values
    and all coordinates are within valid ranges.
    """

    # Longitude must be between -180 and 180 degrees
    min_lon: float = Field(..., ge=-180, le=180)
    max_lon: float = Field(..., ge=-180, le=180)
    # Latitude must be between -90 and 90 degrees
    min_lat: float = Field(..., ge=-90, le=90)
    max_lat: float = Field(..., ge=-90, le=90)

    @model_validator(mode="after")
    def validate_coordinates(self) -> Self:
        """
        Ensure that the coordinates define a valid bounding box:
        - min_lon < max_lon
        - min_lat < max_lat

        Returns
        -------
        Self
            The validated model instance

        Raises
        ------
        ValueError
            If min_lon >= max_lon or min_lat >= max_lat
        """
        if self.min_lon >= self.max_lon:
            raise ValueError(
                f"min_lon ({self.min_lon}) must be less than max_lon ({self.max_lon})."
            )
        if self.min_lat >= self.max_lat:
            raise ValueError(
                f"min_lat ({self.min_lat}) must be less than max_lat ({self.max_lat})."
            )

        return self

    def to_string(self) -> str:
        """
        Convert the bounding box to a string representation.

        Returns
        -------
        str
            String representation in the format "bbox(min_lon,min_lat,max_lon,max_lat)"
        """
        return f"bbox({self.min_lon},{self.min_lat},{self.max_lon},{self.max_lat})"

    def where_clause_and_params(self, table: Optional[str] = "") -> tuple[str, dict]:
        """
        Generate SQL WHERE clause and parameters for filtering by this bounding box.

        Parameters
        ----------
        table : Optional[str], default=""
            Table name prefix for the SQL query

        Returns
        -------
        tuple[str, dict]
            Tuple containing:
            - SQL WHERE clause string with parameter placeholders
            - Dictionary of parameter values
        """
        if table:
            table = f"{table}."

        # Filter on latitude and longitude within the bounding box
        where = f"{table}start_lat BETWEEN :min_lat AND :max_lat AND {table}start_lon BETWEEN :min_lon AND :max_lon"
        params: dict[str, Any] = self.model_dump()
        return where, params


class TemporalDuration(BaseModel):
    """
    Temporal coverage defined by start and end dates.

    Parameters
    ----------
    start_date : date
        Start date of the temporal coverage
    end_date : date, default=today
        End date of the temporal coverage

    Notes
    -----
    The model includes validation to ensure start_date is before or equal to end_date.
    """

    start_date: date = Field(
        ...,
        title="Start date",
        description="Please provide the start date of the dataset's temporal coverage.",
    )
    end_date: date = Field(
        default_factory=date.today,
        title="End date",
        description="Please provide the end date of the dataset's temporal coverage.",
    )

    @model_validator(mode="after")
    def check_dates_in_order(self) -> Self:
        """
        Validate that start_date is before or equal to end_date.

        Returns
        -------
        Self
            The validated model instance

        Raises
        ------
        ValueError
            If start_date > end_date
        """
        if self.start_date > self.end_date:
            raise ValueError("Start time must be before or equal to end time.")
        return self

    def to_string(self) -> str:
        """
        Convert the temporal duration to a string representation.

        Returns
        -------
        str
            String representation in the format "(start_date,end_date)"
        """
        return f"({self.start_date},{self.end_date})"

    def where_clause_and_params(
        self, table: Optional[str] = ""
    ) -> tuple[str, dict[str, Any]]:
        """
        Generate SQL WHERE clause and parameters for filtering by this temporal duration.

        Parameters
        ----------
        table : Optional[str], default=""
            Table name prefix for the SQL query

        Returns
        -------
        tuple[str, dict[str, Any]]
            Tuple containing:
            - SQL WHERE clause string with parameter placeholders
            - Dictionary of parameter values with ISO-formatted date strings
        """
        if table:
            table = f"{table}."

        where = f"{table}start_time BETWEEN TO_DATE(:start_date, 'YYYY-MM-DD') AND TO_DATE(:end_date, 'YYYY-MM-DD')"
        params = {k: v.isoformat() for k, v in self.model_dump().items()}
        return where, params

    class Config:
        # Set all strings to not be empty
        min_anystr_length = 1
        # don't allow extra fields
        extra = "forbid"

        title = "Temporal Duration"


class ParameterCodes(BaseModel):
    """
    Collection of parameter codes for filtering data.

    Parameters
    ----------
    codes : list[str]
        List of parameter codes
    """

    codes: list[str]

    def where_clause_and_params(self, table: Optional[str] = "") -> tuple[str, dict]:
        """
        Generate SQL WHERE clause and parameters for filtering by parameter codes.

        Parameters
        ----------
        table : Optional[str], default=""
            Table name prefix for the SQL query

        Returns
        -------
        tuple[str, dict]
            Tuple containing:
            - SQL WHERE clause string with parameter placeholders
            - Dictionary of parameter values mapped to their placeholders
        """

        if not self.codes:
            return "", {}

        if table:
            table = f"{table}."
        placeholders = ", ".join(
            [self.pc_placeholder(i) for i in range(len(self.codes))]
        )
        where = f"{table}PARAMETER_CODE IN ({placeholders})"
        params = {self.pc_placeholder(i): pc for i, pc in enumerate(self.codes)}
        return where, params

    @staticmethod
    def pc_placeholder(i: int) -> str:
        """
        Generate a placeholder name for a parameter code at a given index.

        Parameters
        ----------
        i : int
            Index of the parameter code

        Returns
        -------
        str
            Placeholder name in the format ":param_code_{i}"
        """
        return f":param_code_{str(i)}"


class SurveyNames(BaseModel):
    """Set of survey codes for filtering data.

    Parameters
    ----------
    surveys : list
        List of survey codes to filter for.

    """

    names: list[str]

    def where_clause_and_params(self, table: Optional[str] = "") -> tuple[str, dict]:
        """
        Generate SQL WHERE clause and parameters for filtering by survey codes.

        Parameters
        ----------
        table : Optional[str], default=""
            Table name prefix for the SQL query

        Returns
        -------
        tuple[str, dict]
            Tuple containing:
            - SQL WHERE clause string with survey placeholders
            - Dictionary of survey values mapped to their placeholders
        """

        if not self.names:
            return "", {}

        if table:
            table = f"{table}."
        placeholders = ", ".join(
            [self.survey_placeholder(i) for i in range(len(self.names))]
        )
        where = f"{table}SURVEY_NAME IN ({placeholders})"
        params = {
            self.survey_placeholder(i): survey for i, survey in enumerate(self.names)
        }
        return where, params

    @staticmethod
    def survey_placeholder(i: int) -> str:
        return f":survey_name_{str(i)}"
