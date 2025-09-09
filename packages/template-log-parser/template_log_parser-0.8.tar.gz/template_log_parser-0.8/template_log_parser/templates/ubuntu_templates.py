from template_log_parser.templates.debian_templates import base_debian_templates

apt_daemon = "{time} {server_name} {process}: {level}: {message}"
dbus_daemon = '{time} {server_name} dbus-daemon: {message}'
desktop = "{time} {server_name} {process}.des {message}"
desktop_2 = "{time} {server_name} {process}.desktop{message}"
desktop_3 = "{time} {server_name} {process}.deskto{message}"
desktop_4 = "{time} {server_name} {process}.deskt {message}"
gdm = "{time} {server_name} gdm{process}: {action}: {message}"
package_kit = "{time} {server_name} PackageKit: {message}"
pycharm = "{time} {server_name} pycharm-{process} {message}"
snapd = "{time} {server_name} {process}.snapd- {message}"
sticky_notes = "{time} {server_name} sticky-notes-simple_sticky-notes{message}"
ubuntu = "{time} {server_name} ubuntu-{process} {message}"
vsce_sign = '{time} {server_name} vsce-sign: {message}'

base_ubuntu_templates = [
    [desktop, "desktop", ".des"],
    [desktop_2, "desktop", ".desktop"],
    [desktop_3, 'desktop', ".deskto"],
    [desktop_4, 'desktop', ".deskt"],
    [package_kit, 'package_kit', "PackageKit"],
    [pycharm, "pycharm"],
    [gdm, 'gdm'],
    [ubuntu, 'ubuntu'],
    [sticky_notes, 'sticky_notes', 'sticky-notes-simple_sticky-notes'],
    [dbus_daemon, 'dbus_daemon', 'dbus-daemon'],
    [apt_daemon, 'apt_daemon', 'AptDaemon'],
    [snapd, 'snapd'],
    [vsce_sign, 'vsce_sign','vsce-sign']
]

base_ubuntu_templates += base_debian_templates

ubuntu_column_process_dict = {}
ubuntu_merge_events_dict = {}