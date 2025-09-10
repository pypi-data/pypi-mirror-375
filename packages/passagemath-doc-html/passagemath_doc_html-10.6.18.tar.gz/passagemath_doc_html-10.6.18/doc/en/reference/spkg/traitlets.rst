.. _spkg_traitlets:

traitlets: Traitlets Python configuration system
================================================

Description
-----------

Traitlets Python configuration system

License
-------

BSD

Upstream Contact
----------------

https://pypi.org/project/traitlets/



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

    5.14.3

version_requirements.txt::

    traitlets >=4.3.3

Equivalent System Packages
--------------------------

.. tab:: conda-forge:

   .. CODE-BLOCK:: bash

       $ conda install traitlets

.. tab:: Gentoo Linux:

   .. CODE-BLOCK:: bash

       $ sudo emerge dev-python/traitlets

.. tab:: MacPorts:

   .. CODE-BLOCK:: bash

       $ sudo port install py-traitlets

.. tab:: openSUSE:

   .. CODE-BLOCK:: bash

       $ sudo zypper install python3\$\{PYTHON_MINOR\}-traitlets

.. tab:: Void Linux:

   .. CODE-BLOCK:: bash

       $ sudo xbps-install python3-traitlets

# See https://repology.org/project/traitlets/versions, https://repology.org/project/python:traitlets/versions

If the system package is installed and if the (experimental) option
``--enable-system-site-packages`` is passed to ``./configure``, then ``./configure`` will check if the system package can be used.
