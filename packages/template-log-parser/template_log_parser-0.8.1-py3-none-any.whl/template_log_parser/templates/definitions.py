from typing import NamedTuple
from parse import Parser

event_data_column = "event_data"
event_type_column = "event_type"

other_type_column = "Other"
unparsed_text_column = "Unparsed_text"


class SimpleTemplate(NamedTuple):
    """
    Compiled template, event_type string, and search_string
    """
    template: Parser
    event_type: str
    search_string: str



