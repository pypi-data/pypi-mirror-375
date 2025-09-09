from template_log_parser.column_functions import (
    calc_data_usage,
    isolate_ip_from_parentheses,
)

# Tasks
backup_task = "{time} {server_name} {package_name} {system_user}:#011[{type}][{task_name}] {message}"
backup_version_rotation = "{time} {server_name} {package_name} {system_user}:#011[{task_name}] Trigger version rotation."
backup_version_rotation_status = "{time} {server_name} {package_name}: {system_user}:#011[{task_name}] Version rotation {status} from ID [{id}]."
backup_rotate_version = "{time} {server_name} {package_name}: {system_user}:#011[{task_name}] Rotate version [{version}] from ID [{id}]."
scheduled_task_message = "{time} {server_name} System {system_user}:#011Scheduled Task [{task_name}] {message}"
hyper_backup_task_message = "{time} {server_name} Hyper_Backup: {system_user}:#011Backup task [{task_name}] {message}"
task_setting = "{time} {server_name} {package_name}: {system_user}:#011Setting of {message}"
credentials_changed = "{time} {server_name} {package_name} {system_user}:#011[{type}] Credentials changed on the destination."

# General System
auto_install = "{time} {server_name} System {system_user}:#011Start install [{package}] automatically."
back_online = "{time} {server_name} System {system_user}:#011Server back online."
countdown = "{time} {server_name} System {system_user}:#011System started counting down to {state}."
dns_setting_changed = "{time} {server_name} System {system_user}:#011DNS server setting was changed."
download_task = "{time} {server_name} System {system_user}:#011Download task for [{task}] {result}."
external_disk_ejected = "{time} {server_name} System {system_user}:#011External disk [{external_disk}] is ejected."
external_disk_not_ejected_properly = "{time} {server_name} System {system_user}:#011The external device [{external_disk}] was not ejected properly. You should eject the device before unplugging it or turning it off."
external_disk_failed_to_eject = "{time} {server_name} System {system_user}:#011The system failed to eject external disk [{external_disk}]."
external_disk_initialized = "{time} {server_name} System {system_user}:#011The system successfully initialized the external disk [{disk_id}] to [{format}] format."
external_disk_renamed = "{time} {server_name} System {system_user}:#011The share name [{name}] was found as [{name_one}] and [{name_two}], and the latter was renamed to [{name_two_renamed}]."
failed_video_conversion = "{time} {server_name} System {system_user}:#011System failed to convert video [{video}] to {format}."
fan_speed_set = "{time} {server_name} System {system_user}:#011Fan speed was set to [{speed}]."
interface_set = "{time} {server_name} System {system_user}:#011[{interface}] was set to [{set_to}]."
interface_changed = "{time} {server_name} System {system_user}:#011{attribute} of [{interface}] was changed from [{from}] to [{to}]."
link_state = "{time} {server_name} System {system_user}:#011[{interface}] link {state}."
on_battery = "{time} {server_name} System {system_user}:#011Server is on battery."
package_change = "{time} {server_name} System {system_user}:#011Package [{package}] has been successfully {state}."
process_start_or_stop = "{time} {server_name} System: System successfully {result} [{process}]."
scrubbing = "{time} {server_name} System {system_user}:#011System {state} {type} scrubbing on [{location}]."
service_started_or_stopped = "{time} {server_name} System {system_user}:#011[{service}] service was {state}."
restarted_service = "{time} {server_name} System {system_user}:#011System successfully restarted {service} service."
shared_folder = "{time} {server_name} System {system_user}:#011{kind} shared folder [{shared_folder}] {message}"
shared_folder_application = "{time} {server_name} System {system_user}:#011Shared folder [{shared_folder}] {message} [{application}]."
setting_enabled = "{time} {server_name} System {system_user}:#011[{setting}] was enabled."
storage_pool_degraded = "{time} {server_name} System {system_user}:#011Storage Pool [{storage_pool_number}] degraded [{message}]. Please repair it."
storage_pool_repair_start = "{time} {server_name} System {system_user}:#011System started to perform {repair} on [{storage_pool}] with [{drive}]."
storage_pool_repair_complete = "{time} {server_name} System {system_user}:#011System successfully repaired [{storage_pool}] with drive [{drive}]."
update = "{time} {server_name} System {system_user}:#011Update was {result}."
unknown_error = "{time} {server_name} System {system_user}:#011An unknown error occurred, {message}"

