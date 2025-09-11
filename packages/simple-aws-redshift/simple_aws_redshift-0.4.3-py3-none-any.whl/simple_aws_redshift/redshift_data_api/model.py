# -*- coding: utf-8 -*-

"""
Data models for AWS Redshift Data API resources.

Ref:

- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift-data.html
"""

import typing as T
import enum
import base64
import dataclasses
from functools import cached_property
from datetime import date, time, datetime

from func_args.api import T_KWARGS, REQ
from iterproxy import IterProxy
from ..lazy_imports import tabulate, pd, pl

from ..utils import parse_datetime
from ..model import Base

try:
    from rich import print as rprint
except ImportError:  # pragma: no cover
    pass


if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_redshift_data.literals import (
        StatusStringType,
    )
    from mypy_boto3_redshift_data.type_defs import (
        DescribeStatementResponseTypeDef,
        SqlParameterTypeDef,
        SubStatementDataTypeDef,
        GetStatementResultResponseTypeDef,
        ColumnMetadataTypeDef,
        FieldTypeDef,
    )


@dataclasses.dataclass
class DescribeStatementResponse(Base):
    """
    API response for
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift-data/client/describe_statement.html
    """

    raw_data: "DescribeStatementResponseTypeDef" = dataclasses.field(default=REQ)

    @property
    def cluster_identifier(self) -> T.Optional[str]:
        return self.raw_data.get("ClusterIdentifier")

    @property
    def created_at(self) -> T.Optional[datetime]:
        return self.raw_data.get("CreatedAt")

    @property
    def database(self) -> T.Optional[str]:
        return self.raw_data.get("Database")

    @property
    def db_user(self) -> T.Optional[str]:
        return self.raw_data.get("DbUser")

    @property
    def duration(self) -> T.Optional[int]:
        return self.raw_data.get("Duration")

    @property
    def error(self) -> T.Optional[str]:
        return self.raw_data.get("Error")

    @property
    def has_result_set(self) -> T.Optional[bool]:
        return self.raw_data.get("HasResultSet")

    @property
    def id(self) -> T.Optional[str]:
        return self.raw_data.get("Id")

    @property
    def query_parameters(self) -> T.Optional[T.List["SqlParameterTypeDef"]]:
        return self.raw_data.get("QueryParameters")

    @property
    def query_string(self) -> T.Optional[str]:
        return self.raw_data.get("QueryString")

    @property
    def redshift_pid(self) -> T.Optional[int]:
        return self.raw_data.get("RedshiftPid")

    @property
    def redshift_query_id(self) -> T.Optional[int]:
        return self.raw_data.get("RedshiftQueryId")

    @property
    def result_format(self) -> T.Optional[str]:
        return self.raw_data.get("ResultFormat")

    @property
    def result_rows(self) -> T.Optional[int]:
        return self.raw_data.get("ResultRows")

    @property
    def result_size(self) -> T.Optional[int]:
        return self.raw_data.get("ResultSize")

    @property
    def secret_arn(self) -> T.Optional[str]:
        return self.raw_data.get("SecretArn")

    @property
    def session_id(self) -> T.Optional[str]:
        return self.raw_data.get("SessionId")

    @property
    def status(self) -> T.Optional["StatusStringType"]:
        return self.raw_data.get("Status")

    @property
    def sub_statements(self) -> T.Optional[T.List["SubStatementDataTypeDef"]]:
        return self.raw_data.get("SubStatements")

    @property
    def updated_at(self) -> T.Optional[datetime]:
        return self.raw_data.get("UpdatedAt")

    @property
    def workgroup_name(self) -> T.Optional[str]:
        return self.raw_data.get("WorkgroupName")

    @property
    def is_aborted(self) -> bool:
        return self.status == "ABORTED"

    @property
    def is_all(self) -> bool:
        return self.status == "ALL"

    @property
    def is_failed(self) -> bool:
        return self.status == "FAILED"

    @property
    def is_finished(self) -> bool:
        return self.status == "FINISHED"

    @property
    def is_picked(self) -> bool:
        return self.status == "PICKED"

    @property
    def is_started(self) -> bool:
        return self.status == "STARTED"

    @property
    def is_submitted(self) -> bool:
        return self.status == "SUBMITTED"

    @property
    def core_data(self) -> T_KWARGS:
        return {
            "id": self.id,
            "status": self.status,
            "query_string": self.query_string,
            "database": self.database,
            "created_at": self.created_at,
            "duration": self.duration,
            "has_result_set": self.has_result_set,
        }


