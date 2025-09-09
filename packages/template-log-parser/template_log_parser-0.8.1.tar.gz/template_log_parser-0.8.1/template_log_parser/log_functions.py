import pandas as pd
import numpy as np
from typing import Callable, Literal, Dict, List, Union, Optional, Any, Tuple
from io import BytesIO, StringIO, TextIOBase
from pathlib import Path

from template_log_parser.templates.definitions import (
    event_data_column,
    event_type_column,
    other_type_column,
    unparsed_text_column,
    SimpleTemplate
)

# set display options
pd.options.display.max_columns = 40
pd.options.display.width = 120
pd.set_option("max_colwidth", 400)


def _pre_filter_log_file(
    df: pd.DataFrame,
    column: str,
    match: str | List[str] | None = None,
    eliminate: str | List[str] | None = None,
    match_type: Literal["any", "all"] = "any",
    eliminate_type: Literal["any", "all"] = "any",
) -> pd.DataFrame:
    """Filter a DataFrame based on inclusion (match) and exclusion (eliminate) string criteria.

    Eliminate applied second, and therefore supersedes any words in match should duplicate criteria exist.

    :param df: DataFrame for filtering, single column of raw text
    :type df: Pandas.DataFrame

    :param column: name of single column
    :type column: str

    :param match: (optional) A single word or list of words must be present within the line otherwise dropped.
    :type match: str, List[str], None

    :param eliminate: (optional) A single word or a list of words if present within line will result in it being dropped
    :type eliminate: str, List[str], None

    :param match_type: (optional) criteria to determine if any words must be present to match, or all words
    :type match_type: Literal["any", "all"]

    :param eliminate_type: (optional) criteria to determine if any words must be present to eliminate, or all words
    :type eliminate_type: Literal["any", "all"]

    :return: Dataframe filtered by match and/or eliminate criteria
    :rtype: Pandas.DataFrame

    :raises ValueError: If the specified column does not exist in the DataFrame.
    """
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame.")

    series = df[column].astype(str)

    if match:
        if isinstance(match, str):
            match = [match]
        match = [str(m) for m in match]
        if match_type.lower() == "all":
            matching = np.logical_and.reduce(
                [series.str.contains(m, regex=False, na=False) for m in match]
            )
        else:
            matching = np.logical_or.reduce(
                [series.str.contains(m, regex=False, na=False) for m in match]
            )
        df = df[matching]

    if eliminate:
        if isinstance(eliminate, str):
            eliminate = [eliminate]
        eliminate = [str(e) for e in eliminate]
        if eliminate_type.lower() == "all":
            to_eliminate = np.logical_and.reduce(
                [series.str.contains(e, regex=False, na=False) for e in eliminate]
            )
        else:
            to_eliminate = np.logical_or.reduce(
                [series.str.contains(e, regex=False, na=False) for e in eliminate]
            )
        df = df[~to_eliminate]

    return df


def parse_function(
    event: str, templates: list[SimpleTemplate]
) -> dict[str, str]:
    """Return a dictionary of information parsed from a log file string based on matching template.

    :param event: String data, should ideally match a repeated format throughout a text file
    :type event: str

    :param templates: formatted as a list of namedtuple (SimpleTemplate) [(compiled_template, event_type, search_string), ...]
    :type templates: list[SimpleTemplate]

    :return: dictionary containing:
        - event_type along parsed values if successful.  Otherwise, {"Unparsed_text": original_text, "event_type": "Other"}
    :rtype: dict[str, str]
    """
    for template_tuple in templates:
        if template_tuple.search_string not in event:
            continue

        parsed_result = template_tuple.template.parse(event)

        if parsed_result and len(parsed_result.named) == len(template_tuple.template.named_fields):
            output = parsed_result.named
            output[event_type_column] = template_tuple.event_type
            return output

    return {unparsed_text_column: event, event_type_column: other_type_column}