# User Activity
blocked = "{time} {server_name} System {user}:#011Host [{client_ip}] was blocked via [{service}]."
unblock = "{time} {server_name} System {system_user}:#011Delete host IP [{client_ip}] from Block List."
login = "{time} {server_name} Connection: User [{user}] from [{client_ip}] logged in successfully via [{method}]."
failed_login = "{time} {server_name} Connection: User [{user}] from [{client_ip}] failed to log in via [{method}] due to {message}"
failed_host_connection = "{time} {server_name} Connection: Host [{client_ip}] failed to connect via [{service}] due to [{message}]."
logout = "{time} {server_name} Connection: User [{user}] from [{client_ip}] logged out the server via [{method}] with totally [{data_uploaded}] uploaded and [{data_downloaded}] downloaded."
sign_in = "{time} {server_name} Connection: User [{user}] from [{client_ip}] signed in to [{service}] successfully via [{auth_method}]."
failed_sign_in = "{time} {server_name} Connection: User [{user}] from [{client_ip}] failed to sign in to [{service}] via [{auth_method}] due to authorization failure."
folder_access = "{time} {server_name} Connection: User [{user}] from [{client_ip}] via [{method}] accessed shared folder [{folder}]."
cleared_notifications = "{time} {server_name} System {system_user}:#011Cleared [{user}] all notifications successfully."
new_user = "{time} {server_name} System {system_user}:#011User [{modified_user}] was created."
deleted_user = "{time} {server_name} System {system_user}:#011System successfully deleted User [{modified_user}]."
renamed_user = "{time} {server_name} System {system_ser}:#011User [{user}] was renamed to [{modified}]."
user_app_privilege = "{time} {server_name} System {system_user}:#011The app privilege on app [{app}] for user [{user}] {message}"
user_group = "{time} {server_name} System {system_user}:#011User [{user}] was {action} the group [{group}]."
win_file_service_event = "{time} {server_name} WinFileService Event: {event}, Path: {path}, File/Folder: {file_or_folder}, Size: {size}, User: {user}, IP: {client_ip}"
configuration_export = "{time} {server_name} System {system_user}:#011System successfully exported configurations."
report_profile = "{time} {server_name} System {system_user}:#011{action} report profile named [{profile_name}]"

tasks_templates = [
    [backup_task, "backup_task", "Backup"],
    [backup_version_rotation, "backup_version_rotation_trigger", "Trigger version rotation"],
    [backup_version_rotation_status, "backup_version_rotation_status", "Version rotation"],
    [backup_rotate_version, 'backup_rotate_version', "Rotate version"],
    [hyper_backup_task_message, "task_message", "Backup task"],
    [scheduled_task_message, "task_message", "Scheduled Task"],
    [task_setting, "task_setting", "Setting"],
    [credentials_changed, "credentials_changed", "Credentials changed"],
]

general_system_templates = [
    [auto_install, "auto_install", "automatically"],
    [back_online, "back_online", "back online"],
    [countdown, "countdown", "counting down"],
    [download_task, "download_task", "Download task"],
    [failed_video_conversion, "failed_video_conversion", "failed to convert video"],
    [link_state, "link_state", "link"],
    [package_change, "package_change", "Package"],
    [scrubbing, "scrubbing"],
    [process_start_or_stop, "process_start_or_stop", "System successfully"],
    [service_started_or_stopped, "service_start_or_stop", "service was"],
    [restarted_service, "restarted_service", "successfully restarted"],
    [on_battery, "on_battery", "on battery"],
    [update, "update", "Update"],
    [shared_folder, "shared_folder", "shared folder"],
    [shared_folder_application, "shared_folder_application", "Shared folder"],
    [setting_enabled, "setting_enabled", "was enabled"],
    [unknown_error, "unknown_error", "unknown error"],
    [dns_setting_changed, "dns_setting_changed", "DNS server setting was changed"],
    [interface_set, 'interface_set', "was set to"],
    [interface_changed, 'interface_changed', "was changed from"],
    [storage_pool_degraded, "storage_pool_degraded", "degraded"],
    [storage_pool_repair_start, "storage_pool_repair_start", "started to perform"],
    [storage_pool_repair_complete, "storage_pool_repair_complete", "successfully repaired"],
    [external_disk_ejected, "external_disk_ejected", "is ejected"],
    [external_disk_not_ejected_properly, "external_disk_not_ejected_properly", "not ejected properly"],
    [external_disk_failed_to_eject, "external_disk_failed_to_eject", "failed to eject"],
    [external_disk_initialized, "external_disk_initialized", "initialized the external disk"],
    [fan_speed_set, "fan_speed_set", "Fan speed was set"],
    [external_disk_renamed, "external_disk_renamed", "latter was renamed to"],
]

user_activity_templates = [
    [blocked, "host_blocked", "blocked"],
    [unblock, "host_unblocked", "from Block List"],
    [cleared_notifications, "cleared_notifications", "Cleared"],
    [failed_host_connection, "failed_host_connection", "failed to connect"],
    [failed_login, "failed_login", "failed to log in"],
    [failed_sign_in, "failed_sign_in", "failed to sign in"],
    [folder_access, "folder_access", "accessed shared folder"],
    [login, "login", "logged in successfully via"],
    [logout, "logout", "logged out the server"],
    [sign_in, "sign_in", "signed in to"],
    [new_user, "new_user", "was created"],
    [deleted_user, "deleted_user", "deleted"],
    [renamed_user, "renamed_user", "renamed"],
    [user_app_privilege, "user_app_privilege", "app privilege"],
    [user_group, "user_group", "group"],
    [win_file_service_event, "win_file_service_event", "WinFileService Event"],
    [configuration_export, "configuration_export", "exported configurations"],
    [report_profile, "report_profile", "report profile"],
]

base_synology_templates = tasks_templates + general_system_templates + user_activity_templates

# Additional Dictionaries

synology_column_process_dict = {
    "data_uploaded": [calc_data_usage, "data_uploaded_MB"],
    "data_downloaded": [calc_data_usage, "data_download_MB"],
    "client_ip": [isolate_ip_from_parentheses, "client_ip_address"],
}

# Merging events for consolidation
synology_merge_events_dict = {
    "tasks": [value[1] for value in tasks_templates],
    "general_system": [value[1] for value in general_system_templates],
    "user_activity": [value[1] for value in user_activity_templates]
}
