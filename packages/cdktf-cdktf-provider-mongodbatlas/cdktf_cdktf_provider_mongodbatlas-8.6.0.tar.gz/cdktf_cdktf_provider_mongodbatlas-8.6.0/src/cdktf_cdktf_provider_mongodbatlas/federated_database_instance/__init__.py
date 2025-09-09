r'''
# `mongodbatlas_federated_database_instance`

Refer to the Terraform Registry for docs: [`mongodbatlas_federated_database_instance`](https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance).
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


class FederatedDatabaseInstance(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.federatedDatabaseInstance.FederatedDatabaseInstance",
):
    '''Represents a {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance mongodbatlas_federated_database_instance}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        project_id: builtins.str,
        cloud_provider_config: typing.Optional[typing.Union["FederatedDatabaseInstanceCloudProviderConfig", typing.Dict[builtins.str, typing.Any]]] = None,
        data_process_region: typing.Optional[typing.Union["FederatedDatabaseInstanceDataProcessRegion", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        storage_databases: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["FederatedDatabaseInstanceStorageDatabases", typing.Dict[builtins.str, typing.Any]]]]] = None,
        storage_stores: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["FederatedDatabaseInstanceStorageStores", typing.Dict[builtins.str, typing.Any]]]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance mongodbatlas_federated_database_instance} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#name FederatedDatabaseInstance#name}.
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#project_id FederatedDatabaseInstance#project_id}.
        :param cloud_provider_config: cloud_provider_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#cloud_provider_config FederatedDatabaseInstance#cloud_provider_config}
        :param data_process_region: data_process_region block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#data_process_region FederatedDatabaseInstance#data_process_region}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#id FederatedDatabaseInstance#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param storage_databases: storage_databases block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#storage_databases FederatedDatabaseInstance#storage_databases}
        :param storage_stores: storage_stores block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#storage_stores FederatedDatabaseInstance#storage_stores}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6cb69c6e47c3a4872d6765991e11b7ab3d605ca3bad4198ba056319841715d4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = FederatedDatabaseInstanceConfig(
            name=name,
            project_id=project_id,
            cloud_provider_config=cloud_provider_config,
            data_process_region=data_process_region,
            id=id,
            storage_databases=storage_databases,
            storage_stores=storage_stores,
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
        '''Generates CDKTF code for importing a FederatedDatabaseInstance resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the FederatedDatabaseInstance to import.
        :param import_from_id: The id of the existing FederatedDatabaseInstance that should be imported. Refer to the {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the FederatedDatabaseInstance to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a5c5a9e0c04919964c7c11416d8d16d71a2dbcf6a9b6885808d9c3a051294e5)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putCloudProviderConfig")
    def put_cloud_provider_config(
        self,
        *,
        aws: typing.Optional[typing.Union["FederatedDatabaseInstanceCloudProviderConfigAws", typing.Dict[builtins.str, typing.Any]]] = None,
        azure: typing.Optional[typing.Union["FederatedDatabaseInstanceCloudProviderConfigAzure", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param aws: aws block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#aws FederatedDatabaseInstance#aws}
        :param azure: azure block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#azure FederatedDatabaseInstance#azure}
        '''
        value = FederatedDatabaseInstanceCloudProviderConfig(aws=aws, azure=azure)

        return typing.cast(None, jsii.invoke(self, "putCloudProviderConfig", [value]))

    @jsii.member(jsii_name="putDataProcessRegion")
    def put_data_process_region(
        self,
        *,
        cloud_provider: builtins.str,
        region: builtins.str,
    ) -> None:
        '''
        :param cloud_provider: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#cloud_provider FederatedDatabaseInstance#cloud_provider}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#region FederatedDatabaseInstance#region}.
        '''
        value = FederatedDatabaseInstanceDataProcessRegion(
            cloud_provider=cloud_provider, region=region
        )

        return typing.cast(None, jsii.invoke(self, "putDataProcessRegion", [value]))

    @jsii.member(jsii_name="putStorageDatabases")
    def put_storage_databases(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["FederatedDatabaseInstanceStorageDatabases", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b38fc28a2adabe2b0b747e74c098379668d2133c4d0d48d6f59292b3c0c3f313)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putStorageDatabases", [value]))

    @jsii.member(jsii_name="putStorageStores")
    def put_storage_stores(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["FederatedDatabaseInstanceStorageStores", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fc642e50180406b79901a9b8ee7d2acfd91196e6dcf8326dc6fce0d3bbe65d3a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putStorageStores", [value]))

    @jsii.member(jsii_name="resetCloudProviderConfig")
    def reset_cloud_provider_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCloudProviderConfig", []))

    @jsii.member(jsii_name="resetDataProcessRegion")
    def reset_data_process_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataProcessRegion", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetStorageDatabases")
    def reset_storage_databases(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageDatabases", []))

    @jsii.member(jsii_name="resetStorageStores")
    def reset_storage_stores(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStorageStores", []))

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
    @jsii.member(jsii_name="cloudProviderConfig")
    def cloud_provider_config(
        self,
    ) -> "FederatedDatabaseInstanceCloudProviderConfigOutputReference":
        return typing.cast("FederatedDatabaseInstanceCloudProviderConfigOutputReference", jsii.get(self, "cloudProviderConfig"))

    @builtins.property
    @jsii.member(jsii_name="dataProcessRegion")
    def data_process_region(
        self,
    ) -> "FederatedDatabaseInstanceDataProcessRegionOutputReference":
        return typing.cast("FederatedDatabaseInstanceDataProcessRegionOutputReference", jsii.get(self, "dataProcessRegion"))

    @builtins.property
    @jsii.member(jsii_name="hostnames")
    def hostnames(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "hostnames"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="storageDatabases")
    def storage_databases(self) -> "FederatedDatabaseInstanceStorageDatabasesList":
        return typing.cast("FederatedDatabaseInstanceStorageDatabasesList", jsii.get(self, "storageDatabases"))

    @builtins.property
    @jsii.member(jsii_name="storageStores")
    def storage_stores(self) -> "FederatedDatabaseInstanceStorageStoresList":
        return typing.cast("FederatedDatabaseInstanceStorageStoresList", jsii.get(self, "storageStores"))

    @builtins.property
    @jsii.member(jsii_name="cloudProviderConfigInput")
    def cloud_provider_config_input(
        self,
    ) -> typing.Optional["FederatedDatabaseInstanceCloudProviderConfig"]:
        return typing.cast(typing.Optional["FederatedDatabaseInstanceCloudProviderConfig"], jsii.get(self, "cloudProviderConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="dataProcessRegionInput")
    def data_process_region_input(
        self,
    ) -> typing.Optional["FederatedDatabaseInstanceDataProcessRegion"]:
        return typing.cast(typing.Optional["FederatedDatabaseInstanceDataProcessRegion"], jsii.get(self, "dataProcessRegionInput"))

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
    @jsii.member(jsii_name="storageDatabasesInput")
    def storage_databases_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["FederatedDatabaseInstanceStorageDatabases"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["FederatedDatabaseInstanceStorageDatabases"]]], jsii.get(self, "storageDatabasesInput"))

    @builtins.property
    @jsii.member(jsii_name="storageStoresInput")
    def storage_stores_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["FederatedDatabaseInstanceStorageStores"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["FederatedDatabaseInstanceStorageStores"]]], jsii.get(self, "storageStoresInput"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98767f1d78a7f96e0ca91f7fb29b2a27566ebbaff78b6b390723d6c5d59794da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b10a40c749e5863765e6e1a061a787f7544d94e17b4a9bf40b356e5b6174d47d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c9c9c414b3245ce744ea1f8cc3b5c94de158aa3a158c0da54b6602872dcfb94e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.federatedDatabaseInstance.FederatedDatabaseInstanceCloudProviderConfig",
    jsii_struct_bases=[],
    name_mapping={"aws": "aws", "azure": "azure"},
)
class FederatedDatabaseInstanceCloudProviderConfig:
    def __init__(
        self,
        *,
        aws: typing.Optional[typing.Union["FederatedDatabaseInstanceCloudProviderConfigAws", typing.Dict[builtins.str, typing.Any]]] = None,
        azure: typing.Optional[typing.Union["FederatedDatabaseInstanceCloudProviderConfigAzure", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param aws: aws block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#aws FederatedDatabaseInstance#aws}
        :param azure: azure block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#azure FederatedDatabaseInstance#azure}
        '''
        if isinstance(aws, dict):
            aws = FederatedDatabaseInstanceCloudProviderConfigAws(**aws)
        if isinstance(azure, dict):
            azure = FederatedDatabaseInstanceCloudProviderConfigAzure(**azure)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74f449b7f46e263a6a36dcdc6c35858cab6e69f6e1f7274938b99e7c5676b134)
            check_type(argname="argument aws", value=aws, expected_type=type_hints["aws"])
            check_type(argname="argument azure", value=azure, expected_type=type_hints["azure"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if aws is not None:
            self._values["aws"] = aws
        if azure is not None:
            self._values["azure"] = azure

    @builtins.property
    def aws(self) -> typing.Optional["FederatedDatabaseInstanceCloudProviderConfigAws"]:
        '''aws block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#aws FederatedDatabaseInstance#aws}
        '''
        result = self._values.get("aws")
        return typing.cast(typing.Optional["FederatedDatabaseInstanceCloudProviderConfigAws"], result)

    @builtins.property
    def azure(
        self,
    ) -> typing.Optional["FederatedDatabaseInstanceCloudProviderConfigAzure"]:
        '''azure block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#azure FederatedDatabaseInstance#azure}
        '''
        result = self._values.get("azure")
        return typing.cast(typing.Optional["FederatedDatabaseInstanceCloudProviderConfigAzure"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FederatedDatabaseInstanceCloudProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.federatedDatabaseInstance.FederatedDatabaseInstanceCloudProviderConfigAws",
    jsii_struct_bases=[],
    name_mapping={"role_id": "roleId", "test_s3_bucket": "testS3Bucket"},
)
class FederatedDatabaseInstanceCloudProviderConfigAws:
    def __init__(self, *, role_id: builtins.str, test_s3_bucket: builtins.str) -> None:
        '''
        :param role_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#role_id FederatedDatabaseInstance#role_id}.
        :param test_s3_bucket: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#test_s3_bucket FederatedDatabaseInstance#test_s3_bucket}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4c01fba96e2e6b2e2f2d767ff7128345a7856051c1bbd78d7ada58c9398bca6)
            check_type(argname="argument role_id", value=role_id, expected_type=type_hints["role_id"])
            check_type(argname="argument test_s3_bucket", value=test_s3_bucket, expected_type=type_hints["test_s3_bucket"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "role_id": role_id,
            "test_s3_bucket": test_s3_bucket,
        }

    @builtins.property
    def role_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#role_id FederatedDatabaseInstance#role_id}.'''
        result = self._values.get("role_id")
        assert result is not None, "Required property 'role_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def test_s3_bucket(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#test_s3_bucket FederatedDatabaseInstance#test_s3_bucket}.'''
        result = self._values.get("test_s3_bucket")
        assert result is not None, "Required property 'test_s3_bucket' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FederatedDatabaseInstanceCloudProviderConfigAws(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FederatedDatabaseInstanceCloudProviderConfigAwsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.federatedDatabaseInstance.FederatedDatabaseInstanceCloudProviderConfigAwsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__afc0823de14f680380d9b5c2834571f54a4f5c4610d4508040ccb69c2dee3adf)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="externalId")
    def external_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "externalId"))

    @builtins.property
    @jsii.member(jsii_name="iamAssumedRoleArn")
    def iam_assumed_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "iamAssumedRoleArn"))

    @builtins.property
    @jsii.member(jsii_name="iamUserArn")
    def iam_user_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "iamUserArn"))

    @builtins.property
    @jsii.member(jsii_name="roleIdInput")
    def role_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleIdInput"))

    @builtins.property
    @jsii.member(jsii_name="testS3BucketInput")
    def test_s3_bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "testS3BucketInput"))

    @builtins.property
    @jsii.member(jsii_name="roleId")
    def role_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleId"))

    @role_id.setter
    def role_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76889cff24c0129fd721ef0d27968e343e92ccb29e7f9da27b81b9e153afb1ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "roleId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="testS3Bucket")
    def test_s3_bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "testS3Bucket"))

    @test_s3_bucket.setter
    def test_s3_bucket(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ba2c74aead7d7f2ab7218423518cb1f5a4c538494de351e2a1c99b8a709e5d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "testS3Bucket", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[FederatedDatabaseInstanceCloudProviderConfigAws]:
        return typing.cast(typing.Optional[FederatedDatabaseInstanceCloudProviderConfigAws], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[FederatedDatabaseInstanceCloudProviderConfigAws],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed8bd9093e7209f6f67bf1c90b01cf12290ef8b957d51eb823f2be8a29e89791)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.federatedDatabaseInstance.FederatedDatabaseInstanceCloudProviderConfigAzure",
    jsii_struct_bases=[],
    name_mapping={"role_id": "roleId"},
)
class FederatedDatabaseInstanceCloudProviderConfigAzure:
    def __init__(self, *, role_id: builtins.str) -> None:
        '''
        :param role_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#role_id FederatedDatabaseInstance#role_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd87bf0fd71e12c847619d496b6618e4230e90860a8f86981dbbfa84764b9713)
            check_type(argname="argument role_id", value=role_id, expected_type=type_hints["role_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "role_id": role_id,
        }

    @builtins.property
    def role_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#role_id FederatedDatabaseInstance#role_id}.'''
        result = self._values.get("role_id")
        assert result is not None, "Required property 'role_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FederatedDatabaseInstanceCloudProviderConfigAzure(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FederatedDatabaseInstanceCloudProviderConfigAzureOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.federatedDatabaseInstance.FederatedDatabaseInstanceCloudProviderConfigAzureOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d38dbaf8f115be67b06c2ccb0e72dbfee4b6a46b0c1df7e8fe99983b5a6ed3af)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="atlasAppId")
    def atlas_app_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "atlasAppId"))

    @builtins.property
    @jsii.member(jsii_name="servicePrincipalId")
    def service_principal_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "servicePrincipalId"))

    @builtins.property
    @jsii.member(jsii_name="tenantId")
    def tenant_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tenantId"))

    @builtins.property
    @jsii.member(jsii_name="roleIdInput")
    def role_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleIdInput"))

    @builtins.property
    @jsii.member(jsii_name="roleId")
    def role_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleId"))

    @role_id.setter
    def role_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea99cb0a282606b7d229664d9c4d2339c1da8c8eb7d2ff2854d0228d19e4c2df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "roleId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[FederatedDatabaseInstanceCloudProviderConfigAzure]:
        return typing.cast(typing.Optional[FederatedDatabaseInstanceCloudProviderConfigAzure], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[FederatedDatabaseInstanceCloudProviderConfigAzure],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d96ed7117d03e0efb739dea14ceb5cef624aeff43a7ed51bf10da1eb6732bc7d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class FederatedDatabaseInstanceCloudProviderConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.federatedDatabaseInstance.FederatedDatabaseInstanceCloudProviderConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__960a4d78ce9b0c89399c7ed7e128b1c3bdb9e932dbad447af78b92ec7db092f4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAws")
    def put_aws(self, *, role_id: builtins.str, test_s3_bucket: builtins.str) -> None:
        '''
        :param role_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#role_id FederatedDatabaseInstance#role_id}.
        :param test_s3_bucket: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#test_s3_bucket FederatedDatabaseInstance#test_s3_bucket}.
        '''
        value = FederatedDatabaseInstanceCloudProviderConfigAws(
            role_id=role_id, test_s3_bucket=test_s3_bucket
        )

        return typing.cast(None, jsii.invoke(self, "putAws", [value]))

    @jsii.member(jsii_name="putAzure")
    def put_azure(self, *, role_id: builtins.str) -> None:
        '''
        :param role_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#role_id FederatedDatabaseInstance#role_id}.
        '''
        value = FederatedDatabaseInstanceCloudProviderConfigAzure(role_id=role_id)

        return typing.cast(None, jsii.invoke(self, "putAzure", [value]))

    @jsii.member(jsii_name="resetAws")
    def reset_aws(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAws", []))

    @jsii.member(jsii_name="resetAzure")
    def reset_azure(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzure", []))

    @builtins.property
    @jsii.member(jsii_name="aws")
    def aws(self) -> FederatedDatabaseInstanceCloudProviderConfigAwsOutputReference:
        return typing.cast(FederatedDatabaseInstanceCloudProviderConfigAwsOutputReference, jsii.get(self, "aws"))

    @builtins.property
    @jsii.member(jsii_name="azure")
    def azure(self) -> FederatedDatabaseInstanceCloudProviderConfigAzureOutputReference:
        return typing.cast(FederatedDatabaseInstanceCloudProviderConfigAzureOutputReference, jsii.get(self, "azure"))

    @builtins.property
    @jsii.member(jsii_name="awsInput")
    def aws_input(
        self,
    ) -> typing.Optional[FederatedDatabaseInstanceCloudProviderConfigAws]:
        return typing.cast(typing.Optional[FederatedDatabaseInstanceCloudProviderConfigAws], jsii.get(self, "awsInput"))

    @builtins.property
    @jsii.member(jsii_name="azureInput")
    def azure_input(
        self,
    ) -> typing.Optional[FederatedDatabaseInstanceCloudProviderConfigAzure]:
        return typing.cast(typing.Optional[FederatedDatabaseInstanceCloudProviderConfigAzure], jsii.get(self, "azureInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[FederatedDatabaseInstanceCloudProviderConfig]:
        return typing.cast(typing.Optional[FederatedDatabaseInstanceCloudProviderConfig], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[FederatedDatabaseInstanceCloudProviderConfig],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a730cbefbefd77e8d9acc8cefa3b4373f304cacf7861af3b789da3cb2d30bec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.federatedDatabaseInstance.FederatedDatabaseInstanceConfig",
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
        "cloud_provider_config": "cloudProviderConfig",
        "data_process_region": "dataProcessRegion",
        "id": "id",
        "storage_databases": "storageDatabases",
        "storage_stores": "storageStores",
    },
)
class FederatedDatabaseInstanceConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        cloud_provider_config: typing.Optional[typing.Union[FederatedDatabaseInstanceCloudProviderConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        data_process_region: typing.Optional[typing.Union["FederatedDatabaseInstanceDataProcessRegion", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        storage_databases: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["FederatedDatabaseInstanceStorageDatabases", typing.Dict[builtins.str, typing.Any]]]]] = None,
        storage_stores: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["FederatedDatabaseInstanceStorageStores", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#name FederatedDatabaseInstance#name}.
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#project_id FederatedDatabaseInstance#project_id}.
        :param cloud_provider_config: cloud_provider_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#cloud_provider_config FederatedDatabaseInstance#cloud_provider_config}
        :param data_process_region: data_process_region block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#data_process_region FederatedDatabaseInstance#data_process_region}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#id FederatedDatabaseInstance#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param storage_databases: storage_databases block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#storage_databases FederatedDatabaseInstance#storage_databases}
        :param storage_stores: storage_stores block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#storage_stores FederatedDatabaseInstance#storage_stores}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(cloud_provider_config, dict):
            cloud_provider_config = FederatedDatabaseInstanceCloudProviderConfig(**cloud_provider_config)
        if isinstance(data_process_region, dict):
            data_process_region = FederatedDatabaseInstanceDataProcessRegion(**data_process_region)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9a881efd4b865abcc37148d43ead1af588a3dd93a820e17f5d518a87ddbf007)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument cloud_provider_config", value=cloud_provider_config, expected_type=type_hints["cloud_provider_config"])
            check_type(argname="argument data_process_region", value=data_process_region, expected_type=type_hints["data_process_region"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument storage_databases", value=storage_databases, expected_type=type_hints["storage_databases"])
            check_type(argname="argument storage_stores", value=storage_stores, expected_type=type_hints["storage_stores"])
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
        if cloud_provider_config is not None:
            self._values["cloud_provider_config"] = cloud_provider_config
        if data_process_region is not None:
            self._values["data_process_region"] = data_process_region
        if id is not None:
            self._values["id"] = id
        if storage_databases is not None:
            self._values["storage_databases"] = storage_databases
        if storage_stores is not None:
            self._values["storage_stores"] = storage_stores

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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#name FederatedDatabaseInstance#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def project_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#project_id FederatedDatabaseInstance#project_id}.'''
        result = self._values.get("project_id")
        assert result is not None, "Required property 'project_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cloud_provider_config(
        self,
    ) -> typing.Optional[FederatedDatabaseInstanceCloudProviderConfig]:
        '''cloud_provider_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#cloud_provider_config FederatedDatabaseInstance#cloud_provider_config}
        '''
        result = self._values.get("cloud_provider_config")
        return typing.cast(typing.Optional[FederatedDatabaseInstanceCloudProviderConfig], result)

    @builtins.property
    def data_process_region(
        self,
    ) -> typing.Optional["FederatedDatabaseInstanceDataProcessRegion"]:
        '''data_process_region block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#data_process_region FederatedDatabaseInstance#data_process_region}
        '''
        result = self._values.get("data_process_region")
        return typing.cast(typing.Optional["FederatedDatabaseInstanceDataProcessRegion"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#id FederatedDatabaseInstance#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def storage_databases(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["FederatedDatabaseInstanceStorageDatabases"]]]:
        '''storage_databases block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#storage_databases FederatedDatabaseInstance#storage_databases}
        '''
        result = self._values.get("storage_databases")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["FederatedDatabaseInstanceStorageDatabases"]]], result)

    @builtins.property
    def storage_stores(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["FederatedDatabaseInstanceStorageStores"]]]:
        '''storage_stores block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#storage_stores FederatedDatabaseInstance#storage_stores}
        '''
        result = self._values.get("storage_stores")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["FederatedDatabaseInstanceStorageStores"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FederatedDatabaseInstanceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.federatedDatabaseInstance.FederatedDatabaseInstanceDataProcessRegion",
    jsii_struct_bases=[],
    name_mapping={"cloud_provider": "cloudProvider", "region": "region"},
)
class FederatedDatabaseInstanceDataProcessRegion:
    def __init__(self, *, cloud_provider: builtins.str, region: builtins.str) -> None:
        '''
        :param cloud_provider: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#cloud_provider FederatedDatabaseInstance#cloud_provider}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#region FederatedDatabaseInstance#region}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e90e6f9f6a14c8c877674641170d9c5d81b041c59288c2d612c3e35fed7aab1)
            check_type(argname="argument cloud_provider", value=cloud_provider, expected_type=type_hints["cloud_provider"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cloud_provider": cloud_provider,
            "region": region,
        }

    @builtins.property
    def cloud_provider(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#cloud_provider FederatedDatabaseInstance#cloud_provider}.'''
        result = self._values.get("cloud_provider")
        assert result is not None, "Required property 'cloud_provider' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#region FederatedDatabaseInstance#region}.'''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FederatedDatabaseInstanceDataProcessRegion(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FederatedDatabaseInstanceDataProcessRegionOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.federatedDatabaseInstance.FederatedDatabaseInstanceDataProcessRegionOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__616b59b95894ae827b299f58582ce95afea68995bca005de7c4d004bf61bba22)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

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
            type_hints = typing.get_type_hints(_typecheckingstub__8156f951cea46519adefb72f5e05b2815d7362536b0e6929762f568c06e55cde)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cloudProvider", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df655cdaf3a6bdfc2051408a11aeed49481825a5c2cef98d4015fca098a002e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[FederatedDatabaseInstanceDataProcessRegion]:
        return typing.cast(typing.Optional[FederatedDatabaseInstanceDataProcessRegion], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[FederatedDatabaseInstanceDataProcessRegion],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3d6d49ba95d3ecc36f6872a190e101297d0da87223e6f0df169cab3eab66667)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.federatedDatabaseInstance.FederatedDatabaseInstanceStorageDatabases",
    jsii_struct_bases=[],
    name_mapping={"collections": "collections", "name": "name", "views": "views"},
)
class FederatedDatabaseInstanceStorageDatabases:
    def __init__(
        self,
        *,
        collections: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["FederatedDatabaseInstanceStorageDatabasesCollections", typing.Dict[builtins.str, typing.Any]]]]] = None,
        name: typing.Optional[builtins.str] = None,
        views: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["FederatedDatabaseInstanceStorageDatabasesViews", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param collections: collections block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#collections FederatedDatabaseInstance#collections}
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#name FederatedDatabaseInstance#name}.
        :param views: views block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#views FederatedDatabaseInstance#views}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fbb235a63f9c6f74220659f285e8be0c820e25373d6be9553a29a9a57c806b4)
            check_type(argname="argument collections", value=collections, expected_type=type_hints["collections"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument views", value=views, expected_type=type_hints["views"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if collections is not None:
            self._values["collections"] = collections
        if name is not None:
            self._values["name"] = name
        if views is not None:
            self._values["views"] = views

    @builtins.property
    def collections(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["FederatedDatabaseInstanceStorageDatabasesCollections"]]]:
        '''collections block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#collections FederatedDatabaseInstance#collections}
        '''
        result = self._values.get("collections")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["FederatedDatabaseInstanceStorageDatabasesCollections"]]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#name FederatedDatabaseInstance#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def views(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["FederatedDatabaseInstanceStorageDatabasesViews"]]]:
        '''views block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#views FederatedDatabaseInstance#views}
        '''
        result = self._values.get("views")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["FederatedDatabaseInstanceStorageDatabasesViews"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FederatedDatabaseInstanceStorageDatabases(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.federatedDatabaseInstance.FederatedDatabaseInstanceStorageDatabasesCollections",
    jsii_struct_bases=[],
    name_mapping={"data_sources": "dataSources", "name": "name"},
)
class FederatedDatabaseInstanceStorageDatabasesCollections:
    def __init__(
        self,
        *,
        data_sources: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["FederatedDatabaseInstanceStorageDatabasesCollectionsDataSources", typing.Dict[builtins.str, typing.Any]]]]] = None,
        name: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param data_sources: data_sources block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#data_sources FederatedDatabaseInstance#data_sources}
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#name FederatedDatabaseInstance#name}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__606920a8ecd8a0087b6df654e282abb30e3c30446205e2aa34996a1147e356e3)
            check_type(argname="argument data_sources", value=data_sources, expected_type=type_hints["data_sources"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if data_sources is not None:
            self._values["data_sources"] = data_sources
        if name is not None:
            self._values["name"] = name

    @builtins.property
    def data_sources(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["FederatedDatabaseInstanceStorageDatabasesCollectionsDataSources"]]]:
        '''data_sources block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#data_sources FederatedDatabaseInstance#data_sources}
        '''
        result = self._values.get("data_sources")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["FederatedDatabaseInstanceStorageDatabasesCollectionsDataSources"]]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#name FederatedDatabaseInstance#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FederatedDatabaseInstanceStorageDatabasesCollections(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.federatedDatabaseInstance.FederatedDatabaseInstanceStorageDatabasesCollectionsDataSources",
    jsii_struct_bases=[],
    name_mapping={
        "allow_insecure": "allowInsecure",
        "collection": "collection",
        "collection_regex": "collectionRegex",
        "database": "database",
        "database_regex": "databaseRegex",
        "dataset_name": "datasetName",
        "default_format": "defaultFormat",
        "path": "path",
        "provenance_field_name": "provenanceFieldName",
        "store_name": "storeName",
        "urls": "urls",
    },
)
class FederatedDatabaseInstanceStorageDatabasesCollectionsDataSources:
    def __init__(
        self,
        *,
        allow_insecure: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        collection: typing.Optional[builtins.str] = None,
        collection_regex: typing.Optional[builtins.str] = None,
        database: typing.Optional[builtins.str] = None,
        database_regex: typing.Optional[builtins.str] = None,
        dataset_name: typing.Optional[builtins.str] = None,
        default_format: typing.Optional[builtins.str] = None,
        path: typing.Optional[builtins.str] = None,
        provenance_field_name: typing.Optional[builtins.str] = None,
        store_name: typing.Optional[builtins.str] = None,
        urls: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param allow_insecure: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#allow_insecure FederatedDatabaseInstance#allow_insecure}.
        :param collection: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#collection FederatedDatabaseInstance#collection}.
        :param collection_regex: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#collection_regex FederatedDatabaseInstance#collection_regex}.
        :param database: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#database FederatedDatabaseInstance#database}.
        :param database_regex: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#database_regex FederatedDatabaseInstance#database_regex}.
        :param dataset_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#dataset_name FederatedDatabaseInstance#dataset_name}.
        :param default_format: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#default_format FederatedDatabaseInstance#default_format}.
        :param path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#path FederatedDatabaseInstance#path}.
        :param provenance_field_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#provenance_field_name FederatedDatabaseInstance#provenance_field_name}.
        :param store_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#store_name FederatedDatabaseInstance#store_name}.
        :param urls: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#urls FederatedDatabaseInstance#urls}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1be73174fdbafe36c5eaaac1a154805e562561aea3242c1076fcddf77d0fdc10)
            check_type(argname="argument allow_insecure", value=allow_insecure, expected_type=type_hints["allow_insecure"])
            check_type(argname="argument collection", value=collection, expected_type=type_hints["collection"])
            check_type(argname="argument collection_regex", value=collection_regex, expected_type=type_hints["collection_regex"])
            check_type(argname="argument database", value=database, expected_type=type_hints["database"])
            check_type(argname="argument database_regex", value=database_regex, expected_type=type_hints["database_regex"])
            check_type(argname="argument dataset_name", value=dataset_name, expected_type=type_hints["dataset_name"])
            check_type(argname="argument default_format", value=default_format, expected_type=type_hints["default_format"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument provenance_field_name", value=provenance_field_name, expected_type=type_hints["provenance_field_name"])
            check_type(argname="argument store_name", value=store_name, expected_type=type_hints["store_name"])
            check_type(argname="argument urls", value=urls, expected_type=type_hints["urls"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if allow_insecure is not None:
            self._values["allow_insecure"] = allow_insecure
        if collection is not None:
            self._values["collection"] = collection
        if collection_regex is not None:
            self._values["collection_regex"] = collection_regex
        if database is not None:
            self._values["database"] = database
        if database_regex is not None:
            self._values["database_regex"] = database_regex
        if dataset_name is not None:
            self._values["dataset_name"] = dataset_name
        if default_format is not None:
            self._values["default_format"] = default_format
        if path is not None:
            self._values["path"] = path
        if provenance_field_name is not None:
            self._values["provenance_field_name"] = provenance_field_name
        if store_name is not None:
            self._values["store_name"] = store_name
        if urls is not None:
            self._values["urls"] = urls

    @builtins.property
    def allow_insecure(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#allow_insecure FederatedDatabaseInstance#allow_insecure}.'''
        result = self._values.get("allow_insecure")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def collection(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#collection FederatedDatabaseInstance#collection}.'''
        result = self._values.get("collection")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def collection_regex(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#collection_regex FederatedDatabaseInstance#collection_regex}.'''
        result = self._values.get("collection_regex")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def database(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#database FederatedDatabaseInstance#database}.'''
        result = self._values.get("database")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def database_regex(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#database_regex FederatedDatabaseInstance#database_regex}.'''
        result = self._values.get("database_regex")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dataset_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#dataset_name FederatedDatabaseInstance#dataset_name}.'''
        result = self._values.get("dataset_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_format(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#default_format FederatedDatabaseInstance#default_format}.'''
        result = self._values.get("default_format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#path FederatedDatabaseInstance#path}.'''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def provenance_field_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#provenance_field_name FederatedDatabaseInstance#provenance_field_name}.'''
        result = self._values.get("provenance_field_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def store_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#store_name FederatedDatabaseInstance#store_name}.'''
        result = self._values.get("store_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def urls(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#urls FederatedDatabaseInstance#urls}.'''
        result = self._values.get("urls")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FederatedDatabaseInstanceStorageDatabasesCollectionsDataSources(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FederatedDatabaseInstanceStorageDatabasesCollectionsDataSourcesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.federatedDatabaseInstance.FederatedDatabaseInstanceStorageDatabasesCollectionsDataSourcesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e76d166254ee33b0f2c5605497ed4e50c3ccf240f3fcfe50d27db33d13de76e0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "FederatedDatabaseInstanceStorageDatabasesCollectionsDataSourcesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5ff2cc68dce950bfa9da4662b7f368e299139189bbe600e16178e7de02e4643)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("FederatedDatabaseInstanceStorageDatabasesCollectionsDataSourcesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1fcef0b59f55ccc173883d4501fd71f59bba3806ad65f59dbdec959babf8cca4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4bd6121d18e66b70a2a8fd3573a67ccf81dd24cb1b7bb5a1cecfb63193689780)
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
            type_hints = typing.get_type_hints(_typecheckingstub__73edd7d6b7199931860f315ec334bb5bc74a1e613fc8ca1537742eedc35dd6c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FederatedDatabaseInstanceStorageDatabasesCollectionsDataSources]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FederatedDatabaseInstanceStorageDatabasesCollectionsDataSources]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FederatedDatabaseInstanceStorageDatabasesCollectionsDataSources]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea049e230860b850213525e40d651e673c09ca927224165053b12e9fa05e54ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class FederatedDatabaseInstanceStorageDatabasesCollectionsDataSourcesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.federatedDatabaseInstance.FederatedDatabaseInstanceStorageDatabasesCollectionsDataSourcesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__944300362dc69806d481a1370bbed348c62e316e1cc81e0d3318ca307e946ccf)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetAllowInsecure")
    def reset_allow_insecure(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowInsecure", []))

    @jsii.member(jsii_name="resetCollection")
    def reset_collection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCollection", []))

    @jsii.member(jsii_name="resetCollectionRegex")
    def reset_collection_regex(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCollectionRegex", []))

    @jsii.member(jsii_name="resetDatabase")
    def reset_database(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatabase", []))

    @jsii.member(jsii_name="resetDatabaseRegex")
    def reset_database_regex(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatabaseRegex", []))

    @jsii.member(jsii_name="resetDatasetName")
    def reset_dataset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatasetName", []))

    @jsii.member(jsii_name="resetDefaultFormat")
    def reset_default_format(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultFormat", []))

    @jsii.member(jsii_name="resetPath")
    def reset_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPath", []))

    @jsii.member(jsii_name="resetProvenanceFieldName")
    def reset_provenance_field_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProvenanceFieldName", []))

    @jsii.member(jsii_name="resetStoreName")
    def reset_store_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStoreName", []))

    @jsii.member(jsii_name="resetUrls")
    def reset_urls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrls", []))

    @builtins.property
    @jsii.member(jsii_name="allowInsecureInput")
    def allow_insecure_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowInsecureInput"))

    @builtins.property
    @jsii.member(jsii_name="collectionInput")
    def collection_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "collectionInput"))

    @builtins.property
    @jsii.member(jsii_name="collectionRegexInput")
    def collection_regex_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "collectionRegexInput"))

    @builtins.property
    @jsii.member(jsii_name="databaseInput")
    def database_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databaseInput"))

    @builtins.property
    @jsii.member(jsii_name="databaseRegexInput")
    def database_regex_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databaseRegexInput"))

    @builtins.property
    @jsii.member(jsii_name="datasetNameInput")
    def dataset_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "datasetNameInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultFormatInput")
    def default_format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultFormatInput"))

    @builtins.property
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property
    @jsii.member(jsii_name="provenanceFieldNameInput")
    def provenance_field_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "provenanceFieldNameInput"))

    @builtins.property
    @jsii.member(jsii_name="storeNameInput")
    def store_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storeNameInput"))

    @builtins.property
    @jsii.member(jsii_name="urlsInput")
    def urls_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "urlsInput"))

    @builtins.property
    @jsii.member(jsii_name="allowInsecure")
    def allow_insecure(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowInsecure"))

    @allow_insecure.setter
    def allow_insecure(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef5d65978250b2f5ec88ac4322dfad1a160a83c1e5fbeb1531756e68a01c6ae7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowInsecure", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="collection")
    def collection(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "collection"))

    @collection.setter
    def collection(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c69ec0b52efa428a6a8b57e721d2fa5d37a4c62ad9fc60ca3be912beb75c25d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "collection", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="collectionRegex")
    def collection_regex(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "collectionRegex"))

    @collection_regex.setter
    def collection_regex(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38c5ac3bafcaac8d23c249b705cb74a972d8cea9e4620017e10b3f166839cb7d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "collectionRegex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="database")
    def database(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "database"))

    @database.setter
    def database(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3011a5c9eef9520421195217cb29f619150e41191bcd23818e4b146cd1b08008)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "database", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="databaseRegex")
    def database_regex(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "databaseRegex"))

    @database_regex.setter
    def database_regex(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf9e969ecd5f2e7bea49fa7cc5cc18166658d52a31ca87983db10cd7844a2f73)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "databaseRegex", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="datasetName")
    def dataset_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "datasetName"))

    @dataset_name.setter
    def dataset_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ea26829433af2c7e3b00a000125cd7037fa3cc2d2dcf5ac594cd2119c37fceb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "datasetName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultFormat")
    def default_format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultFormat"))

    @default_format.setter
    def default_format(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f25e7438ce35ca289ffea9c8c11ebe934b2b5ef7f72eff02c442011fe4ad578)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultFormat", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f3c16269b0bb9198415c4c5bb4c3bc3016455bf0ac544fa2825778ef4d1b293)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="provenanceFieldName")
    def provenance_field_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "provenanceFieldName"))

    @provenance_field_name.setter
    def provenance_field_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4199fb4292bf0b5bca565bee8ee1a322b975dde3cdafe7c575b4a05e00d7b880)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "provenanceFieldName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="storeName")
    def store_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storeName"))

    @store_name.setter
    def store_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb51d81dea6ebdaacd7588ae54ab0e0166dc1730e31990b945738b4e564526e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storeName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="urls")
    def urls(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "urls"))

    @urls.setter
    def urls(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0798da526ff72f362b7e4b94df549f3ade4a2bacae1877f830c83db749060c86)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "urls", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, FederatedDatabaseInstanceStorageDatabasesCollectionsDataSources]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, FederatedDatabaseInstanceStorageDatabasesCollectionsDataSources]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, FederatedDatabaseInstanceStorageDatabasesCollectionsDataSources]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43320f26d43929c562ff234b60cffd4b19178f650dd7cabd69f9ca9e15401a45)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class FederatedDatabaseInstanceStorageDatabasesCollectionsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.federatedDatabaseInstance.FederatedDatabaseInstanceStorageDatabasesCollectionsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__537ba9d32495752821c866ccc53e09c85533ac8a6594f730e5357577b39a7fb6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "FederatedDatabaseInstanceStorageDatabasesCollectionsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d82b8ccad5c665688b52cf4a45eb032bcb20bbfe7323cb436cd6837032392fa)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("FederatedDatabaseInstanceStorageDatabasesCollectionsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59f77b17bdf33738ebde5ad328ecae558634a4ec5455d2cf21dedaad455e6d4f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8ee643f6cd5d691df9a58a454d0b3df5fda5303e7f472e37e312e0c23eb0d53f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1fa6cf52d4a2c248aa2d42b67776f526254380c51fd6beeb14885653c87bb5cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FederatedDatabaseInstanceStorageDatabasesCollections]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FederatedDatabaseInstanceStorageDatabasesCollections]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FederatedDatabaseInstanceStorageDatabasesCollections]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e1acbfbc9900b06d38a57c204aa0c1e4cefc319fb7094cb062029735ee19b40)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class FederatedDatabaseInstanceStorageDatabasesCollectionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.federatedDatabaseInstance.FederatedDatabaseInstanceStorageDatabasesCollectionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__139eaf0391336bcb88c27b7e613dbf2af31154532e1c99e819adf6e26bc88e60)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putDataSources")
    def put_data_sources(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[FederatedDatabaseInstanceStorageDatabasesCollectionsDataSources, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d330367bcd3dc75ea1371d8f919358f75a2af17e173d9e5481e853d6717d5b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDataSources", [value]))

    @jsii.member(jsii_name="resetDataSources")
    def reset_data_sources(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataSources", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @builtins.property
    @jsii.member(jsii_name="dataSources")
    def data_sources(
        self,
    ) -> FederatedDatabaseInstanceStorageDatabasesCollectionsDataSourcesList:
        return typing.cast(FederatedDatabaseInstanceStorageDatabasesCollectionsDataSourcesList, jsii.get(self, "dataSources"))

    @builtins.property
    @jsii.member(jsii_name="dataSourcesInput")
    def data_sources_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FederatedDatabaseInstanceStorageDatabasesCollectionsDataSources]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FederatedDatabaseInstanceStorageDatabasesCollectionsDataSources]]], jsii.get(self, "dataSourcesInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35847ff734f227297b63e8ce8d3aac5475a29ae557cfcdadd7642da380231516)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, FederatedDatabaseInstanceStorageDatabasesCollections]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, FederatedDatabaseInstanceStorageDatabasesCollections]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, FederatedDatabaseInstanceStorageDatabasesCollections]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8589019e2d545d3f9dd763a16141eeee4d1f03cb5c5c93ecc63eda2ea61ed380)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class FederatedDatabaseInstanceStorageDatabasesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.federatedDatabaseInstance.FederatedDatabaseInstanceStorageDatabasesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__23f40b7937045432745a23cf6cd62077484404eea4bde579ff3d4d4cda4b6c7a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "FederatedDatabaseInstanceStorageDatabasesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8eb5b655b241b1740007d7eab230272b6f517f67d282a7a4761e39f73b8f5aa)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("FederatedDatabaseInstanceStorageDatabasesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59c52cc188f39990cef6b820211df6c539c37d478530379be8fb0abcc9f8934d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ce8f252cfc28d439d29fe2dea20a29659235b488247efa27d10fffc2e4d1371d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__58ce4039bfb44edf32a3211421a194d66dbd16df7992907ac079023178ca9a57)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FederatedDatabaseInstanceStorageDatabases]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FederatedDatabaseInstanceStorageDatabases]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FederatedDatabaseInstanceStorageDatabases]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__437d0c49007027d8fa570a23760c19b792ba0925afbe529c92ac715a63d5109b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class FederatedDatabaseInstanceStorageDatabasesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.federatedDatabaseInstance.FederatedDatabaseInstanceStorageDatabasesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__772cc2f73e8f8e17b8d4e0fce54cd413f0c7d5f93eba5eb0b22b99ee4180622a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putCollections")
    def put_collections(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[FederatedDatabaseInstanceStorageDatabasesCollections, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__085924b29cbec3e1b29b415023b2a5523b4eb6c57d9825c6b49c4ab2f1a8600e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putCollections", [value]))

    @jsii.member(jsii_name="putViews")
    def put_views(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["FederatedDatabaseInstanceStorageDatabasesViews", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18b9970edf93d531ff0ed0e7ddacc9bacce1c9291930ae5ca9dd4d7fc2e3e369)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putViews", [value]))

    @jsii.member(jsii_name="resetCollections")
    def reset_collections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCollections", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetViews")
    def reset_views(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetViews", []))

    @builtins.property
    @jsii.member(jsii_name="collections")
    def collections(self) -> FederatedDatabaseInstanceStorageDatabasesCollectionsList:
        return typing.cast(FederatedDatabaseInstanceStorageDatabasesCollectionsList, jsii.get(self, "collections"))

    @builtins.property
    @jsii.member(jsii_name="maxWildcardCollections")
    def max_wildcard_collections(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxWildcardCollections"))

    @builtins.property
    @jsii.member(jsii_name="views")
    def views(self) -> "FederatedDatabaseInstanceStorageDatabasesViewsList":
        return typing.cast("FederatedDatabaseInstanceStorageDatabasesViewsList", jsii.get(self, "views"))

    @builtins.property
    @jsii.member(jsii_name="collectionsInput")
    def collections_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FederatedDatabaseInstanceStorageDatabasesCollections]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FederatedDatabaseInstanceStorageDatabasesCollections]]], jsii.get(self, "collectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="viewsInput")
    def views_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["FederatedDatabaseInstanceStorageDatabasesViews"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["FederatedDatabaseInstanceStorageDatabasesViews"]]], jsii.get(self, "viewsInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73d1df95b585de0bbdefcd96b9d15ffec9368379dabc951f59d23f9cb955f624)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, FederatedDatabaseInstanceStorageDatabases]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, FederatedDatabaseInstanceStorageDatabases]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, FederatedDatabaseInstanceStorageDatabases]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4020e9bc804b576996ac3ae9a64506127e19a6b2ab62527696dcd589de29c716)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.federatedDatabaseInstance.FederatedDatabaseInstanceStorageDatabasesViews",
    jsii_struct_bases=[],
    name_mapping={},
)
class FederatedDatabaseInstanceStorageDatabasesViews:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FederatedDatabaseInstanceStorageDatabasesViews(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FederatedDatabaseInstanceStorageDatabasesViewsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.federatedDatabaseInstance.FederatedDatabaseInstanceStorageDatabasesViewsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__26e72b7009a2537f3b655938ec7138f136a0a7e48d60e5cd7e95c7ba0605e0d4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "FederatedDatabaseInstanceStorageDatabasesViewsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77c99ffe468a79856999090bd3db1c2389859da8599f8fcef9e5668438751084)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("FederatedDatabaseInstanceStorageDatabasesViewsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b4fdc8670a5befe1af144d63f48b8dccb505ba133a06abeae9326e9b973ad59)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9c17b9a84c03e2a2e9995af05b87e137536045673bc237039fa2a35d61da9671)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6acc74cd801fdcd899e01c0491b9e6675c251ce7fbb5f8463fc3ec4cd33718b8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FederatedDatabaseInstanceStorageDatabasesViews]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FederatedDatabaseInstanceStorageDatabasesViews]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FederatedDatabaseInstanceStorageDatabasesViews]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6afcb412b8574f755409da88e4dd53c1edc8c7c245d6543e2825cd22c7b41923)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class FederatedDatabaseInstanceStorageDatabasesViewsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.federatedDatabaseInstance.FederatedDatabaseInstanceStorageDatabasesViewsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c6015a080f55fd13bd2757022f963d2e1d5a10b26dac6029d767ff8b03b3a132)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="pipeline")
    def pipeline(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pipeline"))

    @builtins.property
    @jsii.member(jsii_name="source")
    def source(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "source"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, FederatedDatabaseInstanceStorageDatabasesViews]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, FederatedDatabaseInstanceStorageDatabasesViews]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, FederatedDatabaseInstanceStorageDatabasesViews]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21985facf4c3d7f3c6425d2830f521d77e221de4e66b1d64d40557ed1c31110b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.federatedDatabaseInstance.FederatedDatabaseInstanceStorageStores",
    jsii_struct_bases=[],
    name_mapping={
        "additional_storage_classes": "additionalStorageClasses",
        "allow_insecure": "allowInsecure",
        "bucket": "bucket",
        "cluster_name": "clusterName",
        "default_format": "defaultFormat",
        "delimiter": "delimiter",
        "include_tags": "includeTags",
        "name": "name",
        "prefix": "prefix",
        "project_id": "projectId",
        "provider": "provider",
        "public": "public",
        "read_preference": "readPreference",
        "region": "region",
        "urls": "urls",
    },
)
class FederatedDatabaseInstanceStorageStores:
    def __init__(
        self,
        *,
        additional_storage_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
        allow_insecure: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        bucket: typing.Optional[builtins.str] = None,
        cluster_name: typing.Optional[builtins.str] = None,
        default_format: typing.Optional[builtins.str] = None,
        delimiter: typing.Optional[builtins.str] = None,
        include_tags: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        name: typing.Optional[builtins.str] = None,
        prefix: typing.Optional[builtins.str] = None,
        project_id: typing.Optional[builtins.str] = None,
        provider: typing.Optional[builtins.str] = None,
        public: typing.Optional[builtins.str] = None,
        read_preference: typing.Optional[typing.Union["FederatedDatabaseInstanceStorageStoresReadPreference", typing.Dict[builtins.str, typing.Any]]] = None,
        region: typing.Optional[builtins.str] = None,
        urls: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param additional_storage_classes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#additional_storage_classes FederatedDatabaseInstance#additional_storage_classes}.
        :param allow_insecure: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#allow_insecure FederatedDatabaseInstance#allow_insecure}.
        :param bucket: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#bucket FederatedDatabaseInstance#bucket}.
        :param cluster_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#cluster_name FederatedDatabaseInstance#cluster_name}.
        :param default_format: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#default_format FederatedDatabaseInstance#default_format}.
        :param delimiter: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#delimiter FederatedDatabaseInstance#delimiter}.
        :param include_tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#include_tags FederatedDatabaseInstance#include_tags}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#name FederatedDatabaseInstance#name}.
        :param prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#prefix FederatedDatabaseInstance#prefix}.
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#project_id FederatedDatabaseInstance#project_id}.
        :param provider: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#provider FederatedDatabaseInstance#provider}.
        :param public: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#public FederatedDatabaseInstance#public}.
        :param read_preference: read_preference block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#read_preference FederatedDatabaseInstance#read_preference}
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#region FederatedDatabaseInstance#region}.
        :param urls: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#urls FederatedDatabaseInstance#urls}.
        '''
        if isinstance(read_preference, dict):
            read_preference = FederatedDatabaseInstanceStorageStoresReadPreference(**read_preference)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76184054f940d898068641e82c6643dd40a8760cf34baaff881d276c65f217d4)
            check_type(argname="argument additional_storage_classes", value=additional_storage_classes, expected_type=type_hints["additional_storage_classes"])
            check_type(argname="argument allow_insecure", value=allow_insecure, expected_type=type_hints["allow_insecure"])
            check_type(argname="argument bucket", value=bucket, expected_type=type_hints["bucket"])
            check_type(argname="argument cluster_name", value=cluster_name, expected_type=type_hints["cluster_name"])
            check_type(argname="argument default_format", value=default_format, expected_type=type_hints["default_format"])
            check_type(argname="argument delimiter", value=delimiter, expected_type=type_hints["delimiter"])
            check_type(argname="argument include_tags", value=include_tags, expected_type=type_hints["include_tags"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument prefix", value=prefix, expected_type=type_hints["prefix"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument public", value=public, expected_type=type_hints["public"])
            check_type(argname="argument read_preference", value=read_preference, expected_type=type_hints["read_preference"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument urls", value=urls, expected_type=type_hints["urls"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if additional_storage_classes is not None:
            self._values["additional_storage_classes"] = additional_storage_classes
        if allow_insecure is not None:
            self._values["allow_insecure"] = allow_insecure
        if bucket is not None:
            self._values["bucket"] = bucket
        if cluster_name is not None:
            self._values["cluster_name"] = cluster_name
        if default_format is not None:
            self._values["default_format"] = default_format
        if delimiter is not None:
            self._values["delimiter"] = delimiter
        if include_tags is not None:
            self._values["include_tags"] = include_tags
        if name is not None:
            self._values["name"] = name
        if prefix is not None:
            self._values["prefix"] = prefix
        if project_id is not None:
            self._values["project_id"] = project_id
        if provider is not None:
            self._values["provider"] = provider
        if public is not None:
            self._values["public"] = public
        if read_preference is not None:
            self._values["read_preference"] = read_preference
        if region is not None:
            self._values["region"] = region
        if urls is not None:
            self._values["urls"] = urls

    @builtins.property
    def additional_storage_classes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#additional_storage_classes FederatedDatabaseInstance#additional_storage_classes}.'''
        result = self._values.get("additional_storage_classes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def allow_insecure(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#allow_insecure FederatedDatabaseInstance#allow_insecure}.'''
        result = self._values.get("allow_insecure")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def bucket(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#bucket FederatedDatabaseInstance#bucket}.'''
        result = self._values.get("bucket")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#cluster_name FederatedDatabaseInstance#cluster_name}.'''
        result = self._values.get("cluster_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_format(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#default_format FederatedDatabaseInstance#default_format}.'''
        result = self._values.get("default_format")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delimiter(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#delimiter FederatedDatabaseInstance#delimiter}.'''
        result = self._values.get("delimiter")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def include_tags(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#include_tags FederatedDatabaseInstance#include_tags}.'''
        result = self._values.get("include_tags")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#name FederatedDatabaseInstance#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#prefix FederatedDatabaseInstance#prefix}.'''
        result = self._values.get("prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def project_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#project_id FederatedDatabaseInstance#project_id}.'''
        result = self._values.get("project_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def provider(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#provider FederatedDatabaseInstance#provider}.'''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def public(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#public FederatedDatabaseInstance#public}.'''
        result = self._values.get("public")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def read_preference(
        self,
    ) -> typing.Optional["FederatedDatabaseInstanceStorageStoresReadPreference"]:
        '''read_preference block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#read_preference FederatedDatabaseInstance#read_preference}
        '''
        result = self._values.get("read_preference")
        return typing.cast(typing.Optional["FederatedDatabaseInstanceStorageStoresReadPreference"], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#region FederatedDatabaseInstance#region}.'''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def urls(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#urls FederatedDatabaseInstance#urls}.'''
        result = self._values.get("urls")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FederatedDatabaseInstanceStorageStores(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FederatedDatabaseInstanceStorageStoresList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.federatedDatabaseInstance.FederatedDatabaseInstanceStorageStoresList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d6c0f7124ea4e282129981cc3d311935ff0da78b06ed828be4469d4e5ac0a144)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "FederatedDatabaseInstanceStorageStoresOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db373f5b3b5a9ea4f9f9f889a2cf3bfd81ed5cf0524ec93dd14629eeef831205)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("FederatedDatabaseInstanceStorageStoresOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ad90395f03239f0e09dd3e41b8e6b6f9b78d0c4ce15640f4915f925131062a8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b92245bd50ec74bb5e7dbcb3e552f3839c8dc15dc3d1be8e76cf555b866c6aa2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1247a1831b329d4dbadeee24099697cf32233cb070788729db94f563ad267f46)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FederatedDatabaseInstanceStorageStores]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FederatedDatabaseInstanceStorageStores]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FederatedDatabaseInstanceStorageStores]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87c01791d53607b0f55a9d920a889bd432ab986c60f909646c34c828eab47592)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class FederatedDatabaseInstanceStorageStoresOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.federatedDatabaseInstance.FederatedDatabaseInstanceStorageStoresOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5490b1826098dbc1f18212356ba6af5d640c570ec73d15f205bb3a5acd263642)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putReadPreference")
    def put_read_preference(
        self,
        *,
        max_staleness_seconds: typing.Optional[jsii.Number] = None,
        mode: typing.Optional[builtins.str] = None,
        tag_sets: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["FederatedDatabaseInstanceStorageStoresReadPreferenceTagSets", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param max_staleness_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#max_staleness_seconds FederatedDatabaseInstance#max_staleness_seconds}.
        :param mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#mode FederatedDatabaseInstance#mode}.
        :param tag_sets: tag_sets block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#tag_sets FederatedDatabaseInstance#tag_sets}
        '''
        value = FederatedDatabaseInstanceStorageStoresReadPreference(
            max_staleness_seconds=max_staleness_seconds, mode=mode, tag_sets=tag_sets
        )

        return typing.cast(None, jsii.invoke(self, "putReadPreference", [value]))

    @jsii.member(jsii_name="resetAdditionalStorageClasses")
    def reset_additional_storage_classes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAdditionalStorageClasses", []))

    @jsii.member(jsii_name="resetAllowInsecure")
    def reset_allow_insecure(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllowInsecure", []))

    @jsii.member(jsii_name="resetBucket")
    def reset_bucket(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBucket", []))

    @jsii.member(jsii_name="resetClusterName")
    def reset_cluster_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterName", []))

    @jsii.member(jsii_name="resetDefaultFormat")
    def reset_default_format(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultFormat", []))

    @jsii.member(jsii_name="resetDelimiter")
    def reset_delimiter(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelimiter", []))

    @jsii.member(jsii_name="resetIncludeTags")
    def reset_include_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIncludeTags", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetPrefix")
    def reset_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrefix", []))

    @jsii.member(jsii_name="resetProjectId")
    def reset_project_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProjectId", []))

    @jsii.member(jsii_name="resetProvider")
    def reset_provider(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProvider", []))

    @jsii.member(jsii_name="resetPublic")
    def reset_public(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublic", []))

    @jsii.member(jsii_name="resetReadPreference")
    def reset_read_preference(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReadPreference", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @jsii.member(jsii_name="resetUrls")
    def reset_urls(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrls", []))

    @builtins.property
    @jsii.member(jsii_name="readPreference")
    def read_preference(
        self,
    ) -> "FederatedDatabaseInstanceStorageStoresReadPreferenceOutputReference":
        return typing.cast("FederatedDatabaseInstanceStorageStoresReadPreferenceOutputReference", jsii.get(self, "readPreference"))

    @builtins.property
    @jsii.member(jsii_name="additionalStorageClassesInput")
    def additional_storage_classes_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "additionalStorageClassesInput"))

    @builtins.property
    @jsii.member(jsii_name="allowInsecureInput")
    def allow_insecure_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "allowInsecureInput"))

    @builtins.property
    @jsii.member(jsii_name="bucketInput")
    def bucket_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterNameInput")
    def cluster_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterNameInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultFormatInput")
    def default_format_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultFormatInput"))

    @builtins.property
    @jsii.member(jsii_name="delimiterInput")
    def delimiter_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "delimiterInput"))

    @builtins.property
    @jsii.member(jsii_name="includeTagsInput")
    def include_tags_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "includeTagsInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="prefixInput")
    def prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "prefixInput"))

    @builtins.property
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="providerInput")
    def provider_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "providerInput"))

    @builtins.property
    @jsii.member(jsii_name="publicInput")
    def public_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "publicInput"))

    @builtins.property
    @jsii.member(jsii_name="readPreferenceInput")
    def read_preference_input(
        self,
    ) -> typing.Optional["FederatedDatabaseInstanceStorageStoresReadPreference"]:
        return typing.cast(typing.Optional["FederatedDatabaseInstanceStorageStoresReadPreference"], jsii.get(self, "readPreferenceInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="urlsInput")
    def urls_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "urlsInput"))

    @builtins.property
    @jsii.member(jsii_name="additionalStorageClasses")
    def additional_storage_classes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "additionalStorageClasses"))

    @additional_storage_classes.setter
    def additional_storage_classes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f101a5b005a80837842643f13b0737df806021848cf43b59b94fcdd20015154)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "additionalStorageClasses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="allowInsecure")
    def allow_insecure(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "allowInsecure"))

    @allow_insecure.setter
    def allow_insecure(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9009a41a1bbba82f1a0cfefab186d2f076885c0340d7b8a15a074127f9650339)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allowInsecure", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bucket")
    def bucket(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucket"))

    @bucket.setter
    def bucket(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7f12bab7c75e464c7f76a6c7fe6bebd3c4135688b3198f2f048d944599f2b77)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bucket", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterName"))

    @cluster_name.setter
    def cluster_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4341500c1b2ba0eb3c8334733653fe0c071d765443ac2fd6979ac992e2b81acc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultFormat")
    def default_format(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultFormat"))

    @default_format.setter
    def default_format(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56479f28537c8123a3fc3bf00e74eb128bbf3d995e5530b81de395e7e703cb7e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultFormat", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="delimiter")
    def delimiter(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delimiter"))

    @delimiter.setter
    def delimiter(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd4bb917a17744bd76a9c01e307552d794cb0d2b664d4eeb9b192ac118fb9a91)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delimiter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="includeTags")
    def include_tags(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "includeTags"))

    @include_tags.setter
    def include_tags(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53be1da78078628552e035383d1884ebdca07c7647339b19e99620e4138d41ca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "includeTags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd8d4f243c89b1906f9ff9748ff6359f74d5f3a1000d2090842d79641b339abf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="prefix")
    def prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "prefix"))

    @prefix.setter
    def prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8995a26f0e3dbd6ccb48892c5cf821aa2c8f0a4f48a8912d7c26f5fb81c59dab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "prefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a3be7a3e27c10044b78b94f8e9e25b9b305b73e3c9fc55428ca38c487e93439)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="provider")
    def provider(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "provider"))

    @provider.setter
    def provider(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e42791a6d780d9d8c683aa7f63e3cb62e990fbe68225b03fc649d5b5d4c2e687)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "provider", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="public")
    def public(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "public"))

    @public.setter
    def public(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08b819797f9f2bfc96b1001ddb9dcf7a6aeb5ddaf2e1687da62fe07d78bf9ea4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "public", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8162abb0e20bea415d3941adf31cd1ccee12624b127596113c39f55a2144668)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="urls")
    def urls(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "urls"))

    @urls.setter
    def urls(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c98b2323462ac31ba142225944ee4534d32b5e697071e6f161f516457cf8c326)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "urls", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, FederatedDatabaseInstanceStorageStores]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, FederatedDatabaseInstanceStorageStores]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, FederatedDatabaseInstanceStorageStores]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26362fca2c96a3ad9daa3139723a97db62ca67278e1eb8159a733eee2a4f0bb3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.federatedDatabaseInstance.FederatedDatabaseInstanceStorageStoresReadPreference",
    jsii_struct_bases=[],
    name_mapping={
        "max_staleness_seconds": "maxStalenessSeconds",
        "mode": "mode",
        "tag_sets": "tagSets",
    },
)
class FederatedDatabaseInstanceStorageStoresReadPreference:
    def __init__(
        self,
        *,
        max_staleness_seconds: typing.Optional[jsii.Number] = None,
        mode: typing.Optional[builtins.str] = None,
        tag_sets: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["FederatedDatabaseInstanceStorageStoresReadPreferenceTagSets", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param max_staleness_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#max_staleness_seconds FederatedDatabaseInstance#max_staleness_seconds}.
        :param mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#mode FederatedDatabaseInstance#mode}.
        :param tag_sets: tag_sets block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#tag_sets FederatedDatabaseInstance#tag_sets}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94f9cd92932fec002e4ab988318e94604120fa7c5070c4909460bcdec04ec1d8)
            check_type(argname="argument max_staleness_seconds", value=max_staleness_seconds, expected_type=type_hints["max_staleness_seconds"])
            check_type(argname="argument mode", value=mode, expected_type=type_hints["mode"])
            check_type(argname="argument tag_sets", value=tag_sets, expected_type=type_hints["tag_sets"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if max_staleness_seconds is not None:
            self._values["max_staleness_seconds"] = max_staleness_seconds
        if mode is not None:
            self._values["mode"] = mode
        if tag_sets is not None:
            self._values["tag_sets"] = tag_sets

    @builtins.property
    def max_staleness_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#max_staleness_seconds FederatedDatabaseInstance#max_staleness_seconds}.'''
        result = self._values.get("max_staleness_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#mode FederatedDatabaseInstance#mode}.'''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tag_sets(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["FederatedDatabaseInstanceStorageStoresReadPreferenceTagSets"]]]:
        '''tag_sets block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#tag_sets FederatedDatabaseInstance#tag_sets}
        '''
        result = self._values.get("tag_sets")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["FederatedDatabaseInstanceStorageStoresReadPreferenceTagSets"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FederatedDatabaseInstanceStorageStoresReadPreference(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FederatedDatabaseInstanceStorageStoresReadPreferenceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.federatedDatabaseInstance.FederatedDatabaseInstanceStorageStoresReadPreferenceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d2ec0575619ab7ae45f54783d637afbddbf4f4e537dd14fd1645cbed7066e73e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putTagSets")
    def put_tag_sets(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["FederatedDatabaseInstanceStorageStoresReadPreferenceTagSets", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ba50dee1b8506a4e21669802dcde93977bc471ed42ec2c5475c4597c5dd8b0a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTagSets", [value]))

    @jsii.member(jsii_name="resetMaxStalenessSeconds")
    def reset_max_staleness_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxStalenessSeconds", []))

    @jsii.member(jsii_name="resetMode")
    def reset_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMode", []))

    @jsii.member(jsii_name="resetTagSets")
    def reset_tag_sets(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTagSets", []))

    @builtins.property
    @jsii.member(jsii_name="tagSets")
    def tag_sets(
        self,
    ) -> "FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsList":
        return typing.cast("FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsList", jsii.get(self, "tagSets"))

    @builtins.property
    @jsii.member(jsii_name="maxStalenessSecondsInput")
    def max_staleness_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxStalenessSecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="modeInput")
    def mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modeInput"))

    @builtins.property
    @jsii.member(jsii_name="tagSetsInput")
    def tag_sets_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["FederatedDatabaseInstanceStorageStoresReadPreferenceTagSets"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["FederatedDatabaseInstanceStorageStoresReadPreferenceTagSets"]]], jsii.get(self, "tagSetsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxStalenessSeconds")
    def max_staleness_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxStalenessSeconds"))

    @max_staleness_seconds.setter
    def max_staleness_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87c17c783e8c251a7db073fb12cd6c4ca72e4b3711a134b51fbdad852ac1a772)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxStalenessSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @mode.setter
    def mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7af36de8fd1b84791eb60c05c346f8c3de579feca199e225b4e8925756c91e83)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[FederatedDatabaseInstanceStorageStoresReadPreference]:
        return typing.cast(typing.Optional[FederatedDatabaseInstanceStorageStoresReadPreference], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[FederatedDatabaseInstanceStorageStoresReadPreference],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c5f402998017de0383ab67720e1dcfc88166f61d019af23ed01c58570488fbd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.federatedDatabaseInstance.FederatedDatabaseInstanceStorageStoresReadPreferenceTagSets",
    jsii_struct_bases=[],
    name_mapping={"tags": "tags"},
)
class FederatedDatabaseInstanceStorageStoresReadPreferenceTagSets:
    def __init__(
        self,
        *,
        tags: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsTags", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param tags: tags block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#tags FederatedDatabaseInstance#tags}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87f0b27e574c0c33ca388ef41eeecf9da12d16771c72583994041cf6f512cbcc)
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "tags": tags,
        }

    @builtins.property
    def tags(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsTags"]]:
        '''tags block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#tags FederatedDatabaseInstance#tags}
        '''
        result = self._values.get("tags")
        assert result is not None, "Required property 'tags' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsTags"]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FederatedDatabaseInstanceStorageStoresReadPreferenceTagSets(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.federatedDatabaseInstance.FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__06d481c5cc0be938798968cc70d2f5162e7cc861eb88d3a5b17be1081b61bac8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96540b34f60084d3b135380df159c4bc243e755e87a86e202be8fd4c658002e3)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__abb1f3fc2dabe7b607d7d13f42e2ee8097362ea39c03a1f78f4f63c57c650c0b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d733a783c134f3a0b0ee93147c8efddf8a067e85ebc4036cc1ff675f8de544e0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__599ab6c7cff243811dbab0f8d00a1f50c47d01c915ab067d8ca8aea2d33dc6f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FederatedDatabaseInstanceStorageStoresReadPreferenceTagSets]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FederatedDatabaseInstanceStorageStoresReadPreferenceTagSets]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FederatedDatabaseInstanceStorageStoresReadPreferenceTagSets]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__075b019060c432b29ba22a2c8f0d040aeb10e8d7b36fc3a248a877f5afd78bf1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.federatedDatabaseInstance.FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__922f75ea68aae717609d5200d8678dfe43c501b49f32e0472451b754b50a2f56)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putTags")
    def put_tags(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsTags", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da25d6c3783ff43df59947da15d45183df0bf26b4e89b6c322e1f3a8804284b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTags", [value]))

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(
        self,
    ) -> "FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsTagsList":
        return typing.cast("FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsTagsList", jsii.get(self, "tags"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsTags"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsTags"]]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, FederatedDatabaseInstanceStorageStoresReadPreferenceTagSets]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, FederatedDatabaseInstanceStorageStoresReadPreferenceTagSets]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, FederatedDatabaseInstanceStorageStoresReadPreferenceTagSets]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2a7e0ca05f26619e9e124fe029ee13179b709858170e1ead03c9baafe9892e2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.federatedDatabaseInstance.FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsTags",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "value": "value"},
)
class FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsTags:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#name FederatedDatabaseInstance#name}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#value FederatedDatabaseInstance#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29a0c60157a761329663613e79e92761d25cab0aa21ea51254599196e84ceca2)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#name FederatedDatabaseInstance#name}.'''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_database_instance#value FederatedDatabaseInstance#value}.'''
        result = self._values.get("value")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsTags(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsTagsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.federatedDatabaseInstance.FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsTagsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__53434c0cb210b283603227f5f3ddcc0ca1577b2331b69ef157e36b7ff9250e7c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsTagsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__500cb7a2e40cece796070c53de0928c099bc6e898c729c51cfac0128b509a252)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsTagsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74a1ea86ab7979f45df1fddcb70636194dc2188e44115e91368576e7d7589787)
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
            type_hints = typing.get_type_hints(_typecheckingstub__48989e52d654549579558106c65a9e5e58a479e0206465dc38df6396c4ee19d7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4721f8f6a2808d901ecc231f6feb0ee2556fbc27837b4c5041340c35905c2a16)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsTags]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsTags]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsTags]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c09f10184a175b8f81e1aa8651fa680fe9186f9ea78c596ce7e61bbdc4ae7e34)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsTagsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.federatedDatabaseInstance.FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsTagsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6a03d8ebcf1d943eb2ce5cf34fc6e8d0a84bd38f6ea1dc7c12f8e50f5afb63e9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetValue")
    def reset_value(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValue", []))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__914be50309b6aa5e8845a5e495a128248398481426cb0e226d95298ff9e4e3ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1eb8f6dd0fdcc8e8850ec8da60db367d62eccc6583e150e5df292e11843b4511)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsTags]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsTags]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsTags]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__198dd16098f053bded5f99f9a511d9f751be5262b854b5008a05c250edb6d130)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "FederatedDatabaseInstance",
    "FederatedDatabaseInstanceCloudProviderConfig",
    "FederatedDatabaseInstanceCloudProviderConfigAws",
    "FederatedDatabaseInstanceCloudProviderConfigAwsOutputReference",
    "FederatedDatabaseInstanceCloudProviderConfigAzure",
    "FederatedDatabaseInstanceCloudProviderConfigAzureOutputReference",
    "FederatedDatabaseInstanceCloudProviderConfigOutputReference",
    "FederatedDatabaseInstanceConfig",
    "FederatedDatabaseInstanceDataProcessRegion",
    "FederatedDatabaseInstanceDataProcessRegionOutputReference",
    "FederatedDatabaseInstanceStorageDatabases",
    "FederatedDatabaseInstanceStorageDatabasesCollections",
    "FederatedDatabaseInstanceStorageDatabasesCollectionsDataSources",
    "FederatedDatabaseInstanceStorageDatabasesCollectionsDataSourcesList",
    "FederatedDatabaseInstanceStorageDatabasesCollectionsDataSourcesOutputReference",
    "FederatedDatabaseInstanceStorageDatabasesCollectionsList",
    "FederatedDatabaseInstanceStorageDatabasesCollectionsOutputReference",
    "FederatedDatabaseInstanceStorageDatabasesList",
    "FederatedDatabaseInstanceStorageDatabasesOutputReference",
    "FederatedDatabaseInstanceStorageDatabasesViews",
    "FederatedDatabaseInstanceStorageDatabasesViewsList",
    "FederatedDatabaseInstanceStorageDatabasesViewsOutputReference",
    "FederatedDatabaseInstanceStorageStores",
    "FederatedDatabaseInstanceStorageStoresList",
    "FederatedDatabaseInstanceStorageStoresOutputReference",
    "FederatedDatabaseInstanceStorageStoresReadPreference",
    "FederatedDatabaseInstanceStorageStoresReadPreferenceOutputReference",
    "FederatedDatabaseInstanceStorageStoresReadPreferenceTagSets",
    "FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsList",
    "FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsOutputReference",
    "FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsTags",
    "FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsTagsList",
    "FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsTagsOutputReference",
]

