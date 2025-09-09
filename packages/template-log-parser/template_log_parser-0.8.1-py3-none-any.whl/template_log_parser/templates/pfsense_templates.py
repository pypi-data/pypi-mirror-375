# Note: These templates adhere to syslog format

from template_log_parser.column_functions import split_by_delimiter

# # Filter Log

# ICMP
filter_log_icmp_ipv4_address_mask = "{time} {firewall} filterlog[{process_id}] {rule_info},4,{ipv4_protocol_info},icmp,{icmp_ipv4_ip_info},address mask{message}"
filter_log_icmp_ipv4_information = "{time} {firewall} filterlog[{process_id}] {rule_info},4,{ipv4_protocol_info},icmp,{icmp_ipv4_ip_info},information {message}"
filter_log_icmp_ipv4_maskreply = "{time} {firewall} filterlog[{process_id}] {rule_info},4,{ipv4_protocol_info},icmp,{icmp_ipv4_ip_info},maskreply,{message}"
filter_log_icmp_ipv4_redirect = "{time} {firewall} filterlog[{process_id}] {rule_info},4,{ipv4_protocol_info},icmp,{icmp_ipv4_ip_info},redirect,{message}"
filter_log_icmp_ipv4_reply = "{time} {firewall} filterlog[{process_id}] {rule_info},4,{ipv4_protocol_info},icmp,{icmp_ipv4_ip_info},reply,{icmp_ipv4_reply_info}"
filter_log_icmp_ipv4_request = "{time} {firewall} filterlog[{process_id}] {rule_info},4,{ipv4_protocol_info},icmp,{icmp_ipv4_ip_info},request,{icmp_ipv4_request_info}"
filter_log_icmp_ipv4_router = "{time} {firewall} filterlog[{process_id}] {rule_info},4,{ipv4_protocol_info},icmp,{icmp_ipv4_ip_info},router {message}"
filter_log_icmp_ipv4_source = "{time} {firewall} filterlog[{process_id}] {rule_info},4,{ipv4_protocol_info},icmp,{icmp_ipv4_ip_info},source {message}"
filter_log_icmp_ipv_time_exceed = "{time} {firewall} filterlog[{process_id}] {rule_info},4,{ipv4_protocol_info},icmp,{icmp_ipv4_ip_info},timexceed,{message}"
filter_log_icmp_ipv4_type = "{time} {firewall} filterlog[{process_id}] {rule_info},4,{ipv4_protocol_info},icmp,{icmp_ipv4_ip_info},type-{type}"
filter_log_icmp_ipv4_tstamp = "{time} {firewall} filterlog[{process_id}] {rule_info},4,{ipv4_protocol_info},icmp,{icmp_ipv4_ip_info},tstamp,{icmp_ipv4_tstamp_info}"
filter_log_icmp_ipv4_tstampreply = "{time} {firewall} filterlog[{process_id}] {rule_info},4,{ipv4_protocol_info},icmp,{icmp_ipv4_ip_info},tstampreply,{icmp_ipv4_tstampreply_info}"
filter_log_icmp_ipv4_unreachport = "{time} {firewall} filterlog[{process_id}] {rule_info},4,{ipv4_protocol_info},icmp,{icmp_ipv4_ip_info},unreachport,{icmp_ipv4_unreachport_info}"
filter_log_icmp_ipv4_unreachproto = "{time} {firewall} filterlog[{process_id}] {rule_info},4,{ipv4_protocol_info},icmp,{icmp_ipv4_ip_info},unreachproto,{icmp_ipv4_unreachproto_info}"
filter_log_icmp_ipv4_unreach = "{time} {firewall} filterlog[{process_id}] {rule_info},4,{ipv4_protocol_info},icmp,{icmp_ipv4_ip_info},unreach,{message}"

filter_log_icmp_ipv6 = "{time} {firewall} filterlog[{process_id}] {rule_info},6,{icmp_ipv6_protocol_info},ICMPv6,{icmp_ipv6_ip_info}"

