from template_log_parser.column_functions import (
    calc_time,
    calc_data_usage,
    split_name_and_mac,
)

# Base templates for Omada Log Analysis

# Client Activity #####################################################################################################
# Blocked
blocked = (
    "{time} {controller}  {site_date} {site_time} {site} - - - [client:{client_name_and_mac}] "
    "failed to connected to [{network_device_type}:{network_device}:{network_device_mac}] "
    'with SSID "{ssid}" on channel {channel} because the user '
    "is blocked by Access Control.({number} {discard_text})"
)

blocked_mac = (
    "{time} {controller}  {site_date} {site_time} {site} - - - [client:{client_name_and_mac}]"
    ' failed to connect to [{network_device_type}:{network_device}:{network_device_mac}] with SSID "{ssid}" '
    "on channel {channel} because the user was blocked by MAC block/MAC Filter/Lock To AP.({number} {discard_text})"
)

# Connections
conn_hw = (
    "{time} {controller}  {site_date} {site_time} {site} - - - [client:{client_name_and_mac}] "
    "is connected to [{network_device_type}:{network_device}:{network_device_mac}] on {network} network."
)

conn_w = (
    "{time} {controller}  {site_date} {site_time} {site} - - - [client:{client_name_and_mac}] "
    'is connected to [{network_device_type}:{network_device}:{network_device_mac}] with SSID "{ssid}" '
    "on channel {channel}."
)

# Disconnections
disc_hw = (
    "{time} {controller}  {site_date} {site_time} {site} - - - [client:{client_name_and_mac}] "
    'was disconnected from network "{network}" on [{network_device_type}:{network_device}:{network_device_mac}]'
    "(connected time:{connected_time} connected, traffic: {data})."
)

disc_w = (
    "{time} {controller}  {site_date} {site_time} {site} - - - [client:{client_name_and_mac}] "
    'is disconnected from SSID "{ssid}" on [{network_device_type}:{network_device}:{network_device_mac}] '
    "({connected_time} connected, {data})."
)

disc_hw_recon = (
    "{time} {controller}  {site_date} {site_time} {site} - - - [client:{client_name_and_mac}] "
    'was disconnected from network "{disc_network}" on '
    "[{network_device_type}:{network_device}:{network_device_mac}](connected time:{connected_time} "
    'connected, traffic: {data}) and connected to network "{recon_network}" on '
    "[{recon_network_device_type}:{recon_network_device}:{recon_network_device_mac}]."
)

disc_w_recon = (
    "{time} {controller}  {site_date} {site_time} {site} - - - [client:{client_name_and_mac}] "
    'is disconnected from SSID "{disc_ssid}" on [{network_device_type}:{network_device}:{network_device_mac}] '
    '({connected_time} connected, {data}) and connected to SSID "{recon_ssid}" on '
    "[{recon_network_device_type}:{recon_network_device}:{recon_network_device_mac}]."
)

# DHCP
dhcp_assign = (
    "{time} {controller}  {site_date} {site_time} {site} - - - "
    "DHCP Server allocated IP address {client_ip} for the client[MAC: {client_mac}].#015"
)

dhcp_assign_2 = ("{time} {controller}  {site_date} {site_time} {site} - - - "
                 "DHCP Server allocated IP address {client_ip} for the [client:{client_mac}].")

dhcp_decline = (
    "{time} {controller}  {site_date} {site_time} {site} - - - "
    "DHCP Server received DHCP Decline from client {client_mac}. IP address {client_ip} is not available.#015"
)

dhcp_decline_2 = (
    "{time} {controller}  {site_date} {site_time} {site} - - - "
    "DHCP Server received DHCP Decline from [client:{client_mac}]. IP address {client_ip} is not available."
)

dhcp_reject = (
    "{time} {controller}  {site_date} {site_time} {site} - - - DHCP Server rejected the request"
    " of the client[MAC: {client_mac} IP: {client_ip}].#015"
)

dhcp_reject_2 = (
    "{time} {controller}  {site_date} {site_time} {site} - - - DHCP Server rejected the request "
    "of the [client:{client_mac}](IP: {client_ip})."
)

# Failed connections
failed_w = (
    "{time} {controller}  {site_date} {site_time} {site} - - - [client:{client_name_and_mac}]"
    ' failed to connect to [{network_device_type}:{network_device}:{network_device_mac}] with SSID "{ssid}" on'
    " channel {channel} because the password was wrong.({number} {discard_text})"
)
# Offline
offline_hw = (
    "{time} {controller}  {site_date} {site_time} {site} - - - [client:{client_name_and_mac}] "
    'went offline from network "{network}" on '
    "[{network_device_type}:{network_device}:{network_device_mac}](connected time:{connected_time} "
    "connected, traffic: {data})."
)

