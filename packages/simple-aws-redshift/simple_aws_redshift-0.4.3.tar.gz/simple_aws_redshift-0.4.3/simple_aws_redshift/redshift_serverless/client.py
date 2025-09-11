# -*- coding: utf-8 -*-

"""
Improve the original redshift-serverless boto3 API.

Ref:

- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift-serverless.html
"""

import typing as T

import botocore.exceptions
from func_args.api import OPT, remove_optional

from .model import (
    RedshiftServerlessNamespace,
    RedshiftServerlessNamespaceIterProxy,
    RedshiftServerlessWorkgroup,
    RedshiftServerlessWorkgroupIterProxy,
)

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_redshift_serverless.client import RedshiftServerlessClient


def list_namespaces(
    redshift_serverless_client: "RedshiftServerlessClient",
    page_size: int = 100,
    max_items: int = 9999,
) -> RedshiftServerlessNamespaceIterProxy:
    """
    List all Redshift Serverless namespaces with pagination support.
    
    Ref:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift-serverless/paginator/ListNamespaces.html

    :return: `~simple_aws_redshift.model_redshift_serverless.py.RedshiftServerlessNamespaceIterProxy`
    """

    # inner generator function to yield objects
    def func():
        paginator = redshift_serverless_client.get_paginator("list_namespaces")
        response_iterator = paginator.paginate(
            PaginationConfig={
                "MaxItems": max_items,
                "PageSize": page_size,
            }
        )
        for response in response_iterator:
            for dct in response.get("namespaces", []):
                yield RedshiftServerlessNamespace(raw_data=dct)

    # return an iterproxy object that wraps the generator
    return RedshiftServerlessNamespaceIterProxy(func())


def get_namespace(
    redshift_serverless_client: "RedshiftServerlessClient",
    namespace_name: str,
) -> T.Optional[RedshiftServerlessNamespace]:
    """
    Get a specific Redshift Serverless namespace by name.
    
    :return: None if the namespace does not exist.

    Ref:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift-serverless/client/get_namespace.html
    """
    try:
        response = redshift_serverless_client.get_namespace(
            namespaceName=namespace_name,
        )
        return RedshiftServerlessNamespace(raw_data=response["namespace"])
    except botocore.exceptions.ClientError as e:
        # return None if the namespace does not exist
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            return None
        else:  # pragma: no cover
            raise


def delete_namespace(
    redshift_serverless_client: "RedshiftServerlessClient",
    namespace_name: str,
    final_snapshot_name: str = OPT,
    final_snapshot_retention_period: int = OPT,
) -> T.Optional[RedshiftServerlessNamespace]:
    """
    Delete a Redshift Serverless namespace with optional final snapshot.
    
    :return: None if the namespace does not exist, otherwise return the deleted namespace object.

    Ref:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift-serverless/client/delete_namespace.html
    """
    try:
        response = redshift_serverless_client.delete_namespace(
            **remove_optional(
                namespaceName=namespace_name,
                finalSnapshotName=final_snapshot_name,
                finalSnapshotRetentionPeriod=final_snapshot_retention_period,
            ),
        )
        return RedshiftServerlessNamespace(raw_data=response["namespace"])
    except botocore.exceptions.ClientError as e:
        # return None if the namespace does not exist
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            return None
        else:  # pragma: no cover
            raise


def list_workgroups(
    redshift_serverless_client: "RedshiftServerlessClient",
    owner_account: str = OPT,
    page_size: int = 100,
    max_items: int = 9999,
) -> RedshiftServerlessWorkgroupIterProxy:
    """
    List all Redshift Serverless workgroups with pagination support.
    
    :return: `~simple_aws_redshift.model_redshift_serverless.py.RedshiftServerlessWorkgroupIterProxy`

    Ref:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift-serverless/paginator/ListWorkgroups.html
    """

    # inner generator function to yield objects
    def func():
        paginator = redshift_serverless_client.get_paginator("list_workgroups")
        response_iterator = paginator.paginate(
            **remove_optional(
                ownerAccount=owner_account,
                PaginationConfig={
                    "MaxItems": max_items,
                    "PageSize": page_size,
                },
            ),
        )
        for response in response_iterator:
            for dct in response.get("workgroups", []):
                yield RedshiftServerlessWorkgroup(raw_data=dct)

    # return an iterproxy object that wraps the generator
    return RedshiftServerlessWorkgroupIterProxy(func())


def get_workgroup(
    redshift_serverless_client: "RedshiftServerlessClient",
    workgroup_name: str,
) -> T.Optional[RedshiftServerlessWorkgroup]:
    """
    Get a specific Redshift Serverless workgroup by name.
    
    :return: None if the workgroup does not exist.

    Ref:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift-serverless/client/get_workgroup.html
    """
    try:
        response = redshift_serverless_client.get_workgroup(
            workgroupName=workgroup_name,
        )
        return RedshiftServerlessWorkgroup(raw_data=response["workgroup"])
    except botocore.exceptions.ClientError as e:
        # return None if the workgroup does not exist
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            return None
        else:  # pragma: no cover
            raise


def delete_workgroup(
    redshift_serverless_client: "RedshiftServerlessClient",
    workgroup_name: str,
) -> T.Optional[RedshiftServerlessWorkgroup]:
    """
    Delete a Redshift Serverless workgroup.
    
    :return: None if the workgroup does not exist, otherwise return the deleted workgroup object.

    Ref:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift-serverless/client/delete_workgroup.html
    """
    try:
        response = redshift_serverless_client.delete_workgroup(
            workgroupName=workgroup_name,
        )
        return RedshiftServerlessWorkgroup(raw_data=response["workgroup"])
    except botocore.exceptions.ClientError as e:
        # return None if the workgroup does not exist
        if e.response["Error"]["Code"] == "ResourceNotFoundException":
            return None
        else:  # pragma: no cover
            raise