# MISC
filter_log_esp_ipv4 = "{time} {firewall} filterlog[{process_id}] {rule_info},4,{ipv4_protocol_info},esp,{ipv4_ip_info}"
filter_log_idrp_ipv4 = "{time} {firewall} filterlog[{process_id}] {rule_info},4,{ipv4_protocol_info},idrp,{ipv4_ip_info}"
filter_log_igmp_ipv4 = "{time} {firewall} filterlog[{process_id}] {rule_info},4,{ipv4_protocol_info},igmp,{ipv4_ip_info}"
filter_log_fire_ipv4 = "{time} {firewall} filterlog[{process_id}] {rule_info},4,{ipv4_protocol_info},fire,{ipv4_ip_info}"
filter_log_gre_ipv4 = "{time} {firewall} filterlog[{process_id}] {rule_info},4,{ipv4_protocol_info},gre,{ipv4_ip_info}"
filter_log_mobile_ipv4 = "{time} {firewall} filterlog[{process_id}] {rule_info},4,{ipv4_protocol_info},mobile,{ipv4_ip_info}"
filter_log_rvd_ipv4 = "{time} {firewall} filterlog[{process_id}] {rule_info},4,{ipv4_protocol_info},rvd,{ipv4_ip_info}"
filter_log_sctp_ipv4 = "{time} {firewall} filterlog[{process_id}] {rule_info},4,{ipv4_protocol_info},sctp,{sctp_ipv4_ip_info}"
filter_log_sun_nd = "{time} {firewall} filterlog[{process_id}] {rule_info},4,{ipv4_protocol_info},sun-nd,{ipv4_ip_info}"
filter_log_swipe_ipv4 = "{time} {firewall} filterlog[{process_id}] {rule_info},4,{ipv4_protocol_info},swipe,{ipv4_ip_info}"
filter_log_unknown_ipv4 = "{time} {firewall} filterlog[{process_id}] {rule_info},4,{ipv4_protocol_info},unknown,{ipv4_ip_info}"

filter_log_ipv4_in_ipv4 = "{time} {firewall} filterlog[{process_id}] {rule_info},4,{ipv4_protocol_info},ipencap,{ipv4_in_ipv4_ip_info},IPV4-IN-IPV4,"
filter_log_ipv6_in_ipv4 = "{time} {firewall} filterlog[{process_id}] {rule_info},4,{ipv4_protocol_info},ipv6,{ipv4_in_ipv6_ip_info},IPV6-IN-IPV4,"

# TCP
filter_log_tcp_ipv4_bad_options = "{time} {firewall} filterlog[{process_id}] {rule_info},4,{ipv4_protocol_info},tcp,{tcp_ipv4_ip_info}[bad opt]{message}"
filter_log_tcp_ipv4_error = "{time} {firewall} filterlog[{process_id}] {rule_info},4,{ipv4_protocol_info},tcp,{tcp_ipv4_error_ip_info},errormsg={message}"
filter_log_tcp_ipv4 = "{time} {firewall} filterlog[{process_id}] {rule_info},4,{ipv4_protocol_info},tcp,{tcp_ipv4_ip_info}"

# UDP
filter_log_udp_ipv4 = "{time} {firewall} filterlog[{process_id}] {rule_info},4,{ipv4_protocol_info},udp,{udp_ipv4_ip_info}"


# General
kernel = "{time} {firewall} kernel{message}"
id_process = "{time} {firewall} {process}[{id}] {message}"
nginx = '{time} {firewall} nginx {dest_ip} - {user} [{timestamp}] "{type} {message}"'
nginx_error = "{time} {firewall} nginx {message_time} [error] {message}"
syslogd = "{time} {firewall} syslogd {message}"


