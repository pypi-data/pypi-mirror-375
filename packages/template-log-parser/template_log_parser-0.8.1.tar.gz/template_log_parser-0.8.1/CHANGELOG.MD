#### 0.8.1
-Bug fix, corrected built_in `modify_templates()` behavior which produced incorrect search_string resulting in improper matching

#### 0.8
---
-Modified `parse_function()` to return a dictionary instead of a tuple (breaking change), event_type included within dictionary

-Changed template data structure (breaking change) functions now take list of namedtuple (SimpleTemplate). Existing template dictionaries will need to be converted into list of lists and compiled using new function `compile_templates()`.

-Added `modify_templates()` to built_ins.  Allows adding prefix/suffix to templates to match logging system

-Removed sample_log attribute from built-in types; attribute added only during testing.

-Bug fix, attempting to return a df (dict_format=False) with a match string of no matches resulted in error


#### 0.7
---
-Re-write `log_pre_process()` for performance (breaking change).  Function returns all template columns instead of just preliminary three. 

-Changed template dictionary format (breaking change), removed expected number of fields which will now be determined in function.

-Added support for Ubuntu, incorporating Debian templates, (breaking changes as Debian templates have changed again)

-Template tweaks and updates for built-ins (potential breaking changes; PFSense templates have been reduced for simplification)

-Reduced PiHole templates to their simplest values (breaking changes).  The templates now match the messages as they originate from PiHole itself.
Any prefixing information should be tailored to the use case as the final output will likely vary.  PiHole built-in no longer incorporates Debian templates.


#### 0.6
---
-Revised docstrings and improved type hints

-Template tweaks and updates for built-ins (potential breaking changes; the number of Debian templates has been greatly reduced for simplification)

-Addition of optional `match` and `eliminate` parameters to applicable log_functions; filter log files prior to parsing (No Breaking Changes)

-Addition of functions `tag_and_or_combine_lines()` and `link_log_file_lines()` to aid in verbose outputs that span multiple lines.

-Added preliminary support for Kodi.

-Modified `parse_function()` to use compiled templates for small performance gain (No Breaking Changes). 


#### 0.5
---
-Improved exception handling for additional column functions.

-Added support for PFSense (syslog format).

-Addition of type hints matching docstrings.


#### 0.4
---
-Consolidated all built-in log file types to use `built_in_process_log()` for simplification (breaking change).
Named function calls from version < 0.4 will need to be replaced with this function from the built_ins module.


#### 0.3
---
-Various bug fixes.

-Added support for PiHole, Open Media Vault, and Debian.