def log_pre_process(
        file:str | BytesIO | StringIO | TextIOBase,
        templates: list[SimpleTemplate],
        match: str | list[str] | None = None,
        eliminate: str | list[str] | None = None,
        match_type: Literal["any", "all"] = "any",
        eliminate_type: Literal["any", "all"] = "any",
        ) -> pd.DataFrame:
    """
    Return a Pandas DataFrame with named columns as specified by templates

    :param file: Path to file or filelike object, most commonly in the format of some_log_process.log
    :type file: str, Path, BytesIO, StringIO, TextIOBase

    :param templates: formatted as a list of namedtuple (SimpleTemplate) [(compiled_template, event_type, search_string), ...]
    :type templates: list[SimpleTemplate]

    :param match: (optional) A single word or list of words must be present within the line otherwise dropped.
    :type match: str, list[str], None

    :param eliminate: (optional) A single word or a list of words if present within line will result in it being dropped
    :type eliminate: str, list[str], None

    :param match_type: (optional) criteria to determine if any words must be present to match, or all words
    :type match_type: Literal["any", "all"]

    :param eliminate_type: (optional) criteria to determine if any words must be present to eliminate, or all words
    :type eliminate_type: Literal["any", "all"]

    :return: DataFrame with columns found in matching templates
    :rtype: Pandas.DataFrame

    :raise ValueError: If wrong file type is provided

    :note:
        eliminate applied second, and therefore supersedes any words in match should duplicate criteria exist.
    """

    def get_lines_from_file(f: Union[str, Path, BytesIO, StringIO, TextIOBase]) -> List[str]:
        if isinstance(f, (str, Path)):
            with open(f, 'r', encoding='utf-8') as file_obj:
                return file_obj.read().splitlines()
        elif isinstance(f, BytesIO):
            f.seek(0)
            return f.read().decode('utf-8').splitlines()
        elif isinstance(f, (StringIO, TextIOBase)):
            f.seek(0)
            return f.read().splitlines()
        else:
            raise ValueError("Unsupported file type. Must be str, Path, BytesIO, StringIO, or TextIOBase.")

    parsed_results = []
    for line in get_lines_from_file(file):
        line = line.strip()
        parsed_data = parse_function(line, templates)
        parsed_data[event_data_column] = line
        parsed_results.append(parsed_data)

    df =  pd.DataFrame(parsed_results)

    df = _pre_filter_log_file(
        df,
        column=event_data_column,
        match=match,
        eliminate=eliminate,
        match_type=match_type,
        eliminate_type=eliminate_type,
    )

    return df


