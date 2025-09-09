r'''
# `data_mongodbatlas_cluster`

Refer to the Terraform Registry for docs: [`data_mongodbatlas_cluster`](https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/data-sources/cluster).
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


class DataMongodbatlasCluster(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasCluster",
):
    '''Represents a {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/data-sources/cluster mongodbatlas_cluster}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        project_id: builtins.str,
        id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/data-sources/cluster mongodbatlas_cluster} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/data-sources/cluster#name DataMongodbatlasCluster#name}.
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/data-sources/cluster#project_id DataMongodbatlasCluster#project_id}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/data-sources/cluster#id DataMongodbatlasCluster#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0250acaa721230a8828d7166ac32cc1ad5bcbd89da30e2fd4a1911e6896e662c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataMongodbatlasClusterConfig(
            name=name,
            project_id=project_id,
            id=id,
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
        '''Generates CDKTF code for importing a DataMongodbatlasCluster resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataMongodbatlasCluster to import.
        :param import_from_id: The id of the existing DataMongodbatlasCluster that should be imported. Refer to the {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/data-sources/cluster#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataMongodbatlasCluster to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bcc3c4a8105656725583090c6cf2dfe6c00a5c68dedc46b149db668684694661)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

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
    def advanced_configuration(
        self,
    ) -> "DataMongodbatlasClusterAdvancedConfigurationList":
        return typing.cast("DataMongodbatlasClusterAdvancedConfigurationList", jsii.get(self, "advancedConfiguration"))

    @builtins.property
    @jsii.member(jsii_name="autoScalingComputeEnabled")
    def auto_scaling_compute_enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "autoScalingComputeEnabled"))

    @builtins.property
    @jsii.member(jsii_name="autoScalingComputeScaleDownEnabled")
    def auto_scaling_compute_scale_down_enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "autoScalingComputeScaleDownEnabled"))

    @builtins.property
    @jsii.member(jsii_name="autoScalingDiskGbEnabled")
    def auto_scaling_disk_gb_enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "autoScalingDiskGbEnabled"))

    @builtins.property
    @jsii.member(jsii_name="backingProviderName")
    def backing_provider_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "backingProviderName"))

    @builtins.property
    @jsii.member(jsii_name="backupEnabled")
    def backup_enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "backupEnabled"))

    @builtins.property
    @jsii.member(jsii_name="biConnectorConfig")
    def bi_connector_config(self) -> "DataMongodbatlasClusterBiConnectorConfigList":
        return typing.cast("DataMongodbatlasClusterBiConnectorConfigList", jsii.get(self, "biConnectorConfig"))

    @builtins.property
    @jsii.member(jsii_name="clusterType")
    def cluster_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterType"))

    @builtins.property
    @jsii.member(jsii_name="connectionStrings")
    def connection_strings(self) -> "DataMongodbatlasClusterConnectionStringsList":
        return typing.cast("DataMongodbatlasClusterConnectionStringsList", jsii.get(self, "connectionStrings"))

    @builtins.property
    @jsii.member(jsii_name="containerId")
    def container_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "containerId"))

    @builtins.property
    @jsii.member(jsii_name="diskSizeGb")
    def disk_size_gb(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "diskSizeGb"))

    @builtins.property
    @jsii.member(jsii_name="encryptionAtRestProvider")
    def encryption_at_rest_provider(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "encryptionAtRestProvider"))

    @builtins.property
    @jsii.member(jsii_name="labels")
    def labels(self) -> "DataMongodbatlasClusterLabelsList":
        return typing.cast("DataMongodbatlasClusterLabelsList", jsii.get(self, "labels"))

    @builtins.property
    @jsii.member(jsii_name="mongoDbMajorVersion")
    def mongo_db_major_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mongoDbMajorVersion"))

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
    @jsii.member(jsii_name="numShards")
    def num_shards(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numShards"))

    @builtins.property
    @jsii.member(jsii_name="paused")
    def paused(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "paused"))

    @builtins.property
    @jsii.member(jsii_name="pinnedFcv")
    def pinned_fcv(self) -> "DataMongodbatlasClusterPinnedFcvList":
        return typing.cast("DataMongodbatlasClusterPinnedFcvList", jsii.get(self, "pinnedFcv"))

    @builtins.property
    @jsii.member(jsii_name="pitEnabled")
    def pit_enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "pitEnabled"))

    @builtins.property
    @jsii.member(jsii_name="providerAutoScalingComputeMaxInstanceSize")
    def provider_auto_scaling_compute_max_instance_size(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "providerAutoScalingComputeMaxInstanceSize"))

    @builtins.property
    @jsii.member(jsii_name="providerAutoScalingComputeMinInstanceSize")
    def provider_auto_scaling_compute_min_instance_size(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "providerAutoScalingComputeMinInstanceSize"))

    @builtins.property
    @jsii.member(jsii_name="providerBackupEnabled")
    def provider_backup_enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "providerBackupEnabled"))

    @builtins.property
    @jsii.member(jsii_name="providerDiskIops")
    def provider_disk_iops(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "providerDiskIops"))

    @builtins.property
    @jsii.member(jsii_name="providerDiskTypeName")
    def provider_disk_type_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "providerDiskTypeName"))

    @builtins.property
    @jsii.member(jsii_name="providerEncryptEbsVolume")
    def provider_encrypt_ebs_volume(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "providerEncryptEbsVolume"))

    @builtins.property
    @jsii.member(jsii_name="providerEncryptEbsVolumeFlag")
    def provider_encrypt_ebs_volume_flag(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "providerEncryptEbsVolumeFlag"))

    @builtins.property
    @jsii.member(jsii_name="providerInstanceSizeName")
    def provider_instance_size_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "providerInstanceSizeName"))

    @builtins.property
    @jsii.member(jsii_name="providerName")
    def provider_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "providerName"))

    @builtins.property
    @jsii.member(jsii_name="providerRegionName")
    def provider_region_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "providerRegionName"))

    @builtins.property
    @jsii.member(jsii_name="providerVolumeType")
    def provider_volume_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "providerVolumeType"))

    @builtins.property
    @jsii.member(jsii_name="redactClientLogData")
    def redact_client_log_data(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "redactClientLogData"))

    @builtins.property
    @jsii.member(jsii_name="replicationFactor")
    def replication_factor(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "replicationFactor"))

    @builtins.property
    @jsii.member(jsii_name="replicationSpecs")
    def replication_specs(self) -> "DataMongodbatlasClusterReplicationSpecsList":
        return typing.cast("DataMongodbatlasClusterReplicationSpecsList", jsii.get(self, "replicationSpecs"))

    @builtins.property
    @jsii.member(jsii_name="snapshotBackupPolicy")
    def snapshot_backup_policy(
        self,
    ) -> "DataMongodbatlasClusterSnapshotBackupPolicyList":
        return typing.cast("DataMongodbatlasClusterSnapshotBackupPolicyList", jsii.get(self, "snapshotBackupPolicy"))

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
    def tags(self) -> "DataMongodbatlasClusterTagsList":
        return typing.cast("DataMongodbatlasClusterTagsList", jsii.get(self, "tags"))

    @builtins.property
    @jsii.member(jsii_name="terminationProtectionEnabled")
    def termination_protection_enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "terminationProtectionEnabled"))

    @builtins.property
    @jsii.member(jsii_name="versionReleaseSystem")
    def version_release_system(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "versionReleaseSystem"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26bb0a5238b27a29cd7e292b77347c6ae265ba125b646ec0d0489359e3678ed2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4cd2074c8e365f16873dfae83e2d08e26cbce8e69ed20b08469ee5523c31020)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3fcc92e99c39102c9218afad2701f7ebf0356ceb91850483376b85d582dbf8d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterAdvancedConfiguration",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataMongodbatlasClusterAdvancedConfiguration:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataMongodbatlasClusterAdvancedConfiguration(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataMongodbatlasClusterAdvancedConfigurationList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterAdvancedConfigurationList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b9bd131968d39d3243751480eda857eee48585cbf80a28f40d0a04643311be31)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataMongodbatlasClusterAdvancedConfigurationOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__962a03b21e5620134f0f20bce9f7e551040c2f08d07df736e2c290af05b2eabb)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataMongodbatlasClusterAdvancedConfigurationOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__764a3731ba3ae99a0e9b8f961a7aed2f18eb2def5a7bbd16429ecb9298039b57)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f3e64d0d15ed96739b82e4dc010909b71458463ddfdfcd358305d7899f580dd5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__14362b65b014659f21488afe84e8d5c4d24a7b7f8e14ba7343504d17cbda1c36)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataMongodbatlasClusterAdvancedConfigurationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterAdvancedConfigurationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7895538c69f0e43a7ac717c3591645e70d8962b595d13c851782a6539d4c84db)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="changeStreamOptionsPreAndPostImagesExpireAfterSeconds")
    def change_stream_options_pre_and_post_images_expire_after_seconds(
        self,
    ) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "changeStreamOptionsPreAndPostImagesExpireAfterSeconds"))

    @builtins.property
    @jsii.member(jsii_name="customOpensslCipherConfigTls12")
    def custom_openssl_cipher_config_tls12(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "customOpensslCipherConfigTls12"))

    @builtins.property
    @jsii.member(jsii_name="defaultMaxTimeMs")
    def default_max_time_ms(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "defaultMaxTimeMs"))

    @builtins.property
    @jsii.member(jsii_name="defaultReadConcern")
    def default_read_concern(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultReadConcern"))

    @builtins.property
    @jsii.member(jsii_name="defaultWriteConcern")
    def default_write_concern(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultWriteConcern"))

    @builtins.property
    @jsii.member(jsii_name="failIndexKeyTooLong")
    def fail_index_key_too_long(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "failIndexKeyTooLong"))

    @builtins.property
    @jsii.member(jsii_name="javascriptEnabled")
    def javascript_enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "javascriptEnabled"))

    @builtins.property
    @jsii.member(jsii_name="minimumEnabledTlsProtocol")
    def minimum_enabled_tls_protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minimumEnabledTlsProtocol"))

    @builtins.property
    @jsii.member(jsii_name="noTableScan")
    def no_table_scan(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "noTableScan"))

    @builtins.property
    @jsii.member(jsii_name="oplogMinRetentionHours")
    def oplog_min_retention_hours(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "oplogMinRetentionHours"))

    @builtins.property
    @jsii.member(jsii_name="oplogSizeMb")
    def oplog_size_mb(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "oplogSizeMb"))

    @builtins.property
    @jsii.member(jsii_name="sampleRefreshIntervalBiConnector")
    def sample_refresh_interval_bi_connector(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sampleRefreshIntervalBiConnector"))

    @builtins.property
    @jsii.member(jsii_name="sampleSizeBiConnector")
    def sample_size_bi_connector(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sampleSizeBiConnector"))

    @builtins.property
    @jsii.member(jsii_name="tlsCipherConfigMode")
    def tls_cipher_config_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tlsCipherConfigMode"))

    @builtins.property
    @jsii.member(jsii_name="transactionLifetimeLimitSeconds")
    def transaction_lifetime_limit_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "transactionLifetimeLimitSeconds"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataMongodbatlasClusterAdvancedConfiguration]:
        return typing.cast(typing.Optional[DataMongodbatlasClusterAdvancedConfiguration], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataMongodbatlasClusterAdvancedConfiguration],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4798c45bb49795cf05eb52d030a2bc8a9117c0e29e3ef5c9eb63dccd2191cd6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterBiConnectorConfig",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataMongodbatlasClusterBiConnectorConfig:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataMongodbatlasClusterBiConnectorConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataMongodbatlasClusterBiConnectorConfigList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterBiConnectorConfigList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__abe508952197406ce4fea5b81ae99f75a415e71ee26a595ef0c1071a2b33a3e7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataMongodbatlasClusterBiConnectorConfigOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89593909ffd5a0c3545fafe013bad98cf29d1b5b788f55b160fb588913649b87)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataMongodbatlasClusterBiConnectorConfigOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc3036d39a80d6e983f16d80e107269a32a72ba48bd77aac9f612851aecd1685)
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
            type_hints = typing.get_type_hints(_typecheckingstub__56509c6cb86d3ebd5b5de5f8011afe85425375473f52ef132974483f284eca4c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f656abd58e93ed9c38cc0da33af9baaba0f5cb13722549938ab85321c890eb77)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataMongodbatlasClusterBiConnectorConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterBiConnectorConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__48bde2d5688ba887a5c88efdeb755bae974aa565e10744fd29692a4badc9bd08)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "enabled"))

    @builtins.property
    @jsii.member(jsii_name="readPreference")
    def read_preference(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "readPreference"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataMongodbatlasClusterBiConnectorConfig]:
        return typing.cast(typing.Optional[DataMongodbatlasClusterBiConnectorConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataMongodbatlasClusterBiConnectorConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52d15ffbe6fbfb1df69e144511f56291515e91395463095ff8eaa4829e715709)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterConfig",
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
        "id": "id",
    },
)
class DataMongodbatlasClusterConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/data-sources/cluster#name DataMongodbatlasCluster#name}.
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/data-sources/cluster#project_id DataMongodbatlasCluster#project_id}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/data-sources/cluster#id DataMongodbatlasCluster#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93fc09cc4c3cb912b4b8b442c73f04b8a294c203bc4f17b073bb7924ffc38054)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
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
        if id is not None:
            self._values["id"] = id

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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/data-sources/cluster#name DataMongodbatlasCluster#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def project_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/data-sources/cluster#project_id DataMongodbatlasCluster#project_id}.'''
        result = self._values.get("project_id")
        assert result is not None, "Required property 'project_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/data-sources/cluster#id DataMongodbatlasCluster#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataMongodbatlasClusterConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterConnectionStrings",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataMongodbatlasClusterConnectionStrings:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataMongodbatlasClusterConnectionStrings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataMongodbatlasClusterConnectionStringsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterConnectionStringsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8527ee9f80574814ead88bca26557c573a7fd05364f4c83895146a19192782bb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataMongodbatlasClusterConnectionStringsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c18bfad12e5eff7cdf992000179c63503238015e977325f0887861e3dff36d9)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataMongodbatlasClusterConnectionStringsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62b880265c7707252b61c025e719573b202cbe61a319041b649950ff617a35e0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a8b520be7384128225ee798f527accf17fffd7dc94aa82cf957ba72f6b5ffc11)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0c6c52e05982a26de53638795f6072758b3bd2acae111842db062a8a40233e2f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataMongodbatlasClusterConnectionStringsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterConnectionStringsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9076da1291915d25296b17893dc1d09f005f7e29a97fc7f74efab23a4d98fe9f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="awsPrivateLink")
    def aws_private_link(self) -> _cdktf_9a9027ec.StringMap:
        return typing.cast(_cdktf_9a9027ec.StringMap, jsii.get(self, "awsPrivateLink"))

    @builtins.property
    @jsii.member(jsii_name="awsPrivateLinkSrv")
    def aws_private_link_srv(self) -> _cdktf_9a9027ec.StringMap:
        return typing.cast(_cdktf_9a9027ec.StringMap, jsii.get(self, "awsPrivateLinkSrv"))

    @builtins.property
    @jsii.member(jsii_name="private")
    def private(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "private"))

    @builtins.property
    @jsii.member(jsii_name="privateEndpoint")
    def private_endpoint(
        self,
    ) -> "DataMongodbatlasClusterConnectionStringsPrivateEndpointList":
        return typing.cast("DataMongodbatlasClusterConnectionStringsPrivateEndpointList", jsii.get(self, "privateEndpoint"))

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
    def internal_value(
        self,
    ) -> typing.Optional[DataMongodbatlasClusterConnectionStrings]:
        return typing.cast(typing.Optional[DataMongodbatlasClusterConnectionStrings], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataMongodbatlasClusterConnectionStrings],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b0fdca1c2832a26aafc358a81b660cdbe64b095d42c59c42227a6785b69acc4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterConnectionStringsPrivateEndpoint",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataMongodbatlasClusterConnectionStringsPrivateEndpoint:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataMongodbatlasClusterConnectionStringsPrivateEndpoint(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterConnectionStringsPrivateEndpointEndpoints",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataMongodbatlasClusterConnectionStringsPrivateEndpointEndpoints:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataMongodbatlasClusterConnectionStringsPrivateEndpointEndpoints(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataMongodbatlasClusterConnectionStringsPrivateEndpointEndpointsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterConnectionStringsPrivateEndpointEndpointsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6338bf1b793e3285b87fbe6afe5193652966afbc2cc4cac994060f9c583ca258)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataMongodbatlasClusterConnectionStringsPrivateEndpointEndpointsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__355f388a66485310e0932f6f20e757632fd742f5c1224321c2f5a4eb26f8346e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataMongodbatlasClusterConnectionStringsPrivateEndpointEndpointsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e2b782e71120ef2a04277e124f130a880fa0ba7aa4c9005a1f7fb478d9b9ac5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__356dd9cef5670e4ce9f81dbd391618e033523363fd05fdd0492d58f994f7e595)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3972e09f1a6339161c95ad9b29e8d3e4646857822e10e1195e779a2dd3c5c08f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataMongodbatlasClusterConnectionStringsPrivateEndpointEndpointsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterConnectionStringsPrivateEndpointEndpointsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__28b2770d052777e7afaa59616cb85b8b1d180229e6747ae0b0a85607ae08cf06)
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
    ) -> typing.Optional[DataMongodbatlasClusterConnectionStringsPrivateEndpointEndpoints]:
        return typing.cast(typing.Optional[DataMongodbatlasClusterConnectionStringsPrivateEndpointEndpoints], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataMongodbatlasClusterConnectionStringsPrivateEndpointEndpoints],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb3207d6a8273fe42bc91c4335da793677b32e4d8acc5a72fb8de332f59fb085)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataMongodbatlasClusterConnectionStringsPrivateEndpointList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterConnectionStringsPrivateEndpointList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__54c52c87c0d8a685eff16e614542f7386639787d7657c3ba81676b2fe690dde0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataMongodbatlasClusterConnectionStringsPrivateEndpointOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69301cf8938eb927ed995d0205ae4ee536816aefa126b04ceb005ecff60d59ff)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataMongodbatlasClusterConnectionStringsPrivateEndpointOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d71299e1eed6fe3c9effb9efe03c520661f396653c3983806fd5cc422051f39f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__63679b0f7dad15543f0b4709ddfdd0bdfdce62eb28ba986c45e0bb547a361264)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5b172dd83ab8b773b50398cbc9852447898f197eb058795772016820142996d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataMongodbatlasClusterConnectionStringsPrivateEndpointOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterConnectionStringsPrivateEndpointOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e961164c756923e8f661436e31eedc4336df6f58f5c5435991cf7995a137c9d4)
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
    def endpoints(
        self,
    ) -> DataMongodbatlasClusterConnectionStringsPrivateEndpointEndpointsList:
        return typing.cast(DataMongodbatlasClusterConnectionStringsPrivateEndpointEndpointsList, jsii.get(self, "endpoints"))

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
    ) -> typing.Optional[DataMongodbatlasClusterConnectionStringsPrivateEndpoint]:
        return typing.cast(typing.Optional[DataMongodbatlasClusterConnectionStringsPrivateEndpoint], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataMongodbatlasClusterConnectionStringsPrivateEndpoint],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__65dd847c5ec0ba0e89ba57884299af16a2f06170e64f996bab2fb363549048d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterLabels",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataMongodbatlasClusterLabels:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataMongodbatlasClusterLabels(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataMongodbatlasClusterLabelsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterLabelsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__47773551bad8a7ba427f66e593d40418023c2dc0c780e7557e81fc9f7935a719)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "DataMongodbatlasClusterLabelsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b858a3aaeddc852811dd75d5df3cbeade63918602a8abd2646137365f526ebb1)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataMongodbatlasClusterLabelsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34f4e1f51348affeb363e845e191463639511d1ced5d8e63dffb5359e3a0e8f9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9000cd23798afce7db1b9dcb81a447b49b6b2627ba7770cc5090f5c3d27fa38e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d7e097573230512bf04063f9daa8e19687462b390192dd8b6805384997b318dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataMongodbatlasClusterLabelsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterLabelsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b36cf262f999463450a3742afc440fc701e55cff1593c841f6908d69a94bb68c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataMongodbatlasClusterLabels]:
        return typing.cast(typing.Optional[DataMongodbatlasClusterLabels], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataMongodbatlasClusterLabels],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2ddf5bd4b5335815717c527401d0d9fc9ea9ab2926673fedb0cf3997d202dd2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterPinnedFcv",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataMongodbatlasClusterPinnedFcv:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataMongodbatlasClusterPinnedFcv(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataMongodbatlasClusterPinnedFcvList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterPinnedFcvList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f6d6d255d383259e87afd0e8c944fe37c57a52c7af024e1641dfc4686f08eb47)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataMongodbatlasClusterPinnedFcvOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d21001687ff6937a92a55e2078261bc366748fd9e0249b3b56909a091dc50bb)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataMongodbatlasClusterPinnedFcvOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43a7dd473f507400c37bae7f8f455b66da579d32b8491864653d23a002bb195c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9af093ea05705543b2acc443882021c4d71d83a807ee039c463081c0748310a9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__20fb8cd74c6d1c522cfcdd7e5d5abca4c6eb323de21cd4f4ec30a76b023f7b00)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataMongodbatlasClusterPinnedFcvOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterPinnedFcvOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__69f097cdf0da4d057183341babddd9f00b0bf8dd7a03a2882301afe23f7a2166)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="expirationDate")
    def expiration_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "expirationDate"))

    @builtins.property
    @jsii.member(jsii_name="version")
    def version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "version"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataMongodbatlasClusterPinnedFcv]:
        return typing.cast(typing.Optional[DataMongodbatlasClusterPinnedFcv], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataMongodbatlasClusterPinnedFcv],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__328fbf1f20059e2d255232b931f530820f0d26503f24711c0dd7929699deaabf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterReplicationSpecs",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataMongodbatlasClusterReplicationSpecs:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataMongodbatlasClusterReplicationSpecs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataMongodbatlasClusterReplicationSpecsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterReplicationSpecsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bbb5711d5fce7b6d7903053d9bc450f03880687ea1cd33ed11831051b7b48c31)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataMongodbatlasClusterReplicationSpecsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__810c994cdc7796ed5aecea17e45662eb5703bfbaf79b93cd9f9373030e2f32a2)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataMongodbatlasClusterReplicationSpecsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0f22af6cd941a1938bc04a4727b89fced83e69d18ae3df4e11fea2cc14bbb9b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6bc13d2851fec675f2ea353639c4f93477ca9fe18a402760af07c82454664e6e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__21433cbc2855ea27fe1c321143b1ae4a4fd0c5147d462f6c671e14652938736e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataMongodbatlasClusterReplicationSpecsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterReplicationSpecsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a12da0295473f672431d9abb8d49a39fb25c8985f5d11d48a8ad5e80497c4ae1)
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
    @jsii.member(jsii_name="numShards")
    def num_shards(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numShards"))

    @builtins.property
    @jsii.member(jsii_name="regionsConfig")
    def regions_config(
        self,
    ) -> "DataMongodbatlasClusterReplicationSpecsRegionsConfigList":
        return typing.cast("DataMongodbatlasClusterReplicationSpecsRegionsConfigList", jsii.get(self, "regionsConfig"))

    @builtins.property
    @jsii.member(jsii_name="zoneName")
    def zone_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneName"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataMongodbatlasClusterReplicationSpecs]:
        return typing.cast(typing.Optional[DataMongodbatlasClusterReplicationSpecs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataMongodbatlasClusterReplicationSpecs],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46239319c2c2158b9e33152e597923f92a938636cc46a2596efbcbbaf09d8cca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterReplicationSpecsRegionsConfig",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataMongodbatlasClusterReplicationSpecsRegionsConfig:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataMongodbatlasClusterReplicationSpecsRegionsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataMongodbatlasClusterReplicationSpecsRegionsConfigList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterReplicationSpecsRegionsConfigList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__79577cea6bc650b187a64c1b429e459279b76f24ef46a01d96c9a12e830a1195)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataMongodbatlasClusterReplicationSpecsRegionsConfigOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40cb2904f778dde65057e7f81f0e7348c28df5cc2b8d7f3033c067175fb2cc40)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataMongodbatlasClusterReplicationSpecsRegionsConfigOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cb4b0ae4cc89a5e01d4862b96bd46e4ad27176e7435b997911e577abdaad942)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6146815b498d2bb75c2a6bfa24438aff34273b9db9d558fc06b1f61c3c5cf6e5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__37a0be3b4622ef03be25304dd7310836f7c7b948763d83e143b87e8db04bdcb6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataMongodbatlasClusterReplicationSpecsRegionsConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterReplicationSpecsRegionsConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5e0820eff3afb02cc63f1a7877bd5b6d23a67bdc86174e45dc3875bec1442579)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="analyticsNodes")
    def analytics_nodes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "analyticsNodes"))

    @builtins.property
    @jsii.member(jsii_name="electableNodes")
    def electable_nodes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "electableNodes"))

    @builtins.property
    @jsii.member(jsii_name="priority")
    def priority(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "priority"))

    @builtins.property
    @jsii.member(jsii_name="readOnlyNodes")
    def read_only_nodes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "readOnlyNodes"))

    @builtins.property
    @jsii.member(jsii_name="regionName")
    def region_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "regionName"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataMongodbatlasClusterReplicationSpecsRegionsConfig]:
        return typing.cast(typing.Optional[DataMongodbatlasClusterReplicationSpecsRegionsConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataMongodbatlasClusterReplicationSpecsRegionsConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eec5b9d2cc15986e7347ec37b180ffbbb185b421c91f4608e43590227956fafa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterSnapshotBackupPolicy",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataMongodbatlasClusterSnapshotBackupPolicy:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataMongodbatlasClusterSnapshotBackupPolicy(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataMongodbatlasClusterSnapshotBackupPolicyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterSnapshotBackupPolicyList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0be734ce9b97c14979906394e6c48a3851970782dfc8ef76901bba014a92dfa8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataMongodbatlasClusterSnapshotBackupPolicyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9fcf9b4d93a2e37ae40da70ca3fde98edd223297d150c49ec2afa3e18cd5730a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataMongodbatlasClusterSnapshotBackupPolicyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43baa698c32fbc6f563151990f412f600eff78bff2855cdd6751037f745d7246)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9294afb042bd549b18c5c4a5d3e72d525ddf67e0f61422f1f288de50a930ae29)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0ebcf47aa10a6a7bda1952c4f9788d0fc86e288b435fd3068fa53b9eb4dbc980)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataMongodbatlasClusterSnapshotBackupPolicyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterSnapshotBackupPolicyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b2e4c8a724a4a02c0032fe856fbbaa5dad2fec5efa74c7bc83685e3f3ec8794e)
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
    def policies(self) -> "DataMongodbatlasClusterSnapshotBackupPolicyPoliciesList":
        return typing.cast("DataMongodbatlasClusterSnapshotBackupPolicyPoliciesList", jsii.get(self, "policies"))

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
    def internal_value(
        self,
    ) -> typing.Optional[DataMongodbatlasClusterSnapshotBackupPolicy]:
        return typing.cast(typing.Optional[DataMongodbatlasClusterSnapshotBackupPolicy], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataMongodbatlasClusterSnapshotBackupPolicy],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ae2d8a207f9487271d04af3eb16097909fc235ce286f7a7bcdf4fcb865afeb7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterSnapshotBackupPolicyPolicies",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataMongodbatlasClusterSnapshotBackupPolicyPolicies:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataMongodbatlasClusterSnapshotBackupPolicyPolicies(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataMongodbatlasClusterSnapshotBackupPolicyPoliciesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterSnapshotBackupPolicyPoliciesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d0696d9abfbe4456119dc5c7e815d76c0fea56751156f593d9413499eddcb272)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataMongodbatlasClusterSnapshotBackupPolicyPoliciesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13d498575d865f0d38635cb569af13e9fad0163be517c0ee8a9b1927ae637860)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataMongodbatlasClusterSnapshotBackupPolicyPoliciesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f54581b01ddf96b10eae380832063bfe35c4b249fedf53c5220a58e4075a7b11)
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
            type_hints = typing.get_type_hints(_typecheckingstub__807244868087bf108c5e410dfa9fdf9e881048aeb1d4688dce9409bbbb1773af)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8e11fb4d8fda2454e6511c1802a9d9db25f254c94413047962727579260817a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataMongodbatlasClusterSnapshotBackupPolicyPoliciesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterSnapshotBackupPolicyPoliciesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3e3a2f393329696f67179306e730a2c4195d377313e74c58a27b5f36ff7cc08f)
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
    def policy_item(
        self,
    ) -> "DataMongodbatlasClusterSnapshotBackupPolicyPoliciesPolicyItemList":
        return typing.cast("DataMongodbatlasClusterSnapshotBackupPolicyPoliciesPolicyItemList", jsii.get(self, "policyItem"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataMongodbatlasClusterSnapshotBackupPolicyPolicies]:
        return typing.cast(typing.Optional[DataMongodbatlasClusterSnapshotBackupPolicyPolicies], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataMongodbatlasClusterSnapshotBackupPolicyPolicies],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__092d75e1217d7bff62e2809835d54997c10a6089bdba1f990eb17f2e0ea5a4de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterSnapshotBackupPolicyPoliciesPolicyItem",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataMongodbatlasClusterSnapshotBackupPolicyPoliciesPolicyItem:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataMongodbatlasClusterSnapshotBackupPolicyPoliciesPolicyItem(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataMongodbatlasClusterSnapshotBackupPolicyPoliciesPolicyItemList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterSnapshotBackupPolicyPoliciesPolicyItemList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__67ca24a05c56e6112096d2148150ea52cdc328833749ecb95bfc0994a698bade)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataMongodbatlasClusterSnapshotBackupPolicyPoliciesPolicyItemOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__850026c1fa4d61352f9b52d693ce3b5d07e518c666cc36e502e759f1c91ca2c2)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataMongodbatlasClusterSnapshotBackupPolicyPoliciesPolicyItemOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0cd3f10662d582e92825b4c85cf561d4a7f7456ea9cf7468d9c38c2ffaf40417)
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
            type_hints = typing.get_type_hints(_typecheckingstub__657d44b4cfbfb205f97266156ced03a4820c53a742d313691bb69bbca369b3a7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__342b9390e04b8a16129ac6ae21b449d5e5f18b3f082513c415f681ddf96fa230)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataMongodbatlasClusterSnapshotBackupPolicyPoliciesPolicyItemOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterSnapshotBackupPolicyPoliciesPolicyItemOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__912ab83dff148039d5a12403fb2d9cb855896fce4a166e30eb5dcf38de4343bb)
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
    ) -> typing.Optional[DataMongodbatlasClusterSnapshotBackupPolicyPoliciesPolicyItem]:
        return typing.cast(typing.Optional[DataMongodbatlasClusterSnapshotBackupPolicyPoliciesPolicyItem], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataMongodbatlasClusterSnapshotBackupPolicyPoliciesPolicyItem],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bafce830f1226c3f8cdb98e85daf0210f7e34f6452d3eb6ce3cf871af42edd3d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterTags",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataMongodbatlasClusterTags:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataMongodbatlasClusterTags(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataMongodbatlasClusterTagsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterTagsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bbdcb464190f962d774b296704e41a073a8da23317d9b127fa54716eddf0953c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "DataMongodbatlasClusterTagsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7079bdc52b368922b9b997d851949f7faa508ef620cbd162af323bab4993ea03)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataMongodbatlasClusterTagsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34791e936548b8579fa0ffb6c685478428a74e56dbe6ffefde2b56588040d39e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5dfb2b5cc78abff577780ad397a26086577ff53a12e06ae0277fa0dde6a589ae)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3c6ca25d5f180c5ee734f283a446a580febed201cc74a2eb8792cf86962ae5f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataMongodbatlasClusterTagsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasCluster.DataMongodbatlasClusterTagsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8bf59b4c75ea9ab19074ac08d9c1c1d6041b4d9a0f566e5ae06045cc23cbd142)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="key")
    def key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "key"))

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataMongodbatlasClusterTags]:
        return typing.cast(typing.Optional[DataMongodbatlasClusterTags], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataMongodbatlasClusterTags],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2de45c089df1cf07c5ab12bf1c6bfd8d6cf27fd29257a666660d8905dd71b31e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataMongodbatlasCluster",
    "DataMongodbatlasClusterAdvancedConfiguration",
    "DataMongodbatlasClusterAdvancedConfigurationList",
    "DataMongodbatlasClusterAdvancedConfigurationOutputReference",
    "DataMongodbatlasClusterBiConnectorConfig",
    "DataMongodbatlasClusterBiConnectorConfigList",
    "DataMongodbatlasClusterBiConnectorConfigOutputReference",
    "DataMongodbatlasClusterConfig",
    "DataMongodbatlasClusterConnectionStrings",
    "DataMongodbatlasClusterConnectionStringsList",
    "DataMongodbatlasClusterConnectionStringsOutputReference",
    "DataMongodbatlasClusterConnectionStringsPrivateEndpoint",
    "DataMongodbatlasClusterConnectionStringsPrivateEndpointEndpoints",
    "DataMongodbatlasClusterConnectionStringsPrivateEndpointEndpointsList",
    "DataMongodbatlasClusterConnectionStringsPrivateEndpointEndpointsOutputReference",
    "DataMongodbatlasClusterConnectionStringsPrivateEndpointList",
    "DataMongodbatlasClusterConnectionStringsPrivateEndpointOutputReference",
    "DataMongodbatlasClusterLabels",
    "DataMongodbatlasClusterLabelsList",
    "DataMongodbatlasClusterLabelsOutputReference",
    "DataMongodbatlasClusterPinnedFcv",
    "DataMongodbatlasClusterPinnedFcvList",
    "DataMongodbatlasClusterPinnedFcvOutputReference",
    "DataMongodbatlasClusterReplicationSpecs",
    "DataMongodbatlasClusterReplicationSpecsList",
    "DataMongodbatlasClusterReplicationSpecsOutputReference",
    "DataMongodbatlasClusterReplicationSpecsRegionsConfig",
    "DataMongodbatlasClusterReplicationSpecsRegionsConfigList",
    "DataMongodbatlasClusterReplicationSpecsRegionsConfigOutputReference",
    "DataMongodbatlasClusterSnapshotBackupPolicy",
    "DataMongodbatlasClusterSnapshotBackupPolicyList",
    "DataMongodbatlasClusterSnapshotBackupPolicyOutputReference",
    "DataMongodbatlasClusterSnapshotBackupPolicyPolicies",
    "DataMongodbatlasClusterSnapshotBackupPolicyPoliciesList",
    "DataMongodbatlasClusterSnapshotBackupPolicyPoliciesOutputReference",
    "DataMongodbatlasClusterSnapshotBackupPolicyPoliciesPolicyItem",
    "DataMongodbatlasClusterSnapshotBackupPolicyPoliciesPolicyItemList",
    "DataMongodbatlasClusterSnapshotBackupPolicyPoliciesPolicyItemOutputReference",
    "DataMongodbatlasClusterTags",
    "DataMongodbatlasClusterTagsList",
    "DataMongodbatlasClusterTagsOutputReference",
]

