from importlib.resources import files
import pandas as pd
import logging

from template_log_parser.log_type_classes import debian, kodi, omada, omv, pfsense, pihole, synology, ubuntu

log_file_path = "test.sample_log_files"

# Sample Log Files for testing built-in types
debian_sample_log = files(log_file_path).joinpath("debian_sample_log.log")

kodi_sample_log = files(log_file_path).joinpath("kodi_sample_log.log")
kodi_unlinked_lines = files(log_file_path).joinpath("kodi_unlinked_lines.log")

omada_sample_log = files(log_file_path).joinpath("omada_sample_log.log")

omv_sample_log = files(log_file_path).joinpath("omv_sample_log.log")
omv_debian_sample_log = files(log_file_path).joinpath("omv_debian_sample_log.log")

pfsense_sample_log = files(log_file_path).joinpath("pfsense_sample_log.log")

pihole_sample_log = files(log_file_path).joinpath("pihole_sample_log.log")

synology_sample_log = files(log_file_path).joinpath("synology_sample_log.log")

ubuntu_sample_log = files(log_file_path).joinpath("ubuntu_sample_log.log")
ubuntu_debian_sample_log = files(log_file_path).joinpath("ubuntu_debian_sample_log.log")

# Create new files by adding debian to omv, pihole, and ubuntu
file_types = [
    [omv_sample_log, omv_debian_sample_log],
    [ubuntu_sample_log, ubuntu_debian_sample_log]
]

for (original_log, merged_log) in file_types:
    with open(str(merged_log), 'w') as outfile:
        for file in [original_log, debian_sample_log]:
            with open(str(file)) as infile:
                outfile.write(infile.read())

# Sample df that contains columns suitable for testing of built-in column functions
def sample_df():
    df = pd.DataFrame(
        {
            "utc_time": ["2025-07-03T04:05:11+01:00", "2025-07-03T04:05:11+01:00"],
            "data": ["45MB", "132.0KB"],
            "time": ["2025-07-03T04:05:11+01:00", "2025-07-03T04:05:11+01:00"],
            "client_name_and_mac": ["name_1:E4-A8-EF-4A-40-DC", "name2:b8-3e-9d-41-0b-6d"],
            "time_elapsed": ["26h5m", "30s"],
            "ip_address_raw": ["192.168.0.1", "(10.0.0.1)"],
            "delimited_data": ["10, 10", "11, 11"],
            "delimited_by_periods": ["10.10", "11.11"],
        }
    )
    return df

log_types_with_files = {
    debian: debian_sample_log,
    kodi: kodi_sample_log,
    omada: omada_sample_log,
    omv: omv_debian_sample_log,
    pfsense: pfsense_sample_log,
    pihole: pihole_sample_log,
    synology: synology_sample_log,
    ubuntu: ubuntu_debian_sample_log
}

built_in_log_file_types = []

for log_type, sample_log in log_types_with_files.items():
    log_type.sample_log_file = sample_log
    built_in_log_file_types.append(log_type)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
