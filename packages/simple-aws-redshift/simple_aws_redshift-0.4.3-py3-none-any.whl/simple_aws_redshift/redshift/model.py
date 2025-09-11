# -*- coding: utf-8 -*-

"""
Data models for AWS Redshift Cluster resources.

Ref:

- https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift-serverless.html
"""

import typing as T
import datetime
import dataclasses

from func_args.api import T_KWARGS, REQ
from enum_mate.api import BetterStrEnum
from iterproxy import IterProxy

from ..model import Base

if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_redshift.type_defs import (
        ClusterTypeDef,
        ClusterSecurityGroupMembershipTypeDef,
        VpcSecurityGroupMembershipTypeDef,
        ClusterParameterGroupStatusTypeDef,
        PendingModifiedValuesTypeDef,
        RestoreStatusTypeDef,
        DataTransferProgressTypeDef,
        HsmStatusTypeDef,
        ClusterSnapshotCopyStatusTypeDef,
        ClusterNodeTypeDef,
        ElasticIpStatusTypeDef,
        EndpointTypeDef,
        ClusterIamRoleTypeDef,
        DeferredMaintenanceWindowTypeDef,
        ScheduleStateType,
        AquaConfigurationTypeDef,
        ReservedNodeExchangeStatusTypeDef,
        SecondaryClusterInfoTypeDef,
        ResizeInfoTypeDef,
    )
    from mypy_boto3_redshift.client import RedshiftClient


class ClusterStatus(BetterStrEnum):
    """
    Enum for Redshift cluster status.
    """

    AVAILABLE = "available"
    AVAILABLE_PREP_FOR_RESIZE = "available, prep-for-resize"
    AVAILABLE_RESIZE_CLEANUP = "available, resize-cleanup"
    CANCELLING_RESIZE = "cancelling-resize"
    CREATING = "creating"
    DELETING = "deleting"
    FINAL_SNAPSHOT = "final-snapshot"
    HARDWARE_FAILURE = "hardware-failure"
    INCOMPATIBLE_HSM = "incompatible-hsm"
    INCOMPATIBLE_NETWORK = "incompatible-network"
    INCOMPATIBLE_PARAMETERS = "incompatible-parameters"
    INCOMPATIBLE_RESTORE = "incompatible-restore"
    MODIFYING = "modifying"
    PAUSED = "paused"
    REBOOTING = "rebooting"
    RENAMING = "renaming"
    RESIZING = "resizing"
    ROTATING_KEYS = "rotating-keys"
    STORAGE_FULL = "storage-full"
    UPDATING_HSM = "updating-hsm"


class ClusterAvailabilityStatus(BetterStrEnum):
    """
    Enum for Redshift cluster availability status.
    """

    AVAILABLE = "Available"
    UNAVAILABLE = "Unavailable"
    MAINTENANCE = "Maintenance"
    MODIFYING = "Modifying"
    FAILED = "Failed"


