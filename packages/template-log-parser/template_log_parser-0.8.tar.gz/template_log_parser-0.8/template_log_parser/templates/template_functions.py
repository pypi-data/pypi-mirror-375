import re
from parse import compile as parse_compile
from typing import Literal

from template_log_parser.templates.definitions import SimpleTemplate


def compile_templates(templates: list[list[str]], search_string_criteria: Literal["find", "copy"] = "find") -> list[SimpleTemplate]:
    """
    Return a list of namedtuple (simple_template) after compiling templates and identifying search_string

    :param templates: list containing list of strings whose length is 2 or 3 [[template, event_type, search_string (optional)], ...]
    :type templates: list[list[str]]

    :param search_string_criteria: decision to either find a search_string using regex or copy the event_type as the search_string if none provided
    :type search_string_criteria: Literal["find", "copy"]

    :return: list of SimpleTemplate namedtuple
    :rtype: list[SimpleTemplate]

    :note: expected format:  [[template, event_type, search_string], [template, event_type], ...]
    """

    output = []

    for item in templates:
        template = item[0]
        compiled_template = parse_compile(template)
        event_type = item[1]

        if len(item) == 3:
            search_string = item[2]

        else:
            if search_string_criteria == "copy":
                search_string = event_type

            # Find the longest string in template not enclosed within {} for use as the search_string
            else:
                parts = re.split(r'\{[^{}]*}', template)
                search_string =  max((part.strip() for part in parts), key=len, default='')

        compiled_tuple = SimpleTemplate(template=compiled_template, event_type=event_type, search_string=search_string)
        output.append(compiled_tuple)


    return output
