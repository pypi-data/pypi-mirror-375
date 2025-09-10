.. _spkg_mistune:

mistune: Sane and fast Markdown parser with useful plugins and renderers
========================================================================

Description
-----------

Sane and fast Markdown parser with useful plugins and renderers

License
-------

BSD-3-Clause

Upstream Contact
----------------

https://pypi.org/project/mistune/



Type
----

standard


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- :ref:`spkg_cython`

Version Information
-------------------

package-version.txt::

    2.0.4

version_requirements.txt::

    mistune >=0.8.4

Equivalent System Packages
--------------------------

.. tab:: conda-forge:

   .. CODE-BLOCK:: bash

       $ conda install mistune

.. tab:: Fedora/Redhat/CentOS:

   .. CODE-BLOCK:: bash

       $ sudo dnf install python3-mistune

.. tab:: Gentoo Linux:

   .. CODE-BLOCK:: bash

       $ sudo emerge dev-python/mistune

.. tab:: Void Linux:

   .. CODE-BLOCK:: bash

       $ sudo xbps-install python3-mistune

# See https://repology.org/project/mistune/versions, https://repology.org/project/python:mistune/versions

If the system package is installed and if the (experimental) option
``--enable-system-site-packages`` is passed to ``./configure``, then ``./configure`` will check if the system package can be used.