@dataclasses.dataclass
class RedshiftCluster(Base):
    """
    Redshift Cluster object.

    Ref:

    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift/client/describe_clusters.html
    - https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/redshift/paginator/DescribeClusters.html
    """

    raw_data: "ClusterTypeDef" = dataclasses.field(default=REQ)

    @property
    def allow_version_upgrade(self) -> T.Optional[bool]:
        return self.raw_data.get("AllowVersionUpgrade")

    @property
    def automated_snapshot_retention_period(self) -> T.Optional[int]:
        return self.raw_data.get("AutomatedSnapshotRetentionPeriod")

    @property
    def availability_zone(self) -> T.Optional[str]:
        return self.raw_data.get("AvailabilityZone")

    @property
    def availability_zone_relocation_status(self) -> T.Optional[str]:
        return self.raw_data.get("AvailabilityZoneRelocationStatus")

    @property
    def cluster_availability_status(self) -> T.Optional[str]:
        return self.raw_data.get("ClusterAvailabilityStatus")

    @property
    def cluster_create_time(self) -> T.Optional[datetime.datetime]:
        return self.raw_data.get("ClusterCreateTime")

    @property
    def cluster_identifier(self) -> T.Optional[str]:
        return self.raw_data.get("ClusterIdentifier")

    @property
    def cluster_namespace_arn(self) -> T.Optional[str]:
        return self.raw_data.get("ClusterNamespaceArn")

    @property
    def cluster_nodes(self) -> T.Optional[T.List["ClusterNodeTypeDef"]]:
        return self.raw_data.get("ClusterNodes")

    @property
    def cluster_parameter_groups(
        self,
    ) -> T.Optional[T.List["ClusterParameterGroupStatusTypeDef"]]:
        return self.raw_data.get("ClusterParameterGroups")

    @property
    def cluster_public_key(self) -> T.Optional[str]:
        return self.raw_data.get("ClusterPublicKey")

    @property
    def cluster_revision_number(self) -> T.Optional[str]:
        return self.raw_data.get("ClusterRevisionNumber")

    @property
    def cluster_security_groups(
        self,
    ) -> T.Optional[T.List["ClusterSecurityGroupMembershipTypeDef"]]:
        return self.raw_data.get("ClusterSecurityGroups")

    @property
    def cluster_snapshot_copy_status(
        self,
    ) -> T.Optional["ClusterSnapshotCopyStatusTypeDef"]:
        return self.raw_data.get("ClusterSnapshotCopyStatus")

    @property
    def cluster_status(self) -> T.Optional[str]:
        return self.raw_data.get("ClusterStatus")

    @property
    def cluster_subnet_group_name(self) -> T.Optional[str]:
        return self.raw_data.get("ClusterSubnetGroupName")

    @property
    def cluster_version(self) -> T.Optional[str]:
        return self.raw_data.get("ClusterVersion")

    @property
    def custom_domain_certificate_arn(self) -> T.Optional[str]:
        return self.raw_data.get("CustomDomainCertificateArn")

    @property
    def custom_domain_certificate_expiry_date(self) -> T.Optional[datetime.datetime]:
        return self.raw_data.get("CustomDomainCertificateExpiryDate")

    @property
    def custom_domain_name(self) -> T.Optional[str]:
        return self.raw_data.get("CustomDomainName")

    @property
    def data_transfer_progress(self) -> T.Optional["DataTransferProgressTypeDef"]:
        return self.raw_data.get("DataTransferProgress")

    @property
    def db_name(self) -> T.Optional[str]:
        return self.raw_data.get("DBName")

    @property
    def default_iam_role_arn(self) -> T.Optional[str]:
        return self.raw_data.get("DefaultIamRoleArn")

    @property
    def deferred_maintenance_windows(
        self,
    ) -> T.Optional[T.List["DeferredMaintenanceWindowTypeDef"]]:
        return self.raw_data.get("DeferredMaintenanceWindows")

    @property
    def elastic_ip_status(self) -> T.Optional["ElasticIpStatusTypeDef"]:
        return self.raw_data.get("ElasticIpStatus")

    @property
    def elastic_resize_number_of_node_options(self) -> T.Optional[str]:
        return self.raw_data.get("ElasticResizeNumberOfNodeOptions")

    @property
    def encrypted(self) -> T.Optional[bool]:
        return self.raw_data.get("Encrypted")

    @property
    def endpoint(self) -> T.Optional["EndpointTypeDef"]:
        return self.raw_data.get("Endpoint")

    @property
    def enhanced_vpc_routing(self) -> T.Optional[bool]:
        return self.raw_data.get("EnhancedVpcRouting")

    @property
    def expected_next_snapshot_schedule_time(self) -> T.Optional[datetime.datetime]:
        return self.raw_data.get("ExpectedNextSnapshotScheduleTime")

    @property
    def expected_next_snapshot_schedule_time_status(self) -> T.Optional[str]:
        return self.raw_data.get("ExpectedNextSnapshotScheduleTimeStatus")

    @property
    def hsm_status(self) -> T.Optional["HsmStatusTypeDef"]:
        return self.raw_data.get("HsmStatus")

    @property
    def iam_roles(self) -> T.Optional[T.List["ClusterIamRoleTypeDef"]]:
        return self.raw_data.get("IamRoles")

    @property
    def ip_address_type(self) -> T.Optional[str]:
        return self.raw_data.get("IpAddressType")

    @property
    def kms_key_id(self) -> T.Optional[str]:
        return self.raw_data.get("KmsKeyId")

    @property
    def maintenance_track_name(self) -> T.Optional[str]:
        return self.raw_data.get("MaintenanceTrackName")

    @property
    def manual_snapshot_retention_period(self) -> T.Optional[int]:
        return self.raw_data.get("ManualSnapshotRetentionPeriod")

    @property
    def master_password_secret_arn(self) -> T.Optional[str]:
        return self.raw_data.get("MasterPasswordSecretArn")

    @property
    def master_password_secret_kms_key_id(self) -> T.Optional[str]:
        return self.raw_data.get("MasterPasswordSecretKmsKeyId")

    @property
    def master_username(self) -> T.Optional[str]:
        return self.raw_data.get("MasterUsername")

    @property
    def modify_status(self) -> T.Optional[str]:
        return self.raw_data.get("ModifyStatus")

    @property
    def multi_az(self) -> T.Optional[str]:
        return self.raw_data.get("MultiAZ")

    @property
    def multi_az_secondary(self) -> T.Optional["SecondaryClusterInfoTypeDef"]:
        return self.raw_data.get("MultiAZSecondary")

    @property
    def next_maintenance_window_start_time(self) -> T.Optional[datetime.datetime]:
        return self.raw_data.get("NextMaintenanceWindowStartTime")

    @property
    def node_type(self) -> T.Optional[str]:
        return self.raw_data.get("NodeType")

    @property
    def number_of_nodes(self) -> T.Optional[int]:
        return self.raw_data.get("NumberOfNodes")

    @property
    def pending_actions(self) -> T.Optional[T.List[str]]:
        return self.raw_data.get("PendingActions")

    @property
    def pending_modified_values(self) -> T.Optional["PendingModifiedValuesTypeDef"]:
        return self.raw_data.get("PendingModifiedValues")

    @property
    def preferred_maintenance_window(self) -> T.Optional[str]:
        return self.raw_data.get("PreferredMaintenanceWindow")

    @property
    def publicly_accessible(self) -> T.Optional[bool]:
        return self.raw_data.get("PubliclyAccessible")

    @property
    def reserved_node_exchange_status(
        self,
    ) -> T.Optional["ReservedNodeExchangeStatusTypeDef"]:
        return self.raw_data.get("ReservedNodeExchangeStatus")

    @property
    def resize_info(self) -> T.Optional["ResizeInfoTypeDef"]:
        return self.raw_data.get("ResizeInfo")

    @property
    def restore_status(self) -> T.Optional["RestoreStatusTypeDef"]:
        return self.raw_data.get("RestoreStatus")

    @property
    def snapshot_schedule_identifier(self) -> T.Optional[str]:
        return self.raw_data.get("SnapshotScheduleIdentifier")

    @property
    def snapshot_schedule_state(self) -> T.Optional[str]:
        return self.raw_data.get("SnapshotScheduleState")

    @property
    def tags(self) -> T.Optional[T.List[T.Dict[str, str]]]:
        return self.raw_data.get("Tags")

    @property
    def total_storage_capacity_in_mega_bytes(self) -> T.Optional[int]:
        return self.raw_data.get("TotalStorageCapacityInMegaBytes")

    @property
    def vpc_id(self) -> T.Optional[str]:
        return self.raw_data.get("VpcId")

    @property
    def vpc_security_groups(
        self,
    ) -> T.Optional[T.List["VpcSecurityGroupMembershipTypeDef"]]:
        return self.raw_data.get("VpcSecurityGroups")

    @property
    def core_data(self) -> T_KWARGS:
        return {
            "cluster_identifier": self.cluster_identifier,
            "cluster_namespace_arn": self.cluster_namespace_arn,
            "cluster_status": self.cluster_status,
            "cluster_availability_status": self.cluster_availability_status,
            "node_type": self.node_type,
            "number_of_nodes": self.number_of_nodes,
            "cluster_create_time": self.cluster_create_time,
            "db_name": self.db_name,
        }

    @property
    def is_available(self) -> bool:
        return self.cluster_status == ClusterStatus.AVAILABLE.value

    @property
    def is_creating(self) -> bool:
        return self.cluster_status == ClusterStatus.CREATING.value

    @property
    def is_deleting(self) -> bool:
        return self.cluster_status == ClusterStatus.DELETING.value

    @property
    def is_modifying(self) -> bool:
        return self.cluster_status == ClusterStatus.MODIFYING.value

    @property
    def is_paused(self) -> bool:
        return self.cluster_status == ClusterStatus.PAUSED.value

    @property
    def is_rebooting(self) -> bool:
        return self.cluster_status == ClusterStatus.REBOOTING.value

    @property
    def is_resizing(self) -> bool:
        return self.cluster_status == ClusterStatus.RESIZING.value

    @property
    def endpoint_address(self) -> T.Optional[str]:
        if self.endpoint:  # pragma: no cover
            return self.endpoint.get("Address")
        return None

    @property
    def endpoint_port(self) -> T.Optional[int]:
        if self.endpoint:  # pragma: no cover
            return self.endpoint.get("Port")
        return None


class RedshiftClusterIterProxy(IterProxy[RedshiftCluster]):
    """
    Iterator proxy for :class:`RedshiftCluster`.
    """
