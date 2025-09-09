from template_log_parser.templates.debian_templates import base_debian_templates

openmediavault_id_process = "{time} {server_name} openmediavault-{process}[{id}]: {message}"
openmediavault_process = "{time} {server_name} openmediavault-{process} {message}"
omv_id_process = "{time} {server_name} omv-{process}[{id}]:{message}"
omv_process = "{time} {server_name} omv-{process}: {message}"
conf = "{time} {server_name} conf_{version}: {message}"
php = "{time} {server_name} php{version}: {action}: {message}"


omv_process_templates = [
    [omv_id_process, "omv_id_process", " omv-"],
    [omv_process, "omv_process", "omv-"],
]

openmediavault_process_templates = [
    [openmediavault_id_process, "openmediavault_id_process", " openmediavault-"],
    [openmediavault_process, "openmediavault_process", "openmediavault-"],
]

omv_other_templates = [
    [conf, "conf", "conf_"],
    [php, 'php', "php"],
]

base_omv_templates = omv_process_templates + openmediavault_process_templates + omv_other_templates + base_debian_templates

omv_merge_events_dict = {
    "omv": [value[1] for value in omv_process_templates],
    "openmediavault": [value[1] for value in openmediavault_process_templates]
}
