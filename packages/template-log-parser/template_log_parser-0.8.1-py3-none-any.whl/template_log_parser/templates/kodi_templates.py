from template_log_parser.pre_df_functions import tag_and_or_combine_lines

# General Templates
available_video_modes = "{time} T:{T} {level} <{category}>: Available videomodes ({video_modes}):"
binding_wayland = "{time} T:{T} {level} <{category}>: Binding Wayland protocol {message}"
caching_image = "{time} T:{T} {level} <{category}>: Caching image '{file}' to '{image}':"
cached_image = "{time} T:{T} {level} <{category}>: cached image '{image}' size {size}"
compiled = "{time} T:{T} {level} <{category}>: Compiled {message}"
cpython_invoker = "{time} T:{T} {level} <{category}>: CPythonInvoker({instance}): {message}"
dbus = "{time} T:{T} {level} <{category}>: DBus {message}"
device_info = "{time} T:{T} {level} <{category}>: Device{device_number}m_{attribute}:{value}"
egl = "{time} T:{T} {level} <{category}>:   EGL_{attribute}: {value}"
egl_2 = "{time} T:{T} {level} <{category}>: EGL_{attribute} = {value}"
ffmpeg = "{time} T:{T} {level} <{category}>: ffmpeg[{number}]: [{type}] {message}"
general_catchall = "{time} T:{T} {level} <{category}>: {message}"
gen_message = "{time} T:{T} {level} <{category}>: {action}:{message}"
gen_message_2 = "{time} T:{T} {level} <{category}>: {action} - {message}"
gen_message_3 = "{time} T:{T} {level} <{category}>: [{action}] {message}"
gen_message_4 = "{time} T:{T} {level} <{category}>: {action}() {message}"
gl = "{time} T:{T} {level} <{category}>: GL_{attribute} = {value}"
host = "{time} T:{T} {level} <{category}>: connect replacing configured host {configured_host} with resolved host {resolved_host}"
initializing_python = "{time} T:{T} {level} <{category}>: initializing python engine."
json = "{time} T:{T} {level} <{category}>: {data}"
load = "{time} T:{T} {level} <{category}>: load {message}"
loaded = "{time} T:{T} {level} <{category}>: Loaded {message}"
loading = "{time} T:{T} {level} <{category}>: Loading {message}"
loading_2 = "{time} T:{T} {level} <{category}>: loading {message}"
log_level = '{time} T:{T} {level} <{category}>: Log level changed to "{changed_to}"'
metadata = "{time} T:{T} {level} <{category}>: [{resource}]: {message}"
no_attribute = '{time} T:{T} {level} <{category}>: <{tag}> tag has no "{attribute}" attribute'
object_instances = "{time} T:{T} {level} <{category}>: object {object} --> {instances} instances"
on_execution = "{time} T:{T} {level} <{category}>: onExecution{message}({instance})"
output_modes = "{time} T:{T} {level} <{category}>: Output '{output}' has {modes} modes"
output = '{time} T:{T} {level} <{category}>: Entering output "{output}" with scale {scale} and {dpi} dpi'
parent_path = "{time} T:{T} {level} <{category}>:   ParentPath = {path}"
program_action = "{time} T:{T} {level} <{category}>: {program}::{action} - {message}"
program_action_2 = "{time} T:{T} {level} <{category}>: {program}::{action}(){message}"
program_action_3 = "{time} T:{T} {level} <{category}>: {program}::{action}({message})"
program_action_4 = "{time} T:{T} {level} <{category}>: {program}::{action}: {message}"
program_action_5 = "{time} T:{T} {level} <{category}>: {program}[{action}]: {message}"
program_action_6 = "{time} T:{T} {level} <{category}>: {program}::{action} {message}"
program_action_7 = "{time} T:{T} {level} <{category}>: {program} - {action}: {message}"
program_action_8 = "{time} T:{T} {level} <{category}>: {program}[{action}] {message}"
python_interpreter = "{time} T:{T} {level} <{category}>: {message}"
query_part_contains_a_like = "{time} T:{T} {level} <{category}>: This query part contains a like, {message}"
remote_mapping = "{time} T:{T} {level} <{category}>: * {action} remote mapping {message}"
requested_setting = "{time} T:{T} {level} <{category}>: requested setting {message}"
running = "{time} T:{T} {level} <{category}>: Running {message}"
selected = "{time} T:{T} {level} <{category}>: Selected {program} as {as}"
skipped_duplicate_messages = "{time} T:{T} {level} <{category}>: Skipped {number} duplicate messages.."
sql_execute = "{time} T:{T} {level} <{category}>: {sql} execute: {message}"
sql_transaction = "{time} T:{T} {level} <{category}>: {sql} {action} transaction"
thread = "{time} T:{T} {level} <{category}>: Thread {message}"
threads = "{time} T:{T} {level} <{category}>: [threads] {message}"
using = "{time} T:{T} {level} <{category}>: using {criteria} of {item} to {to}"
wayland_capability = "{time} T:{T} {level} <{category}>: Wayland seat <{seat}> gained capability {capability}"
window = "{time} T:{T} {level} <{category}>: ------ Window {message} ------"
xml = "xml {name} {xml_string}"

