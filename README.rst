pybart
======

.. image:: https://img.shields.io/pypi/v/pybart.svg
    :target: https://pypi.python.org/pypi/pybart
    :alt: Version
.. image:: https://img.shields.io/pypi/pyversions/pybart.svg
    :target: http://py3readiness.org/
    :alt: Python versions
.. image:: https://img.shields.io/pypi/wheel/pybart.svg
    :target: http://pythonwheels.com/
    :alt: Wheel status
.. image:: https://img.shields.io/pypi/l/pybart.svg
    :target: https://opensource.org/licenses/BSD-3-Clause
    :alt: License

Real time BART (`Bay Area Rapid Transit <https://www.bart.gov/>`_) information
in your terminal!

.. image:: https://raw.githubusercontent.com/ericdwang/pybart/master/screenshot.png
    :alt: Screenshot

Features
--------

- Real time estimates and service advisories
- `Curses-based <https://en.wikipedia.org/wiki/Curses_(programming_library)>`_
  TUI with auto-refreshing and resizing
- View multiple stations at the same time
- Colors indicating transit lines, estimate times, and train lengths
- Ability to configure a default set of stations
- Other non-TUI commands like opening a map and getting the fare for a trip
- Includes a low-level Python wrapper for the full BART API
- No dependencies; built with only standard libraries

Requirements
------------

- Python 2.6+ or Python 3.0+ with the ``curses`` module installed (i.e. not
  Windows)
- Terminal with 256 color support to correctly display the Richmond-Fremont
  line as orange (magenta otherwise)

  - Note: this usually involves setting the ``TERM`` environment variable to
    ``xterm-256color``

Installation
------------

``pip install pybart``

Usage
-----

::

    usage: bart [-h] [-v] {map,list,est,fare} ...

    Display real time BART estimates.

    optional arguments:
      -h, --help           show this help message and exit
      -v, --version        show program's version number and exit

    commands:
      {map,list,est,fare}
        map                open station map in web browser
        list               show list of stations and their abbreviations
        est                display estimates for specified stations
        fare               show fare for a trip between two stations

    examples:
      bart                 get estimates for $BART_STATIONS
      bart map             open station map
      bart list            list all stations
      bart est mcar        get estimates for MacArthur station
      bart est embr cols   get estimates for Embarcadero and Coliseum stations
      bart fare conc sfia  get fare for a trip between Concord and SFO stations

Configuration
-------------

The following (optional) environment variables can be used to configure pybart:

- ``BART_STATIONS`` - a comma-separated string (e.g. ``mcar,embr,cols``)
  specifying the default stations to use when running ``bart`` with no
  arguments.
- ``BART_API_KEY`` - the BART API key to use when fetching information. A
  public one is used by default, but you can get your own
  `here <https://api.bart.gov/api/register.aspx>`_.

API
---

Even though it doesn't use everything, pybart includes a low-level Python
wrapper for the full
`BART API <https://api.bart.gov/docs/overview/index.aspx>`_ with
``pybart.api.BART``. Every call by default returns the root element of the XML
response using
`ElementTree <https://docs.python.org/3/library/xml.etree.elementtree.html>`_.
JSON is also supported but the format is currently in
`beta <https://api.bart.gov/docs/overview/output.aspx>`_.

Example usage::

    >>> from pybart.api import BART
    >>> bart = BART()  # Uses the public API key by default
    >>> root = bart.stn.stninfo('dbrk')
    >>> station = root.find('stations').find('station')
    >>> print(station.find('address').text + ', ' + station.find('city').text)
    2160 Shattuck Avenue, Berkeley
    >>> print(bart.version().find('apiVersion').text)
    3.10
    >>> bart = BART(json_format=True)  # Now with JSON
    >>> root = bart.stn.stninfo('dbrk')
    >>> station = root['stations']['station']
    >>> print(station['address'] + ', ' + station['city'])
    2160 Shattuck Avenue, Berkeley

License
-------

`BSD 3-Clause <https://opensource.org/licenses/BSD-3-Clause>`_