filter_log_templates = [
    # TCP
    # Search these templates before the standard tcp ipv4 template
    [filter_log_tcp_ipv4_error, "filter_tcp_ipv4_error", "tcp"],
    [filter_log_tcp_ipv4_bad_options, "filter_tcp_ipv4_bad_options", "tcp"],
    [filter_log_tcp_ipv4, "filter_tcp_ipv4", "tcp"],  # Standard tcp ipv4 template
    # ICMP
    [filter_log_icmp_ipv4_address_mask, "filter_icmp_ipv4_address_mask", "address mask"],
    [filter_log_icmp_ipv4_information, "filter_icmp_ipv4_information", "information"],
    [filter_log_icmp_ipv4_maskreply, "filter_icmp_ipv4_maskreply", "maskreply"],
    [filter_log_icmp_ipv4_type, "filter_icmp_ipv4_type", "type"],
    [filter_log_icmp_ipv4_reply, "filter_icmp_ipv4_reply", "reply"],
    [filter_log_icmp_ipv4_request, "filter_icmp_ipv4_request", "request"],
    [filter_log_icmp_ipv4_router, "filter_icmp_ipv4_router", "router"],
    [filter_log_icmp_ipv4_source, "filter_icmp_ipv4_source", "source"],
    [filter_log_icmp_ipv_time_exceed, "filter_icmp_ipv4_time_exceed", "timexceed"],
    [filter_log_icmp_ipv4_tstamp, "filter_icmp_ipv4_tstamp", "tstamp"],
    [filter_log_icmp_ipv4_tstampreply, "filter_icmp_ipv4_tstampreply", "tstampreply"],
    [filter_log_icmp_ipv4_unreachport, "filter_icmp_ipv4_unreachport", "unreachport"],
    [filter_log_icmp_ipv4_unreachproto, "filter_icmp_ipv4_unreachproto", "unreachproto"],
    [filter_log_icmp_ipv4_unreach, "filter_icmp_ipv4_unreach", "unreach,"],
    [filter_log_icmp_ipv4_redirect, "filter_icmp_ipv4_redirect", "redirect"],
    [filter_log_icmp_ipv6, "filter_icmp_ipv6", "ICMPv6"],
    # Misc
    [filter_log_esp_ipv4, "filter_esp_ipv4", "esp"],
    [filter_log_fire_ipv4, "filter_fire_ipv4", "fire"],
    [filter_log_gre_ipv4, "filter_gre_ipv4", "gre"],
    [filter_log_idrp_ipv4, "filter_idrp_ipv4", "idrp"],
    [filter_log_igmp_ipv4, "filter_igmp_ipv4", "igmp"],
    [filter_log_mobile_ipv4, "filter_mobile_ipv4", "mobile"],
    [filter_log_rvd_ipv4, "filter_rvd_ipv4", "rvd"],
    [filter_log_sctp_ipv4, "filter_sctp_ipv4", "sctp"],
    [filter_log_sun_nd, "filter_sun_nd_ipv4", "sun-nd"],
    [filter_log_swipe_ipv4, "filter_swipe_ipv4", "swipe"],
    [filter_log_unknown_ipv4, "filter_ipv4_unknown", "unknown"],
    [filter_log_ipv6_in_ipv4, "filter_ipv6_in_ip4v", "IPV6-IN-IPV4"],
    [filter_log_ipv4_in_ipv4, "filter_ipv4_in_ipv4", "IPV4-IN-IPV4"],
    # UDP
    [filter_log_udp_ipv4, "filter_udp_ipv4", "udp"],
]

general_templates = [
    [kernel, "kernel"],
    [nginx, "nginx"],
    [nginx_error, "nginx_error", "error"],
    [id_process, 'id_process', '] '],
    [syslogd, "syslogd"],
]

base_pfsense_templates = filter_log_templates + general_templates

# Rule Columns
generic_rule_info_columns = [
    "rule_number",
    "sub_rule",
    "anchor",
    "tracker",
    "real_interface",
    "reason",
    "action",
    "direction",
]