# System Info
ffmpeg_version = "{time} T:{T} {level} <{category}>: FFmpeg version/source: {version}"
host_cpu = "{time} T:{T} {level} <{category}>: Host CPU: {cpu}, {cores} cores available"
kodi_compiled = "{time} T:{T} {level} <{category}>: Kodi compiled {compiled_date} by {compiler} for {platform}"
running_on = "{time} T:{T} {level} <{category}>: Running on {runtime}, kernel: {kernel}"
starting_kodi = "{time} T:{T} {level} <{category}>: Starting Kodi ({version}). Platform: {platform}"
using_release = "{time} T:{T} {level} <{category}>: Using Release {release}"


system_info_templates = [
    [ffmpeg_version, "ffmpeg_version", "FFmpeg"],
    [host_cpu, "host_cpu", "Host CPU"],
    [using_release, "using_release", "Using Release"],
    [kodi_compiled, "kodi_compiled", "Kodi compiled"],
    [running_on, "running_on", "Running on"],
    [starting_kodi, "starting_kodi", "Starting Kodi"],
]

# For lines that will be captured by gen_message but fall under a different category, or more common
pre_general_templates = [
    [sql_execute, "sql_execute", "execute"],
    [query_part_contains_a_like, "query_part_contains_a_like", "This query part contains a like"],
    [metadata, "metadata"],
    [cpython_invoker, "cpython_invoker", "CPythonInvoker"],
    [caching_image, "caching_image", "Caching image"],
    [cached_image, "cached_image", "cached image"],
    [ffmpeg, "ffmpeg"],
    [thread, "thread", "Thread"],
    [threads, "thread", "[threads]"],
    [egl, "egl", "EGL"],
    [device_info, "device_info", "Device"],
    [parent_path, "parent_path", "ParentPath"],
    [json, "json", ">: {"],
    [loading, "load", "Loading"],
    [loading_2, "load", "loading"],
    [load, "load"],
    [loaded, "load", "Loaded"],
    [dbus, "dbus", "DBus"],
    [window, "window", "Window"],
]

program_actions_templates = [
    [program_action, "program_action", " - "],
    [program_action_2, "program_action", "()"],
    [program_action_3, "program_action", "("],
    [program_action_4, "program_action", "::"],
    [program_action_5, "program_action", "["],
    [program_action_6, "program_action", ">:"],
    [program_action_7, "program_action", "- "],
]

general_messages_templates = [
    [gen_message_3, "gen_message", ">: ["],
    [gen_message_2, "gen_message", " -"],
    [gen_message, "gen_message", ":"],
    [gen_message_4, "gen_message", ")"],
]

