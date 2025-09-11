# -*- coding: utf-8 -*-

"""
Redshift connection parameters and utility functions.
"""

import typing as T
import dataclasses
from datetime import datetime

try:
    import redshift_connector
except ImportError:  # pragma: no cover
    pass
try:
    import sqlalchemy as sa
    from .dialect import RedshiftPostgresDialect, driver_name, dialect_name
except ImportError:  # pragma: no cover
    pass

from func_args.api import REQ, OPT, remove_optional, BaseModel

from .redshift.api import (
    RedshiftCluster,
    get_redshift_cluster,
)
from .redshift_serverless.api import (
    RedshiftServerlessNamespace,
    RedshiftServerlessWorkgroup,
    get_namespace,
    get_workgroup,
)

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_redshift.client import RedshiftClient
    from mypy_boto3_redshift_serverless.client import RedshiftServerlessClient


@dataclasses.dataclass
class BaseRedshiftConnectionParams(BaseModel):
    """
    Base class for Redshift connection parameters.
    """

    host: str = dataclasses.field(default=REQ)
    port: int = dataclasses.field(default=REQ)
    username: str = dataclasses.field(default=REQ)
    password: str = dataclasses.field(default=REQ)
    database: str = dataclasses.field(default=REQ)

    def get_connection(
        self,
        timeout: int = 3,
    ) -> "redshift_connector.Connection":
        """
        Create a Redshift connection using the parameters.

        :return: A redshift_connector.Connection object.
        """
        return redshift_connector.connect(
            host=self.host,
            port=self.port,
            user=self.username,
            password=self.password,
            database=self.database,
            is_serverless=True,
            timeout=timeout,
        )

    @property
    def sqlalchemy_db_url(self) -> "sa.URL":
        url = sa.URL.create(
            drivername=f"{dialect_name}+{driver_name}",
            username=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
        )
        return url

    def get_engine(self, **kwargs) -> "sa.Engine":
        return sa.create_engine(self.sqlalchemy_db_url, **kwargs)


@dataclasses.dataclass
class RedshiftClusterConnectionParams(BaseRedshiftConnectionParams):
    """
    Parameters for connecting to a Redshift cluster.
    Inherits from RedshiftConnectionParams.
    """

    expiration: datetime = dataclasses.field(default=REQ)
    next_refresh_time: datetime = dataclasses.field(default=REQ)
    cluster: RedshiftCluster = dataclasses.field(default=REQ)

    @classmethod
    def new(
        cls,
        redshift_client: "RedshiftClient",
        db_name: str = OPT,
        cluster_identifier: str = OPT,
        duration_seconds: int = OPT,
        custom_domain_name: str = OPT,
    ):
        """
        Create a new instance of :class:`RedshiftClusterConnectionParams`
        based on the Redshift cluster identifier.

        :param redshift_client: boto3.client("redshift") object
        :param db_name: The name of the database to connect to.
        :param cluster_identifier: The identifier of the Redshift cluster.
        :param duration_seconds: Optional duration in seconds for the credentials.
        :param custom_domain_name: Optional custom domain name for the connection.
        """
        cluster = get_redshift_cluster(
            redshift_client=redshift_client,
            cluster_identifier=cluster_identifier,
        )
        kwargs = dict(
            DbName=db_name,
            ClusterIdentifier=cluster_identifier,
            DurationSeconds=duration_seconds,
            CustomDomainName=custom_domain_name,
        )
        response = redshift_client.get_cluster_credentials_with_iam(
            **remove_optional(**kwargs)
        )
        return cls(
            host=cluster.endpoint_address,
            port=cluster.endpoint_port,
            username=response["DbUser"],
            password=response["DbPassword"],
            database=db_name,
            cluster=cluster,
            expiration=response["Expiration"],
            next_refresh_time=response["NextRefreshTime"],
        )


@dataclasses.dataclass
class RedshiftServerlessConnectionParams(BaseRedshiftConnectionParams):
    expiration: datetime = dataclasses.field(default=REQ)
    next_refresh_time: datetime = dataclasses.field(default=REQ)
    namespace: RedshiftServerlessNamespace = dataclasses.field(default=REQ)
    workgroup: RedshiftServerlessWorkgroup = dataclasses.field(default=REQ)

    @classmethod
    def new(
        cls,
        redshift_serverless_client: "RedshiftServerlessClient",
        namespace_name: str,
        workgroup_name: str,
        custom_domain_name: str = OPT,
        duration_seconds: int = OPT,
    ):
        """
        Create a new instance of :class:`RedshiftServerlessConnectionParams`
        based on the redshift serverless namespace and workgroup.

        :param redshift_serverless_client: boto3.client("redshift-serverless") object
        :param namespace_name: The name of the Redshift serverless namespace.
        :param workgroup_name: The name of the Redshift serverless workgroup.
        :param custom_domain_name: Optional custom domain name for the connection.
        :param duration_seconds: Optional duration in seconds for the credentials.
        """
        namespace = get_namespace(
            redshift_serverless_client=redshift_serverless_client,
            namespace_name=namespace_name,
        )
        workgroup = get_workgroup(
            redshift_serverless_client=redshift_serverless_client,
            workgroup_name=workgroup_name,
        )
        kwargs = dict(
            dbName=namespace.db_name,
            workgroupName=workgroup_name,
            customDomainName=custom_domain_name,
            durationSeconds=duration_seconds,
        )
        response = redshift_serverless_client.get_credentials(
            **remove_optional(**kwargs)
        )
        params = cls(
            host=workgroup.endpoint_address,
            port=workgroup.endpoint_port,
            username=response["dbUser"],
            password=response["dbPassword"],
            database=namespace.db_name,
            expiration=response["expiration"],
            next_refresh_time=response["nextRefreshTime"],
            namespace=namespace,
            workgroup=workgroup,
        )
        return params