offline_w = (
    "{time} {controller}  {site_date} {site_time} {site} - - - [client:{client_name_and_mac}]"
    '  went offline from SSID "{ssid}" on [{network_device_type}:{network_device}:{network_device_mac}]'
    " ({connected_time} connected, {data})."
)

offline_w_username = (
    "{time} {controller}  {site_date} {site_time} {site} - - - [client:{client_name_and_mac}] "
    '(IP: {client_ip}, Username: {username}) went offline from SSID "{ssid}" on '
    "[{network_device_type}:{network_device}:{network_device_mac}] ({connected_time} connected, {data})."
)

offline_w_no_username = (
    "{time} {controller}  {site_date} {site_time} {site} - - - [client:{client_name_and_mac}]"
    ' (IP: {client_ip}) went offline from SSID "{ssid}" on '
    "[{network_device_type}:{network_device}:{network_device_mac}] ({connected_time} connected, {data})."
)

# Online
online_hw = (
    "{time} {controller}  {site_date} {site_time} {site} - - - [client:{client_name_and_mac}] "
    "went online on [{network_device_type}:{network_device}:{network_device_mac}] on {network} network."
)

online_w = (
    "{time} {controller}  {site_date} {site_time} {site} - - - [client:{client_name_and_mac}]"
    "  went online on [{network_device_type}:{network_device}:{network_device_mac}] "
    'with SSID "{ssid}" on channel {channel}.'
)

online_w_username = (
    "{time} {controller}  {site_date} {site_time} {site} - - - [client:{client_name_and_mac}] "
    "(IP: {client_ip}, Username:{username}) went online on "
    '[{network_device_type}:{network_device}:{network_device_mac}] with SSID "{ssid}" on channel {channel}.'
)

online_w_no_username = (
    "{time} {controller}  {site_date} {site_time} {site} - - - [client:{client_name_and_mac}]"
    " (IP: {client_ip}) went online on [{network_device_type}:{network_device}:{network_device_mac}]"
    ' with SSID "{ssid}" on channel {channel}.'
)

# Roaming
roaming = (
    "{time} {controller}  {site_date} {site_time} {site} - - - [client:{client_name_and_mac}] "
    "is roaming from [{network_device_type}:{network_device}:{network_device_mac}][Channel {channel}] to "
    "[{roaming_network_device_type}:{roaming_network_device}:{roaming_network_device_mac}][channel {roaming_channel}] "
    "with SSID {roaming_ssid}"
)


# Logins ##############################################################################################################
login = (
    "{time} {controller}  {site_date} {site_time} {site} - - - "
    "{user} logged in to the controller from {client_ip}."
)

failed_login = (
    "{time} {controller}  {site_date} {site_time} {site} - - - "
    "{user} failed to log in to the controller from {client_ip}."
)

# Network device activity #############################################################################################
device_connected = (
    "{time} {controller}  {site_date} {site_time} {site} - - - "
    "[{network_device_type}:{network_device}:{network_device_mac}] was connected."
)

device_disconnected = (
    "{time} {controller}  {site_date} {site_time} {site} - - - "
    "[{network_device_type}:{network_device}:{network_device_mac}] was disconnected."
)

dhcps = "{time} {controller}  {site_date} {site_time} {site} - - - DHCPS initialization {result}"

got_ip_address = (
    "{time} {controller}  {site_date} {site_time} {site} - - - "
    "[{network_device_type}:{network_device}:{network_device_mac}] "
    "got IP address {ip_address}/{subnet_mask}."
)

got_ip_address_2 = (
    "{time} {controller}  {site_date} {site_time} {site} - - - "
                    "[{network_device_type}:{network_device_mac}] got IP address {ip_address}/{subnet_mask}."
)

online_detection = (
    "{time} {controller}  {site_date} {site_time} {site} - - - "
    "[{network_device_type}:{network_device}:{network_device_mac}]: "
    "The online detection result of [{interface}] was {state}.#015"
)

physical_connection_status = (
    "{time} {controller}  {site_date} {site_time} {site} - - - "
                              "[{network_device_type}:{network_device_mac}]: The physical connection status of [{interface}] was {state}."
)

up_or_down = (
    "{time} {controller}  {site_date} {site_time} {site} - - - "
    "[{interface}] of [{network_device_type}:{network_device}:{network_device_mac}] is {state}.#015"
)

