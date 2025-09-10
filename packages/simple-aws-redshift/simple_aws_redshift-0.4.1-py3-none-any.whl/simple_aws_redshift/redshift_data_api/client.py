# -*- coding: utf-8 -*-

"""
Improve the original redshift data api boto3 API.

Ref:

- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift-data.html
"""

import typing as T
import warnings
import dataclasses

import botocore.exceptions
from func_args.api import REQ, OPT, remove_optional, BaseModel, BaseFrozenModel
from ..vendor.waiter import Waiter

from .model import (
    DescribeStatementResponse,
    GetStatementResultResponse,
    GetStatementResultResponseIterProxy,
    VirtualDataFrame,
    ConsolidatedStatementResult,
)

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_redshift_data.client import RedshiftDataAPIServiceClient
    from mypy_boto3_redshift_data.literals import ResultFormatStringType
    from mypy_boto3_redshift_data.type_defs import (
        ExecuteStatementOutputTypeDef,
        GetStatementResultResponseTypeDef,
    )


def get_statement_result(
    redshift_data_api_client: "RedshiftDataAPIServiceClient",
    id: str,
    max_items: int = 1000,
) -> GetStatementResultResponseIterProxy:
    """
    Retrieves the result of a SQL statement execution using the Redshift Data API.

    This function automatically paginates through all result pages and returns
    an iterator proxy that yields GetStatementResultResponse objects for each page.

    :param redshift_data_api_client: boto3.client("redshift-data") object
    :param id: The identifier of the SQL statement to retrieve results for
    :param max_items: Maximum number of items to return across all pages

    :return: :class:`~simple_aws_redshift.redshift_data_api.model.GetStatementResultResponseIterProxy`

    Reference:

    - get_statement_result: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift-data/client/get_statement_result.html
    - GetStatementResult: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift-data/paginator/GetStatementResult.html

    .. note::

        get_statement_result can only return results that are in JSON format!
        for CSV, please use get_statement_result_v2.
    """

    def func():
        paginator = redshift_data_api_client.get_paginator("get_statement_result")
        response_iterator = paginator.paginate(
            Id=id,
            PaginationConfig=dict(
                MaxItems=max_items,
            ),
        )
        get_statement_result_response: GetStatementResultResponseTypeDef
        for get_statement_result_response in response_iterator:
            statement_result = GetStatementResultResponse(
                raw_data=get_statement_result_response
            )
            yield statement_result

    return GetStatementResultResponseIterProxy(func())


# TODO: depracate this
@dataclasses.dataclass
class RunSqlResult(BaseModel):
    """
    Result of running a SQL statement using the Redshift Data API.

    :param execute_statement_response: Response from the `execute_statement` API call.
    :param describe_statement_response: Response from the `describe_statement` API call.
    """

    # fmt: off
    execute_statement_response: "ExecuteStatementOutputTypeDef" = dataclasses.field(default=REQ)
    describe_statement_response: "DescribeStatementResponse" = dataclasses.field(default=REQ)
    # fmt: on

    @property
    def execution_id(self) -> str:
        """
        Get the execution ID of the SQL statement. This ID can be used to
        retrieve the results of the SQL execution using the `get_statement_result` API.
        """
        warnings.warn(
            "RunSqlResult is deprecated, use `SqlCommand` instead.",
            category=DeprecationWarning,
        )
        return self.execute_statement_response["Id"]


