Shooju
=======

*shooju-ts* contains loads/dumps functionality for sjts, a json-ish format for time series data designed for use with `Shooju <http://www.shooju.com/>`_ and compatible with loads() and dumps() commands based on the json package.  Currently, it is intended to be used only with the shooju package from pip to speed up retrieval of Shooju data.  We do plan on documenting the format to enable uses beyond Shooju.  The serializer is based on `UltraJSON <https://pypi.python.org/pypi/ujson>`_.


Installation
-------------

Install using pip::

    pip install shooju-ts

Basic Usage
-----------

May be used as a drop in replacement for most other JSON parsers for Python::

    >>> import sjts
    >>> sjts_string = sjts.dumps({'success':True,'series':[{'points':[(13242323324,2)]}]})
    >>> print sjts.dumps(sjts_string)
    {'success':True,'series':[{'points':[(1,2)]}

Source
-------

https://bitbucket.org/shooju/sjts (restricted access for now)

Changelist
----------

0.1
^^^^

- Initial public release not intended for standalone use without the shooju package.


Development
-----------

To compile for windows set environment variable (for VS2015):
    $ SET VS90COMNTOOLS=%VS140COMNTOOLS%

