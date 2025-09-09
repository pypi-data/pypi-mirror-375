# Defines classes for built-in log file types

from typing import Callable

from template_log_parser.templates.template_functions import compile_templates

from template_log_parser.templates.debian_templates import (
    base_debian_templates
)

from template_log_parser.templates.kodi_templates import (
    base_kodi_templates,
    kodi_column_process_dict,
    kodi_merge_events_dict,
)

from template_log_parser.templates.omada_templates import (
    base_omada_templates,
    omada_column_process_dict,
    omada_merge_events_dict,
)

from template_log_parser.templates.omv_templates import (
    base_omv_templates,
    omv_merge_events_dict,
)

from template_log_parser.templates.pfsense_templates import (
    base_pfsense_templates,
    pfsense_column_process_dict,
    pfsense_merge_events_dict,
)

from template_log_parser.templates.pihole_templates import (
    base_pihole_templates,
    pihole_merge_events_dict,
)
from template_log_parser.templates.synology_templates import (
    base_synology_templates,
    synology_column_process_dict,
    synology_merge_events_dict,
)

from template_log_parser.templates.ubuntu_templates import (
    base_ubuntu_templates,
    ubuntu_column_process_dict,
)


class BuiltInLogFileType:
    """Built In Log File Type as a class

    :param name: Simple name to reference the type
    :type name: str

    :param base_templates: uncompiled list of base templates, expected format:  [[template, event_type, search_string], [template, event_type], ...]
    :type base_templates: list[list[str]]

    :param column_functions: Formatted as {column: [function, [new_column(s)], kwargs], ...}
    :type column_functions: dict, None

    :param merge_events: Formatted as {'new_df_name', ['existing_df_1', 'existing_df_2', ...], ...}
    :type merge_events: dict, None

    :param datetime_columns: Columns to be converted using Pandas.to_datetime()
    :type datetime_columns: list, None

    :param localize_datetime_columns: Columns to drop timezone
    :type localize_datetime_columns: list, None
    """

    def __init__(
        self,
        name: str,
        base_templates: list[list[str]],
        column_functions: None | dict[str, list[Callable | str | list[str] | dict[str, int]]],
        merge_events: None | dict[str, list[str]],
        datetime_columns: None | list[str],
        localize_datetime_columns: None | list[str],
    ):
        self.name = name
        self.base_templates = base_templates
        self.templates = compile_templates(self.base_templates, search_string_criteria='copy')
        self.column_functions = column_functions
        self.merge_events = merge_events
        self.datetime_columns = datetime_columns
        self.localize_datetime_columns = localize_datetime_columns

    def modify_templates(self, prefix:str='', suffix:str='') -> None:
        """Compile new list of templates after prefixing and/or suffixing the base templates

        :param prefix: text to place at beginning of template
        :type prefix: str

        :param suffix: text to place at end of template
        :type suffix: str
        """
        modified_base_templates = [[prefix + item[0] + suffix] + item[:1] for item in self.base_templates]

        self.templates = compile_templates(modified_base_templates, search_string_criteria='copy')



# BuiltInLogFileType Instances
debian = BuiltInLogFileType(
    name="debian",
    base_templates=base_debian_templates,
    column_functions=None,
    merge_events=None,
    datetime_columns=["time"],
    localize_datetime_columns=None,
)

kodi = BuiltInLogFileType(
    name="kodi",
    base_templates=base_kodi_templates,
    column_functions=kodi_column_process_dict,
    merge_events=kodi_merge_events_dict,
    datetime_columns=["time"],
    localize_datetime_columns=None,
)

omada = BuiltInLogFileType(
    name="omada",
    base_templates=base_omada_templates,
    column_functions=omada_column_process_dict,
    merge_events=omada_merge_events_dict,
    datetime_columns=["time"],
    localize_datetime_columns=None,
)

omv = BuiltInLogFileType(
    name="omv",
    base_templates=base_omv_templates,
    column_functions=None,
    merge_events=omv_merge_events_dict,
    datetime_columns=["time"],
    localize_datetime_columns=None,
)

pfsense = BuiltInLogFileType(
    name="pfsense",
    base_templates=base_pfsense_templates,
    column_functions=pfsense_column_process_dict,
    merge_events=pfsense_merge_events_dict,
    datetime_columns=["time"],
    localize_datetime_columns=None,
)

pihole = BuiltInLogFileType(
    name="pihole",
    base_templates=base_pihole_templates,
    column_functions=None,
    merge_events=pihole_merge_events_dict,
    datetime_columns=None,
    localize_datetime_columns=None,
)

synology = BuiltInLogFileType(
    name="synology",
    base_templates=base_synology_templates,
    column_functions=synology_column_process_dict,
    merge_events=synology_merge_events_dict,
    datetime_columns=["time"],
    localize_datetime_columns=None,
)

ubuntu = BuiltInLogFileType(
    name='ubuntu',
    base_templates=base_ubuntu_templates,
    column_functions=ubuntu_column_process_dict,
    merge_events=None,
    datetime_columns=["time"],
    localize_datetime_columns=None,
)

built_in_log_file_types = [
    debian,
    kodi,
    omada,
    omv,
    pfsense,
    pihole,
    synology,
    ubuntu
]

dict_built_in_log_file_types = {built_in.name: built_in for built_in in built_in_log_file_types}