publication.publish()

def _typecheckingstub__0250acaa721230a8828d7166ac32cc1ad5bcbd89da30e2fd4a1911e6896e662c(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    project_id: builtins.str,
    id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__bcc3c4a8105656725583090c6cf2dfe6c00a5c68dedc46b149db668684694661(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26bb0a5238b27a29cd7e292b77347c6ae265ba125b646ec0d0489359e3678ed2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4cd2074c8e365f16873dfae83e2d08e26cbce8e69ed20b08469ee5523c31020(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3fcc92e99c39102c9218afad2701f7ebf0356ceb91850483376b85d582dbf8d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9bd131968d39d3243751480eda857eee48585cbf80a28f40d0a04643311be31(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__962a03b21e5620134f0f20bce9f7e551040c2f08d07df736e2c290af05b2eabb(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__764a3731ba3ae99a0e9b8f961a7aed2f18eb2def5a7bbd16429ecb9298039b57(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3e64d0d15ed96739b82e4dc010909b71458463ddfdfcd358305d7899f580dd5(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14362b65b014659f21488afe84e8d5c4d24a7b7f8e14ba7343504d17cbda1c36(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7895538c69f0e43a7ac717c3591645e70d8962b595d13c851782a6539d4c84db(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4798c45bb49795cf05eb52d030a2bc8a9117c0e29e3ef5c9eb63dccd2191cd6(
    value: typing.Optional[DataMongodbatlasClusterAdvancedConfiguration],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abe508952197406ce4fea5b81ae99f75a415e71ee26a595ef0c1071a2b33a3e7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89593909ffd5a0c3545fafe013bad98cf29d1b5b788f55b160fb588913649b87(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc3036d39a80d6e983f16d80e107269a32a72ba48bd77aac9f612851aecd1685(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56509c6cb86d3ebd5b5de5f8011afe85425375473f52ef132974483f284eca4c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f656abd58e93ed9c38cc0da33af9baaba0f5cb13722549938ab85321c890eb77(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48bde2d5688ba887a5c88efdeb755bae974aa565e10744fd29692a4badc9bd08(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52d15ffbe6fbfb1df69e144511f56291515e91395463095ff8eaa4829e715709(
    value: typing.Optional[DataMongodbatlasClusterBiConnectorConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93fc09cc4c3cb912b4b8b442c73f04b8a294c203bc4f17b073bb7924ffc38054(
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
    id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8527ee9f80574814ead88bca26557c573a7fd05364f4c83895146a19192782bb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c18bfad12e5eff7cdf992000179c63503238015e977325f0887861e3dff36d9(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62b880265c7707252b61c025e719573b202cbe61a319041b649950ff617a35e0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8b520be7384128225ee798f527accf17fffd7dc94aa82cf957ba72f6b5ffc11(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c6c52e05982a26de53638795f6072758b3bd2acae111842db062a8a40233e2f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9076da1291915d25296b17893dc1d09f005f7e29a97fc7f74efab23a4d98fe9f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b0fdca1c2832a26aafc358a81b660cdbe64b095d42c59c42227a6785b69acc4(
    value: typing.Optional[DataMongodbatlasClusterConnectionStrings],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6338bf1b793e3285b87fbe6afe5193652966afbc2cc4cac994060f9c583ca258(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__355f388a66485310e0932f6f20e757632fd742f5c1224321c2f5a4eb26f8346e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e2b782e71120ef2a04277e124f130a880fa0ba7aa4c9005a1f7fb478d9b9ac5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__356dd9cef5670e4ce9f81dbd391618e033523363fd05fdd0492d58f994f7e595(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3972e09f1a6339161c95ad9b29e8d3e4646857822e10e1195e779a2dd3c5c08f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28b2770d052777e7afaa59616cb85b8b1d180229e6747ae0b0a85607ae08cf06(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb3207d6a8273fe42bc91c4335da793677b32e4d8acc5a72fb8de332f59fb085(
    value: typing.Optional[DataMongodbatlasClusterConnectionStringsPrivateEndpointEndpoints],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54c52c87c0d8a685eff16e614542f7386639787d7657c3ba81676b2fe690dde0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69301cf8938eb927ed995d0205ae4ee536816aefa126b04ceb005ecff60d59ff(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d71299e1eed6fe3c9effb9efe03c520661f396653c3983806fd5cc422051f39f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63679b0f7dad15543f0b4709ddfdd0bdfdce62eb28ba986c45e0bb547a361264(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b172dd83ab8b773b50398cbc9852447898f197eb058795772016820142996d4(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e961164c756923e8f661436e31eedc4336df6f58f5c5435991cf7995a137c9d4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65dd847c5ec0ba0e89ba57884299af16a2f06170e64f996bab2fb363549048d9(
    value: typing.Optional[DataMongodbatlasClusterConnectionStringsPrivateEndpoint],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47773551bad8a7ba427f66e593d40418023c2dc0c780e7557e81fc9f7935a719(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b858a3aaeddc852811dd75d5df3cbeade63918602a8abd2646137365f526ebb1(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34f4e1f51348affeb363e845e191463639511d1ced5d8e63dffb5359e3a0e8f9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9000cd23798afce7db1b9dcb81a447b49b6b2627ba7770cc5090f5c3d27fa38e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7e097573230512bf04063f9daa8e19687462b390192dd8b6805384997b318dc(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b36cf262f999463450a3742afc440fc701e55cff1593c841f6908d69a94bb68c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2ddf5bd4b5335815717c527401d0d9fc9ea9ab2926673fedb0cf3997d202dd2(
    value: typing.Optional[DataMongodbatlasClusterLabels],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6d6d255d383259e87afd0e8c944fe37c57a52c7af024e1641dfc4686f08eb47(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d21001687ff6937a92a55e2078261bc366748fd9e0249b3b56909a091dc50bb(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43a7dd473f507400c37bae7f8f455b66da579d32b8491864653d23a002bb195c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9af093ea05705543b2acc443882021c4d71d83a807ee039c463081c0748310a9(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20fb8cd74c6d1c522cfcdd7e5d5abca4c6eb323de21cd4f4ec30a76b023f7b00(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69f097cdf0da4d057183341babddd9f00b0bf8dd7a03a2882301afe23f7a2166(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__328fbf1f20059e2d255232b931f530820f0d26503f24711c0dd7929699deaabf(
    value: typing.Optional[DataMongodbatlasClusterPinnedFcv],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbb5711d5fce7b6d7903053d9bc450f03880687ea1cd33ed11831051b7b48c31(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__810c994cdc7796ed5aecea17e45662eb5703bfbaf79b93cd9f9373030e2f32a2(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0f22af6cd941a1938bc04a4727b89fced83e69d18ae3df4e11fea2cc14bbb9b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6bc13d2851fec675f2ea353639c4f93477ca9fe18a402760af07c82454664e6e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21433cbc2855ea27fe1c321143b1ae4a4fd0c5147d462f6c671e14652938736e(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a12da0295473f672431d9abb8d49a39fb25c8985f5d11d48a8ad5e80497c4ae1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46239319c2c2158b9e33152e597923f92a938636cc46a2596efbcbbaf09d8cca(
    value: typing.Optional[DataMongodbatlasClusterReplicationSpecs],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79577cea6bc650b187a64c1b429e459279b76f24ef46a01d96c9a12e830a1195(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40cb2904f778dde65057e7f81f0e7348c28df5cc2b8d7f3033c067175fb2cc40(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cb4b0ae4cc89a5e01d4862b96bd46e4ad27176e7435b997911e577abdaad942(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6146815b498d2bb75c2a6bfa24438aff34273b9db9d558fc06b1f61c3c5cf6e5(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37a0be3b4622ef03be25304dd7310836f7c7b948763d83e143b87e8db04bdcb6(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e0820eff3afb02cc63f1a7877bd5b6d23a67bdc86174e45dc3875bec1442579(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eec5b9d2cc15986e7347ec37b180ffbbb185b421c91f4608e43590227956fafa(
    value: typing.Optional[DataMongodbatlasClusterReplicationSpecsRegionsConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0be734ce9b97c14979906394e6c48a3851970782dfc8ef76901bba014a92dfa8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fcf9b4d93a2e37ae40da70ca3fde98edd223297d150c49ec2afa3e18cd5730a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43baa698c32fbc6f563151990f412f600eff78bff2855cdd6751037f745d7246(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9294afb042bd549b18c5c4a5d3e72d525ddf67e0f61422f1f288de50a930ae29(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ebcf47aa10a6a7bda1952c4f9788d0fc86e288b435fd3068fa53b9eb4dbc980(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2e4c8a724a4a02c0032fe856fbbaa5dad2fec5efa74c7bc83685e3f3ec8794e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ae2d8a207f9487271d04af3eb16097909fc235ce286f7a7bcdf4fcb865afeb7(
    value: typing.Optional[DataMongodbatlasClusterSnapshotBackupPolicy],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0696d9abfbe4456119dc5c7e815d76c0fea56751156f593d9413499eddcb272(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13d498575d865f0d38635cb569af13e9fad0163be517c0ee8a9b1927ae637860(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f54581b01ddf96b10eae380832063bfe35c4b249fedf53c5220a58e4075a7b11(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__807244868087bf108c5e410dfa9fdf9e881048aeb1d4688dce9409bbbb1773af(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e11fb4d8fda2454e6511c1802a9d9db25f254c94413047962727579260817a3(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e3a2f393329696f67179306e730a2c4195d377313e74c58a27b5f36ff7cc08f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__092d75e1217d7bff62e2809835d54997c10a6089bdba1f990eb17f2e0ea5a4de(
    value: typing.Optional[DataMongodbatlasClusterSnapshotBackupPolicyPolicies],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67ca24a05c56e6112096d2148150ea52cdc328833749ecb95bfc0994a698bade(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__850026c1fa4d61352f9b52d693ce3b5d07e518c666cc36e502e759f1c91ca2c2(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0cd3f10662d582e92825b4c85cf561d4a7f7456ea9cf7468d9c38c2ffaf40417(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__657d44b4cfbfb205f97266156ced03a4820c53a742d313691bb69bbca369b3a7(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__342b9390e04b8a16129ac6ae21b449d5e5f18b3f082513c415f681ddf96fa230(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__912ab83dff148039d5a12403fb2d9cb855896fce4a166e30eb5dcf38de4343bb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bafce830f1226c3f8cdb98e85daf0210f7e34f6452d3eb6ce3cf871af42edd3d(
    value: typing.Optional[DataMongodbatlasClusterSnapshotBackupPolicyPoliciesPolicyItem],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbdcb464190f962d774b296704e41a073a8da23317d9b127fa54716eddf0953c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7079bdc52b368922b9b997d851949f7faa508ef620cbd162af323bab4993ea03(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34791e936548b8579fa0ffb6c685478428a74e56dbe6ffefde2b56588040d39e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5dfb2b5cc78abff577780ad397a26086577ff53a12e06ae0277fa0dde6a589ae(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c6ca25d5f180c5ee734f283a446a580febed201cc74a2eb8792cf86962ae5f4(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8bf59b4c75ea9ab19074ac08d9c1c1d6041b4d9a0f566e5ae06045cc23cbd142(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2de45c089df1cf07c5ab12bf1c6bfd8d6cf27fd29257a666660d8905dd71b31e(
    value: typing.Optional[DataMongodbatlasClusterTags],
) -> None:
    """Type checking stubs"""
    pass
