.. _spkg_tdlib:

tdlib: Algorithms for computing tree decompositions of graphs
=============================================================

Description
-----------

This library, now known as treedec,
provides algorithms concerning tree decompositions.


License
-------

- GNU General Public License v2
- GNU General Public License v3


Upstream Contact
----------------

- https://gitlab.com/freetdi/treedec
- https://github.com/freetdi/tdlib
- https://github.com/felix-salfelder


Type
----

optional


Dependencies
------------

- :ref:`spkg_boost_cropped`

Version Information
-------------------

package-version.txt::

    0.9.3.p0

Equivalent System Packages
--------------------------

.. tab:: Arch Linux:

   .. CODE-BLOCK:: bash

       $ sudo pacman -S tdlib

.. tab:: Fedora/Redhat/CentOS:

   .. CODE-BLOCK:: bash

       $ sudo dnf install python3-tdlib python3-tdlib-devel

# See https://repology.org/project/python:tdlib/versions

However, these system packages will not be used for building Sage
because ``spkg-configure.m4`` has not been written for this package;
see :issue:`27330` for more information.
