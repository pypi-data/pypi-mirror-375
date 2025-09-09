import unittest
import pandas as pd
from io import StringIO, BytesIO

from parse import compile as parse_compile

from template_log_parser.templates.definitions import SimpleTemplate

from template_log_parser.log_functions import (
    _pre_filter_log_file,
    parse_function,
    log_pre_process,
)

from template_log_parser.log_functions import (
    event_type_column,
    event_data_column,
    other_type_column,
    unparsed_text_column,
)

from test.resources import built_in_log_file_types, logger

class TestPreProcessFunctions(unittest.TestCase):
    """Defines a class to test functions that pre-process overall log files"""

    def test_pre_filter_log_file(self):
        """Test function to assert that _pre_filter_log_file correctly filters a DataFrame"""
        starting_data = {
            event_data_column: [
                "FirstName",
                "LastName",
                "MiddleName",
                "firstname",
                "lastname",
                "middlename",
                "John Smith",
                "Earth",
                "Mars",
                "FirstName and Lastname",
            ]
        }

        df = pd.DataFrame(starting_data)

        match_single = _pre_filter_log_file(
            df, column=event_data_column, match="Name", match_type="all"
        )
        self.assertTrue(4 == match_single.shape[0])
        for index, row in match_single.iterrows():
            self.assertTrue("Name" in row[event_data_column])

        match_list_any = _pre_filter_log_file(
            df, column=event_data_column, match=["Name", "name"], match_type="any"
        )
        self.assertTrue(7 == match_list_any.shape[0])
        for index, row in match_list_any.iterrows():
            self.assertTrue(
                "Name" in row[event_data_column] or "name" in row[event_data_column]
            )

        match_list_all = _pre_filter_log_file(
            df, column=event_data_column, match=["First", "Last"], match_type="all"
        )
        self.assertTrue(1 == match_list_all.shape[0])
        for index, row in match_list_all.iterrows():
            self.assertTrue(
                "First" in row[event_data_column] and "Last" in row[event_data_column]
            )

        eliminate_single = _pre_filter_log_file(
            df, column=event_data_column, eliminate="First", match_type="any"
        )
        self.assertTrue(8 == eliminate_single.shape[0])
        for index, row in eliminate_single.iterrows():
            self.assertTrue("First" not in row[event_data_column])

        eliminate_list_any = _pre_filter_log_file(
            df,
            column=event_data_column,
            eliminate=["First", "Last"],
            eliminate_type="any",
        )
        self.assertTrue(7 == eliminate_list_any.shape[0])
        for index, row in eliminate_list_any.iterrows():
            self.assertTrue(
                "First" not in row[event_data_column]
                or "Last" not in row[event_data_column]
            )

        eliminate_list_all = _pre_filter_log_file(
            df,
            column=event_data_column,
            eliminate=["Name", "name"],
            eliminate_type="all",
        )

        self.assertTrue(9 == eliminate_list_all.shape[0])
        for index, row in eliminate_list_any.iterrows():
            if "Name" in row[event_data_column]:
                self.assertTrue("name" not in row[event_data_column])
            elif "name" in row[event_data_column]:
                self.assertTrue("Name" not in row[event_data_column])

        invalid_column = "Does Not Exist"
        self.assertRaises(ValueError, _pre_filter_log_file, df, invalid_column)

    def test_parse_function(self):
        """Test function to assert that parse function is returning a string event type and a dictionary of results"""
        # Known event type with a verified template
        # Should return tuple of string and dict respectively
        simple_event = (
            "2024-09-12T00:28:49.037352+01:00 gen_controller  2024-09-11 16:28:44 Controller - - - "
            "user logged in to the controller from 172.0.0.1."
        )

        temp = (
            "{timestamp} {controller_name}  {local_time} Controller - - - "
            "{username} logged in to the controller from {ip}."
        )

        simple_template_list = [SimpleTemplate(template=parse_compile(temp), event_type="login", search_string="logged in")]

        results = parse_function(simple_event, simple_template_list)
        self.assertIsInstance(results, dict)
        self.assertEqual(results[event_type_column], "login")

        # Should return tuple, then string and dict respectively
        anomalous_event = "This event does not match any template."
        # Unknown event type should also pass without error, return dict
        results_2 = parse_function(anomalous_event, simple_template_list)
        self.assertIsInstance(results_2, dict)
        # Should return other event type
        self.assertEqual(results_2[event_type_column], other_type_column)
        # The key to its dict should be unparsed_text_column, event_type_column
        self.assertEqual(list(results_2.keys()), [unparsed_text_column, event_type_column])

    def test_log_pre_process(self):
        """Test function to assert that log_pre_process returns a Pandas DataFrame with the correct three columns"""

        # Check against all built-in log file types
        for built_in in built_in_log_file_types:
            file_types = list()
            file_types.append(built_in.sample_log_file) # String path

            with open(built_in.sample_log_file, 'rb') as f:
                bytes_io_file = BytesIO(f.read())
                file_types.append(bytes_io_file)

            with open(built_in.sample_log_file, 'r') as f:
                lines = f.read()
                string_io_file = StringIO(lines)
                file_types.append(string_io_file)

            logger.info(f"{built_in.name}: test log_pre_process")
            # Generate pre_process df using built_in sample_log_file and templates
            for file in file_types:
                df = log_pre_process(file=file, templates=built_in.templates)
                # Assert df instance
                self.assertIsInstance(df, pd.DataFrame)

                # Assert df has the same number of lines as the original log file
                logger.info("checking log file length against Dataframe shape")
                with open(built_in.sample_log_file, "r") as raw_log:
                    lines = len(raw_log.readlines())
                    logger.debug(f"lines in logfile: {lines}")
                    self.assertEqual(lines, df.shape[0])
                    logger.debug(f"rows in dataframe: {df.shape[0]}")
                    # Assert template dictionary has the same number of items as the log file has lines
                    self.assertEqual(len(built_in.templates), lines)
                    logger.debug(f"length of template dictionary: {len(built_in.templates)}")
                # Print all lines that are not accounted for by templates
                other = df[df[event_type_column] == other_type_column]
                logger.debug(f"Unparsed Lines: {other}")

                # Assert no "Other" event types
                self.assertTrue(other_type_column not in df[event_type_column].tolist())

                expected_event_types = sorted(
                    list([event[1] for event in built_in.templates])
                )
                actual_event_types = sorted(df[event_type_column].tolist())
                logger.debug(
                    f"Expected event types ({len(expected_event_types)}): {expected_event_types}"
                )
                logger.debug(
                    f"Actual event types ({len(actual_event_types)}): {actual_event_types}"
                )

                # Assert all event types are present in the df, equal to the template dictionary values, third item
                self.assertEqual(
                    expected_event_types,
                    actual_event_types,
                )
                logger.info("All event types accounted for")

                improper_file_type = {}
                self.assertRaises(
                    ValueError,
                    log_pre_process,
                    improper_file_type,
                    built_in.templates
                )

                logger.info(f"{built_in.name}: log_pre_process ok")
