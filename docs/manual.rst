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
graphical spreadsheet editors, as long as the file is saved in **csv** format. A simple text editor could also be used 
to create a checklist template (since **csv** files are just plain text).

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

Template Commands
-----------------

The **Finding Details** and **Comments** Vulnerability Attributes within a checklist may contain template commands. A 
template command is a block of text starting and ending with "<cmd>". A mixture of normal text and template commands 
within the same Vulnerability Attribute cell is allowed. By default template commands are treated as normal text. When 
the ``--run-commands`` option is given, template commands are executed on the local host, and command output replaces 
the template command text within the Vulnerability Attribute cell. For example, if the ``--run-commands`` option is 
given and following checklist template is applied:

+----------+--------------------------------------+
| **ID**   | **Finding Details**                  |
+==========+======================================+
| V-000001 | foo text                             |
|          |                                      |
|          | <cmd>sh -c 'bar | grep success'<cmd> |
|          |                                      |
|          | baz text                             |
+----------+--------------------------------------+

The output checklist vulnerability **Finding Details** text will contain::

    foo text

    bar: success

    baz text

Note that if you want to use shell features like pipes, you will need to start a shell as shown in the above example. 
Template commands are executed directly and no shell is started by default.

.. Additional notes on Checklist templates
.. ---------------------------------------

.. REPLACE MODE ONLY

.. gotcha with libreoffice calc need to turn off "smart quotes" so proper utf quotes (") are used

.. input file processing order / template processing order

EXAMPLES
========

Most basic example, generate a ckl from a single xccdf, print it to standard output::

    genckl foo_xccdf.xml

Generate a ckl from 2 STIGs and 1 results xccdf, print it to standard output::

    genckl foo_stig.zip bar_stig.xml baz_xccdf_results.xml

Generate a ckl from a STIG and results, apply a checklist template, and save the checklist to the file output.ckl::

    genckl -o output.ckl -t foo_template.csv bar_stig.zip baz_xccdf_results.xml

Generate a ckl, apply a checklist template, run checklist template commands, set the checklist "Target Data" fields 
based on localhost, print it to standard output::

    genckl -t foo_template.csv -r -s bar_xccdf.xml


COPYRIGHT
=========

.. |copyright-char| unicode:: 0xA9
.. |year| date:: %Y

Copyright |copyright-char| |year|, License GPLv3: GNU GPL version 3 <https://gnu.org/licenses/gpl.html>.
This is free software: you are free to change and redistribute it. There is NO WARRANTY, 
to the extent permitted by law.