# TODO: depracate this
def run_sql(
    redshift_data_api_client: "RedshiftDataAPIServiceClient",
    sql: str,
    client_token: str = OPT,
    cluster_identifier: str = OPT,
    database: str = OPT,
    db_user: str = OPT,
    parameters: dict[str, T.Any] = OPT,
    result_format: "ResultFormatStringType" = OPT,
    secret_arn: str = OPT,
    session_id: str = OPT,
    session_keep_alive_seconds: int = OPT,
    statement_name: str = OPT,
    with_event: bool = OPT,
    workgroup_name: str = OPT,
    delay: int = 1,
    timeout: int = 10,
    verbose: bool = False,
    raises_on_error: bool = True,
):
    """
    Run redshift SQL statement using Data API and get the results. It will
    run ``execute_statement`` API to run the SQL asynchronously, then do a
    long polling to check the status of the SQL execution using``describe_statement``
    API. Once the SQL execution is finished, it will run ``get_statement_result``
    API to get the result.

    In other words, this function is a human-friendly wrapper of the Data API.

    :param redshift_data_api_client: boto3.client("redshift-data") object
    :param sql: SQL statement you want to execute.
    :param client_token: Unique identifier for the request to ensure idempotency.
    :param cluster_identifier: cluster identifier. this is for Redshift provisioned cluster only.
    :param database: database name.
    :param db_user: database user name.
    :param parameters: Parameters for the SQL statement.
    :param result_format: Format of the result set (JSON or CSV).
    :param secret_arn: ARN of the secret containing database credentials.
    :param session_id: Database session identifier.
    :param session_keep_alive_seconds: Number of seconds to keep the session alive.
    :param statement_name: statement name. a human-friendly name you want to give
        to this SQL statement.
    :param with_event: Whether to send an event to Amazon EventBridge.
    :param workgroup_name: workgroup name. this is for Redshift serverless only.
    :param delay: how many seconds to wait between each long polling.
    :param timeout: how many seconds to wait before timeout.
    :param verbose: whether to print verbose output during polling.
    :param raises_on_error: whether to raise an exception when the SQL execution fails.

    Reference:

    - execute_statement: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift-data/client/execute_statement.html
    - describe_statement: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift-data/client/describe_statement.html
    - get_statement_result: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift-data/client/get_statement_result.html

    :return: :class:`RunSqlResult` object.
    """
    warnings.warn(
        "run_sql is deprecated, use `SqlCommand` instead.",
        category=DeprecationWarning,
    )
    # --- execute_statement
    # process arguments
    kwargs = dict(
        Sql=sql,
        ClientToken=client_token,
        ClusterIdentifier=cluster_identifier,
        Database=database,
        DbUser=db_user,
        Parameters=parameters,
        ResultFormat=result_format,
        SecretArn=secret_arn,
        SessionId=session_id,
        SessionKeepAliveSeconds=session_keep_alive_seconds,
        StatementName=statement_name,
        WithEvent=with_event,
        WorkgroupName=workgroup_name,
    )
    execute_statement_response = redshift_data_api_client.execute_statement(
        **remove_optional(**kwargs)
    )
    id = execute_statement_response["Id"]

    # --- describe_statement
    # wait for the status to reach FINISHED
    describe_statement_response = None
    for _ in Waiter(delays=delay, timeout=timeout, verbose=verbose):
        try:
            response = redshift_data_api_client.describe_statement(Id=id)
            describe_statement_response = DescribeStatementResponse(raw_data=response)
            # 'SUBMITTED'|'PICKED'|'STARTED'|'FINISHED'|'ABORTED'|'FAILED'|'ALL'
            status = describe_statement_response.status
            if status == "FINISHED":
                break
            # still pending
            elif status in ["SUBMITTED", "PICKED", "STARTED"]:
                continue
            # raise exception when failed
            elif status == "FAILED":
                if raises_on_error:  # pragma: no cover
                    raise RuntimeError(
                        "FAILED! error: {}".format(describe_statement_response.error)
                    )
                else:
                    break
            elif status == "ABORTED":
                if raises_on_error:  # pragma: no cover
                    raise RuntimeError("ABORTED!")
                else:
                    break
            else:  # pragma: no cover
                raise NotImplementedError
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                continue
            else:  # pragma: no cover
                raise e
    run_sql_result = RunSqlResult(
        execute_statement_response=execute_statement_response,
        describe_statement_response=describe_statement_response,
    )
    return run_sql_result


class SqlCommandKeyEnum:
    """
    Keys for internal data storage in SqlCommand.
    """
    execute_statement_response = "execute_statement_response"
    describe_statement_response = "describe_statement_response"
    get_statement_result_iterproxy = "get_statement_result_iterproxy"
    consolidated_statement_result = "consolidated_statement_result"


