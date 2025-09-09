r'''
# `mongodbatlas_cluster`

Refer to the Terraform Registry for docs: [`mongodbatlas_cluster`](https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster).
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from .._jsii import *

import cdktf as _cdktf_9a9027ec
import constructs as _constructs_77d1e7e8


class Cluster(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cluster.Cluster",
):
    '''Represents a {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster mongodbatlas_cluster}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        project_id: builtins.str,
        provider_instance_size_name: builtins.str,
        provider_name: builtins.str,
        accept_data_risks_and_force_replica_set_reconfig: typing.Optional[builtins.str] = None,
        advanced_configuration: typing.Optional[typing.Union["ClusterAdvancedConfiguration", typing.Dict[builtins.str, typing.Any]]] = None,
        auto_scaling_compute_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        auto_scaling_compute_scale_down_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        auto_scaling_disk_gb_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        backing_provider_name: typing.Optional[builtins.str] = None,
        backup_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        bi_connector_config: typing.Optional[typing.Union["ClusterBiConnectorConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        cloud_backup: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cluster_type: typing.Optional[builtins.str] = None,
        disk_size_gb: typing.Optional[jsii.Number] = None,
        encryption_at_rest_provider: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ClusterLabels", typing.Dict[builtins.str, typing.Any]]]]] = None,
        mongo_db_major_version: typing.Optional[builtins.str] = None,
        num_shards: typing.Optional[jsii.Number] = None,
        paused: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        pinned_fcv: typing.Optional[typing.Union["ClusterPinnedFcv", typing.Dict[builtins.str, typing.Any]]] = None,
        pit_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        provider_auto_scaling_compute_max_instance_size: typing.Optional[builtins.str] = None,
        provider_auto_scaling_compute_min_instance_size: typing.Optional[builtins.str] = None,
        provider_disk_iops: typing.Optional[jsii.Number] = None,
        provider_disk_type_name: typing.Optional[builtins.str] = None,
        provider_encrypt_ebs_volume: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        provider_region_name: typing.Optional[builtins.str] = None,
        provider_volume_type: typing.Optional[builtins.str] = None,
        redact_client_log_data: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        replication_factor: typing.Optional[jsii.Number] = None,
        replication_specs: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ClusterReplicationSpecs", typing.Dict[builtins.str, typing.Any]]]]] = None,
        retain_backups_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ClusterTags", typing.Dict[builtins.str, typing.Any]]]]] = None,
        termination_protection_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        timeouts: typing.Optional[typing.Union["ClusterTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        version_release_system: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster mongodbatlas_cluster} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#name Cluster#name}.
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#project_id Cluster#project_id}.
        :param provider_instance_size_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#provider_instance_size_name Cluster#provider_instance_size_name}.
        :param provider_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#provider_name Cluster#provider_name}.
        :param accept_data_risks_and_force_replica_set_reconfig: Submit this field alongside your topology reconfiguration to request a new regional outage resistant topology. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#accept_data_risks_and_force_replica_set_reconfig Cluster#accept_data_risks_and_force_replica_set_reconfig}
        :param advanced_configuration: advanced_configuration block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#advanced_configuration Cluster#advanced_configuration}
        :param auto_scaling_compute_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#auto_scaling_compute_enabled Cluster#auto_scaling_compute_enabled}.
        :param auto_scaling_compute_scale_down_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#auto_scaling_compute_scale_down_enabled Cluster#auto_scaling_compute_scale_down_enabled}.
        :param auto_scaling_disk_gb_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#auto_scaling_disk_gb_enabled Cluster#auto_scaling_disk_gb_enabled}.
        :param backing_provider_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#backing_provider_name Cluster#backing_provider_name}.
        :param backup_enabled: Clusters running MongoDB FCV 4.2 or later and any new Atlas clusters of any type do not support this parameter. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#backup_enabled Cluster#backup_enabled}
        :param bi_connector_config: bi_connector_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#bi_connector_config Cluster#bi_connector_config}
        :param cloud_backup: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#cloud_backup Cluster#cloud_backup}.
        :param cluster_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#cluster_type Cluster#cluster_type}.
        :param disk_size_gb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#disk_size_gb Cluster#disk_size_gb}.
        :param encryption_at_rest_provider: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#encryption_at_rest_provider Cluster#encryption_at_rest_provider}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#id Cluster#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param labels: labels block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#labels Cluster#labels}
        :param mongo_db_major_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#mongo_db_major_version Cluster#mongo_db_major_version}.
        :param num_shards: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#num_shards Cluster#num_shards}.
        :param paused: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#paused Cluster#paused}.
        :param pinned_fcv: pinned_fcv block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#pinned_fcv Cluster#pinned_fcv}
        :param pit_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#pit_enabled Cluster#pit_enabled}.
        :param provider_auto_scaling_compute_max_instance_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#provider_auto_scaling_compute_max_instance_size Cluster#provider_auto_scaling_compute_max_instance_size}.
        :param provider_auto_scaling_compute_min_instance_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#provider_auto_scaling_compute_min_instance_size Cluster#provider_auto_scaling_compute_min_instance_size}.
        :param provider_disk_iops: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#provider_disk_iops Cluster#provider_disk_iops}.
        :param provider_disk_type_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#provider_disk_type_name Cluster#provider_disk_type_name}.
        :param provider_encrypt_ebs_volume: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#provider_encrypt_ebs_volume Cluster#provider_encrypt_ebs_volume}.
        :param provider_region_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#provider_region_name Cluster#provider_region_name}.
        :param provider_volume_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#provider_volume_type Cluster#provider_volume_type}.
        :param redact_client_log_data: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#redact_client_log_data Cluster#redact_client_log_data}.
        :param replication_factor: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#replication_factor Cluster#replication_factor}.
        :param replication_specs: replication_specs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#replication_specs Cluster#replication_specs}
        :param retain_backups_enabled: Flag that indicates whether to retain backup snapshots for the deleted dedicated cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#retain_backups_enabled Cluster#retain_backups_enabled}
        :param tags: tags block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#tags Cluster#tags}
        :param termination_protection_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#termination_protection_enabled Cluster#termination_protection_enabled}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#timeouts Cluster#timeouts}
        :param version_release_system: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#version_release_system Cluster#version_release_system}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__742db278a5f8ce3b0569707b0a97c64056cd4b49a739041d7f3cf330a8e32fd3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = ClusterConfig(
            name=name,
            project_id=project_id,
            provider_instance_size_name=provider_instance_size_name,
            provider_name=provider_name,
            accept_data_risks_and_force_replica_set_reconfig=accept_data_risks_and_force_replica_set_reconfig,
            advanced_configuration=advanced_configuration,
            auto_scaling_compute_enabled=auto_scaling_compute_enabled,
            auto_scaling_compute_scale_down_enabled=auto_scaling_compute_scale_down_enabled,
            auto_scaling_disk_gb_enabled=auto_scaling_disk_gb_enabled,
            backing_provider_name=backing_provider_name,
            backup_enabled=backup_enabled,
            bi_connector_config=bi_connector_config,
            cloud_backup=cloud_backup,
            cluster_type=cluster_type,
            disk_size_gb=disk_size_gb,
            encryption_at_rest_provider=encryption_at_rest_provider,
            id=id,
            labels=labels,
            mongo_db_major_version=mongo_db_major_version,
            num_shards=num_shards,
            paused=paused,
            pinned_fcv=pinned_fcv,
            pit_enabled=pit_enabled,
            provider_auto_scaling_compute_max_instance_size=provider_auto_scaling_compute_max_instance_size,
            provider_auto_scaling_compute_min_instance_size=provider_auto_scaling_compute_min_instance_size,
            provider_disk_iops=provider_disk_iops,
            provider_disk_type_name=provider_disk_type_name,
            provider_encrypt_ebs_volume=provider_encrypt_ebs_volume,
            provider_region_name=provider_region_name,
            provider_volume_type=provider_volume_type,
            redact_client_log_data=redact_client_log_data,
            replication_factor=replication_factor,
            replication_specs=replication_specs,
            retain_backups_enabled=retain_backups_enabled,
            tags=tags,
            termination_protection_enabled=termination_protection_enabled,
            timeouts=timeouts,
            version_release_system=version_release_system,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a Cluster resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the Cluster to import.
        :param import_from_id: The id of the existing Cluster that should be imported. Refer to the {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the Cluster to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7a794416e32a4df7b4cbce061ae7dfa583c3f5e20f3076d57d79f083435c184)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putAdvancedConfiguration")
    def put_advanced_configuration(
        self,
        *,
        change_stream_options_pre_and_post_images_expire_after_seconds: typing.Optional[jsii.Number] = None,
        custom_openssl_cipher_config_tls12: typing.Optional[typing.Sequence[builtins.str]] = None,
        default_max_time_ms: typing.Optional[jsii.Number] = None,
        default_read_concern: typing.Optional[builtins.str] = None,
        default_write_concern: typing.Optional[builtins.str] = None,
        fail_index_key_too_long: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        javascript_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        minimum_enabled_tls_protocol: typing.Optional[builtins.str] = None,
        no_table_scan: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        oplog_min_retention_hours: typing.Optional[jsii.Number] = None,
        oplog_size_mb: typing.Optional[jsii.Number] = None,
        sample_refresh_interval_bi_connector: typing.Optional[jsii.Number] = None,
        sample_size_bi_connector: typing.Optional[jsii.Number] = None,
        tls_cipher_config_mode: typing.Optional[builtins.str] = None,
        transaction_lifetime_limit_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param change_stream_options_pre_and_post_images_expire_after_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#change_stream_options_pre_and_post_images_expire_after_seconds Cluster#change_stream_options_pre_and_post_images_expire_after_seconds}.
        :param custom_openssl_cipher_config_tls12: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#custom_openssl_cipher_config_tls12 Cluster#custom_openssl_cipher_config_tls12}.
        :param default_max_time_ms: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#default_max_time_ms Cluster#default_max_time_ms}.
        :param default_read_concern: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#default_read_concern Cluster#default_read_concern}.
        :param default_write_concern: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#default_write_concern Cluster#default_write_concern}.
        :param fail_index_key_too_long: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#fail_index_key_too_long Cluster#fail_index_key_too_long}.
        :param javascript_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#javascript_enabled Cluster#javascript_enabled}.
        :param minimum_enabled_tls_protocol: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#minimum_enabled_tls_protocol Cluster#minimum_enabled_tls_protocol}.
        :param no_table_scan: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#no_table_scan Cluster#no_table_scan}.
        :param oplog_min_retention_hours: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#oplog_min_retention_hours Cluster#oplog_min_retention_hours}.
        :param oplog_size_mb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#oplog_size_mb Cluster#oplog_size_mb}.
        :param sample_refresh_interval_bi_connector: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#sample_refresh_interval_bi_connector Cluster#sample_refresh_interval_bi_connector}.
        :param sample_size_bi_connector: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#sample_size_bi_connector Cluster#sample_size_bi_connector}.
        :param tls_cipher_config_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#tls_cipher_config_mode Cluster#tls_cipher_config_mode}.
        :param transaction_lifetime_limit_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#transaction_lifetime_limit_seconds Cluster#transaction_lifetime_limit_seconds}.
        '''
        value = ClusterAdvancedConfiguration(
            change_stream_options_pre_and_post_images_expire_after_seconds=change_stream_options_pre_and_post_images_expire_after_seconds,
            custom_openssl_cipher_config_tls12=custom_openssl_cipher_config_tls12,
            default_max_time_ms=default_max_time_ms,
            default_read_concern=default_read_concern,
            default_write_concern=default_write_concern,
            fail_index_key_too_long=fail_index_key_too_long,
            javascript_enabled=javascript_enabled,
            minimum_enabled_tls_protocol=minimum_enabled_tls_protocol,
            no_table_scan=no_table_scan,
            oplog_min_retention_hours=oplog_min_retention_hours,
            oplog_size_mb=oplog_size_mb,
            sample_refresh_interval_bi_connector=sample_refresh_interval_bi_connector,
            sample_size_bi_connector=sample_size_bi_connector,
            tls_cipher_config_mode=tls_cipher_config_mode,
            transaction_lifetime_limit_seconds=transaction_lifetime_limit_seconds,
        )

        return typing.cast(None, jsii.invoke(self, "putAdvancedConfiguration", [value]))

    @jsii.member(jsii_name="putBiConnectorConfig")
    def put_bi_connector_config(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        read_preference: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#enabled Cluster#enabled}.
        :param read_preference: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#read_preference Cluster#read_preference}.
        '''
        value = ClusterBiConnectorConfig(
            enabled=enabled, read_preference=read_preference
        )

        return typing.cast(None, jsii.invoke(self, "putBiConnectorConfig", [value]))

    @jsii.member(jsii_name="putLabels")
    def put_labels(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ClusterLabels", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d79e0f634f55bab2f500fe754a5acf37b0994ea8454f5870ff5d018b4cd8825)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putLabels", [value]))

    @jsii.member(jsii_name="putPinnedFcv")
    def put_pinned_fcv(self, *, expiration_date: builtins.str) -> None:
        '''
        :param expiration_date: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#expiration_date Cluster#expiration_date}.
        '''
        value = ClusterPinnedFcv(expiration_date=expiration_date)

        return typing.cast(None, jsii.invoke(self, "putPinnedFcv", [value]))

    @jsii.member(jsii_name="putReplicationSpecs")
    def put_replication_specs(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ClusterReplicationSpecs", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f5c35d1e3a3d5cbba67b4b06ed0523f7fb641f2bd5fb861ed1ca0910ecf5605)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putReplicationSpecs", [value]))

    @jsii.member(jsii_name="putTags")
    def put_tags(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ClusterTags", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__700bf3a6567a7d87520fe50fa8c17bf8e8d1d58037e267dad9fd37fcc984c99f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTags", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#create Cluster#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#delete Cluster#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#update Cluster#update}.
        '''
        value = ClusterTimeouts(create=create, delete=delete, update=update)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetAcceptDataRisksAndForceReplicaSetReconfig")
    def reset_accept_data_risks_and_force_replica_set_reconfig(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAcceptDataRisksAndForceReplicaSetReconfig", []))

    @jsii.member(jsii_name="resetAdvancedConfiguration")
    def reset_advanced_configuration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdvancedConfiguration", []))

    @jsii.member(jsii_name="resetAutoScalingComputeEnabled")
    def reset_auto_scaling_compute_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoScalingComputeEnabled", []))

    @jsii.member(jsii_name="resetAutoScalingComputeScaleDownEnabled")
    def reset_auto_scaling_compute_scale_down_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoScalingComputeScaleDownEnabled", []))

    @jsii.member(jsii_name="resetAutoScalingDiskGbEnabled")
    def reset_auto_scaling_disk_gb_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoScalingDiskGbEnabled", []))

    @jsii.member(jsii_name="resetBackingProviderName")
    def reset_backing_provider_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackingProviderName", []))

    @jsii.member(jsii_name="resetBackupEnabled")
    def reset_backup_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackupEnabled", []))

    @jsii.member(jsii_name="resetBiConnectorConfig")
    def reset_bi_connector_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBiConnectorConfig", []))

    @jsii.member(jsii_name="resetCloudBackup")
    def reset_cloud_backup(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCloudBackup", []))

    @jsii.member(jsii_name="resetClusterType")
    def reset_cluster_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterType", []))

    @jsii.member(jsii_name="resetDiskSizeGb")
    def reset_disk_size_gb(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDiskSizeGb", []))

    @jsii.member(jsii_name="resetEncryptionAtRestProvider")
    def reset_encryption_at_rest_provider(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionAtRestProvider", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetLabels")
    def reset_labels(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLabels", []))

    @jsii.member(jsii_name="resetMongoDbMajorVersion")
    def reset_mongo_db_major_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMongoDbMajorVersion", []))

    @jsii.member(jsii_name="resetNumShards")
    def reset_num_shards(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumShards", []))

    @jsii.member(jsii_name="resetPaused")
    def reset_paused(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPaused", []))

    @jsii.member(jsii_name="resetPinnedFcv")
    def reset_pinned_fcv(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPinnedFcv", []))

    @jsii.member(jsii_name="resetPitEnabled")
    def reset_pit_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPitEnabled", []))

    @jsii.member(jsii_name="resetProviderAutoScalingComputeMaxInstanceSize")
    def reset_provider_auto_scaling_compute_max_instance_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProviderAutoScalingComputeMaxInstanceSize", []))

    @jsii.member(jsii_name="resetProviderAutoScalingComputeMinInstanceSize")
    def reset_provider_auto_scaling_compute_min_instance_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProviderAutoScalingComputeMinInstanceSize", []))

    @jsii.member(jsii_name="resetProviderDiskIops")
    def reset_provider_disk_iops(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProviderDiskIops", []))

    @jsii.member(jsii_name="resetProviderDiskTypeName")
    def reset_provider_disk_type_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProviderDiskTypeName", []))

    @jsii.member(jsii_name="resetProviderEncryptEbsVolume")
    def reset_provider_encrypt_ebs_volume(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProviderEncryptEbsVolume", []))

    @jsii.member(jsii_name="resetProviderRegionName")
    def reset_provider_region_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProviderRegionName", []))

    @jsii.member(jsii_name="resetProviderVolumeType")
    def reset_provider_volume_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProviderVolumeType", []))

    @jsii.member(jsii_name="resetRedactClientLogData")
    def reset_redact_client_log_data(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRedactClientLogData", []))

    @jsii.member(jsii_name="resetReplicationFactor")
    def reset_replication_factor(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReplicationFactor", []))

    @jsii.member(jsii_name="resetReplicationSpecs")
    def reset_replication_specs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReplicationSpecs", []))

    @jsii.member(jsii_name="resetRetainBackupsEnabled")
    def reset_retain_backups_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetainBackupsEnabled", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTerminationProtectionEnabled")
    def reset_termination_protection_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTerminationProtectionEnabled", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

    @jsii.member(jsii_name="resetVersionReleaseSystem")
    def reset_version_release_system(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersionReleaseSystem", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="synthesizeHclAttributes")
    def _synthesize_hcl_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeHclAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="advancedConfiguration")
    def advanced_configuration(self) -> "ClusterAdvancedConfigurationOutputReference":
        return typing.cast("ClusterAdvancedConfigurationOutputReference", jsii.get(self, "advancedConfiguration"))

    @builtins.property
    @jsii.member(jsii_name="biConnectorConfig")
    def bi_connector_config(self) -> "ClusterBiConnectorConfigOutputReference":
        return typing.cast("ClusterBiConnectorConfigOutputReference", jsii.get(self, "biConnectorConfig"))

    @builtins.property
    @jsii.member(jsii_name="clusterId")
    def cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterId"))

    @builtins.property
    @jsii.member(jsii_name="connectionStrings")
    def connection_strings(self) -> "ClusterConnectionStringsList":
        return typing.cast("ClusterConnectionStringsList", jsii.get(self, "connectionStrings"))

    @builtins.property
    @jsii.member(jsii_name="containerId")
    def container_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "containerId"))

    @builtins.property
    @jsii.member(jsii_name="labels")
    def labels(self) -> "ClusterLabelsList":
        return typing.cast("ClusterLabelsList", jsii.get(self, "labels"))

    @builtins.property
    @jsii.member(jsii_name="mongoDbVersion")
    def mongo_db_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mongoDbVersion"))

    @builtins.property
    @jsii.member(jsii_name="mongoUri")
    def mongo_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mongoUri"))

    @builtins.property
    @jsii.member(jsii_name="mongoUriUpdated")
    def mongo_uri_updated(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mongoUriUpdated"))

    @builtins.property
    @jsii.member(jsii_name="mongoUriWithOptions")
    def mongo_uri_with_options(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mongoUriWithOptions"))

    @builtins.property
    @jsii.member(jsii_name="pinnedFcv")
    def pinned_fcv(self) -> "ClusterPinnedFcvOutputReference":
        return typing.cast("ClusterPinnedFcvOutputReference", jsii.get(self, "pinnedFcv"))

    @builtins.property
    @jsii.member(jsii_name="providerEncryptEbsVolumeFlag")
    def provider_encrypt_ebs_volume_flag(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "providerEncryptEbsVolumeFlag"))

    @builtins.property
    @jsii.member(jsii_name="replicationSpecs")
    def replication_specs(self) -> "ClusterReplicationSpecsList":
        return typing.cast("ClusterReplicationSpecsList", jsii.get(self, "replicationSpecs"))

    @builtins.property
    @jsii.member(jsii_name="snapshotBackupPolicy")
    def snapshot_backup_policy(self) -> "ClusterSnapshotBackupPolicyList":
        return typing.cast("ClusterSnapshotBackupPolicyList", jsii.get(self, "snapshotBackupPolicy"))

    @builtins.property
    @jsii.member(jsii_name="srvAddress")
    def srv_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "srvAddress"))

    @builtins.property
    @jsii.member(jsii_name="stateName")
    def state_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stateName"))

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> "ClusterTagsList":
        return typing.cast("ClusterTagsList", jsii.get(self, "tags"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "ClusterTimeoutsOutputReference":
        return typing.cast("ClusterTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="acceptDataRisksAndForceReplicaSetReconfigInput")
    def accept_data_risks_and_force_replica_set_reconfig_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "acceptDataRisksAndForceReplicaSetReconfigInput"))

    @builtins.property
    @jsii.member(jsii_name="advancedConfigurationInput")
    def advanced_configuration_input(
        self,
    ) -> typing.Optional["ClusterAdvancedConfiguration"]:
        return typing.cast(typing.Optional["ClusterAdvancedConfiguration"], jsii.get(self, "advancedConfigurationInput"))

    @builtins.property
    @jsii.member(jsii_name="autoScalingComputeEnabledInput")
    def auto_scaling_compute_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "autoScalingComputeEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="autoScalingComputeScaleDownEnabledInput")
    def auto_scaling_compute_scale_down_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "autoScalingComputeScaleDownEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="autoScalingDiskGbEnabledInput")
    def auto_scaling_disk_gb_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "autoScalingDiskGbEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="backingProviderNameInput")
    def backing_provider_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "backingProviderNameInput"))

    @builtins.property
    @jsii.member(jsii_name="backupEnabledInput")
    def backup_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "backupEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="biConnectorConfigInput")
    def bi_connector_config_input(self) -> typing.Optional["ClusterBiConnectorConfig"]:
        return typing.cast(typing.Optional["ClusterBiConnectorConfig"], jsii.get(self, "biConnectorConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="cloudBackupInput")
    def cloud_backup_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "cloudBackupInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterTypeInput")
    def cluster_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="diskSizeGbInput")
    def disk_size_gb_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "diskSizeGbInput"))

    @builtins.property
    @jsii.member(jsii_name="encryptionAtRestProviderInput")
    def encryption_at_rest_provider_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "encryptionAtRestProviderInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="labelsInput")
    def labels_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ClusterLabels"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ClusterLabels"]]], jsii.get(self, "labelsInput"))

    @builtins.property
    @jsii.member(jsii_name="mongoDbMajorVersionInput")
    def mongo_db_major_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mongoDbMajorVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="numShardsInput")
    def num_shards_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numShardsInput"))

    @builtins.property
    @jsii.member(jsii_name="pausedInput")
    def paused_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "pausedInput"))

    @builtins.property
    @jsii.member(jsii_name="pinnedFcvInput")
    def pinned_fcv_input(self) -> typing.Optional["ClusterPinnedFcv"]:
        return typing.cast(typing.Optional["ClusterPinnedFcv"], jsii.get(self, "pinnedFcvInput"))

    @builtins.property
    @jsii.member(jsii_name="pitEnabledInput")
    def pit_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "pitEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="providerAutoScalingComputeMaxInstanceSizeInput")
    def provider_auto_scaling_compute_max_instance_size_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "providerAutoScalingComputeMaxInstanceSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="providerAutoScalingComputeMinInstanceSizeInput")
    def provider_auto_scaling_compute_min_instance_size_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "providerAutoScalingComputeMinInstanceSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="providerDiskIopsInput")
    def provider_disk_iops_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "providerDiskIopsInput"))

    @builtins.property
    @jsii.member(jsii_name="providerDiskTypeNameInput")
    def provider_disk_type_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "providerDiskTypeNameInput"))

    @builtins.property
    @jsii.member(jsii_name="providerEncryptEbsVolumeInput")
    def provider_encrypt_ebs_volume_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "providerEncryptEbsVolumeInput"))

    @builtins.property
    @jsii.member(jsii_name="providerInstanceSizeNameInput")
    def provider_instance_size_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "providerInstanceSizeNameInput"))

    @builtins.property
    @jsii.member(jsii_name="providerNameInput")
    def provider_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "providerNameInput"))

    @builtins.property
    @jsii.member(jsii_name="providerRegionNameInput")
    def provider_region_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "providerRegionNameInput"))

    @builtins.property
    @jsii.member(jsii_name="providerVolumeTypeInput")
    def provider_volume_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "providerVolumeTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="redactClientLogDataInput")
    def redact_client_log_data_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "redactClientLogDataInput"))

    @builtins.property
    @jsii.member(jsii_name="replicationFactorInput")
    def replication_factor_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "replicationFactorInput"))

    @builtins.property
    @jsii.member(jsii_name="replicationSpecsInput")
    def replication_specs_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ClusterReplicationSpecs"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ClusterReplicationSpecs"]]], jsii.get(self, "replicationSpecsInput"))

    @builtins.property
    @jsii.member(jsii_name="retainBackupsEnabledInput")
    def retain_backups_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "retainBackupsEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ClusterTags"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ClusterTags"]]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="terminationProtectionEnabledInput")
    def termination_protection_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "terminationProtectionEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ClusterTimeouts"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "ClusterTimeouts"]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="versionReleaseSystemInput")
    def version_release_system_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "versionReleaseSystemInput"))

    @builtins.property
    @jsii.member(jsii_name="acceptDataRisksAndForceReplicaSetReconfig")
    def accept_data_risks_and_force_replica_set_reconfig(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "acceptDataRisksAndForceReplicaSetReconfig"))

    @accept_data_risks_and_force_replica_set_reconfig.setter
    def accept_data_risks_and_force_replica_set_reconfig(
        self,
        value: builtins.str,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64db6507310cc49535192032ef79aca34f62c06082b7996c9493179d6941dec0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "acceptDataRisksAndForceReplicaSetReconfig", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autoScalingComputeEnabled")
    def auto_scaling_compute_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "autoScalingComputeEnabled"))

    @auto_scaling_compute_enabled.setter
    def auto_scaling_compute_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c06a22a89a09418ee6b46b8a139f9bb7763b9fb1c38356b42f7388577dbc4608)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoScalingComputeEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autoScalingComputeScaleDownEnabled")
    def auto_scaling_compute_scale_down_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "autoScalingComputeScaleDownEnabled"))

    @auto_scaling_compute_scale_down_enabled.setter
    def auto_scaling_compute_scale_down_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59aa7d29979718b4b2ecf6232414400327f659633942b7724b2e45386b08fbce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoScalingComputeScaleDownEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autoScalingDiskGbEnabled")
    def auto_scaling_disk_gb_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "autoScalingDiskGbEnabled"))

    @auto_scaling_disk_gb_enabled.setter
    def auto_scaling_disk_gb_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6bdde510bfd567d47cb7a1a2957efa04a0f0de6546e3670a761451410f06d83)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoScalingDiskGbEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backingProviderName")
    def backing_provider_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backingProviderName"))

    @backing_provider_name.setter
    def backing_provider_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10b4feb06b6bd6d3f28fc89c9a5a8b084941a547fc81171f75544ae94262735c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backingProviderName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backupEnabled")
    def backup_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "backupEnabled"))

    @backup_enabled.setter
    def backup_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57c3fc02d67f921afa6b1f8a97b13c25eaa049046b5c2a07793b989229f60207)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backupEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cloudBackup")
    def cloud_backup(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "cloudBackup"))

    @cloud_backup.setter
    def cloud_backup(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86ed796f0cb588520cd6e186c26523b3a31121e909a5dcd5f8474fa82ebe236e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cloudBackup", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clusterType")
    def cluster_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterType"))

    @cluster_type.setter
    def cluster_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d8e8abe391524843551c83ce5ae45348499a4cb4dce528965841b190fc0c8d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="diskSizeGb")
    def disk_size_gb(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "diskSizeGb"))

    @disk_size_gb.setter
    def disk_size_gb(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce455b1b3ed68d93edbf93af1cfdf8b6319f70d0762aa0455fd18617b5d6e057)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "diskSizeGb", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="encryptionAtRestProvider")
    def encryption_at_rest_provider(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptionAtRestProvider"))

    @encryption_at_rest_provider.setter
    def encryption_at_rest_provider(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__810665018bf9edd7b21c7f5d21aea144d132ee5809f4c2ec08b501c14ce25f4d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "encryptionAtRestProvider", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__839d015cd20e225d16ce9e21d44771d75e3f848bca1f57d3a9a57b31972832cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mongoDbMajorVersion")
    def mongo_db_major_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mongoDbMajorVersion"))

    @mongo_db_major_version.setter
    def mongo_db_major_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2705fd046fb2dccd70d53e142660a7e9c305089fe6e000022b2fed27acfbfcb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mongoDbMajorVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71f105a2df9974361266ad742a127e34bd12d1eb43beed4065a3d08ba8838356)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="numShards")
    def num_shards(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numShards"))

    @num_shards.setter
    def num_shards(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33cd7e1ffe5bc62a488b7c083cd2dd5519670f94c488b16865ffc96a444a5f9b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numShards", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="paused")
    def paused(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "paused"))

    @paused.setter
    def paused(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1709d6e24c2e1fd2ebe95b823d40954e497dda98510a3ceba3192bf6955db6e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "paused", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pitEnabled")
    def pit_enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "pitEnabled"))

    @pit_enabled.setter
    def pit_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__703e8324a0124275716a1f7dcdddbc1ab4ad92c912f694bcf5e1733f7aba0ddd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pitEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c9ebf3dab0896ad2349ffd2a29f0b545507b90903d4d9d6e4a8ed4771ae9afe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="providerAutoScalingComputeMaxInstanceSize")
    def provider_auto_scaling_compute_max_instance_size(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "providerAutoScalingComputeMaxInstanceSize"))

    @provider_auto_scaling_compute_max_instance_size.setter
    def provider_auto_scaling_compute_max_instance_size(
        self,
        value: builtins.str,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ffd021db11b7e8084419d3f49509a76b8f75c354a446e0e136a8d4eeab5ab523)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "providerAutoScalingComputeMaxInstanceSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="providerAutoScalingComputeMinInstanceSize")
    def provider_auto_scaling_compute_min_instance_size(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "providerAutoScalingComputeMinInstanceSize"))

    @provider_auto_scaling_compute_min_instance_size.setter
    def provider_auto_scaling_compute_min_instance_size(
        self,
        value: builtins.str,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__971aae3ca04426b83bd0f6404aa5e08b97ebc24df2a416bdedbefff3cd0f7089)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "providerAutoScalingComputeMinInstanceSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="providerDiskIops")
    def provider_disk_iops(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "providerDiskIops"))

    @provider_disk_iops.setter
    def provider_disk_iops(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bdb1b0a533977f12c037278efeab80d9afcde5ae47303a69a87c8261cf4d3bd3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "providerDiskIops", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="providerDiskTypeName")
    def provider_disk_type_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "providerDiskTypeName"))

    @provider_disk_type_name.setter
    def provider_disk_type_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1230f60c6e2bacf31980f5af933705786600d0a419c229f4e65007ccabb06857)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "providerDiskTypeName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="providerEncryptEbsVolume")
    def provider_encrypt_ebs_volume(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "providerEncryptEbsVolume"))

    @provider_encrypt_ebs_volume.setter
    def provider_encrypt_ebs_volume(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c00c07cd5cf0faf5d5fdd14bf16a9b49575f5bbf6e4f914d608a313a7b90c7f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "providerEncryptEbsVolume", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="providerInstanceSizeName")
    def provider_instance_size_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "providerInstanceSizeName"))

    @provider_instance_size_name.setter
    def provider_instance_size_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ceb19f79c49cc3221adcb75a8965acfd0d331dbbea2491aeb455d9d573b8a074)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "providerInstanceSizeName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="providerName")
    def provider_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "providerName"))

    @provider_name.setter
    def provider_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91bc4fe4365c9e4da2f326b3914a4a9f6d72da9172d05e6357c75f62274deeb5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "providerName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="providerRegionName")
    def provider_region_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "providerRegionName"))

    @provider_region_name.setter
    def provider_region_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e1f113d559265c42a48a1e52ac493d7aa2877b79a400bce461552b61bc09153)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "providerRegionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="providerVolumeType")
    def provider_volume_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "providerVolumeType"))

    @provider_volume_type.setter
    def provider_volume_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8d8f33140e2aae8e2dd44b918b40bd74955963477b332a87432cff44692ed8d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "providerVolumeType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="redactClientLogData")
    def redact_client_log_data(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "redactClientLogData"))

    @redact_client_log_data.setter
    def redact_client_log_data(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f17ba69c22cbaf739fcabca49d47551deebdcb2c64c858248db8513ae2ebc81)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "redactClientLogData", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="replicationFactor")
    def replication_factor(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "replicationFactor"))

    @replication_factor.setter
    def replication_factor(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e06f58753d9de9dcbb19cfec751ac3adbec07f4781375f5c7f2f6626c2b1799)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "replicationFactor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retainBackupsEnabled")
    def retain_backups_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "retainBackupsEnabled"))

    @retain_backups_enabled.setter
    def retain_backups_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec9ab4eaae98b3279d5a43f24c7a5620ec4040a103768a488233cc02214e44c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retainBackupsEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terminationProtectionEnabled")
    def termination_protection_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "terminationProtectionEnabled"))

    @termination_protection_enabled.setter
    def termination_protection_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a48c8a7eda198dfbae37841348b853d4fa7150e2de96cd5ecec0d14628751fb0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terminationProtectionEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="versionReleaseSystem")
    def version_release_system(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "versionReleaseSystem"))

    @version_release_system.setter
    def version_release_system(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c95ac87fdb0cc81b48d2d8822ae1e74f1c7be26d4c1d668f105cc78eb35e80c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "versionReleaseSystem", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterAdvancedConfiguration",
    jsii_struct_bases=[],
    name_mapping={
        "change_stream_options_pre_and_post_images_expire_after_seconds": "changeStreamOptionsPreAndPostImagesExpireAfterSeconds",
        "custom_openssl_cipher_config_tls12": "customOpensslCipherConfigTls12",
        "default_max_time_ms": "defaultMaxTimeMs",
        "default_read_concern": "defaultReadConcern",
        "default_write_concern": "defaultWriteConcern",
        "fail_index_key_too_long": "failIndexKeyTooLong",
        "javascript_enabled": "javascriptEnabled",
        "minimum_enabled_tls_protocol": "minimumEnabledTlsProtocol",
        "no_table_scan": "noTableScan",
        "oplog_min_retention_hours": "oplogMinRetentionHours",
        "oplog_size_mb": "oplogSizeMb",
        "sample_refresh_interval_bi_connector": "sampleRefreshIntervalBiConnector",
        "sample_size_bi_connector": "sampleSizeBiConnector",
        "tls_cipher_config_mode": "tlsCipherConfigMode",
        "transaction_lifetime_limit_seconds": "transactionLifetimeLimitSeconds",
    },
)
class ClusterAdvancedConfiguration:
    def __init__(
        self,
        *,
        change_stream_options_pre_and_post_images_expire_after_seconds: typing.Optional[jsii.Number] = None,
        custom_openssl_cipher_config_tls12: typing.Optional[typing.Sequence[builtins.str]] = None,
        default_max_time_ms: typing.Optional[jsii.Number] = None,
        default_read_concern: typing.Optional[builtins.str] = None,
        default_write_concern: typing.Optional[builtins.str] = None,
        fail_index_key_too_long: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        javascript_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        minimum_enabled_tls_protocol: typing.Optional[builtins.str] = None,
        no_table_scan: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        oplog_min_retention_hours: typing.Optional[jsii.Number] = None,
        oplog_size_mb: typing.Optional[jsii.Number] = None,
        sample_refresh_interval_bi_connector: typing.Optional[jsii.Number] = None,
        sample_size_bi_connector: typing.Optional[jsii.Number] = None,
        tls_cipher_config_mode: typing.Optional[builtins.str] = None,
        transaction_lifetime_limit_seconds: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param change_stream_options_pre_and_post_images_expire_after_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#change_stream_options_pre_and_post_images_expire_after_seconds Cluster#change_stream_options_pre_and_post_images_expire_after_seconds}.
        :param custom_openssl_cipher_config_tls12: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#custom_openssl_cipher_config_tls12 Cluster#custom_openssl_cipher_config_tls12}.
        :param default_max_time_ms: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#default_max_time_ms Cluster#default_max_time_ms}.
        :param default_read_concern: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#default_read_concern Cluster#default_read_concern}.
        :param default_write_concern: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#default_write_concern Cluster#default_write_concern}.
        :param fail_index_key_too_long: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#fail_index_key_too_long Cluster#fail_index_key_too_long}.
        :param javascript_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#javascript_enabled Cluster#javascript_enabled}.
        :param minimum_enabled_tls_protocol: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#minimum_enabled_tls_protocol Cluster#minimum_enabled_tls_protocol}.
        :param no_table_scan: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#no_table_scan Cluster#no_table_scan}.
        :param oplog_min_retention_hours: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#oplog_min_retention_hours Cluster#oplog_min_retention_hours}.
        :param oplog_size_mb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#oplog_size_mb Cluster#oplog_size_mb}.
        :param sample_refresh_interval_bi_connector: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#sample_refresh_interval_bi_connector Cluster#sample_refresh_interval_bi_connector}.
        :param sample_size_bi_connector: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#sample_size_bi_connector Cluster#sample_size_bi_connector}.
        :param tls_cipher_config_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#tls_cipher_config_mode Cluster#tls_cipher_config_mode}.
        :param transaction_lifetime_limit_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#transaction_lifetime_limit_seconds Cluster#transaction_lifetime_limit_seconds}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__065331b466e1b27c260c6206aedb9472cb98d9aacb65db3a6deccadd579de774)
            check_type(argname="argument change_stream_options_pre_and_post_images_expire_after_seconds", value=change_stream_options_pre_and_post_images_expire_after_seconds, expected_type=type_hints["change_stream_options_pre_and_post_images_expire_after_seconds"])
            check_type(argname="argument custom_openssl_cipher_config_tls12", value=custom_openssl_cipher_config_tls12, expected_type=type_hints["custom_openssl_cipher_config_tls12"])
            check_type(argname="argument default_max_time_ms", value=default_max_time_ms, expected_type=type_hints["default_max_time_ms"])
            check_type(argname="argument default_read_concern", value=default_read_concern, expected_type=type_hints["default_read_concern"])
            check_type(argname="argument default_write_concern", value=default_write_concern, expected_type=type_hints["default_write_concern"])
            check_type(argname="argument fail_index_key_too_long", value=fail_index_key_too_long, expected_type=type_hints["fail_index_key_too_long"])
            check_type(argname="argument javascript_enabled", value=javascript_enabled, expected_type=type_hints["javascript_enabled"])
            check_type(argname="argument minimum_enabled_tls_protocol", value=minimum_enabled_tls_protocol, expected_type=type_hints["minimum_enabled_tls_protocol"])
            check_type(argname="argument no_table_scan", value=no_table_scan, expected_type=type_hints["no_table_scan"])
            check_type(argname="argument oplog_min_retention_hours", value=oplog_min_retention_hours, expected_type=type_hints["oplog_min_retention_hours"])
            check_type(argname="argument oplog_size_mb", value=oplog_size_mb, expected_type=type_hints["oplog_size_mb"])
            check_type(argname="argument sample_refresh_interval_bi_connector", value=sample_refresh_interval_bi_connector, expected_type=type_hints["sample_refresh_interval_bi_connector"])
            check_type(argname="argument sample_size_bi_connector", value=sample_size_bi_connector, expected_type=type_hints["sample_size_bi_connector"])
            check_type(argname="argument tls_cipher_config_mode", value=tls_cipher_config_mode, expected_type=type_hints["tls_cipher_config_mode"])
            check_type(argname="argument transaction_lifetime_limit_seconds", value=transaction_lifetime_limit_seconds, expected_type=type_hints["transaction_lifetime_limit_seconds"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if change_stream_options_pre_and_post_images_expire_after_seconds is not None:
            self._values["change_stream_options_pre_and_post_images_expire_after_seconds"] = change_stream_options_pre_and_post_images_expire_after_seconds
        if custom_openssl_cipher_config_tls12 is not None:
            self._values["custom_openssl_cipher_config_tls12"] = custom_openssl_cipher_config_tls12
        if default_max_time_ms is not None:
            self._values["default_max_time_ms"] = default_max_time_ms
        if default_read_concern is not None:
            self._values["default_read_concern"] = default_read_concern
        if default_write_concern is not None:
            self._values["default_write_concern"] = default_write_concern
        if fail_index_key_too_long is not None:
            self._values["fail_index_key_too_long"] = fail_index_key_too_long
        if javascript_enabled is not None:
            self._values["javascript_enabled"] = javascript_enabled
        if minimum_enabled_tls_protocol is not None:
            self._values["minimum_enabled_tls_protocol"] = minimum_enabled_tls_protocol
        if no_table_scan is not None:
            self._values["no_table_scan"] = no_table_scan
        if oplog_min_retention_hours is not None:
            self._values["oplog_min_retention_hours"] = oplog_min_retention_hours
        if oplog_size_mb is not None:
            self._values["oplog_size_mb"] = oplog_size_mb
        if sample_refresh_interval_bi_connector is not None:
            self._values["sample_refresh_interval_bi_connector"] = sample_refresh_interval_bi_connector
        if sample_size_bi_connector is not None:
            self._values["sample_size_bi_connector"] = sample_size_bi_connector
        if tls_cipher_config_mode is not None:
            self._values["tls_cipher_config_mode"] = tls_cipher_config_mode
        if transaction_lifetime_limit_seconds is not None:
            self._values["transaction_lifetime_limit_seconds"] = transaction_lifetime_limit_seconds

    @builtins.property
    def change_stream_options_pre_and_post_images_expire_after_seconds(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#change_stream_options_pre_and_post_images_expire_after_seconds Cluster#change_stream_options_pre_and_post_images_expire_after_seconds}.'''
        result = self._values.get("change_stream_options_pre_and_post_images_expire_after_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def custom_openssl_cipher_config_tls12(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#custom_openssl_cipher_config_tls12 Cluster#custom_openssl_cipher_config_tls12}.'''
        result = self._values.get("custom_openssl_cipher_config_tls12")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def default_max_time_ms(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#default_max_time_ms Cluster#default_max_time_ms}.'''
        result = self._values.get("default_max_time_ms")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def default_read_concern(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#default_read_concern Cluster#default_read_concern}.'''
        result = self._values.get("default_read_concern")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_write_concern(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#default_write_concern Cluster#default_write_concern}.'''
        result = self._values.get("default_write_concern")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def fail_index_key_too_long(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#fail_index_key_too_long Cluster#fail_index_key_too_long}.'''
        result = self._values.get("fail_index_key_too_long")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def javascript_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#javascript_enabled Cluster#javascript_enabled}.'''
        result = self._values.get("javascript_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def minimum_enabled_tls_protocol(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#minimum_enabled_tls_protocol Cluster#minimum_enabled_tls_protocol}.'''
        result = self._values.get("minimum_enabled_tls_protocol")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def no_table_scan(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#no_table_scan Cluster#no_table_scan}.'''
        result = self._values.get("no_table_scan")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def oplog_min_retention_hours(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#oplog_min_retention_hours Cluster#oplog_min_retention_hours}.'''
        result = self._values.get("oplog_min_retention_hours")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def oplog_size_mb(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#oplog_size_mb Cluster#oplog_size_mb}.'''
        result = self._values.get("oplog_size_mb")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def sample_refresh_interval_bi_connector(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#sample_refresh_interval_bi_connector Cluster#sample_refresh_interval_bi_connector}.'''
        result = self._values.get("sample_refresh_interval_bi_connector")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def sample_size_bi_connector(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#sample_size_bi_connector Cluster#sample_size_bi_connector}.'''
        result = self._values.get("sample_size_bi_connector")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def tls_cipher_config_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#tls_cipher_config_mode Cluster#tls_cipher_config_mode}.'''
        result = self._values.get("tls_cipher_config_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def transaction_lifetime_limit_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#transaction_lifetime_limit_seconds Cluster#transaction_lifetime_limit_seconds}.'''
        result = self._values.get("transaction_lifetime_limit_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ClusterAdvancedConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ClusterAdvancedConfigurationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterAdvancedConfigurationOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__996b89adf682b99f5e0979d471cfa16b8d95ee308097a088356121e8247a1382)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetChangeStreamOptionsPreAndPostImagesExpireAfterSeconds")
    def reset_change_stream_options_pre_and_post_images_expire_after_seconds(
        self,
    ) -> None:
        return typing.cast(None, jsii.invoke(self, "resetChangeStreamOptionsPreAndPostImagesExpireAfterSeconds", []))

    @jsii.member(jsii_name="resetCustomOpensslCipherConfigTls12")
    def reset_custom_openssl_cipher_config_tls12(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomOpensslCipherConfigTls12", []))

    @jsii.member(jsii_name="resetDefaultMaxTimeMs")
    def reset_default_max_time_ms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultMaxTimeMs", []))

    @jsii.member(jsii_name="resetDefaultReadConcern")
    def reset_default_read_concern(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultReadConcern", []))

    @jsii.member(jsii_name="resetDefaultWriteConcern")
    def reset_default_write_concern(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultWriteConcern", []))

    @jsii.member(jsii_name="resetFailIndexKeyTooLong")
    def reset_fail_index_key_too_long(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFailIndexKeyTooLong", []))

    @jsii.member(jsii_name="resetJavascriptEnabled")
    def reset_javascript_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJavascriptEnabled", []))

    @jsii.member(jsii_name="resetMinimumEnabledTlsProtocol")
    def reset_minimum_enabled_tls_protocol(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinimumEnabledTlsProtocol", []))

    @jsii.member(jsii_name="resetNoTableScan")
    def reset_no_table_scan(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNoTableScan", []))

    @jsii.member(jsii_name="resetOplogMinRetentionHours")
    def reset_oplog_min_retention_hours(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOplogMinRetentionHours", []))

    @jsii.member(jsii_name="resetOplogSizeMb")
    def reset_oplog_size_mb(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOplogSizeMb", []))

    @jsii.member(jsii_name="resetSampleRefreshIntervalBiConnector")
    def reset_sample_refresh_interval_bi_connector(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSampleRefreshIntervalBiConnector", []))

    @jsii.member(jsii_name="resetSampleSizeBiConnector")
    def reset_sample_size_bi_connector(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSampleSizeBiConnector", []))

    @jsii.member(jsii_name="resetTlsCipherConfigMode")
    def reset_tls_cipher_config_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsCipherConfigMode", []))

    @jsii.member(jsii_name="resetTransactionLifetimeLimitSeconds")
    def reset_transaction_lifetime_limit_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTransactionLifetimeLimitSeconds", []))

    @builtins.property
    @jsii.member(jsii_name="changeStreamOptionsPreAndPostImagesExpireAfterSecondsInput")
    def change_stream_options_pre_and_post_images_expire_after_seconds_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "changeStreamOptionsPreAndPostImagesExpireAfterSecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="customOpensslCipherConfigTls12Input")
    def custom_openssl_cipher_config_tls12_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "customOpensslCipherConfigTls12Input"))

    @builtins.property
    @jsii.member(jsii_name="defaultMaxTimeMsInput")
    def default_max_time_ms_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "defaultMaxTimeMsInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultReadConcernInput")
    def default_read_concern_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultReadConcernInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultWriteConcernInput")
    def default_write_concern_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultWriteConcernInput"))

    @builtins.property
    @jsii.member(jsii_name="failIndexKeyTooLongInput")
    def fail_index_key_too_long_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "failIndexKeyTooLongInput"))

    @builtins.property
    @jsii.member(jsii_name="javascriptEnabledInput")
    def javascript_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "javascriptEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="minimumEnabledTlsProtocolInput")
    def minimum_enabled_tls_protocol_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "minimumEnabledTlsProtocolInput"))

    @builtins.property
    @jsii.member(jsii_name="noTableScanInput")
    def no_table_scan_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "noTableScanInput"))

    @builtins.property
    @jsii.member(jsii_name="oplogMinRetentionHoursInput")
    def oplog_min_retention_hours_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "oplogMinRetentionHoursInput"))

    @builtins.property
    @jsii.member(jsii_name="oplogSizeMbInput")
    def oplog_size_mb_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "oplogSizeMbInput"))

    @builtins.property
    @jsii.member(jsii_name="sampleRefreshIntervalBiConnectorInput")
    def sample_refresh_interval_bi_connector_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sampleRefreshIntervalBiConnectorInput"))

    @builtins.property
    @jsii.member(jsii_name="sampleSizeBiConnectorInput")
    def sample_size_bi_connector_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sampleSizeBiConnectorInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsCipherConfigModeInput")
    def tls_cipher_config_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tlsCipherConfigModeInput"))

    @builtins.property
    @jsii.member(jsii_name="transactionLifetimeLimitSecondsInput")
    def transaction_lifetime_limit_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "transactionLifetimeLimitSecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="changeStreamOptionsPreAndPostImagesExpireAfterSeconds")
    def change_stream_options_pre_and_post_images_expire_after_seconds(
        self,
    ) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "changeStreamOptionsPreAndPostImagesExpireAfterSeconds"))

    @change_stream_options_pre_and_post_images_expire_after_seconds.setter
    def change_stream_options_pre_and_post_images_expire_after_seconds(
        self,
        value: jsii.Number,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e450f0400deafbeb72c09daa253b68745eaa9f07cfa5f20f4482f1eea5bf949a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "changeStreamOptionsPreAndPostImagesExpireAfterSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="customOpensslCipherConfigTls12")
    def custom_openssl_cipher_config_tls12(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customOpensslCipherConfigTls12"))

    @custom_openssl_cipher_config_tls12.setter
    def custom_openssl_cipher_config_tls12(
        self,
        value: typing.List[builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2896d3336af63bcba78af96c52ba1e86bac226b9835cf8bcc80220a18f0009d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customOpensslCipherConfigTls12", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultMaxTimeMs")
    def default_max_time_ms(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "defaultMaxTimeMs"))

    @default_max_time_ms.setter
    def default_max_time_ms(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a14d85aaa79685af0f2919085cd2b32dff2e07dec9c88a3b9c28f7211681d8a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultMaxTimeMs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultReadConcern")
    def default_read_concern(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultReadConcern"))

    @default_read_concern.setter
    def default_read_concern(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__754287fa100cb7bedfb29777a4fde1d77738b2ab3a1c93ec9deede761591ed5b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultReadConcern", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultWriteConcern")
    def default_write_concern(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultWriteConcern"))

    @default_write_concern.setter
    def default_write_concern(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__197e2b20b46a799f55867a98f6a4bd215488733dd875286cbeeae11f3bfcd443)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultWriteConcern", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="failIndexKeyTooLong")
    def fail_index_key_too_long(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "failIndexKeyTooLong"))

    @fail_index_key_too_long.setter
    def fail_index_key_too_long(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0f3bc8d83e3b509fcec4e527dafe222dfe9f6ec2b97550629b2f735ac132751)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "failIndexKeyTooLong", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="javascriptEnabled")
    def javascript_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "javascriptEnabled"))

    @javascript_enabled.setter
    def javascript_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12622488c890619540e24ab1ce32a1fb3a1cf640a19f22e753e6b1d06984941a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "javascriptEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minimumEnabledTlsProtocol")
    def minimum_enabled_tls_protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minimumEnabledTlsProtocol"))

    @minimum_enabled_tls_protocol.setter
    def minimum_enabled_tls_protocol(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__837337c62ddf45b76d1724490b0f8869b2a9a56211daca52d83c54be02af439d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minimumEnabledTlsProtocol", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="noTableScan")
    def no_table_scan(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "noTableScan"))

    @no_table_scan.setter
    def no_table_scan(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dab30f25c9a42c4873940bd050334afccfeff6668a1090e04a3dbda5b194e2c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "noTableScan", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oplogMinRetentionHours")
    def oplog_min_retention_hours(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "oplogMinRetentionHours"))

    @oplog_min_retention_hours.setter
    def oplog_min_retention_hours(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34a491a4a52d6a086b975d187473fbec2ed8c4f5dfa9836962bc78c4928e4fd4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oplogMinRetentionHours", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oplogSizeMb")
    def oplog_size_mb(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "oplogSizeMb"))

    @oplog_size_mb.setter
    def oplog_size_mb(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65f61f7458573d6d03be0ab302d8258f01aa6da18ad99f7f621a818767814dec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oplogSizeMb", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sampleRefreshIntervalBiConnector")
    def sample_refresh_interval_bi_connector(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sampleRefreshIntervalBiConnector"))

    @sample_refresh_interval_bi_connector.setter
    def sample_refresh_interval_bi_connector(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a014340b87f1e348d4b069754bfddecffd8979e1bfab3b32c21188d4605632b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sampleRefreshIntervalBiConnector", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sampleSizeBiConnector")
    def sample_size_bi_connector(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sampleSizeBiConnector"))

    @sample_size_bi_connector.setter
    def sample_size_bi_connector(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b64d900bb1bcc981fae851fddb7547ec9da5d841965fa423e5d60c0afd674d3c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sampleSizeBiConnector", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tlsCipherConfigMode")
    def tls_cipher_config_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tlsCipherConfigMode"))

    @tls_cipher_config_mode.setter
    def tls_cipher_config_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af51e2d1e888340bba0834b5fd84be9018e1266b301cf917c9c7facfcdc0c9cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tlsCipherConfigMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="transactionLifetimeLimitSeconds")
    def transaction_lifetime_limit_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "transactionLifetimeLimitSeconds"))

    @transaction_lifetime_limit_seconds.setter
    def transaction_lifetime_limit_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f34c8fbc8ae8790216871f6287e141cbdabdd878068ffdc17b34ae3c0b63433)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "transactionLifetimeLimitSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ClusterAdvancedConfiguration]:
        return typing.cast(typing.Optional[ClusterAdvancedConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ClusterAdvancedConfiguration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb7eb932152aac8a1e720ae3d8f2073cd64e3778aabf50c7a0fcb4b4dcdcbe16)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterBiConnectorConfig",
    jsii_struct_bases=[],
    name_mapping={"enabled": "enabled", "read_preference": "readPreference"},
)
class ClusterBiConnectorConfig:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        read_preference: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#enabled Cluster#enabled}.
        :param read_preference: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#read_preference Cluster#read_preference}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72c2885a36e3c0e5ade0ede10eec426f2776f34c582816cfeaab6163b0986212)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument read_preference", value=read_preference, expected_type=type_hints["read_preference"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if read_preference is not None:
            self._values["read_preference"] = read_preference

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#enabled Cluster#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def read_preference(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#read_preference Cluster#read_preference}.'''
        result = self._values.get("read_preference")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ClusterBiConnectorConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ClusterBiConnectorConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterBiConnectorConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4917f9a13d8b75832177e7ed501aa1bc7a085be73043abbefa17323caa904f97)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetReadPreference")
    def reset_read_preference(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReadPreference", []))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="readPreferenceInput")
    def read_preference_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "readPreferenceInput"))

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2144c0c7882ee778c36e07efcd1223cf8fa38befec4e9fc2d2bd36b585ca806d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="readPreference")
    def read_preference(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "readPreference"))

    @read_preference.setter
    def read_preference(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9074ef1c6d3bd9b68c2117877cc162354315884c82a02bc542d3307b8e2b392b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "readPreference", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ClusterBiConnectorConfig]:
        return typing.cast(typing.Optional[ClusterBiConnectorConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ClusterBiConnectorConfig]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8edd8036e3e5f8a4c267728ce5f09145bc926898f6af45bcb7df3434c638ec02)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "name": "name",
        "project_id": "projectId",
        "provider_instance_size_name": "providerInstanceSizeName",
        "provider_name": "providerName",
        "accept_data_risks_and_force_replica_set_reconfig": "acceptDataRisksAndForceReplicaSetReconfig",
        "advanced_configuration": "advancedConfiguration",
        "auto_scaling_compute_enabled": "autoScalingComputeEnabled",
        "auto_scaling_compute_scale_down_enabled": "autoScalingComputeScaleDownEnabled",
        "auto_scaling_disk_gb_enabled": "autoScalingDiskGbEnabled",
        "backing_provider_name": "backingProviderName",
        "backup_enabled": "backupEnabled",
        "bi_connector_config": "biConnectorConfig",
        "cloud_backup": "cloudBackup",
        "cluster_type": "clusterType",
        "disk_size_gb": "diskSizeGb",
        "encryption_at_rest_provider": "encryptionAtRestProvider",
        "id": "id",
        "labels": "labels",
        "mongo_db_major_version": "mongoDbMajorVersion",
        "num_shards": "numShards",
        "paused": "paused",
        "pinned_fcv": "pinnedFcv",
        "pit_enabled": "pitEnabled",
        "provider_auto_scaling_compute_max_instance_size": "providerAutoScalingComputeMaxInstanceSize",
        "provider_auto_scaling_compute_min_instance_size": "providerAutoScalingComputeMinInstanceSize",
        "provider_disk_iops": "providerDiskIops",
        "provider_disk_type_name": "providerDiskTypeName",
        "provider_encrypt_ebs_volume": "providerEncryptEbsVolume",
        "provider_region_name": "providerRegionName",
        "provider_volume_type": "providerVolumeType",
        "redact_client_log_data": "redactClientLogData",
        "replication_factor": "replicationFactor",
        "replication_specs": "replicationSpecs",
        "retain_backups_enabled": "retainBackupsEnabled",
        "tags": "tags",
        "termination_protection_enabled": "terminationProtectionEnabled",
        "timeouts": "timeouts",
        "version_release_system": "versionReleaseSystem",
    },
)
class ClusterConfig(_cdktf_9a9027ec.TerraformMetaArguments):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
        name: builtins.str,
        project_id: builtins.str,
        provider_instance_size_name: builtins.str,
        provider_name: builtins.str,
        accept_data_risks_and_force_replica_set_reconfig: typing.Optional[builtins.str] = None,
        advanced_configuration: typing.Optional[typing.Union[ClusterAdvancedConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
        auto_scaling_compute_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        auto_scaling_compute_scale_down_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        auto_scaling_disk_gb_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        backing_provider_name: typing.Optional[builtins.str] = None,
        backup_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        bi_connector_config: typing.Optional[typing.Union[ClusterBiConnectorConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        cloud_backup: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cluster_type: typing.Optional[builtins.str] = None,
        disk_size_gb: typing.Optional[jsii.Number] = None,
        encryption_at_rest_provider: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ClusterLabels", typing.Dict[builtins.str, typing.Any]]]]] = None,
        mongo_db_major_version: typing.Optional[builtins.str] = None,
        num_shards: typing.Optional[jsii.Number] = None,
        paused: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        pinned_fcv: typing.Optional[typing.Union["ClusterPinnedFcv", typing.Dict[builtins.str, typing.Any]]] = None,
        pit_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        provider_auto_scaling_compute_max_instance_size: typing.Optional[builtins.str] = None,
        provider_auto_scaling_compute_min_instance_size: typing.Optional[builtins.str] = None,
        provider_disk_iops: typing.Optional[jsii.Number] = None,
        provider_disk_type_name: typing.Optional[builtins.str] = None,
        provider_encrypt_ebs_volume: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        provider_region_name: typing.Optional[builtins.str] = None,
        provider_volume_type: typing.Optional[builtins.str] = None,
        redact_client_log_data: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        replication_factor: typing.Optional[jsii.Number] = None,
        replication_specs: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ClusterReplicationSpecs", typing.Dict[builtins.str, typing.Any]]]]] = None,
        retain_backups_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ClusterTags", typing.Dict[builtins.str, typing.Any]]]]] = None,
        termination_protection_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        timeouts: typing.Optional[typing.Union["ClusterTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        version_release_system: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#name Cluster#name}.
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#project_id Cluster#project_id}.
        :param provider_instance_size_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#provider_instance_size_name Cluster#provider_instance_size_name}.
        :param provider_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#provider_name Cluster#provider_name}.
        :param accept_data_risks_and_force_replica_set_reconfig: Submit this field alongside your topology reconfiguration to request a new regional outage resistant topology. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#accept_data_risks_and_force_replica_set_reconfig Cluster#accept_data_risks_and_force_replica_set_reconfig}
        :param advanced_configuration: advanced_configuration block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#advanced_configuration Cluster#advanced_configuration}
        :param auto_scaling_compute_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#auto_scaling_compute_enabled Cluster#auto_scaling_compute_enabled}.
        :param auto_scaling_compute_scale_down_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#auto_scaling_compute_scale_down_enabled Cluster#auto_scaling_compute_scale_down_enabled}.
        :param auto_scaling_disk_gb_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#auto_scaling_disk_gb_enabled Cluster#auto_scaling_disk_gb_enabled}.
        :param backing_provider_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#backing_provider_name Cluster#backing_provider_name}.
        :param backup_enabled: Clusters running MongoDB FCV 4.2 or later and any new Atlas clusters of any type do not support this parameter. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#backup_enabled Cluster#backup_enabled}
        :param bi_connector_config: bi_connector_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#bi_connector_config Cluster#bi_connector_config}
        :param cloud_backup: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#cloud_backup Cluster#cloud_backup}.
        :param cluster_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#cluster_type Cluster#cluster_type}.
        :param disk_size_gb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#disk_size_gb Cluster#disk_size_gb}.
        :param encryption_at_rest_provider: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#encryption_at_rest_provider Cluster#encryption_at_rest_provider}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#id Cluster#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param labels: labels block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#labels Cluster#labels}
        :param mongo_db_major_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#mongo_db_major_version Cluster#mongo_db_major_version}.
        :param num_shards: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#num_shards Cluster#num_shards}.
        :param paused: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#paused Cluster#paused}.
        :param pinned_fcv: pinned_fcv block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#pinned_fcv Cluster#pinned_fcv}
        :param pit_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#pit_enabled Cluster#pit_enabled}.
        :param provider_auto_scaling_compute_max_instance_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#provider_auto_scaling_compute_max_instance_size Cluster#provider_auto_scaling_compute_max_instance_size}.
        :param provider_auto_scaling_compute_min_instance_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#provider_auto_scaling_compute_min_instance_size Cluster#provider_auto_scaling_compute_min_instance_size}.
        :param provider_disk_iops: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#provider_disk_iops Cluster#provider_disk_iops}.
        :param provider_disk_type_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#provider_disk_type_name Cluster#provider_disk_type_name}.
        :param provider_encrypt_ebs_volume: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#provider_encrypt_ebs_volume Cluster#provider_encrypt_ebs_volume}.
        :param provider_region_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#provider_region_name Cluster#provider_region_name}.
        :param provider_volume_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#provider_volume_type Cluster#provider_volume_type}.
        :param redact_client_log_data: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#redact_client_log_data Cluster#redact_client_log_data}.
        :param replication_factor: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#replication_factor Cluster#replication_factor}.
        :param replication_specs: replication_specs block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#replication_specs Cluster#replication_specs}
        :param retain_backups_enabled: Flag that indicates whether to retain backup snapshots for the deleted dedicated cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#retain_backups_enabled Cluster#retain_backups_enabled}
        :param tags: tags block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#tags Cluster#tags}
        :param termination_protection_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#termination_protection_enabled Cluster#termination_protection_enabled}.
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#timeouts Cluster#timeouts}
        :param version_release_system: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#version_release_system Cluster#version_release_system}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(advanced_configuration, dict):
            advanced_configuration = ClusterAdvancedConfiguration(**advanced_configuration)
        if isinstance(bi_connector_config, dict):
            bi_connector_config = ClusterBiConnectorConfig(**bi_connector_config)
        if isinstance(pinned_fcv, dict):
            pinned_fcv = ClusterPinnedFcv(**pinned_fcv)
        if isinstance(timeouts, dict):
            timeouts = ClusterTimeouts(**timeouts)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d3acc59c9f3a6397879db2decd266e7b657db28546e04ebaf7f26cdf5ccf06d)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument provider_instance_size_name", value=provider_instance_size_name, expected_type=type_hints["provider_instance_size_name"])
            check_type(argname="argument provider_name", value=provider_name, expected_type=type_hints["provider_name"])
            check_type(argname="argument accept_data_risks_and_force_replica_set_reconfig", value=accept_data_risks_and_force_replica_set_reconfig, expected_type=type_hints["accept_data_risks_and_force_replica_set_reconfig"])
            check_type(argname="argument advanced_configuration", value=advanced_configuration, expected_type=type_hints["advanced_configuration"])
            check_type(argname="argument auto_scaling_compute_enabled", value=auto_scaling_compute_enabled, expected_type=type_hints["auto_scaling_compute_enabled"])
            check_type(argname="argument auto_scaling_compute_scale_down_enabled", value=auto_scaling_compute_scale_down_enabled, expected_type=type_hints["auto_scaling_compute_scale_down_enabled"])
            check_type(argname="argument auto_scaling_disk_gb_enabled", value=auto_scaling_disk_gb_enabled, expected_type=type_hints["auto_scaling_disk_gb_enabled"])
            check_type(argname="argument backing_provider_name", value=backing_provider_name, expected_type=type_hints["backing_provider_name"])
            check_type(argname="argument backup_enabled", value=backup_enabled, expected_type=type_hints["backup_enabled"])
            check_type(argname="argument bi_connector_config", value=bi_connector_config, expected_type=type_hints["bi_connector_config"])
            check_type(argname="argument cloud_backup", value=cloud_backup, expected_type=type_hints["cloud_backup"])
            check_type(argname="argument cluster_type", value=cluster_type, expected_type=type_hints["cluster_type"])
            check_type(argname="argument disk_size_gb", value=disk_size_gb, expected_type=type_hints["disk_size_gb"])
            check_type(argname="argument encryption_at_rest_provider", value=encryption_at_rest_provider, expected_type=type_hints["encryption_at_rest_provider"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument labels", value=labels, expected_type=type_hints["labels"])
            check_type(argname="argument mongo_db_major_version", value=mongo_db_major_version, expected_type=type_hints["mongo_db_major_version"])
            check_type(argname="argument num_shards", value=num_shards, expected_type=type_hints["num_shards"])
            check_type(argname="argument paused", value=paused, expected_type=type_hints["paused"])
            check_type(argname="argument pinned_fcv", value=pinned_fcv, expected_type=type_hints["pinned_fcv"])
            check_type(argname="argument pit_enabled", value=pit_enabled, expected_type=type_hints["pit_enabled"])
            check_type(argname="argument provider_auto_scaling_compute_max_instance_size", value=provider_auto_scaling_compute_max_instance_size, expected_type=type_hints["provider_auto_scaling_compute_max_instance_size"])
            check_type(argname="argument provider_auto_scaling_compute_min_instance_size", value=provider_auto_scaling_compute_min_instance_size, expected_type=type_hints["provider_auto_scaling_compute_min_instance_size"])
            check_type(argname="argument provider_disk_iops", value=provider_disk_iops, expected_type=type_hints["provider_disk_iops"])
            check_type(argname="argument provider_disk_type_name", value=provider_disk_type_name, expected_type=type_hints["provider_disk_type_name"])
            check_type(argname="argument provider_encrypt_ebs_volume", value=provider_encrypt_ebs_volume, expected_type=type_hints["provider_encrypt_ebs_volume"])
            check_type(argname="argument provider_region_name", value=provider_region_name, expected_type=type_hints["provider_region_name"])
            check_type(argname="argument provider_volume_type", value=provider_volume_type, expected_type=type_hints["provider_volume_type"])
            check_type(argname="argument redact_client_log_data", value=redact_client_log_data, expected_type=type_hints["redact_client_log_data"])
            check_type(argname="argument replication_factor", value=replication_factor, expected_type=type_hints["replication_factor"])
            check_type(argname="argument replication_specs", value=replication_specs, expected_type=type_hints["replication_specs"])
            check_type(argname="argument retain_backups_enabled", value=retain_backups_enabled, expected_type=type_hints["retain_backups_enabled"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument termination_protection_enabled", value=termination_protection_enabled, expected_type=type_hints["termination_protection_enabled"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
            check_type(argname="argument version_release_system", value=version_release_system, expected_type=type_hints["version_release_system"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "project_id": project_id,
            "provider_instance_size_name": provider_instance_size_name,
            "provider_name": provider_name,
        }
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners
        if accept_data_risks_and_force_replica_set_reconfig is not None:
            self._values["accept_data_risks_and_force_replica_set_reconfig"] = accept_data_risks_and_force_replica_set_reconfig
        if advanced_configuration is not None:
            self._values["advanced_configuration"] = advanced_configuration
        if auto_scaling_compute_enabled is not None:
            self._values["auto_scaling_compute_enabled"] = auto_scaling_compute_enabled
        if auto_scaling_compute_scale_down_enabled is not None:
            self._values["auto_scaling_compute_scale_down_enabled"] = auto_scaling_compute_scale_down_enabled
        if auto_scaling_disk_gb_enabled is not None:
            self._values["auto_scaling_disk_gb_enabled"] = auto_scaling_disk_gb_enabled
        if backing_provider_name is not None:
            self._values["backing_provider_name"] = backing_provider_name
        if backup_enabled is not None:
            self._values["backup_enabled"] = backup_enabled
        if bi_connector_config is not None:
            self._values["bi_connector_config"] = bi_connector_config
        if cloud_backup is not None:
            self._values["cloud_backup"] = cloud_backup
        if cluster_type is not None:
            self._values["cluster_type"] = cluster_type
        if disk_size_gb is not None:
            self._values["disk_size_gb"] = disk_size_gb
        if encryption_at_rest_provider is not None:
            self._values["encryption_at_rest_provider"] = encryption_at_rest_provider
        if id is not None:
            self._values["id"] = id
        if labels is not None:
            self._values["labels"] = labels
        if mongo_db_major_version is not None:
            self._values["mongo_db_major_version"] = mongo_db_major_version
        if num_shards is not None:
            self._values["num_shards"] = num_shards
        if paused is not None:
            self._values["paused"] = paused
        if pinned_fcv is not None:
            self._values["pinned_fcv"] = pinned_fcv
        if pit_enabled is not None:
            self._values["pit_enabled"] = pit_enabled
        if provider_auto_scaling_compute_max_instance_size is not None:
            self._values["provider_auto_scaling_compute_max_instance_size"] = provider_auto_scaling_compute_max_instance_size
        if provider_auto_scaling_compute_min_instance_size is not None:
            self._values["provider_auto_scaling_compute_min_instance_size"] = provider_auto_scaling_compute_min_instance_size
        if provider_disk_iops is not None:
            self._values["provider_disk_iops"] = provider_disk_iops
        if provider_disk_type_name is not None:
            self._values["provider_disk_type_name"] = provider_disk_type_name
        if provider_encrypt_ebs_volume is not None:
            self._values["provider_encrypt_ebs_volume"] = provider_encrypt_ebs_volume
        if provider_region_name is not None:
            self._values["provider_region_name"] = provider_region_name
        if provider_volume_type is not None:
            self._values["provider_volume_type"] = provider_volume_type
        if redact_client_log_data is not None:
            self._values["redact_client_log_data"] = redact_client_log_data
        if replication_factor is not None:
            self._values["replication_factor"] = replication_factor
        if replication_specs is not None:
            self._values["replication_specs"] = replication_specs
        if retain_backups_enabled is not None:
            self._values["retain_backups_enabled"] = retain_backups_enabled
        if tags is not None:
            self._values["tags"] = tags
        if termination_protection_enabled is not None:
            self._values["termination_protection_enabled"] = termination_protection_enabled
        if timeouts is not None:
            self._values["timeouts"] = timeouts
        if version_release_system is not None:
            self._values["version_release_system"] = version_release_system

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]], result)

    @builtins.property
    def count(
        self,
    ) -> typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]], result)

    @builtins.property
    def depends_on(
        self,
    ) -> typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[_cdktf_9a9027ec.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[_cdktf_9a9027ec.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]], result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#name Cluster#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def project_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#project_id Cluster#project_id}.'''
        result = self._values.get("project_id")
        assert result is not None, "Required property 'project_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def provider_instance_size_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#provider_instance_size_name Cluster#provider_instance_size_name}.'''
        result = self._values.get("provider_instance_size_name")
        assert result is not None, "Required property 'provider_instance_size_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def provider_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#provider_name Cluster#provider_name}.'''
        result = self._values.get("provider_name")
        assert result is not None, "Required property 'provider_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def accept_data_risks_and_force_replica_set_reconfig(
        self,
    ) -> typing.Optional[builtins.str]:
        '''Submit this field alongside your topology reconfiguration to request a new regional outage resistant topology.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#accept_data_risks_and_force_replica_set_reconfig Cluster#accept_data_risks_and_force_replica_set_reconfig}
        '''
        result = self._values.get("accept_data_risks_and_force_replica_set_reconfig")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def advanced_configuration(self) -> typing.Optional[ClusterAdvancedConfiguration]:
        '''advanced_configuration block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#advanced_configuration Cluster#advanced_configuration}
        '''
        result = self._values.get("advanced_configuration")
        return typing.cast(typing.Optional[ClusterAdvancedConfiguration], result)

    @builtins.property
    def auto_scaling_compute_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#auto_scaling_compute_enabled Cluster#auto_scaling_compute_enabled}.'''
        result = self._values.get("auto_scaling_compute_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def auto_scaling_compute_scale_down_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#auto_scaling_compute_scale_down_enabled Cluster#auto_scaling_compute_scale_down_enabled}.'''
        result = self._values.get("auto_scaling_compute_scale_down_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def auto_scaling_disk_gb_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#auto_scaling_disk_gb_enabled Cluster#auto_scaling_disk_gb_enabled}.'''
        result = self._values.get("auto_scaling_disk_gb_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def backing_provider_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#backing_provider_name Cluster#backing_provider_name}.'''
        result = self._values.get("backing_provider_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def backup_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Clusters running MongoDB FCV 4.2 or later and any new Atlas clusters of any type do not support this parameter.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#backup_enabled Cluster#backup_enabled}
        '''
        result = self._values.get("backup_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def bi_connector_config(self) -> typing.Optional[ClusterBiConnectorConfig]:
        '''bi_connector_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#bi_connector_config Cluster#bi_connector_config}
        '''
        result = self._values.get("bi_connector_config")
        return typing.cast(typing.Optional[ClusterBiConnectorConfig], result)

    @builtins.property
    def cloud_backup(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#cloud_backup Cluster#cloud_backup}.'''
        result = self._values.get("cloud_backup")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def cluster_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#cluster_type Cluster#cluster_type}.'''
        result = self._values.get("cluster_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disk_size_gb(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#disk_size_gb Cluster#disk_size_gb}.'''
        result = self._values.get("disk_size_gb")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def encryption_at_rest_provider(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#encryption_at_rest_provider Cluster#encryption_at_rest_provider}.'''
        result = self._values.get("encryption_at_rest_provider")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#id Cluster#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def labels(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ClusterLabels"]]]:
        '''labels block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#labels Cluster#labels}
        '''
        result = self._values.get("labels")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ClusterLabels"]]], result)

    @builtins.property
    def mongo_db_major_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#mongo_db_major_version Cluster#mongo_db_major_version}.'''
        result = self._values.get("mongo_db_major_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def num_shards(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#num_shards Cluster#num_shards}.'''
        result = self._values.get("num_shards")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def paused(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#paused Cluster#paused}.'''
        result = self._values.get("paused")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def pinned_fcv(self) -> typing.Optional["ClusterPinnedFcv"]:
        '''pinned_fcv block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#pinned_fcv Cluster#pinned_fcv}
        '''
        result = self._values.get("pinned_fcv")
        return typing.cast(typing.Optional["ClusterPinnedFcv"], result)

    @builtins.property
    def pit_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#pit_enabled Cluster#pit_enabled}.'''
        result = self._values.get("pit_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def provider_auto_scaling_compute_max_instance_size(
        self,
    ) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#provider_auto_scaling_compute_max_instance_size Cluster#provider_auto_scaling_compute_max_instance_size}.'''
        result = self._values.get("provider_auto_scaling_compute_max_instance_size")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def provider_auto_scaling_compute_min_instance_size(
        self,
    ) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#provider_auto_scaling_compute_min_instance_size Cluster#provider_auto_scaling_compute_min_instance_size}.'''
        result = self._values.get("provider_auto_scaling_compute_min_instance_size")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def provider_disk_iops(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#provider_disk_iops Cluster#provider_disk_iops}.'''
        result = self._values.get("provider_disk_iops")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def provider_disk_type_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#provider_disk_type_name Cluster#provider_disk_type_name}.'''
        result = self._values.get("provider_disk_type_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def provider_encrypt_ebs_volume(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#provider_encrypt_ebs_volume Cluster#provider_encrypt_ebs_volume}.'''
        result = self._values.get("provider_encrypt_ebs_volume")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def provider_region_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#provider_region_name Cluster#provider_region_name}.'''
        result = self._values.get("provider_region_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def provider_volume_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#provider_volume_type Cluster#provider_volume_type}.'''
        result = self._values.get("provider_volume_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def redact_client_log_data(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#redact_client_log_data Cluster#redact_client_log_data}.'''
        result = self._values.get("redact_client_log_data")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def replication_factor(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#replication_factor Cluster#replication_factor}.'''
        result = self._values.get("replication_factor")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def replication_specs(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ClusterReplicationSpecs"]]]:
        '''replication_specs block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#replication_specs Cluster#replication_specs}
        '''
        result = self._values.get("replication_specs")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ClusterReplicationSpecs"]]], result)

    @builtins.property
    def retain_backups_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag that indicates whether to retain backup snapshots for the deleted dedicated cluster.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#retain_backups_enabled Cluster#retain_backups_enabled}
        '''
        result = self._values.get("retain_backups_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tags(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ClusterTags"]]]:
        '''tags block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#tags Cluster#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ClusterTags"]]], result)

    @builtins.property
    def termination_protection_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#termination_protection_enabled Cluster#termination_protection_enabled}.'''
        result = self._values.get("termination_protection_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["ClusterTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#timeouts Cluster#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["ClusterTimeouts"], result)

    @builtins.property
    def version_release_system(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#version_release_system Cluster#version_release_system}.'''
        result = self._values.get("version_release_system")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ClusterConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterConnectionStrings",
    jsii_struct_bases=[],
    name_mapping={},
)
class ClusterConnectionStrings:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ClusterConnectionStrings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ClusterConnectionStringsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterConnectionStringsList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e29704e4075ba995514f146ccf8cfd64677d75de7df64f9f330c81c4f9fb750)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ClusterConnectionStringsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1626dcf42933d52a7600e776db6e94517340ab0bf7b3055bc5f9bb74d5fd289)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ClusterConnectionStringsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__235fb7f34b8d85e5ea84b590c4f2ab1cca0ee2613d45cfd4f8332312219ec657)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed7a8d746987656aa1e6ee566087dc289f373a6aef6fa4b3233d1352f5a83427)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a73f35c5773cffdfab39d76949a10d62ac85e3d654e3948f4338b142acd588f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class ClusterConnectionStringsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterConnectionStringsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__465ba0b2198b4e05f4ed493110700f19aefb4343146fa0f36f34b6af42aef7ca)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="private")
    def private(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "private"))

    @builtins.property
    @jsii.member(jsii_name="privateEndpoint")
    def private_endpoint(self) -> "ClusterConnectionStringsPrivateEndpointList":
        return typing.cast("ClusterConnectionStringsPrivateEndpointList", jsii.get(self, "privateEndpoint"))

    @builtins.property
    @jsii.member(jsii_name="privateSrv")
    def private_srv(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateSrv"))

    @builtins.property
    @jsii.member(jsii_name="standard")
    def standard(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "standard"))

    @builtins.property
    @jsii.member(jsii_name="standardSrv")
    def standard_srv(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "standardSrv"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ClusterConnectionStrings]:
        return typing.cast(typing.Optional[ClusterConnectionStrings], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ClusterConnectionStrings]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__123a661513edb03486b421f04e709a159e6b0abd6a83b8095291bfc628787064)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterConnectionStringsPrivateEndpoint",
    jsii_struct_bases=[],
    name_mapping={},
)
class ClusterConnectionStringsPrivateEndpoint:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ClusterConnectionStringsPrivateEndpoint(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterConnectionStringsPrivateEndpointEndpoints",
    jsii_struct_bases=[],
    name_mapping={},
)
class ClusterConnectionStringsPrivateEndpointEndpoints:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ClusterConnectionStringsPrivateEndpointEndpoints(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ClusterConnectionStringsPrivateEndpointEndpointsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterConnectionStringsPrivateEndpointEndpointsList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f822541b1a69368e0910abdf9128309781518aa568460b3d238bf37a4343d0dc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ClusterConnectionStringsPrivateEndpointEndpointsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06834d4ca3befad69a0bc4abd800741697d84d7adb66416469ba60d1565e130c)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ClusterConnectionStringsPrivateEndpointEndpointsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4aa8bae683f6faea7784793ec7df627a9050fa8b93a0239fa2c0dad6c01e755e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de81d18a2089e9924e3af20cf916029c3332191af6fe7dbbe537ed727403957f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87ee92d67ce7a8ec66ed72b8ea30382183a6152ef5915035d468bc77e9072240)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class ClusterConnectionStringsPrivateEndpointEndpointsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterConnectionStringsPrivateEndpointEndpointsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f6c44b0971206e8c9cda90619b94b285018fd732595194f282424b2681d966a4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="endpointId")
    def endpoint_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "endpointId"))

    @builtins.property
    @jsii.member(jsii_name="providerName")
    def provider_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "providerName"))

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ClusterConnectionStringsPrivateEndpointEndpoints]:
        return typing.cast(typing.Optional[ClusterConnectionStringsPrivateEndpointEndpoints], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ClusterConnectionStringsPrivateEndpointEndpoints],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9744bf2afb6fef3abea0716fbed85b1a1d9cebc4fc51303b1dc340fb37efda98)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ClusterConnectionStringsPrivateEndpointList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterConnectionStringsPrivateEndpointList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a699c27a211a19735b0375c4985d63e7724480518d42efb8b36b4ce09f425e8b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ClusterConnectionStringsPrivateEndpointOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__321844be66a10e6e0e86a41579a7ba6de604d0e32b9d16e8be8477fb166f015c)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ClusterConnectionStringsPrivateEndpointOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__afb006779896af2b0fdb597cc793dbc22c406d8593b32d90bea4f19c212060a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a1b8634b9b0ce680f692b0848d8743e9b351f178d50646f06fde31ab75a7b1a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e1b48a921d04e1712d587c09382a39888058583b70ab5c6923e040e2a9c2f62)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class ClusterConnectionStringsPrivateEndpointOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterConnectionStringsPrivateEndpointOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b66c574a2d21a7ee844ad605aa29c32acd97cf82646c6a797aa656db45ee9589)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="connectionString")
    def connection_string(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connectionString"))

    @builtins.property
    @jsii.member(jsii_name="endpoints")
    def endpoints(self) -> ClusterConnectionStringsPrivateEndpointEndpointsList:
        return typing.cast(ClusterConnectionStringsPrivateEndpointEndpointsList, jsii.get(self, "endpoints"))

    @builtins.property
    @jsii.member(jsii_name="srvConnectionString")
    def srv_connection_string(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "srvConnectionString"))

    @builtins.property
    @jsii.member(jsii_name="srvShardOptimizedConnectionString")
    def srv_shard_optimized_connection_string(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "srvShardOptimizedConnectionString"))

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ClusterConnectionStringsPrivateEndpoint]:
        return typing.cast(typing.Optional[ClusterConnectionStringsPrivateEndpoint], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ClusterConnectionStringsPrivateEndpoint],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55a5c82338b295145c256938ba30fe3ac0391ff9cea7af49821ac902294ffb41)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterLabels",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class ClusterLabels:
    def __init__(
        self,
        *,
        key: typing.Optional[builtins.str] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#key Cluster#key}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#value Cluster#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c81b4660dc48908502afbba1bf0bcdd95d584ace9074eba15fe848109cfe15ff)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if key is not None:
            self._values["key"] = key
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#key Cluster#key}.'''
        result = self._values.get("key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#value Cluster#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ClusterLabels(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ClusterLabelsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterLabelsList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b40ae318e3d0825772c73b6bcfb45c7dcc5f9a322f57d34a8b23bde2a7dc561)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ClusterLabelsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62cce240dda714bb54c3fa50ec3710d30714666e77258d500a7b6fced72f6802)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ClusterLabelsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7bbedb933aa8093241304083b2c9fce0595449b5231a11ea46034dcfef60ddd5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__deae2f01673579e7becf88ec25289d7ef81af400daf69c630cb55ddeece3b269)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__873d557dc7128a2075678478a4f6bb07b2640437c21fa52773f1f9ffdce31024)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ClusterLabels]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ClusterLabels]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ClusterLabels]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4196e829e5b9d941a340078a5db8a9753fd67efcdef6d4828e5424ec7c299c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ClusterLabelsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterLabelsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e97e8f35418569888820159d46531973b3a9addac011570dbc76f365bad21d3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetKey")
    def reset_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKey", []))

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9851751c4d2422d6b3785503ab810606eb6bbb9f040bc4f0590deccc51443551)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c589f6125e8c1e049b920d10c2892866b9165dfc175b1b36605a7a75498bc20)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ClusterLabels]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ClusterLabels]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ClusterLabels]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a789b222c0530171d5fcd21f06d0222c2a967ea33f4525c6b8dd8225051a797)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterPinnedFcv",
    jsii_struct_bases=[],
    name_mapping={"expiration_date": "expirationDate"},
)
class ClusterPinnedFcv:
    def __init__(self, *, expiration_date: builtins.str) -> None:
        '''
        :param expiration_date: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#expiration_date Cluster#expiration_date}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eaacf5d618f27b104a9533a5f39f57cccf4f8cb35a6ca6094c2581beeb8b36e4)
            check_type(argname="argument expiration_date", value=expiration_date, expected_type=type_hints["expiration_date"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "expiration_date": expiration_date,
        }

    @builtins.property
    def expiration_date(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#expiration_date Cluster#expiration_date}.'''
        result = self._values.get("expiration_date")
        assert result is not None, "Required property 'expiration_date' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ClusterPinnedFcv(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ClusterPinnedFcvOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterPinnedFcvOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e71586e93c1787e1cf8d7dff5dfa703b51f2ee970015b5c6546b67df62dbd865)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @builtins.property
    @jsii.member(jsii_name="expirationDateInput")
    def expiration_date_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "expirationDateInput"))

    @builtins.property
    @jsii.member(jsii_name="expirationDate")
    def expiration_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "expirationDate"))

    @expiration_date.setter
    def expiration_date(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__403053d9efbad4d18d970913f259cc8afaa8df4640911be4d1f2d1120d7f31cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "expirationDate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ClusterPinnedFcv]:
        return typing.cast(typing.Optional[ClusterPinnedFcv], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ClusterPinnedFcv]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c57d0f795542318a86fbed6519930fbfc50010f3aa4886d2b32209f6775872f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterReplicationSpecs",
    jsii_struct_bases=[],
    name_mapping={
        "num_shards": "numShards",
        "id": "id",
        "regions_config": "regionsConfig",
        "zone_name": "zoneName",
    },
)
class ClusterReplicationSpecs:
    def __init__(
        self,
        *,
        num_shards: jsii.Number,
        id: typing.Optional[builtins.str] = None,
        regions_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ClusterReplicationSpecsRegionsConfig", typing.Dict[builtins.str, typing.Any]]]]] = None,
        zone_name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param num_shards: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#num_shards Cluster#num_shards}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#id Cluster#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param regions_config: regions_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#regions_config Cluster#regions_config}
        :param zone_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#zone_name Cluster#zone_name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b89d0a827d02331f7c74f8016bcd9b8a4aa4000c061c0b3e2a9a4343bc5d3a51)
            check_type(argname="argument num_shards", value=num_shards, expected_type=type_hints["num_shards"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument regions_config", value=regions_config, expected_type=type_hints["regions_config"])
            check_type(argname="argument zone_name", value=zone_name, expected_type=type_hints["zone_name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "num_shards": num_shards,
        }
        if id is not None:
            self._values["id"] = id
        if regions_config is not None:
            self._values["regions_config"] = regions_config
        if zone_name is not None:
            self._values["zone_name"] = zone_name

    @builtins.property
    def num_shards(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#num_shards Cluster#num_shards}.'''
        result = self._values.get("num_shards")
        assert result is not None, "Required property 'num_shards' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#id Cluster#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def regions_config(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ClusterReplicationSpecsRegionsConfig"]]]:
        '''regions_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#regions_config Cluster#regions_config}
        '''
        result = self._values.get("regions_config")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ClusterReplicationSpecsRegionsConfig"]]], result)

    @builtins.property
    def zone_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#zone_name Cluster#zone_name}.'''
        result = self._values.get("zone_name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ClusterReplicationSpecs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ClusterReplicationSpecsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterReplicationSpecsList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9179eb50637ea4d5468371301df7d51f74a49e679fac3362bdcae3c8efed2a43)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ClusterReplicationSpecsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c1ccdbdb5391f82b3e8d22cddb1f3b1416d22c0173528d369a512dff70026d9)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ClusterReplicationSpecsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e226dd89d7071aa0a58a95c25f1dfe927a7a4f69d8e82e6d20196c11a421ba8b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c7374b360cc18bb1a9addf52085618f4dee17ed30e463bd490ee15133b4a1d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84200f677db927562f7629bf69592fbc828884887089a0e76c2cb69973881b53)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ClusterReplicationSpecs]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ClusterReplicationSpecs]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ClusterReplicationSpecs]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0b73d9d6c032d15dde47f375b00822b1258a1d116b17b6b465278cd6e4214c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ClusterReplicationSpecsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterReplicationSpecsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f54249cecfc43b563ec9fe9397f3ee5732db33f1b006ea34e787471e823ac3f7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putRegionsConfig")
    def put_regions_config(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ClusterReplicationSpecsRegionsConfig", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2935e3e51b59b2a6805fb0820f1c95a31b46e4d040cf0eb299f663bc01bf00c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putRegionsConfig", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetRegionsConfig")
    def reset_regions_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegionsConfig", []))

    @jsii.member(jsii_name="resetZoneName")
    def reset_zone_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetZoneName", []))

    @builtins.property
    @jsii.member(jsii_name="regionsConfig")
    def regions_config(self) -> "ClusterReplicationSpecsRegionsConfigList":
        return typing.cast("ClusterReplicationSpecsRegionsConfigList", jsii.get(self, "regionsConfig"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="numShardsInput")
    def num_shards_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numShardsInput"))

    @builtins.property
    @jsii.member(jsii_name="regionsConfigInput")
    def regions_config_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ClusterReplicationSpecsRegionsConfig"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ClusterReplicationSpecsRegionsConfig"]]], jsii.get(self, "regionsConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneNameInput")
    def zone_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneNameInput"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97121ef32b238d1ca4f4b5020693538590d7ff9442dc24104f7cc7f67997fe0f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="numShards")
    def num_shards(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numShards"))

    @num_shards.setter
    def num_shards(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6fa7666e8a7a83ad62ccdf5cef1b0b4d9778f6ca48a04d5c1259447eef63320)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numShards", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneName")
    def zone_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneName"))

    @zone_name.setter
    def zone_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f57427bbdd27585ae16186e3356ce6c0bb82b6f09ba160a8ffc26cd996286524)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ClusterReplicationSpecs]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ClusterReplicationSpecs]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ClusterReplicationSpecs]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c6c8caa2931819678f7318742973539762941aa6acbbba1864fd9cf15030120)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterReplicationSpecsRegionsConfig",
    jsii_struct_bases=[],
    name_mapping={
        "region_name": "regionName",
        "analytics_nodes": "analyticsNodes",
        "electable_nodes": "electableNodes",
        "priority": "priority",
        "read_only_nodes": "readOnlyNodes",
    },
)
class ClusterReplicationSpecsRegionsConfig:
    def __init__(
        self,
        *,
        region_name: builtins.str,
        analytics_nodes: typing.Optional[jsii.Number] = None,
        electable_nodes: typing.Optional[jsii.Number] = None,
        priority: typing.Optional[jsii.Number] = None,
        read_only_nodes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param region_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#region_name Cluster#region_name}.
        :param analytics_nodes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#analytics_nodes Cluster#analytics_nodes}.
        :param electable_nodes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#electable_nodes Cluster#electable_nodes}.
        :param priority: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#priority Cluster#priority}.
        :param read_only_nodes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#read_only_nodes Cluster#read_only_nodes}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0640b7a5105bc5f1c237e21c6a9152f4b553497c4509be825934ae0de644736)
            check_type(argname="argument region_name", value=region_name, expected_type=type_hints["region_name"])
            check_type(argname="argument analytics_nodes", value=analytics_nodes, expected_type=type_hints["analytics_nodes"])
            check_type(argname="argument electable_nodes", value=electable_nodes, expected_type=type_hints["electable_nodes"])
            check_type(argname="argument priority", value=priority, expected_type=type_hints["priority"])
            check_type(argname="argument read_only_nodes", value=read_only_nodes, expected_type=type_hints["read_only_nodes"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "region_name": region_name,
        }
        if analytics_nodes is not None:
            self._values["analytics_nodes"] = analytics_nodes
        if electable_nodes is not None:
            self._values["electable_nodes"] = electable_nodes
        if priority is not None:
            self._values["priority"] = priority
        if read_only_nodes is not None:
            self._values["read_only_nodes"] = read_only_nodes

    @builtins.property
    def region_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#region_name Cluster#region_name}.'''
        result = self._values.get("region_name")
        assert result is not None, "Required property 'region_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def analytics_nodes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#analytics_nodes Cluster#analytics_nodes}.'''
        result = self._values.get("analytics_nodes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def electable_nodes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#electable_nodes Cluster#electable_nodes}.'''
        result = self._values.get("electable_nodes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def priority(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#priority Cluster#priority}.'''
        result = self._values.get("priority")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def read_only_nodes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#read_only_nodes Cluster#read_only_nodes}.'''
        result = self._values.get("read_only_nodes")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ClusterReplicationSpecsRegionsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ClusterReplicationSpecsRegionsConfigList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterReplicationSpecsRegionsConfigList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ed1527e6fa5fd9ee1c33d2806f419ecf6b40bb8e7ee10a9cdac060d2f4827ce)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ClusterReplicationSpecsRegionsConfigOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__308c4b29414ce70c488407137933c7b88f2241824a86f1ca3b846b09c251bfd4)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ClusterReplicationSpecsRegionsConfigOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b87ee9775103c12d6dd9ddb4606b877a7c73804cc3053c2e0885d4d7cacdedf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c8e38fdf01f8d9a41d7d527fa168d0a5581a40d822abe39c9767b0dc45ca1aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de5fd9e5ec7ec09f3d25cf78e07e09848b462242d0160e05dfdb10ec2856fef9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ClusterReplicationSpecsRegionsConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ClusterReplicationSpecsRegionsConfig]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ClusterReplicationSpecsRegionsConfig]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fce106c1fb3e4ce43c745e8af4f7e14d07579f4b8946d8ec5bdf4c31b6b596db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ClusterReplicationSpecsRegionsConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterReplicationSpecsRegionsConfigOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__deefb2888d0ce9bba253d469b630d842134cb467b60c853331c2c4ad9ec74433)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetAnalyticsNodes")
    def reset_analytics_nodes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAnalyticsNodes", []))

    @jsii.member(jsii_name="resetElectableNodes")
    def reset_electable_nodes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetElectableNodes", []))

    @jsii.member(jsii_name="resetPriority")
    def reset_priority(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPriority", []))

    @jsii.member(jsii_name="resetReadOnlyNodes")
    def reset_read_only_nodes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReadOnlyNodes", []))

    @builtins.property
    @jsii.member(jsii_name="analyticsNodesInput")
    def analytics_nodes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "analyticsNodesInput"))

    @builtins.property
    @jsii.member(jsii_name="electableNodesInput")
    def electable_nodes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "electableNodesInput"))

    @builtins.property
    @jsii.member(jsii_name="priorityInput")
    def priority_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "priorityInput"))

    @builtins.property
    @jsii.member(jsii_name="readOnlyNodesInput")
    def read_only_nodes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "readOnlyNodesInput"))

    @builtins.property
    @jsii.member(jsii_name="regionNameInput")
    def region_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionNameInput"))

    @builtins.property
    @jsii.member(jsii_name="analyticsNodes")
    def analytics_nodes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "analyticsNodes"))

    @analytics_nodes.setter
    def analytics_nodes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf59fff0341a295f59551126527963ab78b42d7a99d7e23484565476c2486643)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "analyticsNodes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="electableNodes")
    def electable_nodes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "electableNodes"))

    @electable_nodes.setter
    def electable_nodes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1572c2ec07c15338a9a1e9129fa1dbfd14c45249b9c840d6390830aeecf43527)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "electableNodes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="priority")
    def priority(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "priority"))

    @priority.setter
    def priority(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18debef176e137db27346863922b95b03d1ae486ef6d5fe9fca36b79b32675ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "priority", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="readOnlyNodes")
    def read_only_nodes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "readOnlyNodes"))

    @read_only_nodes.setter
    def read_only_nodes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c79b7a68d1b409ddd9af029e41942c60956a19b1d73e3e4ac2ca282cbdee2955)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "readOnlyNodes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="regionName")
    def region_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "regionName"))

    @region_name.setter
    def region_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01a9fe4ac62d56f26f9b94d5f7191d2e344e98286e403b81dbc16fa45969e82a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "regionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ClusterReplicationSpecsRegionsConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ClusterReplicationSpecsRegionsConfig]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ClusterReplicationSpecsRegionsConfig]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d374952b16aec64b6d55706daa3a5888918069fbcbd4104975fe5eec508a4915)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterSnapshotBackupPolicy",
    jsii_struct_bases=[],
    name_mapping={},
)
class ClusterSnapshotBackupPolicy:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ClusterSnapshotBackupPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ClusterSnapshotBackupPolicyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterSnapshotBackupPolicyList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d47857d5b423b1f94dce37369ed68b7f79cc437addccabb6ab7f974cd64d9989)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ClusterSnapshotBackupPolicyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18dd674a5e2ba7be57b3ddca2fa86cf451128d94feb5a8c72ad3ad9a7919555f)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ClusterSnapshotBackupPolicyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4a917ae3ab1b64ec73c46da722f19d3d2f275cc8999c6e02cc85fa733ee32ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3fd279cdb3eb403b640729e0724ee9234e0bc586db23d858ab0728af7ab4a2a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2aa627dd1fe95dbab5b8e756fe0609fc764b7b4fb5ea7cfd6b86f410beb9b972)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class ClusterSnapshotBackupPolicyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterSnapshotBackupPolicyOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79a725b025cdb8ee4ef69451d3a74798818ba98d97139ca20c9dcdb32e921098)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="clusterId")
    def cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterId"))

    @builtins.property
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterName"))

    @builtins.property
    @jsii.member(jsii_name="nextSnapshot")
    def next_snapshot(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nextSnapshot"))

    @builtins.property
    @jsii.member(jsii_name="policies")
    def policies(self) -> "ClusterSnapshotBackupPolicyPoliciesList":
        return typing.cast("ClusterSnapshotBackupPolicyPoliciesList", jsii.get(self, "policies"))

    @builtins.property
    @jsii.member(jsii_name="referenceHourOfDay")
    def reference_hour_of_day(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "referenceHourOfDay"))

    @builtins.property
    @jsii.member(jsii_name="referenceMinuteOfHour")
    def reference_minute_of_hour(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "referenceMinuteOfHour"))

    @builtins.property
    @jsii.member(jsii_name="restoreWindowDays")
    def restore_window_days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "restoreWindowDays"))

    @builtins.property
    @jsii.member(jsii_name="updateSnapshots")
    def update_snapshots(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "updateSnapshots"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ClusterSnapshotBackupPolicy]:
        return typing.cast(typing.Optional[ClusterSnapshotBackupPolicy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ClusterSnapshotBackupPolicy],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3955f3eb48fcbe0d75042ee6b3e7c54d4310044b1d67b560583af7d039855abc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterSnapshotBackupPolicyPolicies",
    jsii_struct_bases=[],
    name_mapping={},
)
class ClusterSnapshotBackupPolicyPolicies:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ClusterSnapshotBackupPolicyPolicies(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ClusterSnapshotBackupPolicyPoliciesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterSnapshotBackupPolicyPoliciesList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2659847b335bbe29006623b729b7cf2425826476f64307b7e2a34c978ad48a41)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ClusterSnapshotBackupPolicyPoliciesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__661ecb9ea381fb350b8cbb1471e5ddc5de6ec098d79dbcf92be74afb41f4e5fd)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ClusterSnapshotBackupPolicyPoliciesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ce507306b137ca864654998576d77c90b33e26315cca56bd425a89057733fac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__115f2a4f0e2bc0d51151935eadbe9e8170b7b202954d7093c81fac53f6e93c8d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__addb8c21fb7282f4fbec82314c3999ab5276f5dd268936e6e88fd095b098516e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class ClusterSnapshotBackupPolicyPoliciesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterSnapshotBackupPolicyPoliciesOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d86c1e5cbeaf3708d3194194176abe58bc4bddba21d7d3727409fb21175ce59)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="policyItem")
    def policy_item(self) -> "ClusterSnapshotBackupPolicyPoliciesPolicyItemList":
        return typing.cast("ClusterSnapshotBackupPolicyPoliciesPolicyItemList", jsii.get(self, "policyItem"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ClusterSnapshotBackupPolicyPolicies]:
        return typing.cast(typing.Optional[ClusterSnapshotBackupPolicyPolicies], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ClusterSnapshotBackupPolicyPolicies],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44ad554e20c6b40d8ba95f883dae0f0039015ea3467e959e8733652ddd946305)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterSnapshotBackupPolicyPoliciesPolicyItem",
    jsii_struct_bases=[],
    name_mapping={},
)
class ClusterSnapshotBackupPolicyPoliciesPolicyItem:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ClusterSnapshotBackupPolicyPoliciesPolicyItem(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ClusterSnapshotBackupPolicyPoliciesPolicyItemList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterSnapshotBackupPolicyPoliciesPolicyItemList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6b75dce9401eb716be9371391512014b17d9786f267e031256020aa16e8adee)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ClusterSnapshotBackupPolicyPoliciesPolicyItemOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4dc654f219d60af47f3e3feaeee92ea3ff530a77911c010e4c5029303a5557b2)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ClusterSnapshotBackupPolicyPoliciesPolicyItemOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1190cdf30855db116b01fdc71747bdfb6eb4847b136b814b4db71055f94db3ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fed26a5d7d8d1f7e814538dd4ed9509bc3e58d58f48a14c2de0e97d511c8f7a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24724f9a1c80081664f4b1414bdc55d9842c0fe5e10c1f7dcea382d9ee11fc28)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class ClusterSnapshotBackupPolicyPoliciesPolicyItemOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterSnapshotBackupPolicyPoliciesPolicyItemOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72a28b24a420979f855abe24a164ac9c2d5067d8bcc8afb9b01a7b6688185f68)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="frequencyInterval")
    def frequency_interval(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "frequencyInterval"))

    @builtins.property
    @jsii.member(jsii_name="frequencyType")
    def frequency_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "frequencyType"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="retentionUnit")
    def retention_unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "retentionUnit"))

    @builtins.property
    @jsii.member(jsii_name="retentionValue")
    def retention_value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "retentionValue"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[ClusterSnapshotBackupPolicyPoliciesPolicyItem]:
        return typing.cast(typing.Optional[ClusterSnapshotBackupPolicyPoliciesPolicyItem], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ClusterSnapshotBackupPolicyPoliciesPolicyItem],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27dc1912d4a387fe064e292ec9fccd32a5ef42cffc9fda85990822ab5c4ae204)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterTags",
    jsii_struct_bases=[],
    name_mapping={"key": "key", "value": "value"},
)
class ClusterTags:
    def __init__(self, *, key: builtins.str, value: builtins.str) -> None:
        '''
        :param key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#key Cluster#key}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#value Cluster#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efd8f9f6b5b3cf3d78eb03b545744fa0841eb0e6ae085168f5e3f11ff72dd1ac)
            check_type(argname="argument key", value=key, expected_type=type_hints["key"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "key": key,
            "value": value,
        }

    @builtins.property
    def key(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#key Cluster#key}.'''
        result = self._values.get("key")
        assert result is not None, "Required property 'key' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#value Cluster#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ClusterTags(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ClusterTagsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterTagsList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d67510ffd5f15989eb0da4bfbaba928fbaacb4026f0e7846d52daa762437a95)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ClusterTagsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0b4e794b9a0fd9f4119f4383d875480b4632a2c9d29cd749f86ab281d080855)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ClusterTagsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebb41567076dd12af8b88d39a054641095d82bc85245f6771c8f6a316a7960fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0fb265b18b6aef386a6805d42b8a9430cc315c1d240418b4c2b7c7bd1275f7eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b9b63288f5bc976488c04e5341742063d8b7493138ba2472c5b75cab2765cd5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ClusterTags]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ClusterTags]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ClusterTags]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1641dddee68f79908cec07425900a7e92d7039f057c6bace27f1a333d1e3e2b8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ClusterTagsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterTagsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c4c68b9f1354a248648235e69c4444936119d60d6d6a374fe079f2ca5561128)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="keyInput")
    def key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @key.setter
    def key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7aee80518752533e36d72e40f5143f483478ece3c7f580bacb8ceaf1bef2095)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "key", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bdbc30ff6ec52798014f464b43c8d9466836969684a34f3114bc3ded85926a23)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ClusterTags]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ClusterTags]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ClusterTags]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e4a0e69d72da7fd671fc168fec03e1b6d688b8e7fe1ee49eb3b0834505a6b8c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete", "update": "update"},
)
class ClusterTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
        update: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#create Cluster#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#delete Cluster#delete}.
        :param update: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#update Cluster#update}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36e444feea44713276a57812646495470437732a2ab970bed6ea9695d342fd32)
            check_type(argname="argument create", value=create, expected_type=type_hints["create"])
            check_type(argname="argument delete", value=delete, expected_type=type_hints["delete"])
            check_type(argname="argument update", value=update, expected_type=type_hints["update"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete
        if update is not None:
            self._values["update"] = update

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#create Cluster#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#delete Cluster#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def update(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cluster#update Cluster#update}.'''
        result = self._values.get("update")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ClusterTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ClusterTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cluster.ClusterTimeoutsOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__604f216d83ce933a7fb5ee0e39071f10bd5bb0207f312a42c8363cd64ab0343f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @jsii.member(jsii_name="resetUpdate")
    def reset_update(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdate", []))

    @builtins.property
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

    @builtins.property
    @jsii.member(jsii_name="updateInput")
    def update_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "updateInput"))

    @builtins.property
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82664bd5fb1d91215ec3f5124995a040ce2a603464c587f72fb67a8d31af0f20)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2033b566bd413d0f0a0fb2d0ce4bbb3332d2a94effbc46eb58112fc6e597ad8d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delete", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="update")
    def update(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "update"))

    @update.setter
    def update(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c4897d5a8eecc948338abdd83ad85be096fa8d9891488615d8c2c0dc2b85d9a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "update", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ClusterTimeouts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ClusterTimeouts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ClusterTimeouts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9b1f838ce0e212045a493a2c2f8b83f8390015580ceeec69e3f80029aa15ce2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "Cluster",
    "ClusterAdvancedConfiguration",
    "ClusterAdvancedConfigurationOutputReference",
    "ClusterBiConnectorConfig",
    "ClusterBiConnectorConfigOutputReference",
    "ClusterConfig",
    "ClusterConnectionStrings",
    "ClusterConnectionStringsList",
    "ClusterConnectionStringsOutputReference",
    "ClusterConnectionStringsPrivateEndpoint",
    "ClusterConnectionStringsPrivateEndpointEndpoints",
    "ClusterConnectionStringsPrivateEndpointEndpointsList",
    "ClusterConnectionStringsPrivateEndpointEndpointsOutputReference",
    "ClusterConnectionStringsPrivateEndpointList",
    "ClusterConnectionStringsPrivateEndpointOutputReference",
    "ClusterLabels",
    "ClusterLabelsList",
    "ClusterLabelsOutputReference",
    "ClusterPinnedFcv",
    "ClusterPinnedFcvOutputReference",
    "ClusterReplicationSpecs",
    "ClusterReplicationSpecsList",
    "ClusterReplicationSpecsOutputReference",
    "ClusterReplicationSpecsRegionsConfig",
    "ClusterReplicationSpecsRegionsConfigList",
    "ClusterReplicationSpecsRegionsConfigOutputReference",
    "ClusterSnapshotBackupPolicy",
    "ClusterSnapshotBackupPolicyList",
    "ClusterSnapshotBackupPolicyOutputReference",
    "ClusterSnapshotBackupPolicyPolicies",
    "ClusterSnapshotBackupPolicyPoliciesList",
    "ClusterSnapshotBackupPolicyPoliciesOutputReference",
    "ClusterSnapshotBackupPolicyPoliciesPolicyItem",
    "ClusterSnapshotBackupPolicyPoliciesPolicyItemList",
    "ClusterSnapshotBackupPolicyPoliciesPolicyItemOutputReference",
    "ClusterTags",
    "ClusterTagsList",
    "ClusterTagsOutputReference",
    "ClusterTimeouts",
    "ClusterTimeoutsOutputReference",
]

