# Sphinx configuration: used for documentation generation

# import project information from package (disable linter messages)
from genckl import __name__  # pylint: disable=no-name-in-module
from genckl import __version__  # pylint: disable=no-name-in-module
from genckl import description  # pylint: disable=no-name-in-module

import datetime
year = str(datetime.datetime.now().year)


# project information vars
master_doc = 'manual'
project = __name__
author = 'ap1x'
copyright = year+', '+author
version = __version__
release = __version__


# config to generate man pages
# (startdocname, name, description, authors, section), ...
man_pages = [('manual', project, description, author, 1)]