publication.publish()

def _typecheckingstub__b6cb69c6e47c3a4872d6765991e11b7ab3d605ca3bad4198ba056319841715d4(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    project_id: builtins.str,
    cloud_provider_config: typing.Optional[typing.Union[FederatedDatabaseInstanceCloudProviderConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    data_process_region: typing.Optional[typing.Union[FederatedDatabaseInstanceDataProcessRegion, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    storage_databases: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[FederatedDatabaseInstanceStorageDatabases, typing.Dict[builtins.str, typing.Any]]]]] = None,
    storage_stores: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[FederatedDatabaseInstanceStorageStores, typing.Dict[builtins.str, typing.Any]]]]] = None,
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

def _typecheckingstub__8a5c5a9e0c04919964c7c11416d8d16d71a2dbcf6a9b6885808d9c3a051294e5(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b38fc28a2adabe2b0b747e74c098379668d2133c4d0d48d6f59292b3c0c3f313(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[FederatedDatabaseInstanceStorageDatabases, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc642e50180406b79901a9b8ee7d2acfd91196e6dcf8326dc6fce0d3bbe65d3a(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[FederatedDatabaseInstanceStorageStores, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__98767f1d78a7f96e0ca91f7fb29b2a27566ebbaff78b6b390723d6c5d59794da(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b10a40c749e5863765e6e1a061a787f7544d94e17b4a9bf40b356e5b6174d47d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9c9c414b3245ce744ea1f8cc3b5c94de158aa3a158c0da54b6602872dcfb94e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74f449b7f46e263a6a36dcdc6c35858cab6e69f6e1f7274938b99e7c5676b134(
    *,
    aws: typing.Optional[typing.Union[FederatedDatabaseInstanceCloudProviderConfigAws, typing.Dict[builtins.str, typing.Any]]] = None,
    azure: typing.Optional[typing.Union[FederatedDatabaseInstanceCloudProviderConfigAzure, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4c01fba96e2e6b2e2f2d767ff7128345a7856051c1bbd78d7ada58c9398bca6(
    *,
    role_id: builtins.str,
    test_s3_bucket: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afc0823de14f680380d9b5c2834571f54a4f5c4610d4508040ccb69c2dee3adf(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76889cff24c0129fd721ef0d27968e343e92ccb29e7f9da27b81b9e153afb1ee(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ba2c74aead7d7f2ab7218423518cb1f5a4c538494de351e2a1c99b8a709e5d6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed8bd9093e7209f6f67bf1c90b01cf12290ef8b957d51eb823f2be8a29e89791(
    value: typing.Optional[FederatedDatabaseInstanceCloudProviderConfigAws],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd87bf0fd71e12c847619d496b6618e4230e90860a8f86981dbbfa84764b9713(
    *,
    role_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d38dbaf8f115be67b06c2ccb0e72dbfee4b6a46b0c1df7e8fe99983b5a6ed3af(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea99cb0a282606b7d229664d9c4d2339c1da8c8eb7d2ff2854d0228d19e4c2df(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d96ed7117d03e0efb739dea14ceb5cef624aeff43a7ed51bf10da1eb6732bc7d(
    value: typing.Optional[FederatedDatabaseInstanceCloudProviderConfigAzure],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__960a4d78ce9b0c89399c7ed7e128b1c3bdb9e932dbad447af78b92ec7db092f4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0a730cbefbefd77e8d9acc8cefa3b4373f304cacf7861af3b789da3cb2d30bec(
    value: typing.Optional[FederatedDatabaseInstanceCloudProviderConfig],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9a881efd4b865abcc37148d43ead1af588a3dd93a820e17f5d518a87ddbf007(
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
    cloud_provider_config: typing.Optional[typing.Union[FederatedDatabaseInstanceCloudProviderConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    data_process_region: typing.Optional[typing.Union[FederatedDatabaseInstanceDataProcessRegion, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    storage_databases: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[FederatedDatabaseInstanceStorageDatabases, typing.Dict[builtins.str, typing.Any]]]]] = None,
    storage_stores: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[FederatedDatabaseInstanceStorageStores, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e90e6f9f6a14c8c877674641170d9c5d81b041c59288c2d612c3e35fed7aab1(
    *,
    cloud_provider: builtins.str,
    region: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__616b59b95894ae827b299f58582ce95afea68995bca005de7c4d004bf61bba22(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8156f951cea46519adefb72f5e05b2815d7362536b0e6929762f568c06e55cde(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df655cdaf3a6bdfc2051408a11aeed49481825a5c2cef98d4015fca098a002e1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3d6d49ba95d3ecc36f6872a190e101297d0da87223e6f0df169cab3eab66667(
    value: typing.Optional[FederatedDatabaseInstanceDataProcessRegion],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fbb235a63f9c6f74220659f285e8be0c820e25373d6be9553a29a9a57c806b4(
    *,
    collections: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[FederatedDatabaseInstanceStorageDatabasesCollections, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: typing.Optional[builtins.str] = None,
    views: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[FederatedDatabaseInstanceStorageDatabasesViews, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__606920a8ecd8a0087b6df654e282abb30e3c30446205e2aa34996a1147e356e3(
    *,
    data_sources: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[FederatedDatabaseInstanceStorageDatabasesCollectionsDataSources, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1be73174fdbafe36c5eaaac1a154805e562561aea3242c1076fcddf77d0fdc10(
    *,
    allow_insecure: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    collection: typing.Optional[builtins.str] = None,
    collection_regex: typing.Optional[builtins.str] = None,
    database: typing.Optional[builtins.str] = None,
    database_regex: typing.Optional[builtins.str] = None,
    dataset_name: typing.Optional[builtins.str] = None,
    default_format: typing.Optional[builtins.str] = None,
    path: typing.Optional[builtins.str] = None,
    provenance_field_name: typing.Optional[builtins.str] = None,
    store_name: typing.Optional[builtins.str] = None,
    urls: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e76d166254ee33b0f2c5605497ed4e50c3ccf240f3fcfe50d27db33d13de76e0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5ff2cc68dce950bfa9da4662b7f368e299139189bbe600e16178e7de02e4643(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1fcef0b59f55ccc173883d4501fd71f59bba3806ad65f59dbdec959babf8cca4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4bd6121d18e66b70a2a8fd3573a67ccf81dd24cb1b7bb5a1cecfb63193689780(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73edd7d6b7199931860f315ec334bb5bc74a1e613fc8ca1537742eedc35dd6c1(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea049e230860b850213525e40d651e673c09ca927224165053b12e9fa05e54ed(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FederatedDatabaseInstanceStorageDatabasesCollectionsDataSources]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__944300362dc69806d481a1370bbed348c62e316e1cc81e0d3318ca307e946ccf(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef5d65978250b2f5ec88ac4322dfad1a160a83c1e5fbeb1531756e68a01c6ae7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c69ec0b52efa428a6a8b57e721d2fa5d37a4c62ad9fc60ca3be912beb75c25d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38c5ac3bafcaac8d23c249b705cb74a972d8cea9e4620017e10b3f166839cb7d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3011a5c9eef9520421195217cb29f619150e41191bcd23818e4b146cd1b08008(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf9e969ecd5f2e7bea49fa7cc5cc18166658d52a31ca87983db10cd7844a2f73(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ea26829433af2c7e3b00a000125cd7037fa3cc2d2dcf5ac594cd2119c37fceb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f25e7438ce35ca289ffea9c8c11ebe934b2b5ef7f72eff02c442011fe4ad578(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f3c16269b0bb9198415c4c5bb4c3bc3016455bf0ac544fa2825778ef4d1b293(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4199fb4292bf0b5bca565bee8ee1a322b975dde3cdafe7c575b4a05e00d7b880(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb51d81dea6ebdaacd7588ae54ab0e0166dc1730e31990b945738b4e564526e3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0798da526ff72f362b7e4b94df549f3ade4a2bacae1877f830c83db749060c86(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43320f26d43929c562ff234b60cffd4b19178f650dd7cabd69f9ca9e15401a45(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, FederatedDatabaseInstanceStorageDatabasesCollectionsDataSources]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__537ba9d32495752821c866ccc53e09c85533ac8a6594f730e5357577b39a7fb6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d82b8ccad5c665688b52cf4a45eb032bcb20bbfe7323cb436cd6837032392fa(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59f77b17bdf33738ebde5ad328ecae558634a4ec5455d2cf21dedaad455e6d4f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ee643f6cd5d691df9a58a454d0b3df5fda5303e7f472e37e312e0c23eb0d53f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1fa6cf52d4a2c248aa2d42b67776f526254380c51fd6beeb14885653c87bb5cd(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e1acbfbc9900b06d38a57c204aa0c1e4cefc319fb7094cb062029735ee19b40(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FederatedDatabaseInstanceStorageDatabasesCollections]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__139eaf0391336bcb88c27b7e613dbf2af31154532e1c99e819adf6e26bc88e60(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d330367bcd3dc75ea1371d8f919358f75a2af17e173d9e5481e853d6717d5b2(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[FederatedDatabaseInstanceStorageDatabasesCollectionsDataSources, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35847ff734f227297b63e8ce8d3aac5475a29ae557cfcdadd7642da380231516(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8589019e2d545d3f9dd763a16141eeee4d1f03cb5c5c93ecc63eda2ea61ed380(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, FederatedDatabaseInstanceStorageDatabasesCollections]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23f40b7937045432745a23cf6cd62077484404eea4bde579ff3d4d4cda4b6c7a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8eb5b655b241b1740007d7eab230272b6f517f67d282a7a4761e39f73b8f5aa(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59c52cc188f39990cef6b820211df6c539c37d478530379be8fb0abcc9f8934d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce8f252cfc28d439d29fe2dea20a29659235b488247efa27d10fffc2e4d1371d(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58ce4039bfb44edf32a3211421a194d66dbd16df7992907ac079023178ca9a57(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__437d0c49007027d8fa570a23760c19b792ba0925afbe529c92ac715a63d5109b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FederatedDatabaseInstanceStorageDatabases]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__772cc2f73e8f8e17b8d4e0fce54cd413f0c7d5f93eba5eb0b22b99ee4180622a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__085924b29cbec3e1b29b415023b2a5523b4eb6c57d9825c6b49c4ab2f1a8600e(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[FederatedDatabaseInstanceStorageDatabasesCollections, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18b9970edf93d531ff0ed0e7ddacc9bacce1c9291930ae5ca9dd4d7fc2e3e369(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[FederatedDatabaseInstanceStorageDatabasesViews, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73d1df95b585de0bbdefcd96b9d15ffec9368379dabc951f59d23f9cb955f624(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4020e9bc804b576996ac3ae9a64506127e19a6b2ab62527696dcd589de29c716(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, FederatedDatabaseInstanceStorageDatabases]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26e72b7009a2537f3b655938ec7138f136a0a7e48d60e5cd7e95c7ba0605e0d4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77c99ffe468a79856999090bd3db1c2389859da8599f8fcef9e5668438751084(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b4fdc8670a5befe1af144d63f48b8dccb505ba133a06abeae9326e9b973ad59(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c17b9a84c03e2a2e9995af05b87e137536045673bc237039fa2a35d61da9671(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6acc74cd801fdcd899e01c0491b9e6675c251ce7fbb5f8463fc3ec4cd33718b8(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6afcb412b8574f755409da88e4dd53c1edc8c7c245d6543e2825cd22c7b41923(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FederatedDatabaseInstanceStorageDatabasesViews]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6015a080f55fd13bd2757022f963d2e1d5a10b26dac6029d767ff8b03b3a132(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21985facf4c3d7f3c6425d2830f521d77e221de4e66b1d64d40557ed1c31110b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, FederatedDatabaseInstanceStorageDatabasesViews]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76184054f940d898068641e82c6643dd40a8760cf34baaff881d276c65f217d4(
    *,
    additional_storage_classes: typing.Optional[typing.Sequence[builtins.str]] = None,
    allow_insecure: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    bucket: typing.Optional[builtins.str] = None,
    cluster_name: typing.Optional[builtins.str] = None,
    default_format: typing.Optional[builtins.str] = None,
    delimiter: typing.Optional[builtins.str] = None,
    include_tags: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    name: typing.Optional[builtins.str] = None,
    prefix: typing.Optional[builtins.str] = None,
    project_id: typing.Optional[builtins.str] = None,
    provider: typing.Optional[builtins.str] = None,
    public: typing.Optional[builtins.str] = None,
    read_preference: typing.Optional[typing.Union[FederatedDatabaseInstanceStorageStoresReadPreference, typing.Dict[builtins.str, typing.Any]]] = None,
    region: typing.Optional[builtins.str] = None,
    urls: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6c0f7124ea4e282129981cc3d311935ff0da78b06ed828be4469d4e5ac0a144(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db373f5b3b5a9ea4f9f9f889a2cf3bfd81ed5cf0524ec93dd14629eeef831205(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ad90395f03239f0e09dd3e41b8e6b6f9b78d0c4ce15640f4915f925131062a8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b92245bd50ec74bb5e7dbcb3e552f3839c8dc15dc3d1be8e76cf555b866c6aa2(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1247a1831b329d4dbadeee24099697cf32233cb070788729db94f563ad267f46(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87c01791d53607b0f55a9d920a889bd432ab986c60f909646c34c828eab47592(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FederatedDatabaseInstanceStorageStores]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5490b1826098dbc1f18212356ba6af5d640c570ec73d15f205bb3a5acd263642(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f101a5b005a80837842643f13b0737df806021848cf43b59b94fcdd20015154(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9009a41a1bbba82f1a0cfefab186d2f076885c0340d7b8a15a074127f9650339(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7f12bab7c75e464c7f76a6c7fe6bebd3c4135688b3198f2f048d944599f2b77(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4341500c1b2ba0eb3c8334733653fe0c071d765443ac2fd6979ac992e2b81acc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56479f28537c8123a3fc3bf00e74eb128bbf3d995e5530b81de395e7e703cb7e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd4bb917a17744bd76a9c01e307552d794cb0d2b664d4eeb9b192ac118fb9a91(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53be1da78078628552e035383d1884ebdca07c7647339b19e99620e4138d41ca(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd8d4f243c89b1906f9ff9748ff6359f74d5f3a1000d2090842d79641b339abf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8995a26f0e3dbd6ccb48892c5cf821aa2c8f0a4f48a8912d7c26f5fb81c59dab(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a3be7a3e27c10044b78b94f8e9e25b9b305b73e3c9fc55428ca38c487e93439(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e42791a6d780d9d8c683aa7f63e3cb62e990fbe68225b03fc649d5b5d4c2e687(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08b819797f9f2bfc96b1001ddb9dcf7a6aeb5ddaf2e1687da62fe07d78bf9ea4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8162abb0e20bea415d3941adf31cd1ccee12624b127596113c39f55a2144668(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c98b2323462ac31ba142225944ee4534d32b5e697071e6f161f516457cf8c326(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26362fca2c96a3ad9daa3139723a97db62ca67278e1eb8159a733eee2a4f0bb3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, FederatedDatabaseInstanceStorageStores]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94f9cd92932fec002e4ab988318e94604120fa7c5070c4909460bcdec04ec1d8(
    *,
    max_staleness_seconds: typing.Optional[jsii.Number] = None,
    mode: typing.Optional[builtins.str] = None,
    tag_sets: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[FederatedDatabaseInstanceStorageStoresReadPreferenceTagSets, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2ec0575619ab7ae45f54783d637afbddbf4f4e537dd14fd1645cbed7066e73e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ba50dee1b8506a4e21669802dcde93977bc471ed42ec2c5475c4597c5dd8b0a(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[FederatedDatabaseInstanceStorageStoresReadPreferenceTagSets, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87c17c783e8c251a7db073fb12cd6c4ca72e4b3711a134b51fbdad852ac1a772(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7af36de8fd1b84791eb60c05c346f8c3de579feca199e225b4e8925756c91e83(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c5f402998017de0383ab67720e1dcfc88166f61d019af23ed01c58570488fbd(
    value: typing.Optional[FederatedDatabaseInstanceStorageStoresReadPreference],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87f0b27e574c0c33ca388ef41eeecf9da12d16771c72583994041cf6f512cbcc(
    *,
    tags: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsTags, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06d481c5cc0be938798968cc70d2f5162e7cc861eb88d3a5b17be1081b61bac8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96540b34f60084d3b135380df159c4bc243e755e87a86e202be8fd4c658002e3(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abb1f3fc2dabe7b607d7d13f42e2ee8097362ea39c03a1f78f4f63c57c650c0b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d733a783c134f3a0b0ee93147c8efddf8a067e85ebc4036cc1ff675f8de544e0(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__599ab6c7cff243811dbab0f8d00a1f50c47d01c915ab067d8ca8aea2d33dc6f3(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__075b019060c432b29ba22a2c8f0d040aeb10e8d7b36fc3a248a877f5afd78bf1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FederatedDatabaseInstanceStorageStoresReadPreferenceTagSets]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__922f75ea68aae717609d5200d8678dfe43c501b49f32e0472451b754b50a2f56(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da25d6c3783ff43df59947da15d45183df0bf26b4e89b6c322e1f3a8804284b3(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsTags, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2a7e0ca05f26619e9e124fe029ee13179b709858170e1ead03c9baafe9892e2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, FederatedDatabaseInstanceStorageStoresReadPreferenceTagSets]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29a0c60157a761329663613e79e92761d25cab0aa21ea51254599196e84ceca2(
    *,
    name: typing.Optional[builtins.str] = None,
    value: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53434c0cb210b283603227f5f3ddcc0ca1577b2331b69ef157e36b7ff9250e7c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__500cb7a2e40cece796070c53de0928c099bc6e898c729c51cfac0128b509a252(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74a1ea86ab7979f45df1fddcb70636194dc2188e44115e91368576e7d7589787(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48989e52d654549579558106c65a9e5e58a479e0206465dc38df6396c4ee19d7(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4721f8f6a2808d901ecc231f6feb0ee2556fbc27837b4c5041340c35905c2a16(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c09f10184a175b8f81e1aa8651fa680fe9186f9ea78c596ce7e61bbdc4ae7e34(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsTags]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a03d8ebcf1d943eb2ce5cf34fc6e8d0a84bd38f6ea1dc7c12f8e50f5afb63e9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__914be50309b6aa5e8845a5e495a128248398481426cb0e226d95298ff9e4e3ed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1eb8f6dd0fdcc8e8850ec8da60db367d62eccc6583e150e5df292e11843b4511(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__198dd16098f053bded5f99f9a511d9f751be5262b854b5008a05c250edb6d130(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, FederatedDatabaseInstanceStorageStoresReadPreferenceTagSetsTags]],
) -> None:
    """Type checking stubs"""
    pass