publication.publish()

def _typecheckingstub__742db278a5f8ce3b0569707b0a97c64056cd4b49a739041d7f3cf330a8e32fd3(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    project_id: builtins.str,
    provider_instance_size_name: builtins.str,
    provider_name: builtins.str,
    accept_data_risks_and_force_replica_set_reconfig: typing.Optional[builtins.str] = None,
    advanced_configuration: typing.Optional[typing.Union[ClusterAdvancedConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    auto_scaling_compute_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    auto_scaling_compute_scale_down_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    auto_scaling_disk_gb_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    backing_provider_name: typing.Optional[builtins.str] = None,
    backup_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    bi_connector_config: typing.Optional[typing.Union[ClusterBiConnectorConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    cloud_backup: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cluster_type: typing.Optional[builtins.str] = None,
    disk_size_gb: typing.Optional[jsii.Number] = None,
    encryption_at_rest_provider: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    labels: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ClusterLabels, typing.Dict[builtins.str, typing.Any]]]]] = None,
    mongo_db_major_version: typing.Optional[builtins.str] = None,
    num_shards: typing.Optional[jsii.Number] = None,
    paused: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    pinned_fcv: typing.Optional[typing.Union[ClusterPinnedFcv, typing.Dict[builtins.str, typing.Any]]] = None,
    pit_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    provider_auto_scaling_compute_max_instance_size: typing.Optional[builtins.str] = None,
    provider_auto_scaling_compute_min_instance_size: typing.Optional[builtins.str] = None,
    provider_disk_iops: typing.Optional[jsii.Number] = None,
    provider_disk_type_name: typing.Optional[builtins.str] = None,
    provider_encrypt_ebs_volume: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    provider_region_name: typing.Optional[builtins.str] = None,
    provider_volume_type: typing.Optional[builtins.str] = None,
    redact_client_log_data: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    replication_factor: typing.Optional[jsii.Number] = None,
    replication_specs: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ClusterReplicationSpecs, typing.Dict[builtins.str, typing.Any]]]]] = None,
    retain_backups_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ClusterTags, typing.Dict[builtins.str, typing.Any]]]]] = None,
    termination_protection_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    timeouts: typing.Optional[typing.Union[ClusterTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
    version_release_system: typing.Optional[builtins.str] = None,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7a794416e32a4df7b4cbce061ae7dfa583c3f5e20f3076d57d79f083435c184(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d79e0f634f55bab2f500fe754a5acf37b0994ea8454f5870ff5d018b4cd8825(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ClusterLabels, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f5c35d1e3a3d5cbba67b4b06ed0523f7fb641f2bd5fb861ed1ca0910ecf5605(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ClusterReplicationSpecs, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__700bf3a6567a7d87520fe50fa8c17bf8e8d1d58037e267dad9fd37fcc984c99f(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ClusterTags, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64db6507310cc49535192032ef79aca34f62c06082b7996c9493179d6941dec0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c06a22a89a09418ee6b46b8a139f9bb7763b9fb1c38356b42f7388577dbc4608(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59aa7d29979718b4b2ecf6232414400327f659633942b7724b2e45386b08fbce(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6bdde510bfd567d47cb7a1a2957efa04a0f0de6546e3670a761451410f06d83(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10b4feb06b6bd6d3f28fc89c9a5a8b084941a547fc81171f75544ae94262735c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57c3fc02d67f921afa6b1f8a97b13c25eaa049046b5c2a07793b989229f60207(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86ed796f0cb588520cd6e186c26523b3a31121e909a5dcd5f8474fa82ebe236e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d8e8abe391524843551c83ce5ae45348499a4cb4dce528965841b190fc0c8d4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce455b1b3ed68d93edbf93af1cfdf8b6319f70d0762aa0455fd18617b5d6e057(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__810665018bf9edd7b21c7f5d21aea144d132ee5809f4c2ec08b501c14ce25f4d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__839d015cd20e225d16ce9e21d44771d75e3f848bca1f57d3a9a57b31972832cd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2705fd046fb2dccd70d53e142660a7e9c305089fe6e000022b2fed27acfbfcb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71f105a2df9974361266ad742a127e34bd12d1eb43beed4065a3d08ba8838356(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33cd7e1ffe5bc62a488b7c083cd2dd5519670f94c488b16865ffc96a444a5f9b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1709d6e24c2e1fd2ebe95b823d40954e497dda98510a3ceba3192bf6955db6e3(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__703e8324a0124275716a1f7dcdddbc1ab4ad92c912f694bcf5e1733f7aba0ddd(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c9ebf3dab0896ad2349ffd2a29f0b545507b90903d4d9d6e4a8ed4771ae9afe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffd021db11b7e8084419d3f49509a76b8f75c354a446e0e136a8d4eeab5ab523(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__971aae3ca04426b83bd0f6404aa5e08b97ebc24df2a416bdedbefff3cd0f7089(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bdb1b0a533977f12c037278efeab80d9afcde5ae47303a69a87c8261cf4d3bd3(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1230f60c6e2bacf31980f5af933705786600d0a419c229f4e65007ccabb06857(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c00c07cd5cf0faf5d5fdd14bf16a9b49575f5bbf6e4f914d608a313a7b90c7f8(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ceb19f79c49cc3221adcb75a8965acfd0d331dbbea2491aeb455d9d573b8a074(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91bc4fe4365c9e4da2f326b3914a4a9f6d72da9172d05e6357c75f62274deeb5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e1f113d559265c42a48a1e52ac493d7aa2877b79a400bce461552b61bc09153(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8d8f33140e2aae8e2dd44b918b40bd74955963477b332a87432cff44692ed8d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f17ba69c22cbaf739fcabca49d47551deebdcb2c64c858248db8513ae2ebc81(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e06f58753d9de9dcbb19cfec751ac3adbec07f4781375f5c7f2f6626c2b1799(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec9ab4eaae98b3279d5a43f24c7a5620ec4040a103768a488233cc02214e44c1(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a48c8a7eda198dfbae37841348b853d4fa7150e2de96cd5ecec0d14628751fb0(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c95ac87fdb0cc81b48d2d8822ae1e74f1c7be26d4c1d668f105cc78eb35e80c5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__065331b466e1b27c260c6206aedb9472cb98d9aacb65db3a6deccadd579de774(
    *,
    change_stream_options_pre_and_post_images_expire_after_seconds: typing.Optional[jsii.Number] = None,
    custom_openssl_cipher_config_tls12: typing.Optional[typing.Sequence[builtins.str]] = None,
    default_max_time_ms: typing.Optional[jsii.Number] = None,
    default_read_concern: typing.Optional[builtins.str] = None,
    default_write_concern: typing.Optional[builtins.str] = None,
    fail_index_key_too_long: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    javascript_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    minimum_enabled_tls_protocol: typing.Optional[builtins.str] = None,
    no_table_scan: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    oplog_min_retention_hours: typing.Optional[jsii.Number] = None,
    oplog_size_mb: typing.Optional[jsii.Number] = None,
    sample_refresh_interval_bi_connector: typing.Optional[jsii.Number] = None,
    sample_size_bi_connector: typing.Optional[jsii.Number] = None,
    tls_cipher_config_mode: typing.Optional[builtins.str] = None,
    transaction_lifetime_limit_seconds: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__996b89adf682b99f5e0979d471cfa16b8d95ee308097a088356121e8247a1382(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e450f0400deafbeb72c09daa253b68745eaa9f07cfa5f20f4482f1eea5bf949a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2896d3336af63bcba78af96c52ba1e86bac226b9835cf8bcc80220a18f0009d8(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a14d85aaa79685af0f2919085cd2b32dff2e07dec9c88a3b9c28f7211681d8a2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__754287fa100cb7bedfb29777a4fde1d77738b2ab3a1c93ec9deede761591ed5b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__197e2b20b46a799f55867a98f6a4bd215488733dd875286cbeeae11f3bfcd443(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0f3bc8d83e3b509fcec4e527dafe222dfe9f6ec2b97550629b2f735ac132751(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12622488c890619540e24ab1ce32a1fb3a1cf640a19f22e753e6b1d06984941a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__837337c62ddf45b76d1724490b0f8869b2a9a56211daca52d83c54be02af439d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dab30f25c9a42c4873940bd050334afccfeff6668a1090e04a3dbda5b194e2c0(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34a491a4a52d6a086b975d187473fbec2ed8c4f5dfa9836962bc78c4928e4fd4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65f61f7458573d6d03be0ab302d8258f01aa6da18ad99f7f621a818767814dec(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a014340b87f1e348d4b069754bfddecffd8979e1bfab3b32c21188d4605632b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b64d900bb1bcc981fae851fddb7547ec9da5d841965fa423e5d60c0afd674d3c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af51e2d1e888340bba0834b5fd84be9018e1266b301cf917c9c7facfcdc0c9cb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f34c8fbc8ae8790216871f6287e141cbdabdd878068ffdc17b34ae3c0b63433(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb7eb932152aac8a1e720ae3d8f2073cd64e3778aabf50c7a0fcb4b4dcdcbe16(
    value: typing.Optional[ClusterAdvancedConfiguration],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72c2885a36e3c0e5ade0ede10eec426f2776f34c582816cfeaab6163b0986212(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    read_preference: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4917f9a13d8b75832177e7ed501aa1bc7a085be73043abbefa17323caa904f97(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2144c0c7882ee778c36e07efcd1223cf8fa38befec4e9fc2d2bd36b585ca806d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9074ef1c6d3bd9b68c2117877cc162354315884c82a02bc542d3307b8e2b392b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8edd8036e3e5f8a4c267728ce5f09145bc926898f6af45bcb7df3434c638ec02(
    value: typing.Optional[ClusterBiConnectorConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d3acc59c9f3a6397879db2decd266e7b657db28546e04ebaf7f26cdf5ccf06d(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    project_id: builtins.str,
    provider_instance_size_name: builtins.str,
    provider_name: builtins.str,
    accept_data_risks_and_force_replica_set_reconfig: typing.Optional[builtins.str] = None,
    advanced_configuration: typing.Optional[typing.Union[ClusterAdvancedConfiguration, typing.Dict[builtins.str, typing.Any]]] = None,
    auto_scaling_compute_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    auto_scaling_compute_scale_down_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    auto_scaling_disk_gb_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    backing_provider_name: typing.Optional[builtins.str] = None,
    backup_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    bi_connector_config: typing.Optional[typing.Union[ClusterBiConnectorConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    cloud_backup: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cluster_type: typing.Optional[builtins.str] = None,
    disk_size_gb: typing.Optional[jsii.Number] = None,
    encryption_at_rest_provider: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    labels: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ClusterLabels, typing.Dict[builtins.str, typing.Any]]]]] = None,
    mongo_db_major_version: typing.Optional[builtins.str] = None,
    num_shards: typing.Optional[jsii.Number] = None,
    paused: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    pinned_fcv: typing.Optional[typing.Union[ClusterPinnedFcv, typing.Dict[builtins.str, typing.Any]]] = None,
    pit_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    provider_auto_scaling_compute_max_instance_size: typing.Optional[builtins.str] = None,
    provider_auto_scaling_compute_min_instance_size: typing.Optional[builtins.str] = None,
    provider_disk_iops: typing.Optional[jsii.Number] = None,
    provider_disk_type_name: typing.Optional[builtins.str] = None,
    provider_encrypt_ebs_volume: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    provider_region_name: typing.Optional[builtins.str] = None,
    provider_volume_type: typing.Optional[builtins.str] = None,
    redact_client_log_data: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    replication_factor: typing.Optional[jsii.Number] = None,
    replication_specs: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ClusterReplicationSpecs, typing.Dict[builtins.str, typing.Any]]]]] = None,
    retain_backups_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tags: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ClusterTags, typing.Dict[builtins.str, typing.Any]]]]] = None,
    termination_protection_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    timeouts: typing.Optional[typing.Union[ClusterTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
    version_release_system: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e29704e4075ba995514f146ccf8cfd64677d75de7df64f9f330c81c4f9fb750(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1626dcf42933d52a7600e776db6e94517340ab0bf7b3055bc5f9bb74d5fd289(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__235fb7f34b8d85e5ea84b590c4f2ab1cca0ee2613d45cfd4f8332312219ec657(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed7a8d746987656aa1e6ee566087dc289f373a6aef6fa4b3233d1352f5a83427(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a73f35c5773cffdfab39d76949a10d62ac85e3d654e3948f4338b142acd588f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__465ba0b2198b4e05f4ed493110700f19aefb4343146fa0f36f34b6af42aef7ca(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__123a661513edb03486b421f04e709a159e6b0abd6a83b8095291bfc628787064(
    value: typing.Optional[ClusterConnectionStrings],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f822541b1a69368e0910abdf9128309781518aa568460b3d238bf37a4343d0dc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06834d4ca3befad69a0bc4abd800741697d84d7adb66416469ba60d1565e130c(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4aa8bae683f6faea7784793ec7df627a9050fa8b93a0239fa2c0dad6c01e755e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de81d18a2089e9924e3af20cf916029c3332191af6fe7dbbe537ed727403957f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87ee92d67ce7a8ec66ed72b8ea30382183a6152ef5915035d468bc77e9072240(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6c44b0971206e8c9cda90619b94b285018fd732595194f282424b2681d966a4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9744bf2afb6fef3abea0716fbed85b1a1d9cebc4fc51303b1dc340fb37efda98(
    value: typing.Optional[ClusterConnectionStringsPrivateEndpointEndpoints],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a699c27a211a19735b0375c4985d63e7724480518d42efb8b36b4ce09f425e8b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__321844be66a10e6e0e86a41579a7ba6de604d0e32b9d16e8be8477fb166f015c(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afb006779896af2b0fdb597cc793dbc22c406d8593b32d90bea4f19c212060a6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a1b8634b9b0ce680f692b0848d8743e9b351f178d50646f06fde31ab75a7b1a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e1b48a921d04e1712d587c09382a39888058583b70ab5c6923e040e2a9c2f62(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b66c574a2d21a7ee844ad605aa29c32acd97cf82646c6a797aa656db45ee9589(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55a5c82338b295145c256938ba30fe3ac0391ff9cea7af49821ac902294ffb41(
    value: typing.Optional[ClusterConnectionStringsPrivateEndpoint],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c81b4660dc48908502afbba1bf0bcdd95d584ace9074eba15fe848109cfe15ff(
    *,
    key: typing.Optional[builtins.str] = None,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b40ae318e3d0825772c73b6bcfb45c7dcc5f9a322f57d34a8b23bde2a7dc561(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62cce240dda714bb54c3fa50ec3710d30714666e77258d500a7b6fced72f6802(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7bbedb933aa8093241304083b2c9fce0595449b5231a11ea46034dcfef60ddd5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__deae2f01673579e7becf88ec25289d7ef81af400daf69c630cb55ddeece3b269(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__873d557dc7128a2075678478a4f6bb07b2640437c21fa52773f1f9ffdce31024(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4196e829e5b9d941a340078a5db8a9753fd67efcdef6d4828e5424ec7c299c8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ClusterLabels]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e97e8f35418569888820159d46531973b3a9addac011570dbc76f365bad21d3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9851751c4d2422d6b3785503ab810606eb6bbb9f040bc4f0590deccc51443551(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c589f6125e8c1e049b920d10c2892866b9165dfc175b1b36605a7a75498bc20(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a789b222c0530171d5fcd21f06d0222c2a967ea33f4525c6b8dd8225051a797(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ClusterLabels]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eaacf5d618f27b104a9533a5f39f57cccf4f8cb35a6ca6094c2581beeb8b36e4(
    *,
    expiration_date: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e71586e93c1787e1cf8d7dff5dfa703b51f2ee970015b5c6546b67df62dbd865(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__403053d9efbad4d18d970913f259cc8afaa8df4640911be4d1f2d1120d7f31cf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c57d0f795542318a86fbed6519930fbfc50010f3aa4886d2b32209f6775872f(
    value: typing.Optional[ClusterPinnedFcv],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b89d0a827d02331f7c74f8016bcd9b8a4aa4000c061c0b3e2a9a4343bc5d3a51(
    *,
    num_shards: jsii.Number,
    id: typing.Optional[builtins.str] = None,
    regions_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ClusterReplicationSpecsRegionsConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
    zone_name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9179eb50637ea4d5468371301df7d51f74a49e679fac3362bdcae3c8efed2a43(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c1ccdbdb5391f82b3e8d22cddb1f3b1416d22c0173528d369a512dff70026d9(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e226dd89d7071aa0a58a95c25f1dfe927a7a4f69d8e82e6d20196c11a421ba8b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c7374b360cc18bb1a9addf52085618f4dee17ed30e463bd490ee15133b4a1d8(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84200f677db927562f7629bf69592fbc828884887089a0e76c2cb69973881b53(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0b73d9d6c032d15dde47f375b00822b1258a1d116b17b6b465278cd6e4214c2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ClusterReplicationSpecs]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f54249cecfc43b563ec9fe9397f3ee5732db33f1b006ea34e787471e823ac3f7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2935e3e51b59b2a6805fb0820f1c95a31b46e4d040cf0eb299f663bc01bf00c0(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ClusterReplicationSpecsRegionsConfig, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97121ef32b238d1ca4f4b5020693538590d7ff9442dc24104f7cc7f67997fe0f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6fa7666e8a7a83ad62ccdf5cef1b0b4d9778f6ca48a04d5c1259447eef63320(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f57427bbdd27585ae16186e3356ce6c0bb82b6f09ba160a8ffc26cd996286524(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c6c8caa2931819678f7318742973539762941aa6acbbba1864fd9cf15030120(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ClusterReplicationSpecs]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0640b7a5105bc5f1c237e21c6a9152f4b553497c4509be825934ae0de644736(
    *,
    region_name: builtins.str,
    analytics_nodes: typing.Optional[jsii.Number] = None,
    electable_nodes: typing.Optional[jsii.Number] = None,
    priority: typing.Optional[jsii.Number] = None,
    read_only_nodes: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ed1527e6fa5fd9ee1c33d2806f419ecf6b40bb8e7ee10a9cdac060d2f4827ce(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__308c4b29414ce70c488407137933c7b88f2241824a86f1ca3b846b09c251bfd4(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b87ee9775103c12d6dd9ddb4606b877a7c73804cc3053c2e0885d4d7cacdedf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c8e38fdf01f8d9a41d7d527fa168d0a5581a40d822abe39c9767b0dc45ca1aa(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de5fd9e5ec7ec09f3d25cf78e07e09848b462242d0160e05dfdb10ec2856fef9(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fce106c1fb3e4ce43c745e8af4f7e14d07579f4b8946d8ec5bdf4c31b6b596db(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ClusterReplicationSpecsRegionsConfig]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__deefb2888d0ce9bba253d469b630d842134cb467b60c853331c2c4ad9ec74433(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf59fff0341a295f59551126527963ab78b42d7a99d7e23484565476c2486643(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1572c2ec07c15338a9a1e9129fa1dbfd14c45249b9c840d6390830aeecf43527(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18debef176e137db27346863922b95b03d1ae486ef6d5fe9fca36b79b32675ba(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c79b7a68d1b409ddd9af029e41942c60956a19b1d73e3e4ac2ca282cbdee2955(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01a9fe4ac62d56f26f9b94d5f7191d2e344e98286e403b81dbc16fa45969e82a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d374952b16aec64b6d55706daa3a5888918069fbcbd4104975fe5eec508a4915(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ClusterReplicationSpecsRegionsConfig]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d47857d5b423b1f94dce37369ed68b7f79cc437addccabb6ab7f974cd64d9989(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18dd674a5e2ba7be57b3ddca2fa86cf451128d94feb5a8c72ad3ad9a7919555f(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4a917ae3ab1b64ec73c46da722f19d3d2f275cc8999c6e02cc85fa733ee32ec(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3fd279cdb3eb403b640729e0724ee9234e0bc586db23d858ab0728af7ab4a2a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2aa627dd1fe95dbab5b8e756fe0609fc764b7b4fb5ea7cfd6b86f410beb9b972(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79a725b025cdb8ee4ef69451d3a74798818ba98d97139ca20c9dcdb32e921098(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3955f3eb48fcbe0d75042ee6b3e7c54d4310044b1d67b560583af7d039855abc(
    value: typing.Optional[ClusterSnapshotBackupPolicy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2659847b335bbe29006623b729b7cf2425826476f64307b7e2a34c978ad48a41(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__661ecb9ea381fb350b8cbb1471e5ddc5de6ec098d79dbcf92be74afb41f4e5fd(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ce507306b137ca864654998576d77c90b33e26315cca56bd425a89057733fac(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__115f2a4f0e2bc0d51151935eadbe9e8170b7b202954d7093c81fac53f6e93c8d(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__addb8c21fb7282f4fbec82314c3999ab5276f5dd268936e6e88fd095b098516e(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d86c1e5cbeaf3708d3194194176abe58bc4bddba21d7d3727409fb21175ce59(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44ad554e20c6b40d8ba95f883dae0f0039015ea3467e959e8733652ddd946305(
    value: typing.Optional[ClusterSnapshotBackupPolicyPolicies],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6b75dce9401eb716be9371391512014b17d9786f267e031256020aa16e8adee(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4dc654f219d60af47f3e3feaeee92ea3ff530a77911c010e4c5029303a5557b2(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1190cdf30855db116b01fdc71747bdfb6eb4847b136b814b4db71055f94db3ef(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fed26a5d7d8d1f7e814538dd4ed9509bc3e58d58f48a14c2de0e97d511c8f7a7(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24724f9a1c80081664f4b1414bdc55d9842c0fe5e10c1f7dcea382d9ee11fc28(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72a28b24a420979f855abe24a164ac9c2d5067d8bcc8afb9b01a7b6688185f68(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27dc1912d4a387fe064e292ec9fccd32a5ef42cffc9fda85990822ab5c4ae204(
    value: typing.Optional[ClusterSnapshotBackupPolicyPoliciesPolicyItem],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efd8f9f6b5b3cf3d78eb03b545744fa0841eb0e6ae085168f5e3f11ff72dd1ac(
    *,
    key: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d67510ffd5f15989eb0da4bfbaba928fbaacb4026f0e7846d52daa762437a95(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0b4e794b9a0fd9f4119f4383d875480b4632a2c9d29cd749f86ab281d080855(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebb41567076dd12af8b88d39a054641095d82bc85245f6771c8f6a316a7960fc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fb265b18b6aef386a6805d42b8a9430cc315c1d240418b4c2b7c7bd1275f7eb(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b9b63288f5bc976488c04e5341742063d8b7493138ba2472c5b75cab2765cd5(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1641dddee68f79908cec07425900a7e92d7039f057c6bace27f1a333d1e3e2b8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ClusterTags]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c4c68b9f1354a248648235e69c4444936119d60d6d6a374fe079f2ca5561128(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7aee80518752533e36d72e40f5143f483478ece3c7f580bacb8ceaf1bef2095(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bdbc30ff6ec52798014f464b43c8d9466836969684a34f3114bc3ded85926a23(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e4a0e69d72da7fd671fc168fec03e1b6d688b8e7fe1ee49eb3b0834505a6b8c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ClusterTags]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36e444feea44713276a57812646495470437732a2ab970bed6ea9695d342fd32(
    *,
    create: typing.Optional[builtins.str] = None,
    delete: typing.Optional[builtins.str] = None,
    update: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__604f216d83ce933a7fb5ee0e39071f10bd5bb0207f312a42c8363cd64ab0343f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82664bd5fb1d91215ec3f5124995a040ce2a603464c587f72fb67a8d31af0f20(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2033b566bd413d0f0a0fb2d0ce4bbb3332d2a94effbc46eb58112fc6e597ad8d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c4897d5a8eecc948338abdd83ad85be096fa8d9891488615d8c2c0dc2b85d9a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9b1f838ce0e212045a493a2c2f8b83f8390015580ceeec69e3f80029aa15ce2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ClusterTimeouts]],
) -> None:
    """Type checking stubs"""
    pass