# Protocol Columns
generic_ipv4_protocol_info_columns = [
    "tos",
    "ecn",
    "ttl",
    "id",
    "offset",
    "flags",
    "protocol_id",
]

icmp_ipv6_protocol_info_columns = [
    "class",
    "flow_label",
    "hop_limit"
]

# IP Info Columns
base_ipv4_ip_info_columns = [
    "length",
    "src_ip",
    "dest_ip"
]

generic_ipv4_ip_info_columns = base_ipv4_ip_info_columns + ["data_length"]

base_ipv4_tcp_udp_ip_info_columns = base_ipv4_ip_info_columns + [
    "src_port",
    "dest_port",
    "data_length",
]

tcp_ipv4_ip_info_error_columns = base_ipv4_tcp_udp_ip_info_columns + ["tcp_flags"]

tcp_ipv4_ip_info_columns = base_ipv4_tcp_udp_ip_info_columns + [
    "tcp_flags",
    "seq_number",
    "ack_number",
    "tcp_window",
    "urg",
    "tcp_options",
]

icmp_ipv6_ip_info_columns = [
    "protocol_id",
    "length",
    "src_ip",
    "dest_ip",
    "icmp_data"
]

# Instance specific Columns
icmp_ipv4_generic_info_columns = [
    "icmp_id",
    "icmp_sequence"
]

icmp_ipv4_unreachport_info_columns = [
    "icmp_dest_ip",
    "unreach_protocol",
    "unreach_port",
]
icmp_ipv4_unreachproto_info_columns = [
    "icmp_dest_ip",
    "unreach_protocol"
]

icmp_ipv4_tstampreply_info_columns = [
    "icmp_id",
    "icmp_sequence",
    "icmp_otime",
    "icmp_rtime",
    "icmp_ttime",
]

split_by_delimiter_column_pairs = {
    # Generic
    "rule_info": generic_rule_info_columns,
    "ipv4_protocol_info": generic_ipv4_protocol_info_columns,
    "ipv4_ip_info": generic_ipv4_ip_info_columns,
    # ICMP
    "icmp_ipv4_ip_info": base_ipv4_ip_info_columns,
    "icmp_ipv4_reply_info": icmp_ipv4_generic_info_columns,
    "icmp_ipv4_request_info": icmp_ipv4_generic_info_columns,
    "icmp_ipv4_tstamp_info": icmp_ipv4_generic_info_columns,
    "icmp_ipv4_tstampreply_info": icmp_ipv4_tstampreply_info_columns,
    "icmp_ipv4_unreachport_info": icmp_ipv4_unreachport_info_columns,
    "icmp_ipv4_unreachproto_info": icmp_ipv4_unreachproto_info_columns,
    "icmp_ipv6_protocol_info": icmp_ipv6_protocol_info_columns,
    "icmp_ipv6_ip_info": icmp_ipv6_ip_info_columns,
    # SCTP
    "sctp_ipv4_ip_info": base_ipv4_tcp_udp_ip_info_columns,
    # TCP
    "tcp_ipv4_ip_info": tcp_ipv4_ip_info_columns,
    "tcp_ipv4_error_ip_info": tcp_ipv4_ip_info_error_columns,
    # UDP
    "udp_ipv4_ip_info": base_ipv4_tcp_udp_ip_info_columns,
    # IPv4 in IPv6, IPv4 in IPv4, etc
    "ipv4_in_ipv6_ip_info": base_ipv4_ip_info_columns,
    "ipv4_in_ipv4_ip_info": base_ipv4_ip_info_columns,
}

pfsense_split_by_delimiter_process_dict = {
    column: [split_by_delimiter, columns]
    for column, columns in split_by_delimiter_column_pairs.items()
}

pfsense_column_process_dict = {**pfsense_split_by_delimiter_process_dict}

pfsense_merge_events_dict = {
    "filter_log": [value[1] for value in filter_log_templates],
    "general": [value[1] for value in general_templates]
}
