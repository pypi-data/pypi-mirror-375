from typing import Any, Optional

from pydantic import BaseModel, model_validator

from ncmi_idc_extract_interfaces.models import (
    BoundingBox,
    ParameterCodes,
    SurveyNames,
    TemporalDuration,
)


# Make separate XXXExportQuery classes for each data type, or have a general one with an enum type inside?
# what if query logic etc is different. maybe better to just have a little more boiler plate code. 
class CTDExportQuery(BaseModel):
    """
    Query model for CTD (Conductivity, Temperature, Depth) data export.

    Parameters
    ----------
    bounding_box : Optional[BoundingBox], default=None
        Spatial filter using geographic coordinates

    temporal_duration : Optional[TemporalDuration], default=None
        Temporal filter using start and end dates

    parameter_codes : Optional[ParameterCodes], default=None
        Filter by specific parameter codes

    survey_names : Optional[SurveyNames], default=None
        Filter by specific survey names. Cannot be combined with temporal_duration.

    retain_debug_extras : Optional[bool], default=False
        Retain IDs and extras used within the data warehouse in the final export. Mostly for debugging

    Notes
    -----
    This model generates SQL queries for filtering CTD data based on
    spatial, temporal, and parameter-specific criteria.
    """

    # spatial and temporal filters
    bounding_box: Optional[BoundingBox] = None
    temporal_duration: Optional[TemporalDuration] = None
    # List of Parameter codes to optionally filter by. If empty, all parameter codes will be included.
    parameter_codes: Optional[ParameterCodes] = None
    # List of survey codes to optionally filter
    survey_names: Optional[SurveyNames] = None
    # retain IDs and extras used within the data warehouse in the final export. Mostly for debugging
    retain_debug_extras: Optional[bool] = False

    class Config:
        extra = "forbid"

    _header_table = "h"  # used in queries with joins of multiple tables
    _ctd_data_table = "ctd"
    _component_table = "comp"
    _deployment_table = "d"

    # Column renaming mappings for better readability in output files
    _ctd_instruments_col_rename: dict[str, str] = {
        "SURVEY_NAME": "Survey",
        "STATION_NO": "Station",
        "PARAMETER_UNITS": "UoM",
        "SERIAL_NO": "Serial No",
        "MODEL_NO": "Model",
        "MANUFACTURER": "Manufacturer",
        "NAME": "Instrument",
        "PARAMETER_LABEL": "Parameter",
    }

    _extra_cols = [
        "DATA_ID",
        "PROJECT_ID",
        "DEPLOYMENT_ID",
    ]

    # columns to select from warehouse.ctd_header
    # to be combined for final columns after pivot of warehouse.ctd_data
    # currently ordered by appearance in the final export, comments show positioning of fields from other tables.
    # ordered for a umn to read and know. Python sets are not officially technically ordered.
    @property
    def _ctd_headers_selection(self) -> list[str]:
        _ctd_headers_selection = [
            "SURVEY_NAME",
            # station number
            "START_TIME",
            "END_TIME",
            "MIN_DEPTH",
            "MAX_DEPTH",
            "BOTTOM_DEPTH",
            "BOTTOM_LAT",
            "BOTTOM_LON",
            "END_LAT",
            "END_LON",
            "START_LAT",
            "START_LON",
            # project name
            "MARLIN_UUID",
            # extras (maybe for debug)
        ]
        if self.retain_debug_extras:
            _ctd_headers_selection.extend(self._extra_cols)

        return _ctd_headers_selection

    @model_validator(mode="after")
    def validate_filters_provided(self) -> Any:
        """Validate that if a survey codes filter is provided, then both
        a temporal duration filter and bounding box filter are not provided.


        Returns
        -------
        CTDExportQuery
            _description_

        Raises
        ------
        ValueError
            If filtering by survey codes and temporal duration or bounding box at the same time
        """
        if self.survey_names:
            if not self.survey_names.names:
                raise ValueError(
                    "Survey names cannot be an empty list. Omit filter to include all possible surveys, or use the /api/general/survey-names endpoint to get all valid survey names (a-lot)."
                )
            if self.temporal_duration:
                raise ValueError(
                    "Filtering by survey codes and temporal duration at the same time is not supported. Please omit one of the filters."
                )

        if self.parameter_codes and not self.parameter_codes.codes:
            raise ValueError(
                "Parameter codes cannot be an empty list. Omit filter to use default parameter codes, or use the /api/ctd/parameter-codes endpoint to get all valid codes."
            )

        return self

    @staticmethod
    def _add_where_clause_and_params(
        where_clauses: list[str],
        params: dict[str, Any],
        clause_and_params: Optional[tuple[str, dict]],
    ) -> None:
        """
        Add a WHERE clause and its parameters to the existing lists if provided.

        Parameters
        ----------
        where_clauses : list[str]
            List of WHERE clause strings to append to
        params : dict[str, Any]
            Dictionary of parameters to update
        clause_and_params : Optional[tuple[str, dict]]
            Tuple containing a WHERE clause string and its parameters

        Returns
        -------
        None
            Updates where_clauses and params in place
        """
        if clause_and_params:
            where, new_params = clause_and_params
            where_clauses.append(where)
            params.update(new_params)

    def data_q_where_clause_and_params(
        self, header_table: Optional[str] = "", data_table: Optional[str] = ""
    ) -> tuple[str, dict[str, Any]]:
        """
        Generate the WHERE clause and parameters for CTD data query.

        Combines filters from bounding box, temporal duration, and parameter codes.

        Parameters
        ----------
        header_table : Optional[str], default=""
            Table alias for the CTD header table

        Returns
        -------
        tuple[str, dict[str, Any]]
            Tuple containing:
            - SQL WHERE clause string with parameter placeholders
            - Dictionary of parameter values
        """
        where_clauses: list[str] = []
        where_params: dict[str, Any] = {}

        self._add_where_clause_and_params(
            where_clauses,
            where_params,
            (self.parameter_codes.where_clause_and_params(table=data_table) if self.parameter_codes else None),
        )

        self._add_where_clause_and_params(
            where_clauses,
            where_params,
            (self.temporal_duration.where_clause_and_params(table=header_table) if self.temporal_duration else None),
        )

        self._add_where_clause_and_params(
            where_clauses,
            where_params,
            (self.bounding_box.where_clause_and_params(table=header_table) if self.bounding_box else None),
        )

        self._add_where_clause_and_params(
            where_clauses,
            where_params,
            (self.survey_names.where_clause_and_params(table=header_table) if self.survey_names else None),
        )

        where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        return where_clause, where_params

    def data_and_headers_q_where_clause_and_params(
        self,
        expected_param_codes: set[str],
        header_table: Optional[str] = "",
        data_table: Optional[str] = "",
    ) -> tuple[str, dict[str, Any]]:
        """
        Generate the WHERE clause and parameters for CTD data query.

        Combines filters from bounding box, temporal duration, and uses
        parameter codes that are already know to be found from other given filters

        Parameters
        ----------
        header_table : Optional[str], default=""
            Table alias for the CTD header table

        Returns
        -------
        tuple[str, dict[str, Any]]
            Tuple containing:
            - SQL WHERE clause string with parameter placeholders
            - Dictionary of parameter values
        """
        where_clauses: list[str] = []
        where_params: dict[str, Any] = {}

        # given parameter codes
        parameter_codes = ParameterCodes(codes=list(expected_param_codes))
        self._add_where_clause_and_params(
            where_clauses,
            where_params,
            (parameter_codes.where_clause_and_params(table=data_table)),
        )
        # temporal duration
        self._add_where_clause_and_params(
            where_clauses,
            where_params,
            (self.temporal_duration.where_clause_and_params(table=header_table) if self.temporal_duration else None),
        )
        # bounding box
        self._add_where_clause_and_params(
            where_clauses,
            where_params,
            (self.bounding_box.where_clause_and_params(table=header_table) if self.bounding_box else None),
        )
        # survey names
        self._add_where_clause_and_params(
            where_clauses,
            where_params,
            (self.survey_names.where_clause_and_params(table=header_table) if self.survey_names else None),
        )

        where_clause = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        return where_clause, where_params

    def header_q_where_clause_and_params(
        self, include_where: bool = True, header_table: Optional[str] = ""
    ) -> tuple[str, dict]:
        """
        Generate the WHERE clause and parameters for CTD header query.

        Combines filters from bounding box and temporal duration (no parameter codes).

        Parameters
        ----------
        include_where : bool, default=True
            Whether to include the "WHERE" keyword in the clause
        header_table : Optional[str], default=""
            Table alias for the CTD header table

        Returns
        -------
        tuple[str, dict]
            Tuple containing:
            - SQL WHERE clause string with parameter placeholders
            - Dictionary of parameter values
        """
        where_clauses: list[str] = []
        where_params: dict[str, Any] = {}

        self._add_where_clause_and_params(
            where_clauses,
            where_params,
            (self.temporal_duration.where_clause_and_params(table=header_table) if self.temporal_duration else None),
        )
        self._add_where_clause_and_params(
            where_clauses,
            where_params,
            (self.bounding_box.where_clause_and_params(table=header_table) if self.bounding_box else None),
        )
        # no parameter codes in header table

        self._add_where_clause_and_params(
            where_clauses,
            where_params,
            (self.survey_names.where_clause_and_params(table=header_table) if self.survey_names else None),
        )

        if include_where:
            where = "WHERE "
        else:
            where = ""

        where_clause = where + " AND ".join(where_clauses) if where_clauses else ""
        return where_clause, where_params

    @property
    def data_q_and_params(self) -> tuple[str, dict[str, Any]]:
        """
        Generate the complete SQL query and parameters for CTD data.

        Returns
        -------
        tuple[str, dict[str, Any]]
            Tuple containing:
            class CheckQueryResponse(BaseResponse, ParameterCodes):
            - Complete SQL query string with joins and WHERE clause
            - Dictionary of parameter values
        """
        h = self._header_table
        ctd = self._ctd_data_table
        where_clause, params = self.data_q_where_clause_and_params(header_table=h, data_table=ctd)

        query = f"""SELECT {ctd}.* FROM WAREHOUSE.ctd_data {ctd} JOIN WAREHOUSE.ctd_header {h} ON {ctd}.DATA_ID = h.DATA_ID {where_clause}
        """

        return query, params

    @property
    def unique_param_codes_q_and_params(self) -> tuple[str, dict[str, Any]]:
        """
        Generate a query to retrieve unique parameter codes from the CTD data for given query
        request payload params. Same as data_q_and_params but without the data, just distinct selection

        Returns
        -------
        tuple[str, dict[str, Any]]
            Tuple containing:
            - Complete SQL query string for retrieving unique parameter codes
            - Dictionary of parameter values
        """
        h = self._header_table
        ctd = self._ctd_data_table
        where_clause, params = self.data_q_where_clause_and_params(header_table=h, data_table=ctd)

        query = f"""SELECT DISTINCT {ctd}.PARAMETER_CODE FROM WAREHOUSE.ctd_data {ctd} JOIN WAREHOUSE.ctd_header {h} ON {ctd}.DATA_ID = h.DATA_ID {where_clause}
        """

        return query, params
    
    @property
    def unique_survey_names_q_and_params(self) -> tuple[str, dict[str, Any]]:
        """
        Generate a query to retrieve unique survey names from the CTD data for given query
        request payload params. Same as data_q_and_params but without the data, just distinct selection

        Returns
        -------
        tuple[str, dict[str, Any]]
            Tuple containing:
            - Complete SQL query string for retrieving unique parameter codes
            - Dictionary of parameter values
        """
        h = self._header_table
        ctd = self._ctd_data_table
        where_clause, params = self.data_q_where_clause_and_params(header_table=h, data_table=ctd)

        query = f"""SELECT DISTINCT {h}.SURVEY_NAME FROM WAREHOUSE.ctd_data {ctd} JOIN WAREHOUSE.ctd_header {h} ON {ctd}.DATA_ID = h.DATA_ID {where_clause}
        """

        return query, params

    @property
    def exists_param_codes_q_and_params(self) -> tuple[str, dict[str, Any]]:
        """
        Generate a query to retrieve unique parameter codes from the CTD data for given query
        request payload params. Same as data_q_and_params but without the data, just distinct selection

        Returns
        -------
        tuple[str, dict[str, Any]]
            Tuple containing:
            - Complete SQL query string for retrieving unique parameter codes
            - Dictionary of parameter values
        """
        h = self._header_table
        ctd = self._ctd_data_table
        where_clause, params = self.data_q_where_clause_and_params(header_table=h, data_table=ctd)

        query = f"""SELECT DISTINCT {ctd}.PARAMETER_CODE FROM WAREHOUSE.ctd_data {ctd} JOIN WAREHOUSE.ctd_header {h} ON {ctd}.DATA_ID = h.DATA_ID {where_clause} AND ROWNUM = 1
        """

        return query, params

    def data_and_headers_q_and_params(self, expected_param_codes: set[str]) -> tuple[str, dict[str, Any]]:
        if not expected_param_codes:
            raise ValueError(
                "Must provide a non-empty list of parameter codes, otherwise won't be retrieving any data!"
            )

        h = self._header_table
        ctd = self._ctd_data_table
        where_clause, params = self.data_and_headers_q_where_clause_and_params(
            header_table=h, data_table=ctd, expected_param_codes=expected_param_codes
        )
        header_select = f"{h}." + f", {h}.".join(self._ctd_headers_selection)

        pivot_select = self._pivot_select(expected_param_codes=expected_param_codes)
        # other selections to make for metadata not from the ctd_headers table (and therefor not in header_select)
        other_select = "d.STATION_NO, p.PROJECT_NAME"
        query = f"""
            SELECT {header_select}, {other_select}, {ctd}.PRESSURE, \n {pivot_select} 
            FROM WAREHOUSE.ctd_data {ctd} JOIN WAREHOUSE.ctd_header {h} ON {ctd}.DATA_ID = h.DATA_ID 
            LEFT JOIN WAREHOUSE.deployment d ON h.DEPLOYMENT_ID = d.DEPLOYMENT_ID
            LEFT JOIN WAREHOUSE.project p ON h.PROJECT_ID = p.PROJECT_ID
            {where_clause}
            GROUP BY ctd.PRESSURE, {header_select}, {other_select}
        """.strip()

        return query, params

    def _pivot_select(self, expected_param_codes: set[str]) -> str:
        """
        Generate the pivot select statements for the given parameter codes.

        Parameters
        ----------
        expected_param_codes : set[str]
            Set of expected parameter codes to pivot
        Returns
        -------
        list[str]
            List of SQL select statements for pivoting
        """
        ctd = self._ctd_data_table
        pivot_selects = []
        for pc in expected_param_codes:
            # required because of the dash in SIGMA-T. Will appear as SIGMA_T in the final export
            pc_as = pc.replace("-", "_")
            pivot_selects.append(f"MAX(CASE WHEN {ctd}.PARAMETER_CODE = '{pc}' THEN {ctd}.VALUE END) AS {pc_as}")
            pivot_selects.append(f"MAX(CASE WHEN {ctd}.PARAMETER_CODE = '{pc}' THEN {ctd}.QC_FLAG END) AS {pc_as}_QC")

        return ",\n".join(pivot_selects)

    def get_instruments_q_and_params(self, param_codes: list[str]) -> tuple[str, dict[str, Any]]:
        """
        Generate a query to retrieve the instruments used in deployments.

        Parameters
        ----------
        param_codes : list[str]
            List of parameter codes to filter by. These should be parameter codes
            that are actually present in the returned data.

        Returns
        -------
        tuple[str, dict[str, Any]]
            Tuple containing:
            - Complete SQL query string for retrieving instrument data
            - Dictionary of parameter values

        Raises
        ------
        ValueError
            If param_codes is empty
        """
        if not param_codes:
            raise ValueError(
                "Must provide a non-empty list of parameter codes for their measurement instruments, otherwise what instruments do you want data for?!"
            )

        c = self._component_table
        h = self._header_table
        d = self._deployment_table

        # Query parameters for the different parameter codes.
        q_params = {}
        params_where, params_params = ParameterCodes(codes=param_codes).where_clause_and_params(table=c)
        q_params.update(params_params)

        # Query parameters for the bounding box and temporal duration which are applied to the headers table
        headers_where, headers_params = self.header_q_where_clause_and_params(include_where=False, header_table=h)
        q_params.update(headers_params)

        q = f"""
            SELECT {d}.STATION_NO, {d}.SURVEY_NAME, {c}.PARAMETER_CODE, {c}.NAME, {c}.MANUFACTURER, {c}.MODEL_NO, {c}.SERIAL_NO, pc.PARAMETER_LABEL, pc.PARAMETER_UNITS
            FROM WAREHOUSE.CTD_HEADER {h}  -- left joins to protect against missing data in tables seeking to retrieve additional data for. Rather have a few empty cols than entire missing row.
            LEFT JOIN WAREHOUSE.DEPLOYMENT_COMPONENT dc ON {h}.DEPLOYMENT_ID = dc.DEPLOYMENT_ID
            LEFT JOIN WAREHOUSE.COMPONENT {c} ON dc.COMPONENT_ID = {c}.COMPONENT_ID 
            LEFT JOIN WAREHOUSE.PARAMETER_SET pc ON {c}.PARAMETER_CODE = pc.PARAMETER_CODE
            LEFT JOIN WAREHOUSE.DEPLOYMENT {d} on dc.DEPLOYMENT_ID = {d}.DEPLOYMENT_ID
            WHERE {params_where}
        """

        if headers_where:
            q += f" AND {headers_where}"

        return q, q_params

