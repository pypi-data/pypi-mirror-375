.. _spkg_jupymake:

jupymake: A Python wrapper for the polymake shell
=================================================

Description
-----------

The Python module JuPyMake provides an interface to polymake.

License
-------

-  GPL v2


Upstream Contact
----------------

   https://github.com/polymake/JuPyMake

Special Update/Build Instructions
---------------------------------


Type
----

optional


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- :ref:`spkg_polymake`

Version Information
-------------------

package-version.txt::

    0.9

version_requirements.txt::

    jupymake >=0.9

Equivalent System Packages
--------------------------

.. tab:: Fedora/Redhat/CentOS:

   .. CODE-BLOCK:: bash

       $ sudo dnf install python3-jupymake

# See https://repology.org/project/jupymake/versions, https://repology.org/project/python:jupymake/versions

If the system package is installed and if the (experimental) option
``--enable-system-site-packages`` is passed to ``./configure``, then ``./configure`` will check if the system package can be used.