upgrade = (
    "{time} {controller}  {site_date} {site_time} {site} - - - "
    "[{network_device_type}:{network_device}:{network_device_mac}] was upgrade to {result}"
)

# System ##############################################################################################################
auto_backup = (
    "{time} {controller}  {site_date} {site_time} {site} - - - "
    "Auto Backup executed with generating file {filename}."
)

auto_backup_2 = (
    "{time} {controller}  {site_date} {site_time} {site} - - - "
    "Backup Schedule executed with generating file {filename}."
)

log_storage_limit = (
    "{time} {controller}  {site_date} {site_time} {site} - - - "
    "The number of logs is about to reach the storage limit of the Controller. "
    "Please back up the data in time, otherwise oldest data will be deleted after the limit is reached."
)

operation_details = '{time} {controller}  {site_date} {site_time} {site} - - - {"details":{details},"operation":"{operation}"}'

resolved = "{time} {controller}  {site_date} {site_time} {site} - - - Resolved: {message}"


client_activity_templates = [
    [blocked, "blocked", "blocked by Access Control"],
    [blocked_mac, "blocked", "blocked by MAC"],
    [failed_w, "failed_wireless_connection", "failed to connect"],
    [conn_hw, "hardwired_connection", "is connected to"],
    [conn_w, "wireless_connection", "connected to"],
    [dhcp_assign, "dhcp_assign", "allocated IP address"],
    [dhcp_assign_2, 'dhcp_assign', "allocated IP address"],
    [dhcp_reject, "dhcp_reject", "rejected the request"],
    [dhcp_reject_2, 'dhcp_reject', "rejected the request of"],
    [dhcp_decline, "dhcp_decline", "DHCP Decline"],
    [dhcp_decline_2, "dhcp_decline", "DHCP Decline from"],
    [disc_hw, "hardwired_disconnect", "was disconnected from network"],
    [disc_w, "wireless_disconnect", "is disconnected from SSID"],
    [disc_hw_recon, "hardwired_reconnect", "disconnected from network"],
    [disc_w_recon, "wireless_reconnect", "disconnected from SSID"],
    [online_hw, "hardwired_online", "went online"],
    [offline_hw, "hardwired_offline", "went offline from network"],
    [online_w_username, "wireless_online_username", "went online on"],
    [online_w, "wireless_online", " went online on "],
    [online_w_no_username, "wireless_online_no_username", " went online "],
    [offline_w_username, "wireless_offline_username", "went offline from SSID"],
    [offline_w, "wireless_offline", "went offline from SSID "],
    [offline_w_no_username, "wireless_offline_no_username", " went offline from SSID"],
    [roaming, "roaming"],
    ]

login_templates = [
    [login, "login", "logged in to"],
    [failed_login, "failed_login", "failed to log in"],
]

network_devices_activity_templates = [
    [device_connected, "device_connected", "was connected."],
    [device_disconnected, "device_disconnected", "was disconnected."],
    [dhcps, "dhcps_initialization", "DHCPS initialization"],
    [up_or_down, "interface_up_or_down", "] of ["],
    [got_ip_address, "device_dhcp_assign", "got IP address"],
    [got_ip_address_2, "unnamed_device_dhcp_assign", "got IP address "],
    [online_detection, "online_detection", "online detection"],
    [upgrade, "upgrade"],
    [physical_connection_status, "physical_connection_status", "physical connection status"],
]

system_templates = [
    [auto_backup, "auto_backup", "Auto Backup executed"],
    [auto_backup_2, "auto_backup", "Backup Schedule"],
    [log_storage_limit, "log_storage_limit", "about to reach the storage limit"],
    [resolved, "resolved", "Resolved"],
    [operation_details, 'operation_details', "- {"]
]


base_omada_templates = client_activity_templates + login_templates + network_devices_activity_templates + system_templates


# Additional Dictionaries
# Three columns need cleanup, connection time, data usage, and client_name/mac
omada_column_process_dict = {
    "connected_time": [calc_time, "conn_time_min"],
    "data": [calc_data_usage, "data_usage_MB"],
    "client_name_and_mac": [split_name_and_mac, ["client_name", "client_mac"]],
}

# Merging events for consolidation
omada_merge_events_dict = {
    "client_activity": [value[1] for value in client_activity_templates],
    "logins": [value[1] for value in login_templates],
    "network_device_activity": [value[1] for value in network_devices_activity_templates],
    "system": [value[1] for value in system_templates],
}
