.. _spkg_pyx:

pyx: Generate PostScript, PDF, and SVG files in Python
======================================================

Description
-----------

Python package for the generation of PostScript, PDF, and SVG files

https://pypi.python.org/pypi/PyX


Type
----

optional


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)

Version Information
-------------------

requirements.txt::

    pyx

Equivalent System Packages
--------------------------

.. tab:: MacPorts:

   .. CODE-BLOCK:: bash

       $ sudo port install py-pyx

.. tab:: openSUSE:

   .. CODE-BLOCK:: bash

       $ sudo zypper install python3\$\{PYTHON_MINOR\}-PyX

.. tab:: Void Linux:

   .. CODE-BLOCK:: bash

       $ sudo xbps-install python3-pyx

# See https://repology.org/project/python:pyx/versions

If the system package is installed and if the (experimental) option
``--enable-system-site-packages`` is passed to ``./configure``, then ``./configure`` will check if the system package can be used.