@dataclasses.dataclass(frozen=True)
class SqlCommand(BaseFrozenModel):
    """
    Command pattern class that encapsulates everything needed to execute a Redshift SQL 
    statement using the Data API and retrieve its results.

    Usage:

    - Use run() for automatic execution of the complete workflow
    - Or call methods in sequence for more control:
        execute_statement() → wait_until_finished() → get_statement_result() → get_consolidated_result()

    Note: The iterproxy returned by get_statement_result() can only be consumed once.
    If you need to iterate multiple times, call get_consolidated_result() instead.

    :param redshift_data_api_client: boto3.client("redshift-data") object
    :param sql: SQL statement you want to execute.
    :param client_token: Unique identifier for the request to ensure idempotency.
    :param cluster_identifier: cluster identifier. this is for Redshift provisioned cluster only.
    :param database: database name.
    :param db_user: database user name.
    :param parameters: Parameters for the SQL statement.
    :param result_format: Format of the result set (JSON or CSV).
    :param secret_arn: ARN of the secret containing database credentials.
    :param session_id: Database session identifier.
    :param session_keep_alive_seconds: Number of seconds to keep the session alive.
    :param statement_name: statement name. a human-friendly name you want to give
        to this SQL statement.
    :param with_event: Whether to send an event to Amazon EventBridge.
    :param workgroup_name: workgroup name. this is for Redshift serverless only.
    :param delay: how many seconds to wait between each long polling.
    :param timeout: how many seconds to wait before timeout.
    :param verbose: whether to print verbose output during polling.
    :param raises_on_error: whether to raise an exception when the SQL execution fails.
    :param _data: internal data storage.

    Reference:

    - execute_statement: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift-data/client/execute_statement.html
    - describe_statement: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift-data/client/describe_statement.html
    - get_statement_result: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift-data/client/get_statement_result.html
    """

    redshift_data_api_client: "RedshiftDataAPIServiceClient" = dataclasses.field(
        default=REQ
    )
    sql: str = dataclasses.field(default=REQ)
    client_token: str = dataclasses.field(default=OPT)
    cluster_identifier: str = dataclasses.field(default=OPT)
    database: str = dataclasses.field(default=OPT)
    db_user: str = dataclasses.field(default=OPT)
    parameters: dict[str, T.Any] = dataclasses.field(default=OPT)
    result_format: "ResultFormatStringType" = dataclasses.field(default="JSON")
    secret_arn: str = dataclasses.field(default=OPT)
    session_id: str = dataclasses.field(default=OPT)
    session_keep_alive_seconds: int = dataclasses.field(default=OPT)
    statement_name: str = dataclasses.field(default=OPT)
    with_event: bool = dataclasses.field(default=OPT)
    workgroup_name: str = dataclasses.field(default=OPT)
    delay: int = dataclasses.field(default=1)
    timeout: int = dataclasses.field(default=10)
    verbose: bool = dataclasses.field(default=False)
    raises_on_error: bool = dataclasses.field(default=True)
    _data: dict[str, T.Any] = dataclasses.field(default_factory=dict)

    def _get_attr(
        self,
        name: str,
        methods: list[T.Callable]
    ):
        try:
            return self._data[name]
        except KeyError:
            classname = self.__class__.__name__
            parts = [
                f"{classname}.{method.__name__}()"
                for method in methods
            ]
            msg = " or ".join(parts)
            error_msg = f"{classname}.{name} doesn't exists, call {msg} first!"
            raise AttributeError(error_msg)

    @property
    def execute_statement_response(self) -> "ExecuteStatementOutputTypeDef":
        """
        Interface to get the response from the `execute_statement` API call.
        """
        return self._get_attr(
            name=SqlCommandKeyEnum.execute_statement_response,
            methods=[
                self.execute_statement,
                self.run,
            ],
        )

    @property
    def describe_statement_response(self) -> "DescribeStatementResponse":
        """
        Interface to get the statement execution status and metadata.
        """
        return self._get_attr(
            name=SqlCommandKeyEnum.execute_statement_response,
            methods=[
                self.wait_until_finished,
                self.run,
            ],
        )

    @property
    def get_statement_result_iterproxy(self) -> "GetStatementResultResponseIterProxy":
        """
        Interface to get the statement execution results as an iterator proxy (consumable only once).
        """
        return self._get_attr(
            name=SqlCommandKeyEnum.get_statement_result_iterproxy,
            methods=[
                self.get_statement_result,
                self.run,
            ],
        )

    @property
    def result(self) -> "ConsolidatedStatementResult":
        """
        Interface to get consolidated results after running the full workflow.
        """
        return self._get_attr(
            name=SqlCommandKeyEnum.consolidated_statement_result,
            methods=[
                self.get_consolidated_result,
                self.run,
            ],
        )

    @property
    def statement_id(self) -> str:
        """
        Get the statement ID of the SQL statement. This ID can be used to
        retrieve the results of the SQL execution using the `get_statement_result` API.
        """
        return self.execute_statement_response["Id"]

    def execute_statement(self) -> "ExecuteStatementOutputTypeDef":
        """
        Run ``execute_statement`` API to run the SQL asynchronously.

        :return: Response from the `execute_statement` API call.
        """
        # process arguments
        kwargs = dict(
            Sql=self.sql,
            ClientToken=self.client_token,
            ClusterIdentifier=self.cluster_identifier,
            Database=self.database,
            DbUser=self.db_user,
            Parameters=self.parameters,
            ResultFormat=self.result_format,
            SecretArn=self.secret_arn,
            SessionId=self.session_id,
            SessionKeepAliveSeconds=self.session_keep_alive_seconds,
            StatementName=self.statement_name,
            WithEvent=self.with_event,
            WorkgroupName=self.workgroup_name,
        )
        execute_statement_response = self.redshift_data_api_client.execute_statement(
            **remove_optional(**kwargs)
        )
        self._data[SqlCommandKeyEnum.execute_statement_response] = (
            execute_statement_response
        )
        return execute_statement_response

    def wait_until_finished(self) -> "DescribeStatementResponse":
        """
        Poll the statement status until it reaches a final state (FINISHED, FAILED, or ABORTED).
        """
        describe_statement_response = None
        for _ in Waiter(
            delays=self.delay,
            timeout=self.timeout,
            verbose=self.verbose,
        ):
            try:
                response = self.redshift_data_api_client.describe_statement(
                    Id=self.statement_id
                )
                describe_statement_response = DescribeStatementResponse(
                    raw_data=response,
                )
                # 'SUBMITTED'|'PICKED'|'STARTED'|'FINISHED'|'ABORTED'|'FAILED'|'ALL'
                status = describe_statement_response.status
                if status == "FINISHED":
                    break
                # still pending
                elif status in ["SUBMITTED", "PICKED", "STARTED"]:
                    continue
                # raise exception when failed
                elif status == "FAILED":
                    if self.raises_on_error:  # pragma: no cover
                        raise RuntimeError(
                            "FAILED! error: {}".format(
                                describe_statement_response.error
                            )
                        )
                    else:
                        break
                elif status == "ABORTED":
                    if self.raises_on_error:  # pragma: no cover
                        raise RuntimeError("ABORTED!")
                    else:
                        break
                else:  # pragma: no cover
                    raise NotImplementedError
            except botocore.exceptions.ClientError as e:
                if e.response["Error"]["Code"] == "ResourceNotFoundException":
                    continue
                else:  # pragma: no cover
                    raise e
        self._data[SqlCommandKeyEnum.describe_statement_response] = (
            describe_statement_response
        )
        return describe_statement_response

    def get_statement_result(self) -> "GetStatementResultResponseIterProxy":
        """
        Retrieve the statement execution results as an iterator proxy (consumable only once).
        """
        iterproxy = get_statement_result(
            redshift_data_api_client=self.redshift_data_api_client,
            id=self.statement_id,
        )
        self._data[SqlCommandKeyEnum.get_statement_result_iterproxy] = iterproxy
        return iterproxy

    def get_consolidated_result_v1(self) -> "ConsolidatedStatementResult":
        """Consolidate JSON format results into a single result object."""
        result = ConsolidatedStatementResult(
            response_list=self.get_statement_result_iterproxy.all(),
        )
        self._data[SqlCommandKeyEnum.consolidated_statement_result] = result
        return result

    def get_consolidated_result_v2(
        self,
    ) -> "ConsolidatedStatementResult":  # pragma: no cover
        """Consolidate CSV format results into a single result object."""
        raise NotImplementedError

    def get_consolidated_result(self) -> "ConsolidatedStatementResult":
        """
        Get consolidated results in the appropriate format based on result_format setting.
        """
        if self.result_format == "JSON":
            return self.get_consolidated_result_v1()
        else:  # pragma: no cover
            return self.get_consolidated_result_v2()

    def run(self):
        """
        Execute the complete SQL workflow:

        execute → wait → get results → consolidate.
        """
        self.execute_statement()
        self.wait_until_finished()
        self.get_statement_result()
        self.get_consolidated_result()
        return self

    def reset(self):
        """
        Reset the internal state to allow re-execution of the SQL command.
        """
        self._data.clear()
