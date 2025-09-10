# -*- coding: utf-8 -*-

"""
Redshift Dialect for Sqlalchemy Integration
"""

import sqlalchemy.dialects
import sqlalchemy.dialects.postgresql.psycopg2

driver_name = "psycopg2"


class RedshiftPostgresDialect(
    sqlalchemy.dialects.postgresql.psycopg2.PGDialect_psycopg2,
):
    """
    Custom SQLAlchemy dialect for AWS Redshift using psycopg2.

    Limitations:

    - Table Creation Limitation: Since we have not implemented a full Redshift dialect,
        it’s not possible to use SQLAlchemy to create tables. Redshift tables
        have special attributes such as Distribution Keys and Sort Keys,
        which SQLAlchemy does not understand. Therefore, you cannot use
        SQLAlchemy’s metadata-based create_all() functionality. You must
        write raw CREATE TABLE statements manually. However, once the tables are created,
        you can still use SQLAlchemy’s ORM and Table objects to write queries,
        which remains an elegant experience.
    - Metadata Reflection Issue: Because SQLAlchemy assumes the backend is
        standard PostgreSQL, using the MetaData.reflect() function to introspect
        and reconstruct database DDL objects in memory doesn’t work. Redshift’s
        PostgreSQL-compatible schema differs from the official PostgreSQL standard,
        and the reflection functionality cannot accurately interpret those differences.
    - Special Syntax Support: For Redshift-specific syntax such as the COPY command,
        COPY FROM S3, and UNLOAD, you must write raw SQL — there is no ORM-level abstraction.
        However, you can still use SQLAlchemy’s transaction context manager to manage
        the transactional scope of these operations.
    - Data Type Limitation: Redshift-specific data types are not directly supported
        in the ORM. You need to either use generic data types or handle special types
        through raw SQL statements.

    Reference:

    - https://docs.sqlalchemy.org/en/20/dialects/
    """

    driver = driver_name
    # We need this to turn on statement caching
    # See warning:
    #
    # SAWarning: Dialect postgresql:psycopg2 will not make use of SQL compilation
    # caching as it does not set the 'supports_statement_cache' attribute to ``True``.
    # This can have significant performance implications including some
    # performance degradations in comparison to prior SQLAlchemy versions.
    # Dialect maintainers should seek to set this attribute to True after
    # appropriate development and testing for SQLAlchemy 1.4 caching support.
    # Alternatively, this attribute may be set to False which will disable this warning.
    # (Background on this warning at: https://sqlalche.me/e/20/cprf)
    supports_statement_cache = True
    supports_server_side_cursors = True  # 支持如 stream_results=True 的游标分页。
    default_paramstyle = "pyformat"  # 用于传参方式 (%s)。
    supports_sane_multi_rowcount = False  # Redshift 在一次多行删除/更新语句后不返回正确 rowcount，保留 False 比较安全。
    returns_native_bytes = False  # Redshift 返回的二进制字段仍作为字符串（bytes）处理。

    # This method in the Base class has a line
    # ``std_string = connection.exec_driver_sql("show standard_conforming_strings").scalar()``
    # we override it to skip this line
    # See error:
    #
    # sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedObject)
    # unrecognized configuration parameter "standard_conforming_strings"
    def _set_backslash_escapes(self, connection):
        self._backslash_escapes = "off"


dialect_name = "simple_aws_redshift"

sqlalchemy.dialects.registry.register(
    f"{dialect_name}.{driver_name}",
    __name__,
    "RedshiftPostgresDialect",
)