def run_functions_on_columns(
    df: pd.DataFrame,
    additional_column_functions: Optional[Dict[str, List[Any]]] = None,
    datetime_columns: Optional[List[str]] = None,
    localize_timezone_columns: Optional[List[str]] = None,
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Return a tuple with a Pandas Dataframe (having newly created columns based on run functions)
    along with a list of columns that were processed.

    :param df: DataFrame for processing
    :type df: Pandas.DataFrame

    :param additional_column_functions: (optional) {column: [function, [new_column(s)], kwargs], ...}
    :type additional_column_functions: dict[str, list[Callable, str, list[str] or dict[str, Any]]]

    :param datetime_columns: (optional) Columns to be converted using Pandas.to_datetime()
    :type datetime_columns: List[str]

    :param localize_timezone_columns: (optional) Columns to drop timezone
    :type localize_timezone_columns: List[str]

    :return: DataFrame with newly processed columns, list of columns that were processed
    :rtype: tuple[Pandas.DataFrame, List[str]]

    :raises ValueError: If column or transformation config is invalid.
    :raises TypeError: If target column names are not str or list[str].
    :raises RuntimeError: If a function fails during application.

    :example:
        my_kwargs = dict(keyword_1='some_string', keyword_2=1000, keyword_3=[1,2,3])

        my_column_functions = {
            'column_to_run_function_on': [function, 'new_column_name'],
            'column_2_to_run_function_on': [create_two_columns, ['new_col_2, 'new_col_3']],
            'column_4_to_run_function_on': [function_with_kwargs, 'new_col_4', my_kwargs],
            }

    :note:
        This function (excepting datetime columns) is designed to create new columns and provide a list
        of columns to be dropped at a later stage.  One can create custom functions, or use the included functions.
        An example of this would be the calc_time() function which can convert strings such as '1h12m'
        to integer 72.

        Sometimes a function is designed to expand one column into two or more new columns.
        In this instance, one can provide a list of new column names. Please see example.

        If only df parameter is supplied, function will return the original df and an empty list

    """
    processed_columns = []

    if additional_column_functions:
        for column, config in additional_column_functions.items():
            if column not in df.columns:
                continue

            if not isinstance(config, list) or not (2 <= len(config) <= 3):
                raise ValueError(
                    f"Invalid configuration for column '{column}': {config}"
                )

            col_func = config[0]
            new_cols = config[1]
            optional_kwargs = config[2] if len(config) == 3 else {}

            if not callable(col_func):
                raise TypeError(
                    f"The function provided for '{column}' is not callable: {col_func}"
                )

            try:
                if isinstance(new_cols, str):
                    # Single column
                    df[new_cols] = df.apply(
                        lambda row: col_func(row[column], **optional_kwargs), axis=1
                    )

                elif isinstance(new_cols, list):
                    # Multiple new columns (expansion)
                    result = df.apply(
                        lambda row: col_func(row[column], **optional_kwargs),
                        axis=1,
                        result_type="expand",
                    )

                    if result.shape[1] != len(new_cols):
                        raise ValueError(
                            f"Function for column '{column}' returned {result.shape[1]} columns, "
                            f"but {len(new_cols)} new column names were provided: {new_cols}"
                        )

                    result.columns = new_cols
                    df = pd.concat([df, result], axis=1)

                else:
                    raise TypeError(f"Invalid type for new column names: {new_cols}")

                processed_columns.append(column)

            except Exception as e:
                raise RuntimeError(
                    f"Error applying function to column '{column}': {e}\n"
                    f"Config: {config}"
                ) from e

    # Convert datetime columns
    if datetime_columns:
        for col in datetime_columns:
            if col in df.columns:
                try:
                    df[col] = pd.to_datetime(df[col])
                except Exception as e:
                    print(f"Error converting column '{col}' to datetime: {e}")

    # Localize (remove) timezone info
    if localize_timezone_columns:
        for col in localize_timezone_columns:
            if col in df.columns:
                try:
                    df[col] = df[col].dt.tz_localize(None)
                except Exception as e:
                    print(f"Error localizing timezone in column '{col}': {e}")

    return df, processed_columns


def process_event_types(
    df: pd.DataFrame,
    additional_column_functions: None
    | dict[str, list[Callable | str | list[str] | dict[str, int]]] = None,
    datetime_columns: None | list[str] = None,
    localize_timezone_columns: None | list[str] = None,
    drop_columns: bool = True,
) -> dict[str, pd.DataFrame]:
    """Return a dictionary of Pandas DataFrames whose keys are event types

    :param df: DataFrame for processing
    :type df: Pandas.DataFrame

    :param additional_column_functions: (optional) {column: [function, [new_column(s)], kwargs], ...}
    :type additional_column_functions: dict[str, list[Callable, str, list[str] or dict[str, Any]]]

    :param datetime_columns: (optional) Columns to be converted using Pandas.to_datetime()
    :type datetime_columns: List[str]

    :param localize_timezone_columns: (optional) Columns to drop timezone
    :type localize_timezone_columns: List[str]

    :param drop_columns: (optional) If True, 'event_data' will be dropped along with columns processed by additional_column_functions, True by default
    :type drop_columns: bool

    :return: DataFrame Dictionary formatted as {'event_type_1': df_1, 'event_type_2': df_2, ...}
    :rtype: dict
    """
    final_dict = {}
    # For every unique event_type, create a copy df, remove empty columns for that event type
    for event_type in df[event_type_column].unique().tolist():
        event_df = df[df[event_type_column] == event_type].dropna(axis=1).copy()

        # Default Columns to be dropped
        columns_to_drop = [event_data_column]

        # Process columns
        event_df, additional_drop_columns = run_functions_on_columns(
            df=event_df,
            additional_column_functions=additional_column_functions,
            datetime_columns=datetime_columns,
            localize_timezone_columns=localize_timezone_columns,
        )
        columns_to_drop.extend(additional_drop_columns)

        if drop_columns:
            event_df = event_df.drop(columns=columns_to_drop)
        # Add the df to the final dict with a key of its event type
        final_dict[event_type] = event_df

    return final_dict


def merge_event_type_dfs(
    df_dictionary: Dict[str, pd.DataFrame], merge_dictionary: Dict[str, List[str]]
) -> Dict[str, pd.DataFrame]:
    """Return a dictionary of Pandas DataFrames whose keys are the event types, after merging specified event_types and
    deleting the old DataFrames

    :param df_dictionary: Dictionary of DataFrames, formatted as {'event_type_1': df_1, 'event_type_2': df_2, ...}
    :type df_dictionary: dict
    :param merge_dictionary: Formatted as {'new_df_name', ['event_type_1', 'event_type_2', ...], ...}
    :type merge_dictionary: dict

    :return: Dictionary of DataFrames formatted as {'new_df_name': new_df, 'event_type_3': df_3, ...}
    :rtype: dict

    :note:
        Certain log events are categorically similar despite being parsed with different templates.
        For example, client wireless connections and client hardwired connections might be easier to analyze when
        grouped into the same DataFrame.

        This function performs that concatenation and deletes the old DataFrames.
    """

    for new_df_name, list_of_existing_dfs in merge_dictionary.items():
        # Empty list to be filled with dfs that will be merged under a new key name
        list_of_dfs_to_concatenate = []

        for old_name in list_of_existing_dfs:
            # Check to ensure that a key exists for each type of df to prevent an error
            if old_name in df_dictionary.keys():
                # If so add it to the list and remove it from the main dictionary
                list_of_dfs_to_concatenate.append(df_dictionary[old_name])
                del df_dictionary[old_name]
        # Assuming at least one df got appended
        if list_of_dfs_to_concatenate:
            # Create new concat df
            df_dictionary[new_df_name] = pd.concat(list_of_dfs_to_concatenate)

    return df_dictionary


def process_log(
    file: str | BytesIO | StringIO | TextIOBase,
    templates: list[SimpleTemplate],
    additional_column_functions: Optional[Dict[str, List[Any]]] = None,
    merge_dictionary: None | dict[str, list[str]] = None,
    datetime_columns: Optional[List[str]] = None,
    localize_timezone_columns: Optional[List[str]] = None,
    drop_columns: bool = True,
    dict_format: bool = True,
    match: str | List[str] | None = None,
    eliminate: str | List[str] | None = None,
    match_type: Literal["any", "all"] = "any",
    eliminate_type: Literal["any", "all"] = "any",
) -> dict[str, pd.DataFrame] | pd.DataFrame:
    """Return a single Pandas Dataframe or dictionary of DataFrames whose keys are the log file event types,
    utilizing templates.

    :param file: Path to file or filelike object, most commonly in the format of some_log_process.log
    :type file: str, Path, BytesIO, StringIO, TextIOBase

    :param templates: formatted as a list of namedtuple (SimpleTemplate) [(compiled_template, event_type, search_string), ...]
    :type templates: list[SimpleTemplate]

    :param additional_column_functions: (optional) {column: [function, [new_column(s)], kwargs], ...}
    :type additional_column_functions: dict[str, list[Callable, str, list[str] or dict[str, Any]]]

    :param merge_dictionary: Formatted as {'new_df_name', ['existing_df_1', 'existing_df_2', ...], ...}
    :type merge_dictionary: dict

    :param datetime_columns: (optional) Columns to be converted using Pandas.to_datetime()
    :type datetime_columns: List[str]

    :param localize_timezone_columns: (optional) Columns to drop timezone
    :type localize_timezone_columns: List[str]

    :param drop_columns: (optional) If True, 'parsed_info', 'event_data' will be dropped along with processed columns, True by default
    :type drop_columns: bool

    :param dict_format: Return a dictionary of DataFrames when True, one large DataFrame when False, True by default
    :type dict_format: (optional) bool

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

    :note:
        This function incorporates several smaller functions.
        For more specific information, please see help for individual functions:

        parse_function() \n
        log_pre_process() \n
        run_functions_on_columns() \n
        process_event_types() \n
        merge_event_types() \n
    """
    # Initial parsing
    pre_df = log_pre_process(
        file=file,
        templates=templates,
        match=match,
        eliminate=eliminate,
        match_type=match_type,
        eliminate_type=eliminate_type
    )

    # Process each event type
    dict_of_dfs = process_event_types(
        pre_df,
        additional_column_functions=additional_column_functions,
        datetime_columns=datetime_columns,
        localize_timezone_columns=localize_timezone_columns,
        drop_columns=drop_columns,
    )

    # Merge event DataFrames for consolidation, if specified
    if merge_dictionary and dict_format:
        dict_of_dfs = merge_event_type_dfs(
            df_dictionary=dict_of_dfs,
            merge_dictionary=merge_dictionary
        )

    # If dictionary format is False, all dataframes will be concatenated into one, with many NaN columns
    if not dict_format:
        if len(dict_of_dfs) == 0:
            dict_of_dfs = pd.DataFrame(dict_of_dfs)
        else:
            dict_of_dfs = pd.concat([df for df in dict_of_dfs.values()])

    return dict_of_dfs
