import unittest

from template_log_parser.column_functions import (
    split_name_and_mac,
    calc_time,
    calc_data_usage,
    isolate_ip_from_parentheses,
    split_by_delimiter,
)



class TestColumnFunctions(unittest.TestCase):
    """Defines a class to test functions that are run on columns"""

    def test_split_name_and_mac(self):
        """Test function to determine name:mac returns two strings, unnamed if client name not included"""
        client_name = "client_device"

        mac_without_name = "10-F7-D6-07-BD-8A"
        with_name = client_name + ":" + mac_without_name

        # In any case a tuple should be returned
        self.assertIsInstance(split_name_and_mac(mac_without_name), tuple)
        self.assertIsInstance(split_name_and_mac(with_name), tuple)

        no_name, no_name_mac = split_name_and_mac(mac_without_name)
        name, mac = split_name_and_mac(with_name)

        # All items within tuples should be strings
        for item in [no_name, no_name_mac, name, mac]:
            self.assertIsInstance(item, str)

        # Assert correct values for each variable
        self.assertEqual(no_name, "unnamed")
        self.assertEqual(no_name_mac, mac_without_name)
        self.assertEqual(name, client_name)
        self.assertEqual(mac, mac_without_name)

    def test_calc_time(self):
        """Test function to ensure correct float values are returned from generic time counts"""
        time_with_hours = "1h30m"
        time_minutes = "15m"
        # times below one minute will get rounded up to one for simplicity
        time_seconds = "60s"

        time_from_hours_to_seconds = calc_time(time_with_hours, increment="seconds")
        time_from_hours_to_minutes = calc_time(time_with_hours, increment="minutes")
        time_from_hours_to_hours = calc_time(time_with_hours, increment="hours")

        time_from_minutes_to_seconds = calc_time(time_minutes, increment="seconds")
        time_from_minutes_to_minutes = calc_time(time_minutes, increment="minutes")
        time_from_minutes_to_hours = calc_time(time_minutes, increment="hours")

        time_from_seconds_to_seconds = calc_time(time_seconds, increment="seconds")
        time_from_seconds_to_minutes = calc_time(time_seconds, increment="minutes")
        time_from_seconds_to_hours = calc_time(time_seconds, increment="hours")

        all_conversions = [
            time_from_hours_to_seconds,
            time_from_hours_to_minutes,
            time_from_hours_to_hours,
            time_from_minutes_to_seconds,
            time_from_minutes_to_minutes,
            time_from_minutes_to_hours,
            time_from_seconds_to_seconds,
            time_from_seconds_to_minutes,
            time_from_seconds_to_hours,
        ]

        # Assert function returns floats in all instances
        for conversion in all_conversions:
            self.assertIsInstance(conversion, float)

        correct_values = [5400, 90, 1.5, 900, 15, 0.25, 60, 1, (1 / 60)]

        for tup in zip(all_conversions, correct_values):
            self.assertEqual(tup[0], tup[1])

    def test_calc_data_usage(self):
        """Defines a test function to ensure correct MB float values are return from generic data usage strings"""
        bytes_amount = "100 bytes"
        kilobytes = "500KB"
        megabytes = "250 MB"
        gigabytes = "10GB"

        data_from_bytes_to_KB = calc_data_usage(bytes_amount, "KB")
        data_from_bytes_to_MB = calc_data_usage(bytes_amount, "MB")
        data_from_bytes_to_GB = calc_data_usage(bytes_amount, "GB")

        data_from_kilobytes_to_KB = calc_data_usage(kilobytes, "KB")
        data_from_kilobytes_to_MB = calc_data_usage(kilobytes, "MB")
        data_from_kilobytes_to_GB = calc_data_usage(kilobytes, "GB")

        data_from_megabytes_to_KB = calc_data_usage(megabytes, "KB")
        data_from_megabytes_to_MB = calc_data_usage(megabytes, "MB")
        data_from_megabytes_to_GB = calc_data_usage(megabytes, "GB")

        data_from_gigabytes_to_KB = calc_data_usage(gigabytes, "KB")
        data_from_gigabytes_to_MB = calc_data_usage(gigabytes, "MB")
        data_from_gigabytes_to_GB = calc_data_usage(gigabytes, "GB")

        all_conversions = [
            data_from_bytes_to_KB,
            data_from_bytes_to_MB,
            data_from_bytes_to_GB,
            data_from_kilobytes_to_KB,
            data_from_kilobytes_to_MB,
            data_from_kilobytes_to_GB,
            data_from_megabytes_to_KB,
            data_from_megabytes_to_MB,
            data_from_megabytes_to_GB,
            data_from_gigabytes_to_KB,
            data_from_gigabytes_to_MB,
            data_from_gigabytes_to_GB,
        ]

        for conversion in all_conversions:
            # Assert functions returns float values
            self.assertIsInstance(conversion, float)

        correct_values = [
            0.1,
            1e-4,
            1e-7,
            500,
            0.5,
            0.0005,
            250000,
            250,
            0.25,
            1e7,
            10000,
            10,
        ]

        for tup in zip(all_conversions, correct_values):
            self.assertEqual(tup[0], tup[1])

    def test_isolate_ip_from_parentheses(self):
        """Defines a test function to ensure ip addresses are being correctly extracted from string data"""
        ip_with_workgroup = "WORKGROUP(10.20.10.39)"
        ip_in_parentheses = "(10.45.1.32)"
        ipv6_with_client = "client1(fb71::8520:aa9e:dad4:62f3)"
        ipv4_with_client = "client2(10.0.0.101)"
        clean_ip = "127.0.0.1"

        ip_with_workgroup_isolated = isolate_ip_from_parentheses(ip_with_workgroup)
        ip_in_parentheses_isolated = isolate_ip_from_parentheses(ip_in_parentheses)
        ipv6_with_client_isolated = isolate_ip_from_parentheses(ipv6_with_client)
        ipv4_with_client_isolated = isolate_ip_from_parentheses(ipv4_with_client)
        clean_ip_isolated = isolate_ip_from_parentheses(clean_ip)

        self.assertEqual(ip_with_workgroup_isolated, "10.20.10.39")
        self.assertEqual(ip_in_parentheses_isolated, "10.45.1.32")
        self.assertEqual(ipv6_with_client_isolated, "fb71::8520:aa9e:dad4:62f3")
        self.assertEqual(ipv4_with_client_isolated, "10.0.0.101")
        self.assertEqual(clean_ip_isolated, clean_ip)

    def test_split_by_delimiter(self):
        """Defines a test function to ensure split_by_delimiter correctly returns a list of strings"""
        delimited_data = "this, is, five, items, long"
        split_data = split_by_delimiter(delimited_data)

        self.assertIsInstance(split_data, list)
        self.assertEqual(len(split_data), 5)
        for item in split_data:
            self.assertIsInstance(item, str)
