
.. image:: https://readthedocs.org/projects/simple-aws-redshift/badge/?version=latest
    :target: https://simple-aws-redshift.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/simple_aws_redshift-project/actions/workflows/main.yml/badge.svg
    :target: https://github.com/MacHu-GWU/simple_aws_redshift-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/simple_aws_redshift-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MacHu-GWU/simple_aws_redshift-project

.. image:: https://img.shields.io/pypi/v/simple-aws-redshift.svg
    :target: https://pypi.python.org/pypi/simple-aws-redshift

.. image:: https://img.shields.io/pypi/l/simple-aws-redshift.svg
    :target: https://pypi.python.org/pypi/simple-aws-redshift

.. image:: https://img.shields.io/pypi/pyversions/simple-aws-redshift.svg
    :target: https://pypi.python.org/pypi/simple-aws-redshift

.. image:: https://img.shields.io/badge/✍️_Release_History!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/simple_aws_redshift-project/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/⭐_Star_me_on_GitHub!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/simple_aws_redshift-project

------

.. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://simple-aws-redshift.readthedocs.io/en/latest/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/MacHu-GWU/simple_aws_redshift-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/MacHu-GWU/simple_aws_redshift-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/MacHu-GWU/simple_aws_redshift-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/simple-aws-redshift#files


Welcome to ``simple_aws_redshift`` Documentation
==============================================================================
.. image:: https://simple-aws-redshift.readthedocs.io/en/latest/_static/simple_aws_redshift-logo.png
    :target: https://simple-aws-redshift.readthedocs.io/en/latest/

``simple_aws_redshift`` is a Pythonic library that provides a simplified, high-level interface for AWS Redshift operations. Built on top of boto3, it offers intuitive data models, property-based access patterns, and comprehensive type hints to make working with Redshift resources more developer-friendly and maintainable.


Killer Feature - SqlCommand
------------------------------------------------------------------------------
The ``SqlCommand`` class is a game-changer for running SQL queries against Redshift using the Data API. No database connections or credential management needed - just use IAM permissions! The native Data API returns raw JSON that's difficult to work with, but ``SqlCommand`` automatically transforms results into user-friendly formats: Python dictionaries, pandas DataFrames, or polars DataFrames. One simple call handles everything: async execution, polling, and intelligent data parsing.

.. code-block:: python

    import simple_aws_redshift.api as rs
    import boto3

    # Create the command with your SQL
    sql = """
    SELECT
    -- String/VARCHAR
    'Hello World' AS test_string,
    -- Integer (INT4)
    42 AS test_integer,
    -- Float/REAL
    3.14159 AS test_float,
    -- Boolean
    TRUE AS test_boolean,
    -- NULL value
    NULL AS test_null,
    -- Double precision (FLOAT8/DOUBLE PRECISION)
    CAST(123.456789012345 AS REAL) AS test_double,
    -- Long integer (BIGINT/INT8)
    CAST(9223372036854775807 AS BIGINT) AS test_long,
    -- BLOB/BYTEA (binary data)
    'abc'::VARBYTE AS test_blob,
    -- Date types
    CAST('2024-06-12' AS DATE) AS test_date,
    -- Timestamp without timezone
    CAST('2024-06-12 14:30:45.123456' AS TIMESTAMP) AS test_timestamp,
    -- Timestamp with timezone (TIMESTAMPTZ)
    CAST('2024-06-12 14:30:45.123456-05:00' AS TIMESTAMPTZ) AS test_timestamptz,
    -- Time
    CAST('14:30:45' AS TIME) AS test_time,
    -- Additional numeric types for completeness
    CAST(123.45 AS DECIMAL(10,2)) AS test_decimal,
    CAST(123.45 AS NUMERIC(10,2)) AS test_numeric,
    -- Small integer
    CAST(32767 AS SMALLINT) AS test_smallint
    ;
    """

    sql_cmd = rs.redshift_data_api.SqlCommand(
        redshift_data_api_client=boto3.client("redshift-data"),
        sql=sql,
        workgroup_name="my-workgroup",
        database="dev",
    )

    # Run everything with one call - no async complexity!
    sql_cmd.run()

    # Results ready as DataFrame
    sql_cmd.result.vdf.show()           # Pretty print table
    # (1, 15)
    # +---------------+----------------+--------------+----------------+-------------+---------------+---------------------+-------------+-------------+----------------------------+----------------------------------+-------------+----------------+----------------+-----------------+
    # | test_string   |   test_integer |   test_float | test_boolean   | test_null   |   test_double |           test_long | test_blob   | test_date   | test_timestamp             | test_timestamptz                 | test_time   |   test_decimal |   test_numeric |   test_smallint |
    # |---------------+----------------+--------------+----------------+-------------+---------------+---------------------+-------------+-------------+----------------------------+----------------------------------+-------------+----------------+----------------+-----------------|
    # | Hello World   |             42 |      3.14159 | True           |             |       123.457 | 9223372036854775807 | abc         | 2024-06-12  | 2024-06-12 14:30:45.123456 | 2024-06-12 19:30:45.123456+00:00 | 14:30:45    |         123.45 |         123.45 |           32767 |
    # +---------------+----------------+--------------+----------------+-------------+---------------+---------------------+-------------+-------------+----------------------------+----------------------------------+-------------+----------------+----------------+-----------------+

    df = sql_cmd.result.vdf.pandas_df   # Get pandas DataFrame

    df = sql_cmd.result.vdf.polars_df   # Get polars DataFrame


.. _install:

Install
------------------------------------------------------------------------------

``simple_aws_redshift`` is released on PyPI, so all you need is to:

.. code-block:: console

    $ pip install simple-aws-redshift

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade simple-aws-redshift
