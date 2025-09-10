.. _spkg_editables:

editables: Editable installations
=================================

Description
-----------

Editable installations

License
-------

MIT

Upstream Contact
----------------

https://pypi.org/project/editables/



Type
----

standard


Dependencies
------------

- $(PYTHON)
- :ref:`spkg_pip`

Version Information
-------------------

package-version.txt::

    0.5

version_requirements.txt::

    editables

Equivalent System Packages
--------------------------

.. tab:: conda-forge:

   .. CODE-BLOCK:: bash

       $ conda install editables

.. tab:: Fedora/Redhat/CentOS:

   .. CODE-BLOCK:: bash

       $ sudo dnf install python3-editables

.. tab:: Gentoo Linux:

   .. CODE-BLOCK:: bash

       $ sudo emerge dev-python/editables


If the system package is installed and if the (experimental) option
``--enable-system-site-packages`` is passed to ``./configure``, then ``./configure`` will check if the system package can be used.
