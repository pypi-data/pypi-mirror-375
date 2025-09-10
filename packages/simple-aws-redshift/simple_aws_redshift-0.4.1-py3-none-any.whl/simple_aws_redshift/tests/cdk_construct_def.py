# -*- coding: utf-8 -*-

import dataclasses

import requests
from func_args.api import REQ
import cdkit.api as cdkit

import aws_cdk as cdk
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_iam as iam
import aws_cdk.aws_redshiftserverless as redshiftserverless
from constructs import Construct

from .secrets import admin_username, admin_password


def get_my_ip() -> str:
    res = requests.get("https://checkip.amazonaws.com/")
    return res.text.strip()


@dataclasses.dataclass
class ExperimentRedshiftServerlessParams(cdkit.ConstructParams):
    vpc_id: str = dataclasses.field(default=REQ)
    security_group_name: str = dataclasses.field(default=REQ)
    iam_role_name: str = dataclasses.field(default=REQ)
    namespace_name: str = dataclasses.field(default=REQ)
    db_name: str = dataclasses.field(default=REQ)
    admin_username: str = dataclasses.field(default=REQ)
    admin_password: str = dataclasses.field(default=REQ)
    workgroup_name: str = dataclasses.field(default=REQ)


class ExperimentRedshiftServerless(cdkit.BaseConstruct):
    def __init__(
        self,
        scope: Construct,
        params: ExperimentRedshiftServerlessParams,
    ):
        super().__init__(scope=scope, params=params)
        self.params = params

        self.create_security_group()
        self.create_iam_role()
        self.create_namespace()
        self.create_workgroup()

    def create_security_group(self):
        self.vpc = ec2.Vpc.from_lookup(
            scope=self,
            id="Vpc",
            vpc_id=self.params.vpc_id,
        )
        self.sg = ec2.SecurityGroup(
            scope=self,
            id="SecurityGroup",
            vpc=self.vpc,
            allow_all_outbound=True,
        )
        my_ip = get_my_ip()
        self.sg.add_ingress_rule(
            peer=ec2.Peer.ipv4(f"{my_ip}/32"),
            connection=ec2.Port.tcp(5439),
        )

    def create_iam_role(self):
        self.iam_role = iam.Role(
            scope=self,
            id="RedshiftServerlessRole",
            assumed_by=iam.ServicePrincipal("redshift.amazonaws.com"),
            role_name=self.params.iam_role_name,
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonS3ReadOnlyAccess")
            ],
        )

    def create_namespace(self):
        """
        Ref: https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_redshiftserverless/CfnNamespace.html
        """
        self.namespace = redshiftserverless.CfnNamespace(
            scope=self,
            id="RedshiftServerlessNamespace",
            namespace_name=self.params.namespace_name,
            db_name=self.params.db_name,
            admin_username=self.params.admin_username,
            admin_user_password=self.params.admin_password,
            iam_roles=[
                self.iam_role.role_arn,
            ],
        )
        self.namespace.apply_removal_policy(
            cdk.RemovalPolicy.DESTROY,
        )
        self.namespace.node.add_dependency(self.iam_role)

    def create_workgroup(self):
        """
        Ref: https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_redshiftserverless/CfnWorkgroup.html
        """
        selected = self.vpc.select_subnets(subnet_type=ec2.SubnetType.PUBLIC)
        subnet_ids = selected.subnet_ids
        self.workgroup = redshiftserverless.CfnWorkgroup(
            scope=self,
            id="RedshiftServerlessWorkgroup",
            workgroup_name=self.params.workgroup_name,
            namespace_name=self.params.namespace_name,
            base_capacity=8,  # minimal capacity 8 RPUs
            max_capacity=8,
            publicly_accessible=True,
            subnet_ids=subnet_ids,
            security_group_ids=[
                self.sg.security_group_id,
            ],
        )

        self.workgroup.node.add_dependency(self.namespace)
        self.workgroup.node.add_dependency(self.sg)
        self.workgroup.apply_removal_policy(
            cdk.RemovalPolicy.DESTROY,
        )