class RedshiftDataType(str, enum.Enum):
    """
    Enumeration of Redshift data types as returned by the Data API
    """

    # String types
    VARCHAR = "varchar"
    CHAR = "char"
    TEXT = "text"

    # Integer types
    INT2 = "int2"  # SMALLINT
    INT4 = "int4"  # INTEGER
    INT8 = "int8"  # BIGINT

    # Floating point types
    FLOAT4 = "float4"  # REAL
    FLOAT8 = "float8"  # DOUBLE PRECISION

    # Numeric/Decimal types
    NUMERIC = "numeric"
    DECIMAL = "decimal"

    # Boolean type
    BOOL = "bool"

    # Date/Time types
    DATE = "date"
    TIME = "time"
    TIMESTAMP = "timestamp"
    TIMESTAMPTZ = "timestamptz"

    # Binary types
    VARBYTE = "varbyte"

    # Other types that might be encountered
    UUID = "uuid"
    JSON = "json"
    JSONB = "jsonb"

    NAME = "name"
    OID = "oid"
    ACL_ITEM = "_aclitem"
    BLANK_PADDED_CHAR = "bpchar"


type_to_field_mapping = {
    RedshiftDataType.BOOL.value: "booleanValue",
    RedshiftDataType.CHAR.value: "stringValue",
    RedshiftDataType.DATE.value: "stringValue",
    RedshiftDataType.DECIMAL.value: "doubleValue",
    RedshiftDataType.FLOAT4.value: "doubleValue",
    RedshiftDataType.FLOAT8.value: "doubleValue",
    RedshiftDataType.INT2.value: "longValue",
    RedshiftDataType.INT4.value: "longValue",
    RedshiftDataType.INT8.value: "longValue",
    RedshiftDataType.JSON.value: "stringValue",
    RedshiftDataType.JSONB.value: "stringValue",
    RedshiftDataType.NUMERIC.value: "stringValue",
    RedshiftDataType.TEXT.value: "stringValue",
    RedshiftDataType.TIME.value: "stringValue",
    RedshiftDataType.TIMESTAMP.value: "stringValue",
    RedshiftDataType.TIMESTAMPTZ.value: "stringValue",
    RedshiftDataType.UUID.value: "stringValue",
    RedshiftDataType.VARBYTE.value: "stringValue",
    RedshiftDataType.VARCHAR.value: "stringValue",
    RedshiftDataType.NAME.value: "stringValue",
    RedshiftDataType.OID.value: "longValue",
    RedshiftDataType.ACL_ITEM.value: "stringValue",
    RedshiftDataType.BLANK_PADDED_CHAR.value: "stringValue",
}
"""
From redshift column data type to the field key where the value is stored 
in the Redshift Data API response.
"""


def extract_field_raw_value(
    column_metadata: "ColumnMetadataTypeDef",
    field: "FieldTypeDef",
) -> T.Any:
    """
    Extracts the raw value from a Redshift Data API field.
    """
    type_name = column_metadata["typeName"]
    key = type_to_field_mapping[type_name]
    # Todo add support for one type map to multiple field keys and try them in order
    try:
        raw_value = field[key]
        return raw_value
    except KeyError:
        if field.get("isNull", False):
            return None
        else:  # pragma: no cover
            return None


def extract_field_python_native_value(
    column_metadata: "ColumnMetadataTypeDef",
    raw_value: T.Any,
) -> T.Any:
    """
    Extracts the native Python value from a Redshift Data API field.
    """
    if raw_value is None:
        return raw_value
    type_name = column_metadata["typeName"]
    if type_name in [
        RedshiftDataType.TIMESTAMP.value,
        RedshiftDataType.TIMESTAMPTZ.value,
    ]:
        return parse_datetime(raw_value)
    elif type_name == RedshiftDataType.DATE.value:
        return date.fromisoformat(raw_value)
    elif type_name == RedshiftDataType.TIME.value:
        return time.fromisoformat(raw_value)
    elif type_name == RedshiftDataType.VARBYTE.value:
        return base64.b64decode(raw_value)
    else:
        return raw_value


