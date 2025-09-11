
.. image:: https://readthedocs.org/projects/aws-redshift-schema-explorer/badge/?version=latest
    :target: https://aws-redshift-schema-explorer.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/aws_redshift_schema_explorer-project/actions/workflows/main.yml/badge.svg
    :target: https://github.com/MacHu-GWU/aws_redshift_schema_explorer-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/aws_redshift_schema_explorer-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MacHu-GWU/aws_redshift_schema_explorer-project

.. image:: https://img.shields.io/pypi/v/aws-redshift-schema-explorer.svg
    :target: https://pypi.python.org/pypi/aws-redshift-schema-explorer

.. image:: https://img.shields.io/pypi/l/aws-redshift-schema-explorer.svg
    :target: https://pypi.python.org/pypi/aws-redshift-schema-explorer

.. image:: https://img.shields.io/pypi/pyversions/aws-redshift-schema-explorer.svg
    :target: https://pypi.python.org/pypi/aws-redshift-schema-explorer

.. image:: https://img.shields.io/badge/✍️_Release_History!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/aws_redshift_schema_explorer-project/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/⭐_Star_me_on_GitHub!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/aws_redshift_schema_explorer-project

------

.. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://aws-redshift-schema-explorer.readthedocs.io/en/latest/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/MacHu-GWU/aws_redshift_schema_explorer-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/MacHu-GWU/aws_redshift_schema_explorer-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/MacHu-GWU/aws_redshift_schema_explorer-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/aws-redshift-schema-explorer#files


Welcome to ``aws_redshift_schema_explorer`` Documentation
==============================================================================
.. image:: https://aws-redshift-schema-explorer.readthedocs.io/en/latest/_static/aws_redshift_schema_explorer-logo.png
    :target: https://aws-redshift-schema-explorer.readthedocs.io/en/latest/

A Python library that provides a simple, structured interface for extracting AWS Redshift schema metadata. This project focuses purely on the extraction layer, offering clean command-pattern APIs to retrieve database, schema, table, view, and column information from Redshift clusters. The extracted metadata is returned as structured dataclasses, making it ideal for downstream applications like AI-powered text-to-SQL systems. The library handles the complexity of querying Redshift system tables and views, providing a clean abstraction for schema exploration without dictating how the metadata should be encoded or consumed.

Note: the sql command used in this project is based on `my own research <https://github.com/MacHu-GWU/tech_garden-project/blob/main/docs/source/486768641-Extract-Redshift-Schema-Details-For-AI/index.ipynb>`_.


.. _install:

Install
------------------------------------------------------------------------------

``aws_redshift_schema_explorer`` is released on PyPI, so all you need is to:

.. code-block:: console

    $ pip install aws-redshift-schema-explorer

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade aws-redshift-schema-explorer
