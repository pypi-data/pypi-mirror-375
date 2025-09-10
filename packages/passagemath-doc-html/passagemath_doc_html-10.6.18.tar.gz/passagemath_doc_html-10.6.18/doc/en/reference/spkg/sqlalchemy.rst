.. _spkg_sqlalchemy:

sqlalchemy: A database abstraction library
==========================================

Description
-----------

Database Abstraction Library

License
-------

MIT

Upstream Contact
----------------

https://pypi.org/project/SQLAlchemy/



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

    sqlalchemy

Equivalent System Packages
--------------------------

.. tab:: conda-forge:

   .. CODE-BLOCK:: bash

       $ conda install sqlalchemy

.. tab:: Fedora/Redhat/CentOS:

   .. CODE-BLOCK:: bash

       $ sudo dnf install python3-sqlalchemy

.. tab:: MacPorts:

   .. CODE-BLOCK:: bash

       $ sudo port install py-sqlalchemy

.. tab:: openSUSE:

   .. CODE-BLOCK:: bash

       $ sudo zypper install python3\$\{PYTHON_MINOR\}-SQLAlchemy

.. tab:: Void Linux:

   .. CODE-BLOCK:: bash

       $ sudo xbps-install python3-SQLAlchemy

# See https://repology.org/project/python:sqlalchemy/versions

If the system package is installed and if the (experimental) option
``--enable-system-site-packages`` is passed to ``./configure``, then ``./configure`` will check if the system package can be used.
