# -*- coding: utf-8 -*-

import typing as T
import dataclasses
from functools import cached_property

import cdk_mate.api as cdk_mate

import sqlalchemy as sa
import redshift_connector
from boto_session_manager import BotoSesManager

from .secrets import admin_username, admin_password


@dataclasses.dataclass
class Settings:
    aws_profile: str = dataclasses.field()
    vpc_id: str = dataclasses.field()
    security_group_name: str = dataclasses.field()
    iam_role_name: str = dataclasses.field()
    namespace_name: str = dataclasses.field()
    db_name: str = dataclasses.field()
    admin_username: str = dataclasses.field()
    admin_password: str = dataclasses.field()
    workgroup_name: str = dataclasses.field()
    stack_name: str = dataclasses.field()

    @cached_property
    def bsm(self) -> BotoSesManager:
        return BotoSesManager(profile_name=self.aws_profile)

    @cached_property
    def stack_ctx(self):
        return cdk_mate.StackCtx.new(
            stack_name=self.stack_name,
            bsm=self.bsm,
        )

    @cached_property
    def namespace_data(self) -> dict:
        response = self.bsm.redshiftserverless_client.get_namespace(
            namespaceName=self.namespace_name,
        )
        return response["namespace"]

    @cached_property
    def namespace_db_name(self) -> str:
        return self.namespace_data["dbName"]

    @cached_property
    def workgroup_data(self) -> dict:
        response = self.bsm.redshiftserverless_client.get_workgroup(
            workgroupName=self.workgroup_name,
        )
        return response["workgroup"]

    @cached_property
    def workgroup_endpoint_address(self) -> str:
        return self.workgroup_data["endpoint"]["address"]

    @cached_property
    def workgroup_endpoint_port(self) -> int:
        return self.workgroup_data["endpoint"]["port"]

    @cached_property
    def temp_credentials(self) -> dict:
        res = self.bsm.redshiftserverless_client.get_credentials(
            dbName=self.namespace_db_name,
            workgroupName=self.workgroup_name,
        )
        return res

    @cached_property
    def db_user(self) -> str:
        return self.temp_credentials["dbUser"]

    @cached_property
    def db_password(self) -> str:
        return self.temp_credentials["dbPassword"]

    def print_attrs(self):
        print(f"{self.vpc_id = }")
        print(f"{self.security_group_name = }")
        print(f"{self.namespace_name = }")
        print(f"{self.db_name = }")
        print(f"{self.workgroup_name = }")
        print(f"{self.stack_name = }")

        print(f"{self.namespace_db_name = }")
        print(f"{self.workgroup_endpoint_address = }")
        print(f"{self.workgroup_endpoint_port = }")
        print(f"{self.db_user = }")
        print(f"{self.db_password = }")


def run_test_sql_with_redshift_connector(
    conn: redshift_connector.Connection,
):
    cursor = conn.cursor()
    cursor.execute("SELECT 1;")
    rows = cursor.fetchall()
    print(rows[0])


def run_test_sql_with_sqlalchemy_engine(
    engine: "sa.Engine",
):
    with engine.connect() as conn:
        rows = conn.execute(sa.text("SELECT 1;")).fetchall()
        print(rows[0])


def run_test_sql(
    conn_or_engine: T.Union["redshift_connector.Connection", "sa.Engine"],
):
    if isinstance(conn_or_engine, redshift_connector.Connection):
        run_test_sql_with_redshift_connector(conn_or_engine)
    elif isinstance(conn_or_engine, sa.Engine):
        run_test_sql_with_sqlalchemy_engine(conn_or_engine)
    else:  # pragma: no cover
        raise TypeError


from .bsm import aws_profile


def get_settings():
    name = "simple-aws-redshift-dev"
    name_slug = name.replace("_", "-")
    settings = Settings(
        aws_profile=aws_profile,
        vpc_id="vpc-0d87d639dc2503350",
        security_group_name=name_slug,
        iam_role_name=name_slug,
        namespace_name=name_slug,
        db_name="dev",
        admin_username=admin_username.v,
        admin_password=admin_password.v,
        workgroup_name=name_slug,
        stack_name=name_slug,
    )
    return settings


settings = get_settings()
