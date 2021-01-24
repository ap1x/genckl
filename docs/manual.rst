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

.. NEEDFIX :ref: broken on github

-s, --set-hostdata
    set checklist host data based on localhost, this will automatically set the "Target Data" fields (Hostname, MAC, 
    etc) within the output checklist to values gathered from the local system on which **genckl** is running

-t FILE, --template FILE
    checklist template filename, can be specified multiple times, see `CHECKLIST TEMPLATES`_ for more information

-V, --version
    show program's version number and exit

CHECKLIST TEMPLATES
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
