# -*- coding: utf-8 -*-

"""
Data models for AWS Redshift Serverless resources.

Ref:

- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift-serverless.html
"""

import typing as T
import datetime
import dataclasses

from func_args.api import T_KWARGS, REQ
from iterproxy import IterProxy

from ..model import Base

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_redshift_serverless.literals import (
        NamespaceStatusType,
        WorkgroupStatusType,
    )
    from mypy_boto3_redshift_serverless.type_defs import (
        NamespaceTypeDef,
        WorkgroupTypeDef,
    )


@dataclasses.dataclass
class RedshiftServerlessNamespace(Base):
    """
    Redshift Serverless Namespace object.

    Ref:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift-serverless/client/get_namespace.html
    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift-serverless/client/list_namespaces.html
    """

    raw_data: "NamespaceTypeDef" = dataclasses.field(default=REQ)

    @property
    def admin_password_secret_arn(self) -> T.Union[str]:
        return self.raw_data.get("adminPasswordSecretArn")

    @property
    def admin_password_secret_kms_key_id(self) -> T.Optional[str]:
        return self.raw_data.get("adminPasswordSecretKmsKeyId")

    @property
    def admin_username(self) -> T.Optional[str]:
        return self.raw_data.get("adminUsername")

    @property
    def creation_date(self) -> T.Optional[datetime.datetime]:
        return self.raw_data.get("creationDate")

    @property
    def db_name(self) -> T.Optional[str]:
        return self.raw_data.get("dbName")

    @property
    def default_iam_role_arn(self) -> T.Optional[str]:
        return self.raw_data.get("defaultIamRoleArn")

    @property
    def iam_roles(self) -> T.Optional[T.List[str]]:
        return self.raw_data.get("iamRoles")

    @property
    def kms_key_id(self) -> T.Optional[str]:
        return self.raw_data.get("kmsKeyId")

    @property
    def log_exports(self) -> T.Optional[T.List[str]]:
        return self.raw_data.get("logExports")

    @property
    def namespace_arn(self) -> T.Optional[str]:
        return self.raw_data.get("namespaceArn")

    @property
    def namespace_id(self) -> T.Optional[str]:
        return self.raw_data.get("namespaceId")

    @property
    def namespace_name(self) -> T.Optional[str]:
        return self.raw_data.get("namespaceName")

    @property
    def status(self) -> T.Optional["NamespaceStatusType"]:
        return self.raw_data.get("status")

    @property
    def core_data(self) -> T_KWARGS:
        return {
            "namespace_name": self.namespace_name,
            "namespace_id": self.namespace_id,
            "namespace_arn": self.namespace_arn,
            "status": self.status,
            "creation_date": self.creation_date,
        }

    @property
    def is_available(self) -> bool:
        return self.status == "AVAILABLE"

    @property
    def is_modifying(self) -> bool:
        return self.status == "MODIFYING"

    @property
    def is_deleting(self) -> bool:
        return self.status == "DELETING"


@dataclasses.dataclass
class RedshiftServerlessWorkgroup(Base):
    """
    Redshift Serverless Workgroup object.

    Ref:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift-serverless/client/get_workgroup.html
    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift-serverless/client/list_workgroups.html
    """

    raw_data: "WorkgroupTypeDef" = dataclasses.field(default=REQ)

    @property
    def base_capacity(self) -> T.Optional[int]:
        return self.raw_data.get("baseCapacity")

    @property
    def config_parameters(self) -> T.Optional[T.List[T.Dict[str, str]]]:
        return self.raw_data.get("configParameters")

    @property
    def creation_date(self) -> T.Optional[datetime.datetime]:
        return self.raw_data.get("creationDate")

    @property
    def cross_account_vpcs(self) -> T.Optional[T.List[str]]:
        return self.raw_data.get("crossAccountVpcs")

    @property
    def custom_domain_certificate_arn(self) -> T.Optional[str]:
        return self.raw_data.get("customDomainCertificateArn")

    @property
    def custom_domain_certificate_expiry_time(self) -> T.Optional[datetime.datetime]:
        return self.raw_data.get("customDomainCertificateExpiryTime")

    @property
    def custom_domain_name(self) -> T.Optional[str]:
        return self.raw_data.get("customDomainName")

    @property
    def endpoint(self) -> T.Optional[T.Dict[str, T.Any]]:
        return self.raw_data.get("endpoint")

    @property
    def enhanced_vpc_routing(self) -> T.Optional[bool]:
        return self.raw_data.get("enhancedVpcRouting")

    @property
    def ip_address_type(self) -> T.Optional[str]:
        return self.raw_data.get("ipAddressType")

    @property
    def max_capacity(self) -> T.Optional[int]:
        return self.raw_data.get("maxCapacity")

    @property
    def namespace_name(self) -> T.Optional[str]:
        return self.raw_data.get("namespaceName")

    @property
    def port(self) -> T.Optional[int]:
        return self.raw_data.get("port")

    @property
    def publicly_accessible(self) -> T.Optional[bool]:
        return self.raw_data.get("publiclyAccessible")

    @property
    def security_group_ids(self) -> T.Optional[T.List[str]]:
        return self.raw_data.get("securityGroupIds")

    @property
    def status(self) -> T.Optional["WorkgroupStatusType"]:
        return self.raw_data.get("status")

    @property
    def subnet_ids(self) -> T.Optional[T.List[str]]:
        return self.raw_data.get("subnetIds")

    @property
    def workgroup_arn(self) -> T.Optional[str]:
        return self.raw_data.get("workgroupArn")

    @property
    def workgroup_id(self) -> T.Optional[str]:
        return self.raw_data.get("workgroupId")

    @property
    def workgroup_name(self) -> T.Optional[str]:
        return self.raw_data.get("workgroupName")

    @property
    def core_data(self) -> T_KWARGS:
        return {
            "workgroup_name": self.workgroup_name,
            "workgroup_id": self.workgroup_id,
            "workgroup_arn": self.workgroup_arn,
            "status": self.status,
            "namespace_name": self.namespace_name,
            "creation_date": self.creation_date,
        }

    @property
    def is_available(self) -> bool:
        return self.status == "AVAILABLE"

    @property
    def is_creating(self) -> bool:
        return self.status == "CREATING"

    @property
    def is_modifying(self) -> bool:
        return self.status == "MODIFYING"

    @property
    def is_deleting(self) -> bool:
        return self.status == "DELETING"

    @property
    def endpoint_address(self) -> str:
        return self.endpoint["address"]

    @property
    def endpoint_port(self) -> int:
        return self.endpoint["port"]


class RedshiftServerlessNamespaceIterProxy(IterProxy[RedshiftServerlessNamespace]):
    """
    Iterator proxy for :class:`RedshiftServerlessNamespace`.
    """


class RedshiftServerlessWorkgroupIterProxy(IterProxy[RedshiftServerlessWorkgroup]):
    """
    Iterator proxy for :class:`RedshiftServerlessWorkgroup`.
    """
