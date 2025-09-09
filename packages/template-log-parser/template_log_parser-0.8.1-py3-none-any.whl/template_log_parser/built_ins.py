import pandas as pd
from io import BytesIO, StringIO, TextIOBase
from typing import Literal, List

from template_log_parser.log_functions import process_log

from template_log_parser.pre_df_functions import link_log_file_lines

from template_log_parser.log_type_classes import dict_built_in_log_file_types
from template_log_parser.templates.kodi_templates import kodi_line_linking_arguments


def built_in_process_log(
    built_in: Literal["debian", "kodi", "omada", "omv", "pfsense", "pihole", "synology", "ubuntu"],
    file: str | BytesIO | StringIO | TextIOBase,
    dict_format: bool = True,
    match: str | List[str] | None = None,
    eliminate: str | List[str] | None = None,
    match_type: Literal["any", "all"] = "any",
    eliminate_type: Literal["any", "all"] = "any",
) -> dict[str, pd.DataFrame] | pd.DataFrame:
    """Return a single Pandas Dataframe or dictionary of DataFrames whose keys are the log file event types,
    utilizing predefined templates.  This function is tailored to Built-In log file types using Built-In templates.

    :param built_in: built in log file type
    :type built_in: Literal["debian", "kodi", "omada", "omv", "pfsense", "pihole", "synology", "ubuntu"]

    :param file: Path to file or filelike object, most commonly in the format of some_log_process.log
    :type file: str, Path, BytesIO, StringIO, TextIOBase

    :param dict_format: (optional) Return a dictionary of DataFrames when True, one large DataFrame when False, True by default
    :type dict_format: bool

    :param match: (optional) A single word or list of words must be present within the line otherwise dropped.
    :type match: str, List[str], None

    :param eliminate: (optional) A single word or a list of words if present within line will result in it being dropped
    :type eliminate: str, List[str], None

    :param match_type: (optional) criteria to determine if any words must be present to match, or all words
    :type match_type: Literal["any", "all"]

    :param eliminate_type: (optional) criteria to determine if any words must be present to eliminate, or all words
    :type eliminate_type: Literal["any", "all"]

    :return: dict formatted as {'event_type_1': df_1, 'event_type_2': df_2, ...}, Pandas Dataframe will include all event types and all columns
    :rtype: Dict[str, Pandas.DataFrame], Pandas Dataframe

    Note:
        This function utilizes process_log()
    """
    # Determine built_in based on name attribute
    built_in_type = dict_built_in_log_file_types[built_in]

    if built_in == "kodi":
        file = link_log_file_lines(file, kodi_line_linking_arguments)

    output = process_log(
        file=file,
        templates=built_in_type.templates,
        additional_column_functions=built_in_type.column_functions,
        merge_dictionary=built_in_type.merge_events,
        datetime_columns=built_in_type.datetime_columns,
        localize_timezone_columns=built_in_type.localize_datetime_columns,
        drop_columns=True,
        dict_format=dict_format,
        match=match,
        eliminate=eliminate,
        match_type=match_type,
        eliminate_type=eliminate_type,
    )

    return output
