# Pre-built functions to run on columns that need additional processing


def split_name_and_mac(name_and_mac: str) -> tuple[str, str]:
    """Return a tuple of two strings including client name and client mac address after splitting string at colon.

    :param name_and_mac: must either be in the format of 'my_pc:00-00-00-00-00-00', or simply '00-00-00-00-00-00'
    :type name_and_mac: str

    :return: (client_name, client_mac_address) or ('unnamed', client_mac_address) if string includes only mac address
    :rtype: tup

    """
    # Split
    client_name_and_mac = name_and_mac.split(":")
    # Unnamed by default
    client_name = "unnamed"
    # client name will be extracted if present(len == 2), otherwise it will remain unnamed
    if len(client_name_and_mac) == 2:
        client_name = client_name_and_mac[0]
        client_mac = client_name_and_mac[1]

    # This leaves the possibility open that splits lists of three items or greater will be processed incorrectly
    # This issue should be addressed at the template stage and not by this function
    else:
        client_mac = client_name_and_mac[0]

    return client_name, client_mac


def calc_time(time_string: str, increment: str = "minutes") -> float:
    """Return float value of time in specified increment deciphered and converted from string data
    including h,m,s, converted to seconds, minutes, or hours

    :param time_string: Formatted as '23h4m', '47m', or '45s'
    :type time_string: str
    :param increment: (optional) Type of desired time conversion, default minutes
    :type increment: str {'seconds', 'minutes', 'hours'}

    :return: Value of time converted to requested increment
    :rtype: float
    """
    # Default conversion to minutes, values that will be used to divide once data is converted to a numeric type
    s, m, h = 60, 1, 1
    time = 0
    if increment == "seconds":
        s, m, h = 1, (1 / 60), (1 / 3600)
    elif increment == "minutes":
        s, m, h = 60, 1, (1 / 60)
    elif increment == "hours":
        s, m, h = 3600, 60, 1
    # Time presented in seconds ex: '45s'
    if "s" in time_string:
        # Divide by the appropriate conversion number
        time = int(time_string.replace("s", "")) / s

    # Time in only minutes will be in the format 46m, 8m etc
    if len(time_string) < 4 and "m" in time_string:
        # Divide by the appropriate conversion number
        time = int(time_string.replace("m", "")) / m

    # Time in hours will be in the format 24h8m
    if len(time_string) > 3:
        time_split = time_string.split("h")
        # Divide by the appropriate conversion numbers
        hours = int(time_split[0]) / h
        minutes = int(time_split[1].replace("m", "")) / m

        time = hours + minutes

    return time


def calc_data_usage(data_string: str, increment: str = "MB") -> float:
    """Return data usage in specified increment deciphered and converted from string data including bytes, KB, MB, or GB

    :param data_string: Formatted as '0 bytes', '313.5KB', '535MB', or '12GB', spaces will be removed
    :type data_string: str
    :param increment: (optional) Type of desired data conversion, default "MB"
    :type increment: str {'KB', 'MB', 'GB'}

    :return: Value of data converted to requested increment
    :rtype: float

    Note:
        Conversions are performed using factors of 10 for simplicity.
    """
    # Default conversion to MB, function will select appropriate conversion rates if a different selection is made
    b, k, m, g = 1000000, 1000, 1, (1 / 1000)
    if increment == "KB":
        b, k, m, g = 1000, 1, (1 / 1000), (1 / 1000000)
    if increment == "MB":
        b, k, m, g = 1000000, 1000, 1, (1 / 1000)
    if increment == "GB":
        b, k, m, g = 1000000000, 1000000, 1000, 1
    # Remove all spaces
    data_string = data_string.replace(" ", "")
    # Remove alphanumeric characters and adjust to appropriate magnitude
    data_usage = 0
    if "bytes" in data_string:
        data_usage = float(data_string.replace("bytes", "")) / b
    if "KB" in data_string:
        data_usage = float(data_string.replace("KB", "")) / k

    if "MB" in data_string:
        data_usage = float(data_string.replace("MB", "")) / m

    if "GB" in data_string:
        data_usage = float(data_string.replace("GB", "")) / g

    return data_usage


def isolate_ip_from_parentheses(ip_string: str) -> str:
    """Return an ip address from surrounding parentheses

    :param ip_string: Formatted as: '10.0.10.10', '(10.20.30.6)', 'WORKGROUP(10.90.10.3)', etc.
    :type ip_string: str

    :return: IP address
    :rtype: str

    Note:
        Conversion to IPv4/IPv6 Address object is not performed
    """

    # Check if parentheses are present before splitting/selecting the appropriate index
    if "(" in ip_string:
        ip_string = ip_string.split("(")[1]
    if ")" in ip_string:
        ip_string = ip_string.split(")")[0]

    return ip_string


def split_by_delimiter(string_data: str, delimiter: str = ",") -> list[str]:
    """Split data by delimiter and return list of values

    :param string_data: String to split
    :type string_data: str
    :param delimiter: Character to split on
    :type delimiter: str

    :return: List of strings
    :rtype: list[str]
    """
    list_of_split_values = string_data.split(delimiter)

    return list_of_split_values
