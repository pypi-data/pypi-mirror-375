import unittest
import pandas as pd
import pandas.api.types as ptypes

from template_log_parser.built_ins import built_in_process_log
from test.resources import built_in_log_file_types

from test.resources import logger

class TestBuiltInProcessLog(unittest.TestCase):
    """Defines a class to test built in process log"""
    def test_built_process_log_types(self):
        """Assert built_in_process_log returns the expected types"""
        for built_in in built_in_log_file_types:
            logger.info(f"----------Testing built_in_process_log(built_in={built_in.name})----------")
            logger.info('---Testing DF format---')
            df = built_in_process_log(
                built_in=built_in.name,
                file=built_in.sample_log_file,
                dict_format=False
            )
            self.assertIsInstance(df, pd.DataFrame, "built_in_process_log(dict_format=False) did not produce a dataframe")

            if built_in.datetime_columns:
                for datetime_column in built_in.datetime_columns:
                    if datetime_column in df.columns:
                        self.assertTrue(
                            ptypes.is_datetime64_any_dtype(df[datetime_column]),
                            f'{datetime_column} is not a proper datetime column'
                        )
                        logger.info(f"{datetime_column} is a proper datetime column")


            if built_in.column_functions:
                logger.info("Testing column functions")
                for original_column, (func, new_column) in built_in.column_functions.items():
                    self.assertTrue(
                        original_column not in df.columns,
                        f"{original_column} was not dropped"
                    )
                    logger.info(f"{original_column} has been correctly removed")

                    if type(new_column) is str:
                        self.assertTrue(
                            new_column in df.columns,
                            f"{new_column} is not present"
                        )
                        logger.info(f"{new_column} has been correctly added")

                    elif type(new_column) is list:
                        for column in new_column:
                            self.assertTrue(
                                column in df.columns,
                                f"{column} is not present"
                            )
                            logger.info(f"{column} has been correctly added")

            logger.info("---DF format Ok---")

            logger.info('---Testing dictionary format---')
            df_dict = built_in_process_log(built_in.name, built_in.sample_log_file, dict_format=True)
            self.assertIsInstance(df_dict, dict, "built_in_process_log(dict_format=True) did not produce a dictionary")

            for event, df in df_dict.items():
                logger.info(f"Event: {event}")
                if built_in.datetime_columns:
                    for datetime_column in built_in.datetime_columns:
                        if datetime_column in df.columns:
                            self.assertTrue(
                                ptypes.is_datetime64_any_dtype(df[datetime_column]),
                                f'{datetime_column} is not a proper datetime column'
                            )
                            logger.info(f"{datetime_column} is a proper datetime column")

            logger.info("---Dictionary format OK---")

            logger.info(f"----------{built_in.name}: Ok----------")