# For lines that will not be captured by gen_message; generally less common
post_general_templates = [
    [skipped_duplicate_messages, "skipped_duplicate_messages", "Skipped"],
    [initializing_python, "initializing_python_engine", "initializing python engine"],
    [sql_transaction, "sql_transaction", "transaction"],
    [remote_mapping, "remote_mapping", "remote mapping"],
    [using, "using"],
    [host, "host"],
    [binding_wayland, "binding_wayland", "Binding Wayland"],
    [running, "running", "Running"],
    [requested_setting, "requested_setting", "requested setting"],
    [python_interpreter, "python_interpreter", "Python "],
    [general_catchall, "skin"],
    [general_catchall, "button_map", "utton"],
    [selected, "selected", "Selected"],
    [general_catchall, "initialize", "nitialize"],
    [on_execution, "on_execution", "onExecution"],
    [general_catchall, "locale"],
    [general_catchall, "mime_type", "MIME type"],
    [general_catchall, "starting", "arting"],
    [wayland_capability, "wayland_capability", "Wayland seat"],
    [no_attribute, "no_attribute", "tag has no"],
    [program_action_8, "program_action", "] "],
    [egl_2, "egl", "EGL_"],  # Should precede GL_
    [gl, "gl", "GL_"],
    [compiled, "compiled", "Compiled"],
    [object_instances, "object_instances", "object"],
    [output, "output"],
    [general_catchall, "stopping", "topping"],
    [general_catchall, "stopped"],
    [general_catchall, "sections"],
    [general_catchall, "sink", "Sink"],
    [general_catchall, "saving", "Saving"],
    [general_catchall, "storing", "Storing"],
    [log_level, "log_level", "Log level"],
    [general_catchall, "failed"],
    [available_video_modes, "available_video_modes", "Available videomodes"],
    [output_modes, "ouput_modes", "Output"],
    [general_catchall, "closing", "Closing"],
    [general_catchall, "using_visual", "Using visual"],
    [xml, "xml"],
]

misc_templates = [
    [general_catchall, "misc", "Devic"],
    [general_catchall, "misc", "---------------------------"],
    [general_catchall, "misc", "Enumerated"],
    [general_catchall, "misc", "EGL Config"],
    [general_catchall, "misc", "Disabled debug"],
    [general_catchall, "misc", "Enabled debug"],
    [general_catchall, "misc", "experimental"],
    [general_catchall, "misc", ">: removing"],
    [general_catchall, "misc", ">: Checking"],
    [general_catchall, "misc", ">: creating"],
    [general_catchall, "misc", ">: missing"],
    [general_catchall, "misc", "Exiting the application"],
]

base_kodi_templates = (
        system_info_templates +
        pre_general_templates +
        program_actions_templates +
        general_messages_templates +
        post_general_templates +
        misc_templates
)


# Line Linking Functions
devices = [
    [
        tag_and_or_combine_lines,
        dict(
            start_text="Device " + str(number),
            end_text="m_streamTypes",
            tag="<general>: Device" + str(number),
            tag_replace_text="<general>:",
        ),
    ]
    for number in range(20)
]

xml_advanced = [
    [
        tag_and_or_combine_lines,
        dict(
            start_text="<advancedsettings>",
            end_text="</advancedsettings>",
            tag="xml advancedsettings <advancedsettings>",
            tag_replace_text="<advancedsettings>",
            combine=True,
            max_search_lines=100,
        ),
    ]
]

ratings = [
    [
        tag_and_or_combine_lines,
        dict(start_text="returning ratings of", end_text="'rating':", combine=True),
    ]
]

gui_cache_settings = [
    [
        tag_and_or_combine_lines,
        dict(start_text="New Cache GUI Settings", end_text="Chunk Size", combine=True),
    ]
]

unable_to_open_directory = [
    [
        tag_and_or_combine_lines,
        dict(start_text="Unable to open directory", end_text="error :", combine=True),
    ]
]

unable_to_open_file = [
    [
        tag_and_or_combine_lines,
        dict(start_text="Unable to open file", end_text="error :", combine=True),
    ]
]

kodi_line_linking_arguments = (
    devices
    + xml_advanced
    + ratings
    + gui_cache_settings
    + unable_to_open_directory
    + unable_to_open_file
)

kodi_column_process_dict = {}

kodi_merge_events_dict = {
    "system_info": [value[1] for value in system_info_templates]
}
