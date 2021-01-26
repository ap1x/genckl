*************
GENCKL MANUAL
*************


SYNOPSIS
========

**genckl** [*options*] *FILE* [*FILE* ...]


DESCRIPTION
===========

The **genckl** utility generates a STIG Viewer checklist (**ckl**) file based on one or more input *FILE*\ s, which can 
be either STIG **zip**, or xccdf **xml**. If an input *FILE* is a zip, the xccdf xml file within the zip is used as 
input. If xccdf results are found in any of the input files, they are included in the output checklist. 


OPTIONS
=======

-h, --help
    show help message and exit

-o FILE, --output FILE
    output filename, defaults to standard output

-r, --run-commands
    enable template command execution, see `CHECKLIST TEMPLATES`_ for more information

-s, --set-hostdata
    set checklist host data based on localhost, this will automatically set the "Target Data" fields (Hostname, MAC, 
    etc) within the output checklist to values gathered from the local system on which **genckl** is running

-t FILE, --template FILE
    checklist template filename, can be specified multiple times, see `CHECKLIST TEMPLATES`_ for more information

-V, --version
    show program's version number and exit


CHECKLIST TEMPLATES
===================

A checklist template file is a **csv** spreadsheet in which each row represents a Vulnerability (also called a "Rule") 
and each column represents a Vulnerability Attribute. Checklist template files can be created or modified with 
graphical spreadsheet editors, as long as the file is saved in **csv** format. A simple text editor such could also be 
used to create a checklist template (since **csv** files are just plain text).

The example below shows a basic checklist template spreadsheet:

+----------+----------------+------------------------+------------------------+
| **ID**   | **Status**     | **Finding Details**    | **Comments**           |
+==========+================+========================+========================+
| V-000001 | Open           |                        | This setting is not    |
|          |                |                        | compliant due to FOO   |
|          |                |                        | software requirements. |
+----------+----------------+------------------------+------------------------+
| V-000002 |                |                        | compliant, BAR not     |
|          |                |                        | installed              |
+----------+----------------+------------------------+------------------------+
| V-000003 | Not Applicable |                        | N/A due to BAZ         |
+----------+----------------+------------------------+------------------------+
| V-000004 | Not A Finding  | see SPLANK log         |                        |
+----------+----------------+------------------------+------------------------+

The first row in the spreadsheet defines the Vulnerability Attribute(s) to be modified, it is required, but can be 
customized. The columns may be in any order. The only required Vulnerability Attribute is "ID", meaning a (useful) 
template spreadsheet could be as little as 2 columns, one for "ID" and one for the single Vulnerability Attribute to be 
modified. The first row is not case or whitespace sensitive, for example, "finDingDETAILs" is valid.

Each row after the first should have a value in the "ID" column matching the ID of the Vulnerability to be modified, 
and values for any Vulnerability Attributes to be modified in the matching columns. The rows can be in any order. Any 
blank values in a row are ignored and the Vulnerability Attributes are left untouched. If a row does not match any 
Vulnerability ID it is ignored.

The below list contains all available Vulnerability Attributes and accepted values:

- **ID**: Should use format "V-000000"
- **Status**: Should be "Not Reviewed", "Open", "Not A Finding", or "Not Applicable"; variation in case or whitespace 
  is allowed
- **Finding Details**: any text allowed
- **Comments**: any text allowed
- **Severity Override**: Should be "Cat I", "Cat II", or "Cat III"; variation in case or whitespace is allowed; digits 
  are allowed ("cat 3")
- **Severity Override Justification**: any text allowed

.. NEEDFIX TODO

Template Commands
-----------------

checklist templates support running commands

.. Additional notes on Checklist templates
.. ---------------------------------------

.. REPLACE MODE ONLY

.. gotcha with libreoffice calc need to turn off "smart quotes" so proper utf quotes (") are used

EXAMPLES
========

Most basic example, this will generate a ckl from a single xccdf (including results, if any) and print it to standard 
output::

    genckl foo-xccdf.xml

Generate a checklist from 2 stigs and 1 results xccdf::

    genckl stig1.zip stig2-xccdf.xml bar-results-xccdf.xml


COPYRIGHT
=========

.. |copyright-char| unicode:: 0xA9
.. |year| date:: %Y

Copyright |copyright-char| |year|, License GPLv3: GNU GPL version 3 <https://gnu.org/licenses/gpl.html>.
This is free software: you are free to change and redistribute it. There is NO WARRANTY, 
to the extent permitted by law.
