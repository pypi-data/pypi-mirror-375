# template-log-parser : Log Files into Tabular Data
---
`template-log-parser` is designed to streamline the log analysis process by pulling relevant information into DataFrame columns by way of user designed templates.  `parse` and `pandas` perform the heavy lifting. Full credit to those well-designed projects.

This project offers some flexibility in how you can process your log files.  You can utilize built-in template functions (Kodi, Omada Controller, Open Media Vault, PFSense, PiHole, Synology DSM, and Ubuntu) or build your own workflow. 

#### Getting Started
---

```bash
pip install template-log-parser
```

The foundational principle in this project is designing templates that fit repetitive log file formats.

Example log line:
```bash
my_line = "2024-06-13T15:09:35 server_15 login_authentication[12345] rejected login from user[user_1]."
```
    
Example template:
```bash
my_template = "{time} {server_name} {service_process}[{service_id}] {result} login from user[{username}]."
```

The words within the braces will eventually become column names in a DataFrame.  You can capture as much or as little data from the line as you see fit.  For instance, you could opt to omit {result} from the template and thus look to match only rejected logins for this example.

Note that templates will be looking for an exact match.  Items such as timestamps, time elapsed, and data usage should be captured as they are unique to that log line instance.

#### Template Lists
---
After creating templates, they should be compiled and inserted into a SimpleTemplate namedtuple and added to a list:

Manual Compile
```bash
from parse import compile as parse_compile
from template_log_parser.templates.definitions import SimpleTemplate

compiled_template = parse_compile(my_template)

my_template_tuple = SimpleTemplate(template=compiled_template, event_type="login from", search_string="login_attempt")

my_templates = [my_template_tuple, my_template_tuple2, ...]

```
- 'search_string' is text expected to be found in the log file line.  The parsing function will only check the template against the line if the text is present.
- 'template' is the user defined template.
- 'event_type' is an arbitrary string name assigned to this type of occurrence.

Batch compile

Use of function to compile all templates in one run.

```bash
from template_log_parser import compile_templates

uncompiled_templates = [
# [template, event_type, search_string ]
  [my_template, "login_attempt", "login from"],
  [my_template2, "reboot", "Host Restarting"],
  ...
]

my_templates = compile_templates(uncompiled_templates)


```

#### Basic Usage Examples
---
Parse a single event:
```bash
from template_log_parser import parse_function

parsed_info = parse_function(my_line, my_templates)

print(parsed_info)
    {
    "time": "2024-06-13T15:09:35",
    "server_name": "server_15",
    "service_process": "login_authentication", 
    "service_id": "12345",
    "result": "rejected",
    "username": "user_1",
    "event_type": "login_attempt"
    }
```
Parse an entire log file and return a Pandas DataFrame:
```bash
from template_log_parser import log_pre_process

df = log_pre_process('log_file.log', my_templates)

print(df.columns)
Index(['time', 'server_name', 'service_process', 'service_id', 'result', 'username', 'event_type', 'event_data'])
```
This is just a tabular data form of many single parsed events.
 - event_type column value is determined based on the matching template
 - event_data column holds the raw string data for each log line
 - Essentially, each key from the parsed_info dictionary will become its own column populated with the associated value.
 
Note: 
Events that do not match a template will be returned as event_type ('Other') with column: ('Unparsed_text').

#### Granular Log Processing
---
By default, this procedure returns a dictionary of Pandas DataFrames, formatted as {'event_type': df}.

```bash
from template_log_parser import process_log

my_df_dict = process_log('log_file.log', my_templates)

print(my_df_dict.keys())
dict_keys(['login_attempt', 'event_type_2', 'event_type_3', ...])
```

Alternatively as one large DataFrame:
```bash
from template_log_parser import process_log

my_df = process_log('log_file.log', my_templates, dict_format=False)

print(my_df.columns)
Index(['event_type', 'time', 'server_name', 'service_process', 'service_id', 'result', 'username'])
```

Filter results using match to ensure that log lines contain the desired strings, or eliminate to remove lines that are not of interest. 
```bash
from template_log_parser import process_log

my_matched_df = process_log('log_file.log', my_templates, match=['error', 'login'] , dict_format=False)
my_eliminated_df = process_log('log_file.log', my_templates, eliminate=['user: admin', 'success'], match_type='all' , dict_format=False)

```

###### Some Notes
---
- By default `drop_columns=True` instructs `process_log()` to discard 'event_data' along with any other columns modified by column functions (SEE NEXT).
- (OPTIONAL ARGUMENT) `additional_column_functions` allows user to apply functions to specific columns.  These functions will create a new column, or multiple columns if so specified.  The original column will be deleted if `drop_columns=True`.  This argument takes a dictionary formatted as:
```bash
add_col_func = {column_to_run_function_on: [function, new_column_name_OR_list_of_new_colum_names]}
 ```
- (OPTIONAL ARGUMENT) `merge_dictionary` allows user to concatenate DataFrames that are deemed to be related.  Original DataFrames will be discarded, and the newly merged DF will be available within the dictionary by its new key.  When `dict_format=False`, this argument has no effect.  This argument takes a dictionary formatted as:
```bash
my_merge_dict = {'new_df_key': [df_1_key, df_2_key, ...], ...}
```
- (OPTIONAL ARGUMENT) `datetime_columns` takes a list of columns that should be converted using `pd.to_datetime()`
- (OPTIONAL ARGUMENT) `localize_time_columns` takes a list of columns whose timezone should be eliminated (column must also be included in the `datetime_columns` argument).
---
#### Built-Ins
This project includes built-in templates for Kodi, Omada Controller, Open Media Vault, PFSense, PiHole, Synology DSM, and Ubuntu. These are still being actively developed as not all event types have been accounted for.
As a general philosophy, this project aims to find middle ground between useful categorization of log events and sheer number of templates.

Submissions for improvement are welcome.

Notes: 

- PFSense templates match (RFC 5424, with RFC 3339 microsecond precision time stamps)
- Synology templates match (BSD, RFC 3164)
```bash
from template_log_parser.built_ins import built_in_process_log

# built-ins: ["kodi", "omada", "omv", "pfsense", "pihole", "synology", "ubuntu"]

my_omada_log_dict = built_in_process_log(built_in="omada", file="my_omada_file.log")
```

PiHole templates will likely require modification to fit the use case.  PiHole does not natively output remote logs.  
In many cases, additional prefixing information will be present from third parties.  This should be added as needed.


```bash
from template_log_parser.log_type_classes import pihole
from template_log_parser.built_ins import built_in_process_log

# Modify the built-in templates
# Your logfile might have zero width no break space present which can prevent template matches. Make sure to account for it
pihole.modify_templates(prefix="{utc_time} {hostname} - ", suffix="")

my_pihole_log_dict = built_in_process_log(built_in='pihole', file='my_pihole_log.log')
```

All built-ins support the addition of prefixes and/or suffixes


As Open Media Vault and Ubuntu are based on Debian, their templates are combined with Debian templates.  
This can be used separately if desired. 
At present, the templates for Debian events are very spartan; it serves as only a cursory classification mechanism. 

```bash
my_debian_log_dict = built_in_process_log(built_in='debian', file='my_debian_log.log')
```

## DISCLAIMER

**This project is in no way affiliated with the products mentioned (Debian, Kodi, Omada, Open Media Vault, PFSense, PiHole, Synology, or Ubuntu).
Any usage of their services is subject to their respective terms of use.**
