.. _spkg_sage_numerical_backends_gurobi:

sage_numerical_backends_gurobi: Gurobi backend for Sage MixedIntegerLinearProgram
=================================================================================

Description
-----------

Gurobi backend for Sage MixedIntegerLinearProgram

License
-------

GPLv2+

Upstream Contact
----------------

https://pypi.org/project/passagemath-gurobi/



Type
----

optional


Dependencies
------------

- $(PYTHON)
- $(PYTHON_TOOLCHAIN)
- $(SAGERUNTIME)
- :ref:`spkg_cysignals`
- :ref:`spkg_cython`
- :ref:`spkg_ipywidgets`

Version Information
-------------------

package-version.txt::

    10.4.1

version_requirements.txt::

    passagemath-gurobi

Equivalent System Packages
--------------------------

# See https://repology.org/project/sage-numerical-backends-gurobi/versions, https://repology.org/project/python:sage-numerical-backends-gurobi/versions

However, these system packages will not be used for building Sage
because ``spkg-configure.m4`` has not been written for this package;
see :issue:`27330` for more information.
