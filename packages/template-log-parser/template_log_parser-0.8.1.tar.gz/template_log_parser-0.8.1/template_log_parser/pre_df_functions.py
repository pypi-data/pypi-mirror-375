from io import BytesIO, StringIO, TextIOBase
from typing import Callable, Union
from pathlib import Path


def tag_and_or_combine_lines(
    list_all_strings: list[str],
    start_text: str,
    end_text: str,
    combine: bool = False,
    tag: str = "",
    tag_replace_text: str = "",
    max_search_lines: int = 10,
) -> list[str]:
    """Either add tag to or combine associated lines (or both) based on starting/ending text and return list

    :param list_all_strings: list of all text
    :type list_all_strings: list[str]

    :param start_text: text that must be present within the first item
    :type start_text: str

    :param end_text: text that must be present on the final item to associate group
    :type end_text: str

    :param combine: False by default, True to combine all items into a single line
    :type combine: bool

    :param tag: text to be added to associated items, empty by default resulting in no change
    :type tag: str

    :param tag_replace_text: text to replace with tag, empty by default resulting in no change
    :type tag_replace_text: str

    :param max_search_lines: maximum number of lines to look for end_text after start_text
    :type max_search_lines: int

    :return: list of strings or list of single string with combined lines and/or the addition of tags
    :rtype: list

    :note:
        tag_replace_text is intended to select the correct position within the string to tag.

        line = '(info): this is a log file line regarding ip address 10.0.0.186'
        tag_replace_text = 'info'
        tag = 'info security_incident_100'

        tagged_line = '(info security_incident_100): this is a log file line regarding ip address 10.0.0.186'

    """
    return_list = []
    buffer = []
    inside_block = False
    line_count = 0

    for line in list_all_strings:
        if not inside_block:
            if start_text in line:
                inside_block = True
                buffer = [line]
                line_count = 1
            else:
                return_list.append(line)
        else:
            buffer.append(line)
            line_count += 1

            if end_text in line:
                if combine:
                    combined = "".join(text.strip() for text in buffer)
                    if tag and tag_replace_text:
                        combined = combined.replace(tag_replace_text, tag)
                    return_list.append(combined)
                else:
                    if tag and tag_replace_text:
                        buffer = [
                            text.replace(tag_replace_text, tag) for text in buffer
                        ]
                    return_list.extend(buffer)
                buffer = []
                inside_block = False
                line_count = 0

            elif 0 < max_search_lines < line_count:
                return_list.extend(buffer)
                buffer = []
                inside_block = False
                line_count = 0

    # Leftover, start criteria exists but end criteria never found
    if inside_block and buffer:
        return_list.extend(buffer)

    return return_list


def link_log_file_lines(
    logfile: Union[str, Path, BytesIO, StringIO, TextIOBase],
    criteria: list[list[Callable | dict[str, str]]],
) -> StringIO:
    """Run list of line-linking functions against a log file and return a StringIO object to continued analysis

    :param logfile: Path to file or filelike object, most commonly in the format of some_log_process.log
    :type logfile: str, Path, BytesIO, StringIO, TextIOBase

    :criteria: list of lists containing list-linking function and dict of arguments
    :type criteria: list[list[Callable, dict[str, str]]]

    :return: original logfile with the modifications to linked lines
    :rtype: StringIO

    :example:
        link_funcs = [
            [tag_or_combine_lines, dict(start_text="Unable to open file", end_text="error :", combine=True)],
            [func2, dict(arg=1)],
            ...]
    """
    # Read lines depending on input type
    if isinstance(logfile, (str, Path)):
        with open(logfile, "r", encoding="utf-8") as f:
            lines = f.read().splitlines()

    elif isinstance(logfile, BytesIO):
        logfile.seek(0)
        decoded = logfile.read().decode("utf-8-sig")
        lines = decoded.splitlines()

    elif isinstance(logfile, (StringIO, TextIOBase)):
        logfile.seek(0)
        lines = logfile.read().splitlines()

    else:
        raise ValueError(
            "Unsupported logfile type. Must be str, BytesIO, or file-like object."
        )

    # Apply line-linking functions
    for func, kwargs in criteria:
        lines = func(lines, **kwargs)

    # Join and return as StringIO
    return StringIO("\n".join(lines))
