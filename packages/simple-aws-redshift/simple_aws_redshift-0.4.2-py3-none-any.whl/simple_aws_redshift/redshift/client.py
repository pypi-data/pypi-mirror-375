# -*- coding: utf-8 -*-

"""
Improve the original redshift boto3 API.

Ref:

- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift.html
"""

import typing as T

import botocore.exceptions
from func_args.api import OPT, remove_optional

from .model import (
    RedshiftCluster,
    RedshiftClusterIterProxy,
)

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_redshift.client import RedshiftClient


def list_redshift_clusters(
    redshift_client: "RedshiftClient",
    cluster_identifier: str = OPT,
    tag_keys: list[str] = OPT,
    tag_values: list[str] = OPT,
    page_size: int = 100,
    max_items: int = 9999,
) -> RedshiftClusterIterProxy:
    """
    List all Redshift clusters with optional filtering by identifier and tags.

    Ref:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift/paginator/DescribeClusters.html

    :return: `~simple_aws_redshift.redshift.model.RedshiftClusterIterProxy`
    """

    # inner generator function to yield objects
    def func():
        paginator = redshift_client.get_paginator("describe_clusters")
        kwargs = remove_optional(
            ClusterIdentifier=cluster_identifier,
            TagKeys=tag_keys,
            TagValues=tag_values,
            PaginationConfig={
                "MaxItems": max_items,
                "PageSize": page_size,
            },
        )
        response_iterator = paginator.paginate(**remove_optional(**kwargs))
        for response in response_iterator:
            for dct in response.get("Clusters", []):
                yield RedshiftCluster(raw_data=dct)

    # return an iterproxy object that wraps the generator
    return RedshiftClusterIterProxy(func())


def get_redshift_cluster(
    redshift_client: "RedshiftClient",
    cluster_identifier: str = OPT,
) -> T.Optional[RedshiftCluster]:
    """
    Get a specific Redshift cluster by identifier.
    
    :return: None if the redshift cluster does not exist.

    Ref:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift/paginator/DescribeClusters.html
    """
    try:
        redshift_cluster_iterproxy = list_redshift_clusters(
            redshift_client=redshift_client,
            cluster_identifier=cluster_identifier,
        )
        return redshift_cluster_iterproxy.one_or_none()
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "ClusterNotFound":
            return None
        else:
            raise
