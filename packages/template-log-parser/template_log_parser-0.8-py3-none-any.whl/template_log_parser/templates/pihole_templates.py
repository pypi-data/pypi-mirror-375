
# dnsmasq
dnsmasq_cached = "{time} dnsmasq[{id}]: cached {query} is {cached_resolved_ip}"
dnsmasq_cached_stale = "{time} dnsmasq[{id}]: cached-stale {query} is {cached_resolved_ip}"
dnsmasq_compile = "{time} dnsmasq[{id}]: compile time options: {message}"
dnsmasq_config = "{time} dnsmasq[{id}]: config {host} is {result}"
dnsmasq_custom_list = '{time} dnsmasq[{id}]: /etc/pihole/hosts/custom.list {host_ip} is {host_name}'
dnsmasq_domain = "{time} dnsmasq[{id}]: {type} domain {query} is {result}"
dnsmasq_exactly_blacklisted = "{time} dnsmasq[{id}]: exactly blacklisted {query} is {result}"
dnsmasq_exactly_denied = "{time} dnsmasq[{id}]: exactly denied {query} is {result}"
dnsmasq_exiting = "{time} dnsmasq[{id}]: exiting on receipt of SIGTERM"
dnsmasq_forward = "{time} dnsmasq[{id}]: forwarded {query} to {dns_server}"
dnsmasq_gravity_blocked = "{time} dnsmasq[{id}]: gravity blocked {query} is {result}"
dnsmasq_host_name_resolution = "{time} dnsmasq[{id}]: /etc/hosts {host_ip} is {host_name}"
dnsmasq_host_name = "{time} dnsmasq[{id}]: Pi-hole hostname {host_name} is {host_ip}"
dnsmasq_inotify = "{time} dnsmasq[{id}]: inotify: {message}"
dnsmasq_locally_known = "{time} dnsmasq[{id}]: using only locally-known addresses for {result}"
dnsmasq_query = "{time} dnsmasq[{id}]: query[{query_type}] {destination} from {host_ip}"
dnsmasq_rate_limiting = "{time} dnsmasq[{id}]: Rate-limiting {query} is {message}"
dnsmasq_read = "{time} dnsmasq[{id}]: read {path} - {names} names"
dnsmasq_reply = "{time} dnsmasq[{id}]: reply {query} is {resolved_ip}"
dnsmasq_reply_truncated = "{time} dnsmasq[{id}]: reply is truncated"
dnsmasq_started = "{time} dnsmasq[{id}]: started, version {version} cachesize {cachesize}"
dnsmasq_tcp_connection_failed = "{time} dnsmasq[{id}]: TCP connection failed: {message}"
dnsmasq_using_nameserver = "{time} dnsmasq[{id}]: using nameserver {nameserver_ip}#53"
dnsmasq_using_nameserver_domain = "{time} dnsmasq[{id}]: using nameserver {nameserver_ip}#53 for domain {domain}"

# ftl
ftl_error = "{time} [{ids}] ERROR: {message}"
ftl_info = "{time} [{ids}] INFO: {message}"
ftl_warning = "{time} [{ids}] WARNING: {message}"

# webserver
webserver_initializing_http_server = '[{time}] Initializing HTTP server on ports "{ports}"'
webserver_authentication_required = '[{time}] Authentication required, redirecting to {redirect}'

# Gravity
gravity = '{trim}[{result}]{message}'

dnsmasq_templates = [
    [dnsmasq_query, "dnsmasq_query", "query"],
    [dnsmasq_reply, "dnsmasq_reply", "reply"],
    [dnsmasq_cached, "dnsmasq_cached", "cached"],
    [dnsmasq_cached_stale, "dnsmasq_cached_stale", "cached-stale"],
    [dnsmasq_forward, "dnsmasq_forward", "forwarded"],
    [dnsmasq_gravity_blocked, "dnsmasq_gravity_blocked", "gravity blocked"],
    [dnsmasq_exactly_denied, "dnsmasq_exact_denied", "exactly denied"],
    [dnsmasq_domain, "dnsmasq_domain", "domain"],
    [dnsmasq_host_name, "dnsmasq_hostname_resolution", "hostname"],
    [dnsmasq_config, "dnsmasq_config", "config"],
    [dnsmasq_compile, "dnsmasq_compile_time_options", "compile time options"],
    [dnsmasq_exactly_blacklisted, "dnsmasq_exact_blacklist", "exactly blacklisted"],
    [dnsmasq_exiting, "dnsmasq_exiting_sigterm", "exiting on receipt of SIGTERM"],
    [dnsmasq_host_name_resolution, "dnsmasq_hostname_resolution", "hosts"],
    [dnsmasq_locally_known, "dnsmasq_locally_known", "locally-known"],
    [dnsmasq_rate_limiting, "dnsmasq_rate_limiting", "Rate-limiting"],
    [dnsmasq_read, "dnsmasq_read", "read "],
    [dnsmasq_reply_truncated, "dnsmasq_reply_truncated", "reply is truncated"],
    [dnsmasq_started, "dnsmasq_started", "started"],
    [dnsmasq_inotify, 'dsnmasq_inotify', 'inotify'],
    [dnsmasq_using_nameserver, 'dnsmasq_using_nameserver', 'using nameserver'],
    [dnsmasq_using_nameserver_domain, 'dnsmasq_using_nameserver_domain', ' using nameserver'],
    [dnsmasq_custom_list, 'dnsmasq_custom_list', "custom.list"],
    [dnsmasq_tcp_connection_failed, 'dnsmasq_tcp_connection_failed', "TCP connection failed"]
]

ftl_templates = [
    [ftl_error, 'ftl_error', 'ERROR'],
    [ftl_info, 'ftl_info', 'INFO'],
    [ftl_warning, 'ftl_warning', 'WARNING'],
]

webserver_templates = [
    [webserver_initializing_http_server, 'webserver_initializing_server', 'Initializing HTTP server'],
    [webserver_authentication_required, 'webserver_authentication_required', 'Authentication required'],
]

gravity_templates = [
    [gravity, 'gravity_message', '[i]'],
    [gravity, 'gravity_message', '[✓]'],
]

base_pihole_templates = dnsmasq_templates + ftl_templates + webserver_templates + gravity_templates


# Merging events for consolidation
pihole_merge_events_dict = {
    "dnsmasq": [value[1] for value in dnsmasq_templates],
    "ftl": [value[1] for value in ftl_templates],
    "webserver": [value[1] for value in webserver_templates],
    "gravity": [value[1] for value in gravity_templates]
}
