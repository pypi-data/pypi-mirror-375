debug = "{time} {server_name} {process}: debug: {message}"
id_process = "{time} {server_name} {process}[{id}]: {message}"
kernel = "{time} {server_name} kernel: {message}"
pam_unix = "{time} {server_name} {process}: pam_unix({session}): {message}"
mtp_probe = "{time} {server_name} mtp-probe: {message}"
rsync = "{time} {server_name} rsync-{id} {message}"
rsyslogd = "{time} {server_name} rsyslogd: {message}"
sudo = "{time} {server_name} sudo: {message}"
upssched_cmd = "{time} {server_name} upssched-cmd: {message}"

base_debian_templates = [
    [id_process, "id_process", "]:"],
    [kernel, "kernel"],
    [pam_unix, "pam_unix"],
    [sudo, 'sudo'],
    [rsync, "rsync"],
    [rsyslogd, "rsyslogd"],
    [upssched_cmd, 'upssched-cmd'],
    [mtp_probe, 'mtp_probe', 'mtp-probe'],
    [debug, 'debug'],
]