@dataclasses.dataclass
class GetStatementResultResponse(Base):
    """
    API response for
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift-data/paginator/GetStatementResult.html
    """

    raw_data: "GetStatementResultResponseTypeDef" = dataclasses.field(default=REQ)

    @property
    def column_metadata(self) -> list["ColumnMetadataTypeDef"]:
        return self.raw_data.get("ColumnMetadata", [])

    @property
    def records(self) -> list[list["FieldTypeDef"]]:
        return self.raw_data.get("Records", [])

    @property
    def core_data(self) -> T_KWARGS:
        return {
            "column_metadata": self.column_metadata,
            "records": self.records,
        }

    def to_column_oriented_data(
        self,
        debug: bool = False,
    ) -> dict[str, list[T.Any]]:
        """
        Convert records to a column-oriented format. Like::

            {
                "column_name_1": [value1, value2, ...],
                "column_name_2": [value1, value2, ...],
            }
        """
        data = {column_metadata["name"]: [] for column_metadata in self.column_metadata}
        for record in self.records:
            for column_meta, field in zip(self.column_metadata, record):
                try:
                    raw_value = extract_field_raw_value(column_meta, field)
                except Exception:
                    if debug:
                        print("--- column_meta")  # for debug only
                        rprint(column_meta)  # for debug only
                        print("record")  # for debug only
                        rprint(record)  # for debug only
                        print("field")  # for debug only
                        rprint(field)  # for debug only
                    raise
                try:
                    native_value = extract_field_python_native_value(column_meta, raw_value)
                except Exception:
                    if debug:
                        print("--- column_meta")  # for debug only
                        rprint(column_meta)  # for debug only
                        print("record")  # for debug only
                        rprint(record)  # for debug only
                        print("field")  # for debug only
                        rprint(field)  # for debug only
                data[column_meta["name"]].append(native_value)
        return data


class GetStatementResultResponseIterProxy(IterProxy[GetStatementResultResponse]):
    """
    Iterator proxy for :class:`GetStatementResultResponse`.
    """

    def to_column_oriented_data(self) -> dict[str, list[T.Any]]:
        """
        Convert all records in the iterator to a column-oriented format. Like::

            {
                "column_name_1": [value1, value2, ...],
                "column_name_2": [value1, value2, ...],
            }
        """
        data = None
        for get_statement_result in self:
            column_oriented_data = get_statement_result.to_column_oriented_data()
            if data is None:
                data = column_oriented_data
            else:
                for key, value in column_oriented_data.items():
                    data[key].extend(value)
        return data


@dataclasses.dataclass
class VirtualDataFrame:
    """
    A virtual dataframe that can represent tabular data in various formats.

    :param columns: List of column names. Example: ['col1', 'col2', 'col3']
    :param col_data: Dictionary mapping column names to lists of column values.
        Example: {'col1': [1, 2, 3], 'col2': ['a', 'b', 'c'], 'col3': [True, False, True]}
    """

    columns: list[str] = dataclasses.field()
    col_data: dict[str, list[T.Any]] = dataclasses.field()

    def iter_rows(self) -> T.Iterator[tuple[T.Any, ...]]:
        """
        Iterator over rows in the virtual dataframe.
        """
        return zip(*(self.col_data[col] for col in self.columns))

    @cached_property
    def rows(self):
        """
        List of rows in the virtual dataframe.
        """
        return list(zip(*(self.col_data[col] for col in self.columns)))

    @cached_property
    def n_columns(self):
        """
        Number of columns in the virtual dataframe.
        """
        return len(self.columns)

    @cached_property
    def n_rows(self):
        """
        Number of rows in the virtual dataframe.
        """
        return len(self.col_data[self.columns[0]])

    @cached_property
    def tabulate_table(self) -> str:
        """
        Render the virtual dataframe as a table using the `tabulate` library.
        """
        return tabulate.tabulate(
            self.rows,
            headers=self.columns,
            tablefmt="psql",
        )

    @cached_property
    def pandas_df(self) -> "pd.DataFrame":
        """
        Convert the virtual dataframe to a pandas DataFrame.
        """
        return pd.DataFrame(self.col_data)

    @cached_property
    def polars_df(self) -> "pl.DataFrame":
        """
        Convert the virtual dataframe to a polars DataFrame.
        """
        return pl.DataFrame(self.col_data)

    def show(self):
        print(f"({self.n_rows}, {self.n_columns})")
        print(self.tabulate_table)


@dataclasses.dataclass
class ConsolidatedStatementResult:
    """
    Consolidated result from multiple :class:`GetStatementResultResponse` instances.
    """

    response_list: list["GetStatementResultResponse"] = dataclasses.field()

    @cached_property
    def vdf(self) -> "VirtualDataFrame":
        """
        Convert the consolidated results into a VirtualDataFrame.
        """
        columns = None
        col_data: dict[str, list[T.Any]] = dict()
        for res in self.response_list:
            sub_data = res.to_column_oriented_data()
            for col, values in sub_data.items():
                try:
                    col_data[col].extend(values)
                except KeyError:
                    col_data[col] = values
            columns = [dct["name"] for dct in res.column_metadata]
        df = VirtualDataFrame(columns=columns, col_data=col_data)
        return df
