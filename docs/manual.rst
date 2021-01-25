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
and each column represents a Vulnerability Attribute. The first row in the spreadsheet defines the Vulnerability 
Attribute names and column order, it is required.

Checklist template files can be created or modified with graphical tools such as *LibreOffice Calc* or *MS Excel*, as 
long as the file is saved in **csv** format. A text editor such as *vim* can also be used to create a checklist 
template (since **csv** files are just plain text).

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


.. NEEDFIX TODO

Template Commands
-----------------

checklist templates support running commands

.. Additional notes on Checklist templates
.. ---------------------------------------

.. order doesnt matter both column and row

.. REPLACE MODE ONLY

.. Vulns not found in input files are ignored

.. FIRST ROW is not sesnitive to case or whitespace

.. Severity Override is not sesnitive to case or whitespace or digit vs numeral (2 vs II)

..  - ID
..  - Status
..  - Finding Details
..  - Comments
..  - Severity Override
..  - Severity Override Justification

EXAMPLES
========

.. Most basic example, this will produce::

..     genckl xccdf.xml

.. Generate a checklist from 2 stigs and 1 results xccdf::

..     genckl STIG1.zip stig2.xml xccdf-results.xml


COPYRIGHT
=========

.. |copyright-char| unicode:: 0xA9
.. |year| date:: %Y

Copyright |copyright-char| |year|, License GPLv3: GNU GPL version 3 <https://gnu.org/licenses/gpl.html>.
This is free software: you are free to change and redistribute it. There is NO WARRANTY, 
to the extent permitted by law.
