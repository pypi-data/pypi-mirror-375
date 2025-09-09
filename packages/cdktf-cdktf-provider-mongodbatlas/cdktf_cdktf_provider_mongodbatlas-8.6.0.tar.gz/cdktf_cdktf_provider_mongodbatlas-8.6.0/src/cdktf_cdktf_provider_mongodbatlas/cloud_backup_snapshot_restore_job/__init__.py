r'''
# `mongodbatlas_cloud_backup_snapshot_restore_job`

Refer to the Terraform Registry for docs: [`mongodbatlas_cloud_backup_snapshot_restore_job`](https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job).
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


class CloudBackupSnapshotRestoreJob(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cloudBackupSnapshotRestoreJob.CloudBackupSnapshotRestoreJob",
):
    '''Represents a {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job mongodbatlas_cloud_backup_snapshot_restore_job}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        cluster_name: builtins.str,
        project_id: builtins.str,
        delivery_type_config: typing.Optional[typing.Union["CloudBackupSnapshotRestoreJobDeliveryTypeConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        snapshot_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job mongodbatlas_cloud_backup_snapshot_restore_job} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#cluster_name CloudBackupSnapshotRestoreJob#cluster_name}.
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#project_id CloudBackupSnapshotRestoreJob#project_id}.
        :param delivery_type_config: delivery_type_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#delivery_type_config CloudBackupSnapshotRestoreJob#delivery_type_config}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#id CloudBackupSnapshotRestoreJob#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param snapshot_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#snapshot_id CloudBackupSnapshotRestoreJob#snapshot_id}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5b8685f8b7e4c21b3b96778919792d5a13548424ae6a999a99e40cfce45b012)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = CloudBackupSnapshotRestoreJobConfig(
            cluster_name=cluster_name,
            project_id=project_id,
            delivery_type_config=delivery_type_config,
            id=id,
            snapshot_id=snapshot_id,
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
        '''Generates CDKTF code for importing a CloudBackupSnapshotRestoreJob resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the CloudBackupSnapshotRestoreJob to import.
        :param import_from_id: The id of the existing CloudBackupSnapshotRestoreJob that should be imported. Refer to the {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the CloudBackupSnapshotRestoreJob to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1864d4c3ba1f53a063815b361c55166a753cbf94e6bf28427b05c9df839a728d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putDeliveryTypeConfig")
    def put_delivery_type_config(
        self,
        *,
        automated: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        download: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        oplog_inc: typing.Optional[jsii.Number] = None,
        oplog_ts: typing.Optional[jsii.Number] = None,
        point_in_time: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        point_in_time_utc_seconds: typing.Optional[jsii.Number] = None,
        target_cluster_name: typing.Optional[builtins.str] = None,
        target_project_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param automated: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#automated CloudBackupSnapshotRestoreJob#automated}.
        :param download: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#download CloudBackupSnapshotRestoreJob#download}.
        :param oplog_inc: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#oplog_inc CloudBackupSnapshotRestoreJob#oplog_inc}.
        :param oplog_ts: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#oplog_ts CloudBackupSnapshotRestoreJob#oplog_ts}.
        :param point_in_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#point_in_time CloudBackupSnapshotRestoreJob#point_in_time}.
        :param point_in_time_utc_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#point_in_time_utc_seconds CloudBackupSnapshotRestoreJob#point_in_time_utc_seconds}.
        :param target_cluster_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#target_cluster_name CloudBackupSnapshotRestoreJob#target_cluster_name}.
        :param target_project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#target_project_id CloudBackupSnapshotRestoreJob#target_project_id}.
        '''
        value = CloudBackupSnapshotRestoreJobDeliveryTypeConfig(
            automated=automated,
            download=download,
            oplog_inc=oplog_inc,
            oplog_ts=oplog_ts,
            point_in_time=point_in_time,
            point_in_time_utc_seconds=point_in_time_utc_seconds,
            target_cluster_name=target_cluster_name,
            target_project_id=target_project_id,
        )

        return typing.cast(None, jsii.invoke(self, "putDeliveryTypeConfig", [value]))

    @jsii.member(jsii_name="resetDeliveryTypeConfig")
    def reset_delivery_type_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeliveryTypeConfig", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetSnapshotId")
    def reset_snapshot_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSnapshotId", []))

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
    @jsii.member(jsii_name="cancelled")
    def cancelled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "cancelled"))

    @builtins.property
    @jsii.member(jsii_name="deliveryTypeConfig")
    def delivery_type_config(
        self,
    ) -> "CloudBackupSnapshotRestoreJobDeliveryTypeConfigOutputReference":
        return typing.cast("CloudBackupSnapshotRestoreJobDeliveryTypeConfigOutputReference", jsii.get(self, "deliveryTypeConfig"))

    @builtins.property
    @jsii.member(jsii_name="deliveryUrl")
    def delivery_url(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "deliveryUrl"))

    @builtins.property
    @jsii.member(jsii_name="expired")
    def expired(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "expired"))

    @builtins.property
    @jsii.member(jsii_name="expiresAt")
    def expires_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "expiresAt"))

    @builtins.property
    @jsii.member(jsii_name="failed")
    def failed(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "failed"))

    @builtins.property
    @jsii.member(jsii_name="finishedAt")
    def finished_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "finishedAt"))

    @builtins.property
    @jsii.member(jsii_name="snapshotRestoreJobId")
    def snapshot_restore_job_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snapshotRestoreJobId"))

    @builtins.property
    @jsii.member(jsii_name="timestamp")
    def timestamp(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timestamp"))

    @builtins.property
    @jsii.member(jsii_name="clusterNameInput")
    def cluster_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterNameInput"))

    @builtins.property
    @jsii.member(jsii_name="deliveryTypeConfigInput")
    def delivery_type_config_input(
        self,
    ) -> typing.Optional["CloudBackupSnapshotRestoreJobDeliveryTypeConfig"]:
        return typing.cast(typing.Optional["CloudBackupSnapshotRestoreJobDeliveryTypeConfig"], jsii.get(self, "deliveryTypeConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="snapshotIdInput")
    def snapshot_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "snapshotIdInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterName"))

    @cluster_name.setter
    def cluster_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2afd3a07c45d3c46ccf61d2c2a8ebd7d98642a1b349dac1277e69296f802bd05)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56a547f71fc5aef2331cadbd6c11a0ece86c7ed5c2784753490b45ebe1a331d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d25dd4be7ba5174baab0c37c57782c88848b817dfb95650fe243e6ddee99d33)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="snapshotId")
    def snapshot_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "snapshotId"))

    @snapshot_id.setter
    def snapshot_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01659bf74119379ea56496436e30048824116e3561f2db7ad738807d18096750)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "snapshotId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.cloudBackupSnapshotRestoreJob.CloudBackupSnapshotRestoreJobConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "cluster_name": "clusterName",
        "project_id": "projectId",
        "delivery_type_config": "deliveryTypeConfig",
        "id": "id",
        "snapshot_id": "snapshotId",
    },
)
class CloudBackupSnapshotRestoreJobConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        cluster_name: builtins.str,
        project_id: builtins.str,
        delivery_type_config: typing.Optional[typing.Union["CloudBackupSnapshotRestoreJobDeliveryTypeConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        snapshot_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param cluster_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#cluster_name CloudBackupSnapshotRestoreJob#cluster_name}.
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#project_id CloudBackupSnapshotRestoreJob#project_id}.
        :param delivery_type_config: delivery_type_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#delivery_type_config CloudBackupSnapshotRestoreJob#delivery_type_config}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#id CloudBackupSnapshotRestoreJob#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param snapshot_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#snapshot_id CloudBackupSnapshotRestoreJob#snapshot_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(delivery_type_config, dict):
            delivery_type_config = CloudBackupSnapshotRestoreJobDeliveryTypeConfig(**delivery_type_config)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a082f9fd14a15275186cce94255d825e860ac92e4c6fdd0741936823a6afdd8)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument cluster_name", value=cluster_name, expected_type=type_hints["cluster_name"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument delivery_type_config", value=delivery_type_config, expected_type=type_hints["delivery_type_config"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument snapshot_id", value=snapshot_id, expected_type=type_hints["snapshot_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cluster_name": cluster_name,
            "project_id": project_id,
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
        if delivery_type_config is not None:
            self._values["delivery_type_config"] = delivery_type_config
        if id is not None:
            self._values["id"] = id
        if snapshot_id is not None:
            self._values["snapshot_id"] = snapshot_id

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
    def cluster_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#cluster_name CloudBackupSnapshotRestoreJob#cluster_name}.'''
        result = self._values.get("cluster_name")
        assert result is not None, "Required property 'cluster_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def project_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#project_id CloudBackupSnapshotRestoreJob#project_id}.'''
        result = self._values.get("project_id")
        assert result is not None, "Required property 'project_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def delivery_type_config(
        self,
    ) -> typing.Optional["CloudBackupSnapshotRestoreJobDeliveryTypeConfig"]:
        '''delivery_type_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#delivery_type_config CloudBackupSnapshotRestoreJob#delivery_type_config}
        '''
        result = self._values.get("delivery_type_config")
        return typing.cast(typing.Optional["CloudBackupSnapshotRestoreJobDeliveryTypeConfig"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#id CloudBackupSnapshotRestoreJob#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def snapshot_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#snapshot_id CloudBackupSnapshotRestoreJob#snapshot_id}.'''
        result = self._values.get("snapshot_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudBackupSnapshotRestoreJobConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.cloudBackupSnapshotRestoreJob.CloudBackupSnapshotRestoreJobDeliveryTypeConfig",
    jsii_struct_bases=[],
    name_mapping={
        "automated": "automated",
        "download": "download",
        "oplog_inc": "oplogInc",
        "oplog_ts": "oplogTs",
        "point_in_time": "pointInTime",
        "point_in_time_utc_seconds": "pointInTimeUtcSeconds",
        "target_cluster_name": "targetClusterName",
        "target_project_id": "targetProjectId",
    },
)
class CloudBackupSnapshotRestoreJobDeliveryTypeConfig:
    def __init__(
        self,
        *,
        automated: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        download: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        oplog_inc: typing.Optional[jsii.Number] = None,
        oplog_ts: typing.Optional[jsii.Number] = None,
        point_in_time: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        point_in_time_utc_seconds: typing.Optional[jsii.Number] = None,
        target_cluster_name: typing.Optional[builtins.str] = None,
        target_project_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param automated: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#automated CloudBackupSnapshotRestoreJob#automated}.
        :param download: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#download CloudBackupSnapshotRestoreJob#download}.
        :param oplog_inc: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#oplog_inc CloudBackupSnapshotRestoreJob#oplog_inc}.
        :param oplog_ts: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#oplog_ts CloudBackupSnapshotRestoreJob#oplog_ts}.
        :param point_in_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#point_in_time CloudBackupSnapshotRestoreJob#point_in_time}.
        :param point_in_time_utc_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#point_in_time_utc_seconds CloudBackupSnapshotRestoreJob#point_in_time_utc_seconds}.
        :param target_cluster_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#target_cluster_name CloudBackupSnapshotRestoreJob#target_cluster_name}.
        :param target_project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#target_project_id CloudBackupSnapshotRestoreJob#target_project_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ceedfef0407459371eebf9e7a43d915e20475e1c5cf85f27dca3ea2a8bb16d0)
            check_type(argname="argument automated", value=automated, expected_type=type_hints["automated"])
            check_type(argname="argument download", value=download, expected_type=type_hints["download"])
            check_type(argname="argument oplog_inc", value=oplog_inc, expected_type=type_hints["oplog_inc"])
            check_type(argname="argument oplog_ts", value=oplog_ts, expected_type=type_hints["oplog_ts"])
            check_type(argname="argument point_in_time", value=point_in_time, expected_type=type_hints["point_in_time"])
            check_type(argname="argument point_in_time_utc_seconds", value=point_in_time_utc_seconds, expected_type=type_hints["point_in_time_utc_seconds"])
            check_type(argname="argument target_cluster_name", value=target_cluster_name, expected_type=type_hints["target_cluster_name"])
            check_type(argname="argument target_project_id", value=target_project_id, expected_type=type_hints["target_project_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if automated is not None:
            self._values["automated"] = automated
        if download is not None:
            self._values["download"] = download
        if oplog_inc is not None:
            self._values["oplog_inc"] = oplog_inc
        if oplog_ts is not None:
            self._values["oplog_ts"] = oplog_ts
        if point_in_time is not None:
            self._values["point_in_time"] = point_in_time
        if point_in_time_utc_seconds is not None:
            self._values["point_in_time_utc_seconds"] = point_in_time_utc_seconds
        if target_cluster_name is not None:
            self._values["target_cluster_name"] = target_cluster_name
        if target_project_id is not None:
            self._values["target_project_id"] = target_project_id

    @builtins.property
    def automated(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#automated CloudBackupSnapshotRestoreJob#automated}.'''
        result = self._values.get("automated")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def download(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#download CloudBackupSnapshotRestoreJob#download}.'''
        result = self._values.get("download")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def oplog_inc(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#oplog_inc CloudBackupSnapshotRestoreJob#oplog_inc}.'''
        result = self._values.get("oplog_inc")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def oplog_ts(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#oplog_ts CloudBackupSnapshotRestoreJob#oplog_ts}.'''
        result = self._values.get("oplog_ts")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def point_in_time(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#point_in_time CloudBackupSnapshotRestoreJob#point_in_time}.'''
        result = self._values.get("point_in_time")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def point_in_time_utc_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#point_in_time_utc_seconds CloudBackupSnapshotRestoreJob#point_in_time_utc_seconds}.'''
        result = self._values.get("point_in_time_utc_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def target_cluster_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#target_cluster_name CloudBackupSnapshotRestoreJob#target_cluster_name}.'''
        result = self._values.get("target_cluster_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def target_project_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_snapshot_restore_job#target_project_id CloudBackupSnapshotRestoreJob#target_project_id}.'''
        result = self._values.get("target_project_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudBackupSnapshotRestoreJobDeliveryTypeConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudBackupSnapshotRestoreJobDeliveryTypeConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cloudBackupSnapshotRestoreJob.CloudBackupSnapshotRestoreJobDeliveryTypeConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0e935eb3d414d62208ee35bed467d74266e05527f37ab3ed741aeab1ffe1b431)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAutomated")
    def reset_automated(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutomated", []))

    @jsii.member(jsii_name="resetDownload")
    def reset_download(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDownload", []))

    @jsii.member(jsii_name="resetOplogInc")
    def reset_oplog_inc(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOplogInc", []))

    @jsii.member(jsii_name="resetOplogTs")
    def reset_oplog_ts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOplogTs", []))

    @jsii.member(jsii_name="resetPointInTime")
    def reset_point_in_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPointInTime", []))

    @jsii.member(jsii_name="resetPointInTimeUtcSeconds")
    def reset_point_in_time_utc_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPointInTimeUtcSeconds", []))

    @jsii.member(jsii_name="resetTargetClusterName")
    def reset_target_cluster_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetClusterName", []))

    @jsii.member(jsii_name="resetTargetProjectId")
    def reset_target_project_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetProjectId", []))

    @builtins.property
    @jsii.member(jsii_name="automatedInput")
    def automated_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "automatedInput"))

    @builtins.property
    @jsii.member(jsii_name="downloadInput")
    def download_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "downloadInput"))

    @builtins.property
    @jsii.member(jsii_name="oplogIncInput")
    def oplog_inc_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "oplogIncInput"))

    @builtins.property
    @jsii.member(jsii_name="oplogTsInput")
    def oplog_ts_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "oplogTsInput"))

    @builtins.property
    @jsii.member(jsii_name="pointInTimeInput")
    def point_in_time_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "pointInTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="pointInTimeUtcSecondsInput")
    def point_in_time_utc_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "pointInTimeUtcSecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="targetClusterNameInput")
    def target_cluster_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetClusterNameInput"))

    @builtins.property
    @jsii.member(jsii_name="targetProjectIdInput")
    def target_project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetProjectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="automated")
    def automated(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "automated"))

    @automated.setter
    def automated(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40b742d8b6b25d5cc11ac44468c1fe5a91ad4b345b2e185ded94877b771579c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "automated", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="download")
    def download(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "download"))

    @download.setter
    def download(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a36e8f9d10fcd36f684e93630363389e44accf12e0bf11c13eb792f1c099e67f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "download", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oplogInc")
    def oplog_inc(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "oplogInc"))

    @oplog_inc.setter
    def oplog_inc(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__134a5c0919d1555a58613e6c00d70ed9b86b993d820f1142b1148273090aa892)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oplogInc", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="oplogTs")
    def oplog_ts(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "oplogTs"))

    @oplog_ts.setter
    def oplog_ts(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94639b34a1969f7ce85df4c5e38b5e230779fb23d01905d7d577fe33c0e05072)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "oplogTs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pointInTime")
    def point_in_time(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "pointInTime"))

    @point_in_time.setter
    def point_in_time(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3f330f88c54e985721ff2fd98d688cbcdeaa3c9c14eae4081592095f126826c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pointInTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pointInTimeUtcSeconds")
    def point_in_time_utc_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "pointInTimeUtcSeconds"))

    @point_in_time_utc_seconds.setter
    def point_in_time_utc_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e912a5bb455b884a26c9f2184b4f738cdfcf6151de717fedd43e187179ae18ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pointInTimeUtcSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="targetClusterName")
    def target_cluster_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetClusterName"))

    @target_cluster_name.setter
    def target_cluster_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f2c2cdbccd38b04245f95b99c287a46e625ef0332651c54cee6097918d19e64)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetClusterName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="targetProjectId")
    def target_project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetProjectId"))

    @target_project_id.setter
    def target_project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2cc68990f53a8ff0e9ef4765fcc8a29bfde8a578f17e4ea5e93a1493c8942d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetProjectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudBackupSnapshotRestoreJobDeliveryTypeConfig]:
        return typing.cast(typing.Optional[CloudBackupSnapshotRestoreJobDeliveryTypeConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudBackupSnapshotRestoreJobDeliveryTypeConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0421c04482a98bd9c9ed06d7c7dacf8813705e275ed599841dcb676c4b3a0c04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "CloudBackupSnapshotRestoreJob",
    "CloudBackupSnapshotRestoreJobConfig",
    "CloudBackupSnapshotRestoreJobDeliveryTypeConfig",
    "CloudBackupSnapshotRestoreJobDeliveryTypeConfigOutputReference",
]

publication.publish()

def _typecheckingstub__f5b8685f8b7e4c21b3b96778919792d5a13548424ae6a999a99e40cfce45b012(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    cluster_name: builtins.str,
    project_id: builtins.str,
    delivery_type_config: typing.Optional[typing.Union[CloudBackupSnapshotRestoreJobDeliveryTypeConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    snapshot_id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__1864d4c3ba1f53a063815b361c55166a753cbf94e6bf28427b05c9df839a728d(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2afd3a07c45d3c46ccf61d2c2a8ebd7d98642a1b349dac1277e69296f802bd05(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56a547f71fc5aef2331cadbd6c11a0ece86c7ed5c2784753490b45ebe1a331d2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d25dd4be7ba5174baab0c37c57782c88848b817dfb95650fe243e6ddee99d33(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01659bf74119379ea56496436e30048824116e3561f2db7ad738807d18096750(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a082f9fd14a15275186cce94255d825e860ac92e4c6fdd0741936823a6afdd8(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    cluster_name: builtins.str,
    project_id: builtins.str,
    delivery_type_config: typing.Optional[typing.Union[CloudBackupSnapshotRestoreJobDeliveryTypeConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    snapshot_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ceedfef0407459371eebf9e7a43d915e20475e1c5cf85f27dca3ea2a8bb16d0(
    *,
    automated: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    download: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    oplog_inc: typing.Optional[jsii.Number] = None,
    oplog_ts: typing.Optional[jsii.Number] = None,
    point_in_time: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    point_in_time_utc_seconds: typing.Optional[jsii.Number] = None,
    target_cluster_name: typing.Optional[builtins.str] = None,
    target_project_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e935eb3d414d62208ee35bed467d74266e05527f37ab3ed741aeab1ffe1b431(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40b742d8b6b25d5cc11ac44468c1fe5a91ad4b345b2e185ded94877b771579c7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a36e8f9d10fcd36f684e93630363389e44accf12e0bf11c13eb792f1c099e67f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__134a5c0919d1555a58613e6c00d70ed9b86b993d820f1142b1148273090aa892(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94639b34a1969f7ce85df4c5e38b5e230779fb23d01905d7d577fe33c0e05072(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f330f88c54e985721ff2fd98d688cbcdeaa3c9c14eae4081592095f126826c6(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e912a5bb455b884a26c9f2184b4f738cdfcf6151de717fedd43e187179ae18ad(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f2c2cdbccd38b04245f95b99c287a46e625ef0332651c54cee6097918d19e64(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2cc68990f53a8ff0e9ef4765fcc8a29bfde8a578f17e4ea5e93a1493c8942d4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0421c04482a98bd9c9ed06d7c7dacf8813705e275ed599841dcb676c4b3a0c04(
    value: typing.Optional[CloudBackupSnapshotRestoreJobDeliveryTypeConfig],
) -> None:
    """Type checking stubs"""
    pass
