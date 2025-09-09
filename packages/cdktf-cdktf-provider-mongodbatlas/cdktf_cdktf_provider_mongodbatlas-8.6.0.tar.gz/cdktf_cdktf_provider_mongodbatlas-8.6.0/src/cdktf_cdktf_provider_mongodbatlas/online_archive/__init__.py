r'''
# `mongodbatlas_online_archive`

Refer to the Terraform Registry for docs: [`mongodbatlas_online_archive`](https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive).
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


class OnlineArchive(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.onlineArchive.OnlineArchive",
):
    '''Represents a {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive mongodbatlas_online_archive}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        cluster_name: builtins.str,
        coll_name: builtins.str,
        criteria: typing.Union["OnlineArchiveCriteria", typing.Dict[builtins.str, typing.Any]],
        db_name: builtins.str,
        project_id: builtins.str,
        collection_type: typing.Optional[builtins.str] = None,
        data_expiration_rule: typing.Optional[typing.Union["OnlineArchiveDataExpirationRule", typing.Dict[builtins.str, typing.Any]]] = None,
        data_process_region: typing.Optional[typing.Union["OnlineArchiveDataProcessRegion", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        partition_fields: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OnlineArchivePartitionFields", typing.Dict[builtins.str, typing.Any]]]]] = None,
        paused: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        schedule: typing.Optional[typing.Union["OnlineArchiveSchedule", typing.Dict[builtins.str, typing.Any]]] = None,
        sync_creation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive mongodbatlas_online_archive} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#cluster_name OnlineArchive#cluster_name}.
        :param coll_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#coll_name OnlineArchive#coll_name}.
        :param criteria: criteria block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#criteria OnlineArchive#criteria}
        :param db_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#db_name OnlineArchive#db_name}.
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#project_id OnlineArchive#project_id}.
        :param collection_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#collection_type OnlineArchive#collection_type}.
        :param data_expiration_rule: data_expiration_rule block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#data_expiration_rule OnlineArchive#data_expiration_rule}
        :param data_process_region: data_process_region block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#data_process_region OnlineArchive#data_process_region}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#id OnlineArchive#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param partition_fields: partition_fields block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#partition_fields OnlineArchive#partition_fields}
        :param paused: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#paused OnlineArchive#paused}.
        :param schedule: schedule block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#schedule OnlineArchive#schedule}
        :param sync_creation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#sync_creation OnlineArchive#sync_creation}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1dd8d1ca11c164ab0d5dc5e06d9e71c8db190f43b7a833f46b312e4686fcae23)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = OnlineArchiveConfig(
            cluster_name=cluster_name,
            coll_name=coll_name,
            criteria=criteria,
            db_name=db_name,
            project_id=project_id,
            collection_type=collection_type,
            data_expiration_rule=data_expiration_rule,
            data_process_region=data_process_region,
            id=id,
            partition_fields=partition_fields,
            paused=paused,
            schedule=schedule,
            sync_creation=sync_creation,
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
        '''Generates CDKTF code for importing a OnlineArchive resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the OnlineArchive to import.
        :param import_from_id: The id of the existing OnlineArchive that should be imported. Refer to the {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the OnlineArchive to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ee2e10b777488376f44b03e5c7d982a79480e79d0ab3b869cfc0f96883a34eb)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putCriteria")
    def put_criteria(
        self,
        *,
        type: builtins.str,
        date_field: typing.Optional[builtins.str] = None,
        date_format: typing.Optional[builtins.str] = None,
        expire_after_days: typing.Optional[jsii.Number] = None,
        query: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#type OnlineArchive#type}.
        :param date_field: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#date_field OnlineArchive#date_field}.
        :param date_format: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#date_format OnlineArchive#date_format}.
        :param expire_after_days: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#expire_after_days OnlineArchive#expire_after_days}.
        :param query: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#query OnlineArchive#query}.
        '''
        value = OnlineArchiveCriteria(
            type=type,
            date_field=date_field,
            date_format=date_format,
            expire_after_days=expire_after_days,
            query=query,
        )

        return typing.cast(None, jsii.invoke(self, "putCriteria", [value]))

    @jsii.member(jsii_name="putDataExpirationRule")
    def put_data_expiration_rule(self, *, expire_after_days: jsii.Number) -> None:
        '''
        :param expire_after_days: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#expire_after_days OnlineArchive#expire_after_days}.
        '''
        value = OnlineArchiveDataExpirationRule(expire_after_days=expire_after_days)

        return typing.cast(None, jsii.invoke(self, "putDataExpirationRule", [value]))

    @jsii.member(jsii_name="putDataProcessRegion")
    def put_data_process_region(
        self,
        *,
        cloud_provider: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param cloud_provider: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#cloud_provider OnlineArchive#cloud_provider}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#region OnlineArchive#region}.
        '''
        value = OnlineArchiveDataProcessRegion(
            cloud_provider=cloud_provider, region=region
        )

        return typing.cast(None, jsii.invoke(self, "putDataProcessRegion", [value]))

    @jsii.member(jsii_name="putPartitionFields")
    def put_partition_fields(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OnlineArchivePartitionFields", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76e5606784d6acac975631ea2af1161f22ad81d1d668f072c7130ebae2a4b904)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putPartitionFields", [value]))

    @jsii.member(jsii_name="putSchedule")
    def put_schedule(
        self,
        *,
        type: builtins.str,
        day_of_month: typing.Optional[jsii.Number] = None,
        day_of_week: typing.Optional[jsii.Number] = None,
        end_hour: typing.Optional[jsii.Number] = None,
        end_minute: typing.Optional[jsii.Number] = None,
        start_hour: typing.Optional[jsii.Number] = None,
        start_minute: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#type OnlineArchive#type}.
        :param day_of_month: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#day_of_month OnlineArchive#day_of_month}.
        :param day_of_week: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#day_of_week OnlineArchive#day_of_week}.
        :param end_hour: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#end_hour OnlineArchive#end_hour}.
        :param end_minute: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#end_minute OnlineArchive#end_minute}.
        :param start_hour: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#start_hour OnlineArchive#start_hour}.
        :param start_minute: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#start_minute OnlineArchive#start_minute}.
        '''
        value = OnlineArchiveSchedule(
            type=type,
            day_of_month=day_of_month,
            day_of_week=day_of_week,
            end_hour=end_hour,
            end_minute=end_minute,
            start_hour=start_hour,
            start_minute=start_minute,
        )

        return typing.cast(None, jsii.invoke(self, "putSchedule", [value]))

    @jsii.member(jsii_name="resetCollectionType")
    def reset_collection_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCollectionType", []))

    @jsii.member(jsii_name="resetDataExpirationRule")
    def reset_data_expiration_rule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataExpirationRule", []))

    @jsii.member(jsii_name="resetDataProcessRegion")
    def reset_data_process_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataProcessRegion", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetPartitionFields")
    def reset_partition_fields(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPartitionFields", []))

    @jsii.member(jsii_name="resetPaused")
    def reset_paused(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPaused", []))

    @jsii.member(jsii_name="resetSchedule")
    def reset_schedule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSchedule", []))

    @jsii.member(jsii_name="resetSyncCreation")
    def reset_sync_creation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSyncCreation", []))

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
    @jsii.member(jsii_name="archiveId")
    def archive_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "archiveId"))

    @builtins.property
    @jsii.member(jsii_name="criteria")
    def criteria(self) -> "OnlineArchiveCriteriaOutputReference":
        return typing.cast("OnlineArchiveCriteriaOutputReference", jsii.get(self, "criteria"))

    @builtins.property
    @jsii.member(jsii_name="dataExpirationRule")
    def data_expiration_rule(self) -> "OnlineArchiveDataExpirationRuleOutputReference":
        return typing.cast("OnlineArchiveDataExpirationRuleOutputReference", jsii.get(self, "dataExpirationRule"))

    @builtins.property
    @jsii.member(jsii_name="dataProcessRegion")
    def data_process_region(self) -> "OnlineArchiveDataProcessRegionOutputReference":
        return typing.cast("OnlineArchiveDataProcessRegionOutputReference", jsii.get(self, "dataProcessRegion"))

    @builtins.property
    @jsii.member(jsii_name="partitionFields")
    def partition_fields(self) -> "OnlineArchivePartitionFieldsList":
        return typing.cast("OnlineArchivePartitionFieldsList", jsii.get(self, "partitionFields"))

    @builtins.property
    @jsii.member(jsii_name="schedule")
    def schedule(self) -> "OnlineArchiveScheduleOutputReference":
        return typing.cast("OnlineArchiveScheduleOutputReference", jsii.get(self, "schedule"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="clusterNameInput")
    def cluster_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterNameInput"))

    @builtins.property
    @jsii.member(jsii_name="collectionTypeInput")
    def collection_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "collectionTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="collNameInput")
    def coll_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "collNameInput"))

    @builtins.property
    @jsii.member(jsii_name="criteriaInput")
    def criteria_input(self) -> typing.Optional["OnlineArchiveCriteria"]:
        return typing.cast(typing.Optional["OnlineArchiveCriteria"], jsii.get(self, "criteriaInput"))

    @builtins.property
    @jsii.member(jsii_name="dataExpirationRuleInput")
    def data_expiration_rule_input(
        self,
    ) -> typing.Optional["OnlineArchiveDataExpirationRule"]:
        return typing.cast(typing.Optional["OnlineArchiveDataExpirationRule"], jsii.get(self, "dataExpirationRuleInput"))

    @builtins.property
    @jsii.member(jsii_name="dataProcessRegionInput")
    def data_process_region_input(
        self,
    ) -> typing.Optional["OnlineArchiveDataProcessRegion"]:
        return typing.cast(typing.Optional["OnlineArchiveDataProcessRegion"], jsii.get(self, "dataProcessRegionInput"))

    @builtins.property
    @jsii.member(jsii_name="dbNameInput")
    def db_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbNameInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="partitionFieldsInput")
    def partition_fields_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OnlineArchivePartitionFields"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OnlineArchivePartitionFields"]]], jsii.get(self, "partitionFieldsInput"))

    @builtins.property
    @jsii.member(jsii_name="pausedInput")
    def paused_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "pausedInput"))

    @builtins.property
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="scheduleInput")
    def schedule_input(self) -> typing.Optional["OnlineArchiveSchedule"]:
        return typing.cast(typing.Optional["OnlineArchiveSchedule"], jsii.get(self, "scheduleInput"))

    @builtins.property
    @jsii.member(jsii_name="syncCreationInput")
    def sync_creation_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "syncCreationInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterName"))

    @cluster_name.setter
    def cluster_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de8ae41e4f876927ef6981d0b7733937af86ae48eef04c7e84176df670d4d407)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="collectionType")
    def collection_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "collectionType"))

    @collection_type.setter
    def collection_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a4379a10167c092c00fdc988318e28f67ce2718a6a8ee77cd54add0ccfef334)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "collectionType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="collName")
    def coll_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "collName"))

    @coll_name.setter
    def coll_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d037e4474bfd5c2e1333006f2df70dcdc006a9730cb12cdd7f93e621179f0d1f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "collName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dbName")
    def db_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dbName"))

    @db_name.setter
    def db_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__980c51108ac5c6046b9e7ac7aa2d3b50ff4e2a59f4017e3312afc6855606730c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dbName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21ab4336f292487179519348dcc4aec8d86a3848384ded4433c07070dbce697d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__13b151595b2c0db02b6ba933ac0f0af01ed2cae3b3e6a98c2c0b0cf315423aee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "paused", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f015421bc7c023003d29dff1bf83dd6df11009d9f219d612275aa1c7cfd6c69a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="syncCreation")
    def sync_creation(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "syncCreation"))

    @sync_creation.setter
    def sync_creation(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6764ebedc8392745886f1bdf0cd6cf1c67bc0c1261d3de37bf3dcc4e6ac0163c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "syncCreation", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.onlineArchive.OnlineArchiveConfig",
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
        "coll_name": "collName",
        "criteria": "criteria",
        "db_name": "dbName",
        "project_id": "projectId",
        "collection_type": "collectionType",
        "data_expiration_rule": "dataExpirationRule",
        "data_process_region": "dataProcessRegion",
        "id": "id",
        "partition_fields": "partitionFields",
        "paused": "paused",
        "schedule": "schedule",
        "sync_creation": "syncCreation",
    },
)
class OnlineArchiveConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        coll_name: builtins.str,
        criteria: typing.Union["OnlineArchiveCriteria", typing.Dict[builtins.str, typing.Any]],
        db_name: builtins.str,
        project_id: builtins.str,
        collection_type: typing.Optional[builtins.str] = None,
        data_expiration_rule: typing.Optional[typing.Union["OnlineArchiveDataExpirationRule", typing.Dict[builtins.str, typing.Any]]] = None,
        data_process_region: typing.Optional[typing.Union["OnlineArchiveDataProcessRegion", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        partition_fields: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["OnlineArchivePartitionFields", typing.Dict[builtins.str, typing.Any]]]]] = None,
        paused: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        schedule: typing.Optional[typing.Union["OnlineArchiveSchedule", typing.Dict[builtins.str, typing.Any]]] = None,
        sync_creation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param cluster_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#cluster_name OnlineArchive#cluster_name}.
        :param coll_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#coll_name OnlineArchive#coll_name}.
        :param criteria: criteria block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#criteria OnlineArchive#criteria}
        :param db_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#db_name OnlineArchive#db_name}.
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#project_id OnlineArchive#project_id}.
        :param collection_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#collection_type OnlineArchive#collection_type}.
        :param data_expiration_rule: data_expiration_rule block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#data_expiration_rule OnlineArchive#data_expiration_rule}
        :param data_process_region: data_process_region block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#data_process_region OnlineArchive#data_process_region}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#id OnlineArchive#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param partition_fields: partition_fields block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#partition_fields OnlineArchive#partition_fields}
        :param paused: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#paused OnlineArchive#paused}.
        :param schedule: schedule block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#schedule OnlineArchive#schedule}
        :param sync_creation: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#sync_creation OnlineArchive#sync_creation}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(criteria, dict):
            criteria = OnlineArchiveCriteria(**criteria)
        if isinstance(data_expiration_rule, dict):
            data_expiration_rule = OnlineArchiveDataExpirationRule(**data_expiration_rule)
        if isinstance(data_process_region, dict):
            data_process_region = OnlineArchiveDataProcessRegion(**data_process_region)
        if isinstance(schedule, dict):
            schedule = OnlineArchiveSchedule(**schedule)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04a399df69abc4c0e11be19164b166682ee8e362c29595e11f7e4a9e0c6c2ad7)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument cluster_name", value=cluster_name, expected_type=type_hints["cluster_name"])
            check_type(argname="argument coll_name", value=coll_name, expected_type=type_hints["coll_name"])
            check_type(argname="argument criteria", value=criteria, expected_type=type_hints["criteria"])
            check_type(argname="argument db_name", value=db_name, expected_type=type_hints["db_name"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument collection_type", value=collection_type, expected_type=type_hints["collection_type"])
            check_type(argname="argument data_expiration_rule", value=data_expiration_rule, expected_type=type_hints["data_expiration_rule"])
            check_type(argname="argument data_process_region", value=data_process_region, expected_type=type_hints["data_process_region"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument partition_fields", value=partition_fields, expected_type=type_hints["partition_fields"])
            check_type(argname="argument paused", value=paused, expected_type=type_hints["paused"])
            check_type(argname="argument schedule", value=schedule, expected_type=type_hints["schedule"])
            check_type(argname="argument sync_creation", value=sync_creation, expected_type=type_hints["sync_creation"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cluster_name": cluster_name,
            "coll_name": coll_name,
            "criteria": criteria,
            "db_name": db_name,
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
        if collection_type is not None:
            self._values["collection_type"] = collection_type
        if data_expiration_rule is not None:
            self._values["data_expiration_rule"] = data_expiration_rule
        if data_process_region is not None:
            self._values["data_process_region"] = data_process_region
        if id is not None:
            self._values["id"] = id
        if partition_fields is not None:
            self._values["partition_fields"] = partition_fields
        if paused is not None:
            self._values["paused"] = paused
        if schedule is not None:
            self._values["schedule"] = schedule
        if sync_creation is not None:
            self._values["sync_creation"] = sync_creation

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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#cluster_name OnlineArchive#cluster_name}.'''
        result = self._values.get("cluster_name")
        assert result is not None, "Required property 'cluster_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def coll_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#coll_name OnlineArchive#coll_name}.'''
        result = self._values.get("coll_name")
        assert result is not None, "Required property 'coll_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def criteria(self) -> "OnlineArchiveCriteria":
        '''criteria block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#criteria OnlineArchive#criteria}
        '''
        result = self._values.get("criteria")
        assert result is not None, "Required property 'criteria' is missing"
        return typing.cast("OnlineArchiveCriteria", result)

    @builtins.property
    def db_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#db_name OnlineArchive#db_name}.'''
        result = self._values.get("db_name")
        assert result is not None, "Required property 'db_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def project_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#project_id OnlineArchive#project_id}.'''
        result = self._values.get("project_id")
        assert result is not None, "Required property 'project_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def collection_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#collection_type OnlineArchive#collection_type}.'''
        result = self._values.get("collection_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def data_expiration_rule(
        self,
    ) -> typing.Optional["OnlineArchiveDataExpirationRule"]:
        '''data_expiration_rule block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#data_expiration_rule OnlineArchive#data_expiration_rule}
        '''
        result = self._values.get("data_expiration_rule")
        return typing.cast(typing.Optional["OnlineArchiveDataExpirationRule"], result)

    @builtins.property
    def data_process_region(self) -> typing.Optional["OnlineArchiveDataProcessRegion"]:
        '''data_process_region block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#data_process_region OnlineArchive#data_process_region}
        '''
        result = self._values.get("data_process_region")
        return typing.cast(typing.Optional["OnlineArchiveDataProcessRegion"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#id OnlineArchive#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def partition_fields(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OnlineArchivePartitionFields"]]]:
        '''partition_fields block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#partition_fields OnlineArchive#partition_fields}
        '''
        result = self._values.get("partition_fields")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["OnlineArchivePartitionFields"]]], result)

    @builtins.property
    def paused(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#paused OnlineArchive#paused}.'''
        result = self._values.get("paused")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def schedule(self) -> typing.Optional["OnlineArchiveSchedule"]:
        '''schedule block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#schedule OnlineArchive#schedule}
        '''
        result = self._values.get("schedule")
        return typing.cast(typing.Optional["OnlineArchiveSchedule"], result)

    @builtins.property
    def sync_creation(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#sync_creation OnlineArchive#sync_creation}.'''
        result = self._values.get("sync_creation")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OnlineArchiveConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.onlineArchive.OnlineArchiveCriteria",
    jsii_struct_bases=[],
    name_mapping={
        "type": "type",
        "date_field": "dateField",
        "date_format": "dateFormat",
        "expire_after_days": "expireAfterDays",
        "query": "query",
    },
)
class OnlineArchiveCriteria:
    def __init__(
        self,
        *,
        type: builtins.str,
        date_field: typing.Optional[builtins.str] = None,
        date_format: typing.Optional[builtins.str] = None,
        expire_after_days: typing.Optional[jsii.Number] = None,
        query: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#type OnlineArchive#type}.
        :param date_field: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#date_field OnlineArchive#date_field}.
        :param date_format: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#date_format OnlineArchive#date_format}.
        :param expire_after_days: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#expire_after_days OnlineArchive#expire_after_days}.
        :param query: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#query OnlineArchive#query}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd9b0b18cf84be268a917e922a7b1486394bf8dcaa355159d231e29a3b09d8cb)
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument date_field", value=date_field, expected_type=type_hints["date_field"])
            check_type(argname="argument date_format", value=date_format, expected_type=type_hints["date_format"])
            check_type(argname="argument expire_after_days", value=expire_after_days, expected_type=type_hints["expire_after_days"])
            check_type(argname="argument query", value=query, expected_type=type_hints["query"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "type": type,
        }
        if date_field is not None:
            self._values["date_field"] = date_field
        if date_format is not None:
            self._values["date_format"] = date_format
        if expire_after_days is not None:
            self._values["expire_after_days"] = expire_after_days
        if query is not None:
            self._values["query"] = query

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#type OnlineArchive#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def date_field(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#date_field OnlineArchive#date_field}.'''
        result = self._values.get("date_field")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def date_format(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#date_format OnlineArchive#date_format}.'''
        result = self._values.get("date_format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def expire_after_days(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#expire_after_days OnlineArchive#expire_after_days}.'''
        result = self._values.get("expire_after_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def query(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#query OnlineArchive#query}.'''
        result = self._values.get("query")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OnlineArchiveCriteria(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OnlineArchiveCriteriaOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.onlineArchive.OnlineArchiveCriteriaOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__61f5d56d7afb608711f4001474fc1960b5ef61c1007b1880263ec771d518358a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDateField")
    def reset_date_field(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDateField", []))

    @jsii.member(jsii_name="resetDateFormat")
    def reset_date_format(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDateFormat", []))

    @jsii.member(jsii_name="resetExpireAfterDays")
    def reset_expire_after_days(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExpireAfterDays", []))

    @jsii.member(jsii_name="resetQuery")
    def reset_query(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetQuery", []))

    @builtins.property
    @jsii.member(jsii_name="dateFieldInput")
    def date_field_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dateFieldInput"))

    @builtins.property
    @jsii.member(jsii_name="dateFormatInput")
    def date_format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dateFormatInput"))

    @builtins.property
    @jsii.member(jsii_name="expireAfterDaysInput")
    def expire_after_days_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "expireAfterDaysInput"))

    @builtins.property
    @jsii.member(jsii_name="queryInput")
    def query_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "queryInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="dateField")
    def date_field(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dateField"))

    @date_field.setter
    def date_field(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd4e0ba20e5b0b862a63f04f8445b804f602e228975c1c15450e8de0f96e0bf2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dateField", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dateFormat")
    def date_format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dateFormat"))

    @date_format.setter
    def date_format(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80ff4e23db3310b4c344d21b5fb85f472e39c27e390b512bcd36e2504b162226)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dateFormat", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="expireAfterDays")
    def expire_after_days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "expireAfterDays"))

    @expire_after_days.setter
    def expire_after_days(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b040cc2a804a0ef1028330d95e8f0aeb2ed271aed90dfcba97f5967358621638)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "expireAfterDays", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="query")
    def query(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "query"))

    @query.setter
    def query(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00641548134174b7ab92d5909d3ba34e512ae7f35d514f6e505c3411d03b06dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "query", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc035f2c577002ef8ff134389ae108e15bd730d2cae670cd5c9f8d162d84b59f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OnlineArchiveCriteria]:
        return typing.cast(typing.Optional[OnlineArchiveCriteria], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[OnlineArchiveCriteria]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59393b6de332aac17ee2147a65ab972be7a7d450cebedc3e0d884aa56a461924)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.onlineArchive.OnlineArchiveDataExpirationRule",
    jsii_struct_bases=[],
    name_mapping={"expire_after_days": "expireAfterDays"},
)
class OnlineArchiveDataExpirationRule:
    def __init__(self, *, expire_after_days: jsii.Number) -> None:
        '''
        :param expire_after_days: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#expire_after_days OnlineArchive#expire_after_days}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cff3aeca5db843571e3fa788bde10ddfef63fcadfd3ac59838af2362dde080c4)
            check_type(argname="argument expire_after_days", value=expire_after_days, expected_type=type_hints["expire_after_days"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "expire_after_days": expire_after_days,
        }

    @builtins.property
    def expire_after_days(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#expire_after_days OnlineArchive#expire_after_days}.'''
        result = self._values.get("expire_after_days")
        assert result is not None, "Required property 'expire_after_days' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OnlineArchiveDataExpirationRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OnlineArchiveDataExpirationRuleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.onlineArchive.OnlineArchiveDataExpirationRuleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ed105a1c4307d42a621e32a32c51d406d93bf8e3aa609e48fd37f2465e008c85)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="expireAfterDaysInput")
    def expire_after_days_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "expireAfterDaysInput"))

    @builtins.property
    @jsii.member(jsii_name="expireAfterDays")
    def expire_after_days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "expireAfterDays"))

    @expire_after_days.setter
    def expire_after_days(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea55764040596a313632d67813b85b6b8f7f5137e3c4919bfeec38dc26a7b76a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "expireAfterDays", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OnlineArchiveDataExpirationRule]:
        return typing.cast(typing.Optional[OnlineArchiveDataExpirationRule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OnlineArchiveDataExpirationRule],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5486d50354d21e9558a05710bba6e67c880642f36eda57aa6bb22dca27e89fc9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.onlineArchive.OnlineArchiveDataProcessRegion",
    jsii_struct_bases=[],
    name_mapping={"cloud_provider": "cloudProvider", "region": "region"},
)
class OnlineArchiveDataProcessRegion:
    def __init__(
        self,
        *,
        cloud_provider: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param cloud_provider: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#cloud_provider OnlineArchive#cloud_provider}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#region OnlineArchive#region}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65eef28e9ab94073f90263cf34d20fbfbb10a1925282ae292b6b52bab8b4e68f)
            check_type(argname="argument cloud_provider", value=cloud_provider, expected_type=type_hints["cloud_provider"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cloud_provider is not None:
            self._values["cloud_provider"] = cloud_provider
        if region is not None:
            self._values["region"] = region

    @builtins.property
    def cloud_provider(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#cloud_provider OnlineArchive#cloud_provider}.'''
        result = self._values.get("cloud_provider")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#region OnlineArchive#region}.'''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OnlineArchiveDataProcessRegion(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OnlineArchiveDataProcessRegionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.onlineArchive.OnlineArchiveDataProcessRegionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__33c040f149ed6d9dd65f349dc4dfab28ac62b7ea6be49fc9f4f5990e4234500a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCloudProvider")
    def reset_cloud_provider(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCloudProvider", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @builtins.property
    @jsii.member(jsii_name="cloudProviderInput")
    def cloud_provider_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cloudProviderInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="cloudProvider")
    def cloud_provider(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cloudProvider"))

    @cloud_provider.setter
    def cloud_provider(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8311e644b5f632a9ea7d24b114656d9b3e83522e53d4ca97fdeb8c2d6e7d36e2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cloudProvider", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5dccbb5f55958ca9625dd8ef6818b7b6f60d2826f3896bd2f9a0f6a507ce4321)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OnlineArchiveDataProcessRegion]:
        return typing.cast(typing.Optional[OnlineArchiveDataProcessRegion], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[OnlineArchiveDataProcessRegion],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25ab757b5459ec1276351aa81bf96a8c3c0da813592e3d6f9e49fea95be3a1f2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.onlineArchive.OnlineArchivePartitionFields",
    jsii_struct_bases=[],
    name_mapping={"field_name": "fieldName", "order": "order"},
)
class OnlineArchivePartitionFields:
    def __init__(self, *, field_name: builtins.str, order: jsii.Number) -> None:
        '''
        :param field_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#field_name OnlineArchive#field_name}.
        :param order: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#order OnlineArchive#order}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47523a901d278ea6b9c4e5ef4ba1d86916903ba0a9b473509ed58bde34c93066)
            check_type(argname="argument field_name", value=field_name, expected_type=type_hints["field_name"])
            check_type(argname="argument order", value=order, expected_type=type_hints["order"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "field_name": field_name,
            "order": order,
        }

    @builtins.property
    def field_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#field_name OnlineArchive#field_name}.'''
        result = self._values.get("field_name")
        assert result is not None, "Required property 'field_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def order(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#order OnlineArchive#order}.'''
        result = self._values.get("order")
        assert result is not None, "Required property 'order' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OnlineArchivePartitionFields(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OnlineArchivePartitionFieldsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.onlineArchive.OnlineArchivePartitionFieldsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8a22e5aeaa7d49a8304106c78c62dfbb591260920db5f5e1686e5833d2e102d3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "OnlineArchivePartitionFieldsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a6d1f35898175c00aca4de2eea2708b960ab85fdb7c4fb52024b7d03a51c6ff)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("OnlineArchivePartitionFieldsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4c9f82b054eeb30c8064ab3d12fb54690594cc9e0a082206af11c74e69fddc3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7db9dc27b42f707d926c6b3447c7a76f06e246aab5b8f48b59ce6fb840ec5196)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2386e9e4182df9872320ee0e4df089ddde504f3f4ef54846d7e92ff1cce0b87b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OnlineArchivePartitionFields]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OnlineArchivePartitionFields]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OnlineArchivePartitionFields]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5f02dba3058b1ca7823aa00ab2f579108d287a10642dd3b51b0f8308cdd7f19)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class OnlineArchivePartitionFieldsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.onlineArchive.OnlineArchivePartitionFieldsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__15485242bf225f68d9d49a65f30304a4e6056f995968594c12e96c49b82c270a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="fieldType")
    def field_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fieldType"))

    @builtins.property
    @jsii.member(jsii_name="fieldNameInput")
    def field_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fieldNameInput"))

    @builtins.property
    @jsii.member(jsii_name="orderInput")
    def order_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "orderInput"))

    @builtins.property
    @jsii.member(jsii_name="fieldName")
    def field_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fieldName"))

    @field_name.setter
    def field_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88d32d4cb751ba46749055e9da2d8888c8ff2d1d176fedf6f1d5dd40bde20586)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fieldName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="order")
    def order(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "order"))

    @order.setter
    def order(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b40cc701819af6294c13317a2303fa116b2a03e8b58a3a5cb275920671240e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "order", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OnlineArchivePartitionFields]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OnlineArchivePartitionFields]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OnlineArchivePartitionFields]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09eec2ebd86060da8dd71e2d96c173356d482aa746a97c20e1ddc55383d9bd09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.onlineArchive.OnlineArchiveSchedule",
    jsii_struct_bases=[],
    name_mapping={
        "type": "type",
        "day_of_month": "dayOfMonth",
        "day_of_week": "dayOfWeek",
        "end_hour": "endHour",
        "end_minute": "endMinute",
        "start_hour": "startHour",
        "start_minute": "startMinute",
    },
)
class OnlineArchiveSchedule:
    def __init__(
        self,
        *,
        type: builtins.str,
        day_of_month: typing.Optional[jsii.Number] = None,
        day_of_week: typing.Optional[jsii.Number] = None,
        end_hour: typing.Optional[jsii.Number] = None,
        end_minute: typing.Optional[jsii.Number] = None,
        start_hour: typing.Optional[jsii.Number] = None,
        start_minute: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#type OnlineArchive#type}.
        :param day_of_month: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#day_of_month OnlineArchive#day_of_month}.
        :param day_of_week: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#day_of_week OnlineArchive#day_of_week}.
        :param end_hour: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#end_hour OnlineArchive#end_hour}.
        :param end_minute: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#end_minute OnlineArchive#end_minute}.
        :param start_hour: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#start_hour OnlineArchive#start_hour}.
        :param start_minute: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#start_minute OnlineArchive#start_minute}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53be68d7c77dd2ff88dca11f84af98676a1b49f023a66a3a37e25aa8615dec4a)
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument day_of_month", value=day_of_month, expected_type=type_hints["day_of_month"])
            check_type(argname="argument day_of_week", value=day_of_week, expected_type=type_hints["day_of_week"])
            check_type(argname="argument end_hour", value=end_hour, expected_type=type_hints["end_hour"])
            check_type(argname="argument end_minute", value=end_minute, expected_type=type_hints["end_minute"])
            check_type(argname="argument start_hour", value=start_hour, expected_type=type_hints["start_hour"])
            check_type(argname="argument start_minute", value=start_minute, expected_type=type_hints["start_minute"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "type": type,
        }
        if day_of_month is not None:
            self._values["day_of_month"] = day_of_month
        if day_of_week is not None:
            self._values["day_of_week"] = day_of_week
        if end_hour is not None:
            self._values["end_hour"] = end_hour
        if end_minute is not None:
            self._values["end_minute"] = end_minute
        if start_hour is not None:
            self._values["start_hour"] = start_hour
        if start_minute is not None:
            self._values["start_minute"] = start_minute

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#type OnlineArchive#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def day_of_month(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#day_of_month OnlineArchive#day_of_month}.'''
        result = self._values.get("day_of_month")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def day_of_week(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#day_of_week OnlineArchive#day_of_week}.'''
        result = self._values.get("day_of_week")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def end_hour(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#end_hour OnlineArchive#end_hour}.'''
        result = self._values.get("end_hour")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def end_minute(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#end_minute OnlineArchive#end_minute}.'''
        result = self._values.get("end_minute")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def start_hour(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#start_hour OnlineArchive#start_hour}.'''
        result = self._values.get("start_hour")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def start_minute(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/online_archive#start_minute OnlineArchive#start_minute}.'''
        result = self._values.get("start_minute")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "OnlineArchiveSchedule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class OnlineArchiveScheduleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.onlineArchive.OnlineArchiveScheduleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__eeb9e8041ad9d3a2fed8f59759ced882993b6dc3c8d75ad19c654d81e19c6e94)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetDayOfMonth")
    def reset_day_of_month(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDayOfMonth", []))

    @jsii.member(jsii_name="resetDayOfWeek")
    def reset_day_of_week(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDayOfWeek", []))

    @jsii.member(jsii_name="resetEndHour")
    def reset_end_hour(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndHour", []))

    @jsii.member(jsii_name="resetEndMinute")
    def reset_end_minute(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEndMinute", []))

    @jsii.member(jsii_name="resetStartHour")
    def reset_start_hour(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStartHour", []))

    @jsii.member(jsii_name="resetStartMinute")
    def reset_start_minute(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStartMinute", []))

    @builtins.property
    @jsii.member(jsii_name="dayOfMonthInput")
    def day_of_month_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "dayOfMonthInput"))

    @builtins.property
    @jsii.member(jsii_name="dayOfWeekInput")
    def day_of_week_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "dayOfWeekInput"))

    @builtins.property
    @jsii.member(jsii_name="endHourInput")
    def end_hour_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "endHourInput"))

    @builtins.property
    @jsii.member(jsii_name="endMinuteInput")
    def end_minute_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "endMinuteInput"))

    @builtins.property
    @jsii.member(jsii_name="startHourInput")
    def start_hour_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "startHourInput"))

    @builtins.property
    @jsii.member(jsii_name="startMinuteInput")
    def start_minute_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "startMinuteInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="dayOfMonth")
    def day_of_month(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "dayOfMonth"))

    @day_of_month.setter
    def day_of_month(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b55bfc758cd8aa66b8b7d688f8e69215d1dcd30b980bd3b0cca59429e3c2768)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dayOfMonth", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dayOfWeek")
    def day_of_week(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "dayOfWeek"))

    @day_of_week.setter
    def day_of_week(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__daeffe06b48371fcbbdc47f6ab65c8f790b99a66faa0ae0cb181b944c2f95ba0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dayOfWeek", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="endHour")
    def end_hour(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "endHour"))

    @end_hour.setter
    def end_hour(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__abdb511f2043318166d22e40a651c572383ed612013a9fe4ecfe68bdb4cfff8e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "endHour", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="endMinute")
    def end_minute(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "endMinute"))

    @end_minute.setter
    def end_minute(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e41f0ca6d7b6e778ae267b4ca7942cf5eeeb133864db92f6ee4518ca187bc6d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "endMinute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="startHour")
    def start_hour(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "startHour"))

    @start_hour.setter
    def start_hour(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24d0159d3e68f798b688de1c70a26ab9c2e4d25529eb8511adc4612d484980e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "startHour", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="startMinute")
    def start_minute(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "startMinute"))

    @start_minute.setter
    def start_minute(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed48b53be5556d01fb1cfc9e50bd3e6bc0666ca34342d0e3c3bad57557c2f816)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "startMinute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03d0a2d14fb39d7cdf680a59b0ca1bcdb73a678c6219c94701ebeba57eaf29ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[OnlineArchiveSchedule]:
        return typing.cast(typing.Optional[OnlineArchiveSchedule], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[OnlineArchiveSchedule]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9b1c77fb00d7ceb8d8c10254d22bb647cf9f3daac581098f73b38ef7a6de03b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "OnlineArchive",
    "OnlineArchiveConfig",
    "OnlineArchiveCriteria",
    "OnlineArchiveCriteriaOutputReference",
    "OnlineArchiveDataExpirationRule",
    "OnlineArchiveDataExpirationRuleOutputReference",
    "OnlineArchiveDataProcessRegion",
    "OnlineArchiveDataProcessRegionOutputReference",
    "OnlineArchivePartitionFields",
    "OnlineArchivePartitionFieldsList",
    "OnlineArchivePartitionFieldsOutputReference",
    "OnlineArchiveSchedule",
    "OnlineArchiveScheduleOutputReference",
]

publication.publish()

def _typecheckingstub__1dd8d1ca11c164ab0d5dc5e06d9e71c8db190f43b7a833f46b312e4686fcae23(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    cluster_name: builtins.str,
    coll_name: builtins.str,
    criteria: typing.Union[OnlineArchiveCriteria, typing.Dict[builtins.str, typing.Any]],
    db_name: builtins.str,
    project_id: builtins.str,
    collection_type: typing.Optional[builtins.str] = None,
    data_expiration_rule: typing.Optional[typing.Union[OnlineArchiveDataExpirationRule, typing.Dict[builtins.str, typing.Any]]] = None,
    data_process_region: typing.Optional[typing.Union[OnlineArchiveDataProcessRegion, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    partition_fields: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OnlineArchivePartitionFields, typing.Dict[builtins.str, typing.Any]]]]] = None,
    paused: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    schedule: typing.Optional[typing.Union[OnlineArchiveSchedule, typing.Dict[builtins.str, typing.Any]]] = None,
    sync_creation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__4ee2e10b777488376f44b03e5c7d982a79480e79d0ab3b869cfc0f96883a34eb(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76e5606784d6acac975631ea2af1161f22ad81d1d668f072c7130ebae2a4b904(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OnlineArchivePartitionFields, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de8ae41e4f876927ef6981d0b7733937af86ae48eef04c7e84176df670d4d407(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a4379a10167c092c00fdc988318e28f67ce2718a6a8ee77cd54add0ccfef334(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d037e4474bfd5c2e1333006f2df70dcdc006a9730cb12cdd7f93e621179f0d1f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__980c51108ac5c6046b9e7ac7aa2d3b50ff4e2a59f4017e3312afc6855606730c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21ab4336f292487179519348dcc4aec8d86a3848384ded4433c07070dbce697d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13b151595b2c0db02b6ba933ac0f0af01ed2cae3b3e6a98c2c0b0cf315423aee(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f015421bc7c023003d29dff1bf83dd6df11009d9f219d612275aa1c7cfd6c69a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6764ebedc8392745886f1bdf0cd6cf1c67bc0c1261d3de37bf3dcc4e6ac0163c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04a399df69abc4c0e11be19164b166682ee8e362c29595e11f7e4a9e0c6c2ad7(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    cluster_name: builtins.str,
    coll_name: builtins.str,
    criteria: typing.Union[OnlineArchiveCriteria, typing.Dict[builtins.str, typing.Any]],
    db_name: builtins.str,
    project_id: builtins.str,
    collection_type: typing.Optional[builtins.str] = None,
    data_expiration_rule: typing.Optional[typing.Union[OnlineArchiveDataExpirationRule, typing.Dict[builtins.str, typing.Any]]] = None,
    data_process_region: typing.Optional[typing.Union[OnlineArchiveDataProcessRegion, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    partition_fields: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[OnlineArchivePartitionFields, typing.Dict[builtins.str, typing.Any]]]]] = None,
    paused: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    schedule: typing.Optional[typing.Union[OnlineArchiveSchedule, typing.Dict[builtins.str, typing.Any]]] = None,
    sync_creation: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd9b0b18cf84be268a917e922a7b1486394bf8dcaa355159d231e29a3b09d8cb(
    *,
    type: builtins.str,
    date_field: typing.Optional[builtins.str] = None,
    date_format: typing.Optional[builtins.str] = None,
    expire_after_days: typing.Optional[jsii.Number] = None,
    query: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61f5d56d7afb608711f4001474fc1960b5ef61c1007b1880263ec771d518358a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd4e0ba20e5b0b862a63f04f8445b804f602e228975c1c15450e8de0f96e0bf2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80ff4e23db3310b4c344d21b5fb85f472e39c27e390b512bcd36e2504b162226(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b040cc2a804a0ef1028330d95e8f0aeb2ed271aed90dfcba97f5967358621638(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00641548134174b7ab92d5909d3ba34e512ae7f35d514f6e505c3411d03b06dd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc035f2c577002ef8ff134389ae108e15bd730d2cae670cd5c9f8d162d84b59f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59393b6de332aac17ee2147a65ab972be7a7d450cebedc3e0d884aa56a461924(
    value: typing.Optional[OnlineArchiveCriteria],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cff3aeca5db843571e3fa788bde10ddfef63fcadfd3ac59838af2362dde080c4(
    *,
    expire_after_days: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed105a1c4307d42a621e32a32c51d406d93bf8e3aa609e48fd37f2465e008c85(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea55764040596a313632d67813b85b6b8f7f5137e3c4919bfeec38dc26a7b76a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5486d50354d21e9558a05710bba6e67c880642f36eda57aa6bb22dca27e89fc9(
    value: typing.Optional[OnlineArchiveDataExpirationRule],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65eef28e9ab94073f90263cf34d20fbfbb10a1925282ae292b6b52bab8b4e68f(
    *,
    cloud_provider: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33c040f149ed6d9dd65f349dc4dfab28ac62b7ea6be49fc9f4f5990e4234500a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8311e644b5f632a9ea7d24b114656d9b3e83522e53d4ca97fdeb8c2d6e7d36e2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5dccbb5f55958ca9625dd8ef6818b7b6f60d2826f3896bd2f9a0f6a507ce4321(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25ab757b5459ec1276351aa81bf96a8c3c0da813592e3d6f9e49fea95be3a1f2(
    value: typing.Optional[OnlineArchiveDataProcessRegion],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47523a901d278ea6b9c4e5ef4ba1d86916903ba0a9b473509ed58bde34c93066(
    *,
    field_name: builtins.str,
    order: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a22e5aeaa7d49a8304106c78c62dfbb591260920db5f5e1686e5833d2e102d3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a6d1f35898175c00aca4de2eea2708b960ab85fdb7c4fb52024b7d03a51c6ff(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4c9f82b054eeb30c8064ab3d12fb54690594cc9e0a082206af11c74e69fddc3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7db9dc27b42f707d926c6b3447c7a76f06e246aab5b8f48b59ce6fb840ec5196(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2386e9e4182df9872320ee0e4df089ddde504f3f4ef54846d7e92ff1cce0b87b(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5f02dba3058b1ca7823aa00ab2f579108d287a10642dd3b51b0f8308cdd7f19(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[OnlineArchivePartitionFields]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15485242bf225f68d9d49a65f30304a4e6056f995968594c12e96c49b82c270a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88d32d4cb751ba46749055e9da2d8888c8ff2d1d176fedf6f1d5dd40bde20586(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b40cc701819af6294c13317a2303fa116b2a03e8b58a3a5cb275920671240e4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09eec2ebd86060da8dd71e2d96c173356d482aa746a97c20e1ddc55383d9bd09(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, OnlineArchivePartitionFields]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53be68d7c77dd2ff88dca11f84af98676a1b49f023a66a3a37e25aa8615dec4a(
    *,
    type: builtins.str,
    day_of_month: typing.Optional[jsii.Number] = None,
    day_of_week: typing.Optional[jsii.Number] = None,
    end_hour: typing.Optional[jsii.Number] = None,
    end_minute: typing.Optional[jsii.Number] = None,
    start_hour: typing.Optional[jsii.Number] = None,
    start_minute: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eeb9e8041ad9d3a2fed8f59759ced882993b6dc3c8d75ad19c654d81e19c6e94(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b55bfc758cd8aa66b8b7d688f8e69215d1dcd30b980bd3b0cca59429e3c2768(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__daeffe06b48371fcbbdc47f6ab65c8f790b99a66faa0ae0cb181b944c2f95ba0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abdb511f2043318166d22e40a651c572383ed612013a9fe4ecfe68bdb4cfff8e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e41f0ca6d7b6e778ae267b4ca7942cf5eeeb133864db92f6ee4518ca187bc6d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24d0159d3e68f798b688de1c70a26ab9c2e4d25529eb8511adc4612d484980e8(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed48b53be5556d01fb1cfc9e50bd3e6bc0666ca34342d0e3c3bad57557c2f816(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03d0a2d14fb39d7cdf680a59b0ca1bcdb73a678c6219c94701ebeba57eaf29ef(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9b1c77fb00d7ceb8d8c10254d22bb647cf9f3daac581098f73b38ef7a6de03b(
    value: typing.Optional[OnlineArchiveSchedule],
) -> None:
    """Type checking stubs"""
    pass
