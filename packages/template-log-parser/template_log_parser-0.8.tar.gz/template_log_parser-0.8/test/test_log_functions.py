import unittest
import pandas as pd
import io
from contextlib import redirect_stdout, redirect_stderr

from template_log_parser.log_functions import (
    log_pre_process,
    run_functions_on_columns,
    process_event_types,
    merge_event_type_dfs,
)

from template_log_parser.column_functions import (
    split_name_and_mac,
    calc_time,
    calc_data_usage,
    isolate_ip_from_parentheses,
    split_by_delimiter,
)


from test.resources import sample_df, built_in_log_file_types
from template_log_parser.log_functions import event_type_column

from test.resources import logger

class TestLogFunctions(unittest.TestCase):
    """Defines a class to test functions that process overall log files"""

    def test_run_functions_on_columns(self):
        """Defines a test function to ensure run functions on columns is operating correctly"""


        # In order to pass arguments to column functions, kwargs dictionary is created
        data_usage_kwargs = dict(increment="GB")

        # Using all built-in column functions, add in one column that doesn't exist to ensure no error
        function_dict = {
            "column_that_does_not_exist": [len, "fake_column_name"],
            "data": [calc_data_usage, "data_MB", data_usage_kwargs],
            "client_name_and_mac": [split_name_and_mac, ["client_name", "client_mac"]],
            "time_elapsed": [calc_time, "time_min"],
            "ip_address_raw": [isolate_ip_from_parentheses, "ip_address_fixed"],
            "delimited_data": [split_by_delimiter, ["one", "two"]],
            "delimited_by_periods": [
                split_by_delimiter,
                ["period_one", "period_two"],
                dict(delimiter="."),
            ],
        }

        # Assert function returns a tuple
        self.assertIsInstance(
            run_functions_on_columns(
                sample_df(),
                additional_column_functions=function_dict,
                datetime_columns=["utc_time", "time"],
                localize_timezone_columns=["time"],
            ),
            tuple,
        )

        df, list_of_columns = run_functions_on_columns(
            sample_df(),
            additional_column_functions=function_dict,
            datetime_columns=["utc_time", "time"],
            localize_timezone_columns=["time"],
        )

        # Assert variables are df and list respectively
        self.assertIsInstance(df, pd.DataFrame)
        self.assertIsInstance(list_of_columns, list)

        # Assert the expected columns are present
        self.assertTrue(
            (
                [column for column in sample_df().columns]
                + [
                    "data_MB",
                    "client_name",
                    "client_mac",
                    "time_min",
                    "ip_address_fixed",
                    "one",
                    "two",
                    "period_one",
                    "period_two",
                ]
                == df.columns
            ).all()
        )

        # Assert newly created columns have the correct data types
        for index, row in df.iterrows():
            self.assertIsInstance(row["data_MB"], float)
            self.assertIsInstance(row["client_name"], str)
            self.assertIsInstance(row["client_mac"], str)
            self.assertIsInstance(row["time_min"], float)
            self.assertIsInstance(row["ip_address_fixed"], str)
            self.assertIsInstance(row["one"], str)
            self.assertIsInstance(row["two"], str)

        # Assert timezone and no timezone for applicable datetime columns
        self.assertTrue(df["utc_time"].dt.tz is not None)
        self.assertTrue(df["time"].dt.tz is None)

        # Assert return list of columns is equal to the keys from the column function dict EXCEPT 'column_that_does_not_exist'
        self.assertEqual(
            list_of_columns,
            [
                column
                for column in function_dict.keys()
                if column != "column_that_does_not_exist"
            ],
        )

        # If a df is passed without any arguments, the same df should return along with an empty list
        no_changes_df, empty_list = run_functions_on_columns(df.copy())
        # Return df should equal the original df
        self.assertTrue(no_changes_df.equals(df))
        self.assertTrue(len(empty_list) == 0)

        # Exceptions

        # Improper configuration
        self.assertRaises(
            ValueError,
            run_functions_on_columns,
            sample_df(),
            {
                "data": [
                    len,
                ]
            },
        )

        # Function not callable
        self.assertRaises(
            TypeError,
            run_functions_on_columns,
            sample_df(),
            {"data": ["not_a_function", "data_transformed"]},
        )

        # Invalid type for new column names
        self.assertRaises(
            RuntimeError,
            run_functions_on_columns,
            sample_df(),
            {"client_name_and_mac": [len, 1]},
        )

        # General failure runtime
        self.assertRaises(
            RuntimeError,
            run_functions_on_columns,
            sample_df(),
            {
                "client_name_and_mac": [
                    split_name_and_mac,
                    ["client_name", "client_mac", "fake_column"],
                ]
            },
        )

        # dt conversion error, dt localization error, nothing raised, just print statements
        f = io.StringIO()
        f_err = io.StringIO()

        with redirect_stdout(f), redirect_stderr(f_err):
            run_functions_on_columns(sample_df(), {}, ["data"], ["data"])

        print_statement = f.getvalue()

        self.assertTrue("Error converting column" in print_statement)
        self.assertTrue("Error localizing timezone in column" in print_statement)

    def test_process_event_types(self):
        """Defines a function to assert that process_event_types returns a dictionary of dfs correctly"""

        # Using all built ins
        for built_in in built_in_log_file_types:
            logger.info(f"{built_in.name}: test process_event_types")
            # Create sample df with correct three columns
            df = log_pre_process(built_in.sample_log_file, built_in.templates)

            # First run, using drop columns, and setting datetime columns
            logger.info("Using drop columns")
            dict_of_df = process_event_types(
                df.copy(),
                built_in.column_functions,
                datetime_columns=built_in.datetime_columns,
                localize_timezone_columns=built_in.localize_datetime_columns,
                drop_columns=True,
            )

            # Assert a dictionary was returned
            self.assertIsInstance(dict_of_df, dict)
            # Assert list of dictionaries matches a list of unique event types from the original df
            self.assertEqual(
                (list(dict_of_df.keys())), df[event_type_column].unique().tolist()
            )

            # Set of columns that were processed
            if built_in.column_functions:
                drop_columns_list = list(built_in.column_functions.keys())
                drop_columns = set(drop_columns_list)
            else:
                drop_columns_list = []
                drop_columns = set(drop_columns_list)

            # Loop over all dfs
            for df in dict_of_df.values():
                # Assert each value is a pandas DataFrame
                self.assertIsInstance(df, pd.DataFrame)
                # Assert that the intersection of the two sets (drop_columns and df.columns) is empty, having len 0
                # Meaning columns were dropped correctly
                self.assertTrue(len(drop_columns.intersection(set(df.columns))) == 0)
                # Assert timezone and no timezone for applicable datetime columns, "Other" df wouldn't have these columns
                if built_in.datetime_columns:
                    for column in built_in.datetime_columns:
                        if column in df.columns:
                            # Assert column is ANY form of pandas datetime, accounting for all formats
                            self.assertTrue(
                                pd.api.types.is_datetime64_any_dtype(df[column])
                            )

            logger.info("ok")
            # New df
            logger.info("Not using drop columns")
            new_df = log_pre_process(built_in.sample_log_file, built_in.templates)
            # Do not drop columns on this run
            non_drop_dict_of_df = process_event_types(
                new_df.copy(), built_in.column_functions, drop_columns=False
            )
            # Not all processed columns would be present in every df, so this step creates one large df
            concat_df = pd.concat([df for df in non_drop_dict_of_df.values()])
            # Verify that every column is still present within the large df, meaning not dropped
            for column in drop_columns_list:
                self.assertTrue(column in concat_df.columns)
            logger.info("ok")
            logger.info(f"{built_in.name}: process_event_types ok")

    def test_merge_event_type_dfs(self):
        """Defines a test function to assert that dfs specified to be merged are done so correctly"""
        # Using all built_ins
        for built_in in built_in_log_file_types:
            # First create dictionary of dfs:
            pre_df = log_pre_process(built_in.sample_log_file, built_in.templates)
            # No column manipulation or dropping for this test as it is addressed in other test functions
            dict_of_dfs = process_event_types(pre_df.copy())

            # Merge events, if dictionary is present
            if built_in.merge_events:
                dict_of_dfs = merge_event_type_dfs(dict_of_dfs, built_in.merge_events)
                # After the procedure assert the new_df name is present as a key
                for new_df, old_dfs in built_in.merge_events.items():
                    self.assertTrue(new_df in dict_of_dfs.keys())
                    # Assert old df names are no longer present as keys
                    for old_df in old_dfs:
                        self.assertTrue(old_df not in dict_of_dfs.keys())
