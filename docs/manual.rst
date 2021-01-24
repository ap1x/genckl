******
Manual
******

Synopsis
========

**genckl** [*options*] *FILE* [*FILE* ...]

Description
===========

The **genckl** utility generates a STIG Viewer checklist (**ckl**) file based on one or more input *FILE*\ s, which can 
be either STIG **zip**, or xccdf **xml**. If an input *FILE* is a zip, the xccdf xml file within the zip is used as 
input. If xccdf results are found in any of the input files, they are included in the output checklist. 

Options
=======

-h, --help
    show help message and exit

-o FILE, --output FILE
    output filename, defaults to standard output

-r, --run-commands
    enable template command execution, see :ref:`checklist-templates` for more information

-s, --set-hostdata
    set checklist host data based on localhost, this will automatically set the "Target Data" fields (Hostname, MAC, 
    etc) within the output checklist to values gathered from the local system on which **genckl** is running

-t FILE, --template FILE
    checklist template filename, can be specified multiple times, see :ref:`checklist-templates` for more information

-V, --version
    show program's version number and exit

.. _checklist-templates:

Checklist Templates
===================

.. blah blah

.. +------------------------+------------+----------+----------+
.. | Header row, column 1   | Header 2   | Header 3 | Header 4 |
.. | (header rows optional) |            |          |          |
.. +========================+============+==========+==========+
.. | body row 1, column 1   | column 2   | column 3 | column 4 |
.. +------------------------+------------+----------+----------+
.. | body row 2             | ...        | ...      |          |
.. +------------------------+------------+----------+----------+

.. blah blah

Examples
========

.. Most basic example, this will produce::

..     genckl xccdf.xml

.. Generate a checklist from 2 stigs and 1 results xccdf::

..     genckl STIG1.zip stig2.xml xccdf-results.xml

Copyright
=========
Copyright © 2021, License GPLv3: GNU GPL version 3 <https://gnu.org/licenses/gpl.html>.
This is free software: you are free to change and redistribute it. There is NO WARRANTY, to  the extent permitted by law.