.. _spkg_biopython:

biopython: Tools for computational molecular biology
====================================================

Description
-----------

Freely available tools for computational molecular biology.

License
-------

Upstream Contact
----------------

https://pypi.org/project/biopython/

http://biopython.org/


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

    biopython

Equivalent System Packages
--------------------------

.. tab:: conda-forge:

   .. CODE-BLOCK:: bash

       $ conda install biopython

.. tab:: Fedora/Redhat/CentOS:

   .. CODE-BLOCK:: bash

       $ sudo dnf install python3-biopython

.. tab:: MacPorts:

   .. CODE-BLOCK:: bash

       $ sudo port install py-biopython

# See https://repology.org/project/biopython/versions, https://repology.org/project/python:biopython/versions

If the system package is installed and if the (experimental) option
``--enable-system-site-packages`` is passed to ``./configure``, then ``./configure`` will check if the system package can be used.
