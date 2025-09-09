r'''
# `data_mongodbatlas_federated_settings_identity_providers`

Refer to the Terraform Registry for docs: [`data_mongodbatlas_federated_settings_identity_providers`](https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/data-sources/federated_settings_identity_providers).
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


class DataMongodbatlasFederatedSettingsIdentityProviders(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasFederatedSettingsIdentityProviders.DataMongodbatlasFederatedSettingsIdentityProviders",
):
    '''Represents a {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/data-sources/federated_settings_identity_providers mongodbatlas_federated_settings_identity_providers}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        federation_settings_id: builtins.str,
        id: typing.Optional[builtins.str] = None,
        idp_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        protocols: typing.Optional[typing.Sequence[builtins.str]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/data-sources/federated_settings_identity_providers mongodbatlas_federated_settings_identity_providers} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param federation_settings_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/data-sources/federated_settings_identity_providers#federation_settings_id DataMongodbatlasFederatedSettingsIdentityProviders#federation_settings_id}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/data-sources/federated_settings_identity_providers#id DataMongodbatlasFederatedSettingsIdentityProviders#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param idp_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/data-sources/federated_settings_identity_providers#idp_types DataMongodbatlasFederatedSettingsIdentityProviders#idp_types}.
        :param protocols: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/data-sources/federated_settings_identity_providers#protocols DataMongodbatlasFederatedSettingsIdentityProviders#protocols}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e2bec59a71c9edac3c16c1e6e67fb67d38584f36de37ca4e37b2ee0845f1d2d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataMongodbatlasFederatedSettingsIdentityProvidersConfig(
            federation_settings_id=federation_settings_id,
            id=id,
            idp_types=idp_types,
            protocols=protocols,
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
        '''Generates CDKTF code for importing a DataMongodbatlasFederatedSettingsIdentityProviders resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataMongodbatlasFederatedSettingsIdentityProviders to import.
        :param import_from_id: The id of the existing DataMongodbatlasFederatedSettingsIdentityProviders that should be imported. Refer to the {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/data-sources/federated_settings_identity_providers#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataMongodbatlasFederatedSettingsIdentityProviders to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2855b9c6d112d520f9988858e8ca1bba83ea91396ecfe18f5eb7bd4890129d50)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIdpTypes")
    def reset_idp_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdpTypes", []))

    @jsii.member(jsii_name="resetProtocols")
    def reset_protocols(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProtocols", []))

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
    @jsii.member(jsii_name="results")
    def results(
        self,
    ) -> "DataMongodbatlasFederatedSettingsIdentityProvidersResultsList":
        return typing.cast("DataMongodbatlasFederatedSettingsIdentityProvidersResultsList", jsii.get(self, "results"))

    @builtins.property
    @jsii.member(jsii_name="federationSettingsIdInput")
    def federation_settings_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "federationSettingsIdInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="idpTypesInput")
    def idp_types_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "idpTypesInput"))

    @builtins.property
    @jsii.member(jsii_name="protocolsInput")
    def protocols_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "protocolsInput"))

    @builtins.property
    @jsii.member(jsii_name="federationSettingsId")
    def federation_settings_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "federationSettingsId"))

    @federation_settings_id.setter
    def federation_settings_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aad42e91ac376b1ab672247ec91c16523d0e55f382352ca21f86215f2b96bf31)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "federationSettingsId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__915e0d0342bacc56200bae48f535e0fe01e98ff31c777d028c0ab72cb12eddc9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="idpTypes")
    def idp_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "idpTypes"))

    @idp_types.setter
    def idp_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57a1764d2c4ca44a530835504663441154edcedbd769ff3542d4ff207b7c53ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "idpTypes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="protocols")
    def protocols(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "protocols"))

    @protocols.setter
    def protocols(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e67d8f19b12619622bfb87793fed71df7e6a2be7e1276641ec9ac9565e8aaf7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "protocols", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasFederatedSettingsIdentityProviders.DataMongodbatlasFederatedSettingsIdentityProvidersConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "federation_settings_id": "federationSettingsId",
        "id": "id",
        "idp_types": "idpTypes",
        "protocols": "protocols",
    },
)
class DataMongodbatlasFederatedSettingsIdentityProvidersConfig(
    _cdktf_9a9027ec.TerraformMetaArguments,
):
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
        federation_settings_id: builtins.str,
        id: typing.Optional[builtins.str] = None,
        idp_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        protocols: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param federation_settings_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/data-sources/federated_settings_identity_providers#federation_settings_id DataMongodbatlasFederatedSettingsIdentityProviders#federation_settings_id}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/data-sources/federated_settings_identity_providers#id DataMongodbatlasFederatedSettingsIdentityProviders#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param idp_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/data-sources/federated_settings_identity_providers#idp_types DataMongodbatlasFederatedSettingsIdentityProviders#idp_types}.
        :param protocols: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/data-sources/federated_settings_identity_providers#protocols DataMongodbatlasFederatedSettingsIdentityProviders#protocols}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d73a159751fb946b4e80593e8ab2894520d49e74b5eddc68f8aedd540aa45ec)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument federation_settings_id", value=federation_settings_id, expected_type=type_hints["federation_settings_id"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument idp_types", value=idp_types, expected_type=type_hints["idp_types"])
            check_type(argname="argument protocols", value=protocols, expected_type=type_hints["protocols"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "federation_settings_id": federation_settings_id,
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
        if idp_types is not None:
            self._values["idp_types"] = idp_types
        if protocols is not None:
            self._values["protocols"] = protocols

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
    def federation_settings_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/data-sources/federated_settings_identity_providers#federation_settings_id DataMongodbatlasFederatedSettingsIdentityProviders#federation_settings_id}.'''
        result = self._values.get("federation_settings_id")
        assert result is not None, "Required property 'federation_settings_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/data-sources/federated_settings_identity_providers#id DataMongodbatlasFederatedSettingsIdentityProviders#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def idp_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/data-sources/federated_settings_identity_providers#idp_types DataMongodbatlasFederatedSettingsIdentityProviders#idp_types}.'''
        result = self._values.get("idp_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def protocols(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/data-sources/federated_settings_identity_providers#protocols DataMongodbatlasFederatedSettingsIdentityProviders#protocols}.'''
        result = self._values.get("protocols")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataMongodbatlasFederatedSettingsIdentityProvidersConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasFederatedSettingsIdentityProviders.DataMongodbatlasFederatedSettingsIdentityProvidersResults",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataMongodbatlasFederatedSettingsIdentityProvidersResults:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataMongodbatlasFederatedSettingsIdentityProvidersResults(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasFederatedSettingsIdentityProviders.DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgs",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgs:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgs(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasFederatedSettingsIdentityProviders.DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bdf1956342e75ef02482c125276e00f1cf1404529468d3f779e65cb5d5ebe0e0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c386e64a9c5e19ba34a6531ba0199f17fbfb1fe512e31eaab01b21976fad7276)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a5ec47aa75674e660bde81d34c13d3480dc845164cf6fa86df8970f34ee8e4f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ab5766bd0d34cd2f52dae65d81655469feed191e50e64b2ba1bf9f5e420d0944)
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
            type_hints = typing.get_type_hints(_typecheckingstub__581572024f9b5d2dda9afe2907cfb7a3d2a71f3d9650e8fbdf9324408f4a7ad9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasFederatedSettingsIdentityProviders.DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__92e1e3420d9e383522371160e6057ae2e7f91586849db768d3357d7fc3355714)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="domainAllowList")
    def domain_allow_list(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "domainAllowList"))

    @builtins.property
    @jsii.member(jsii_name="domainRestrictionEnabled")
    def domain_restriction_enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "domainRestrictionEnabled"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @builtins.property
    @jsii.member(jsii_name="orgId")
    def org_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "orgId"))

    @builtins.property
    @jsii.member(jsii_name="postAuthRoleGrants")
    def post_auth_role_grants(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "postAuthRoleGrants"))

    @builtins.property
    @jsii.member(jsii_name="roleMappings")
    def role_mappings(
        self,
    ) -> "DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappingsList":
        return typing.cast("DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappingsList", jsii.get(self, "roleMappings"))

    @builtins.property
    @jsii.member(jsii_name="userConflicts")
    def user_conflicts(
        self,
    ) -> "DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsUserConflictsList":
        return typing.cast("DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsUserConflictsList", jsii.get(self, "userConflicts"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgs]:
        return typing.cast(typing.Optional[DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgs], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgs],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9595cbbc675c12a695ef706fcb20daff9a9e1f30b4022e74e00b8d893523e559)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasFederatedSettingsIdentityProviders.DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappings",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappings:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappingsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasFederatedSettingsIdentityProviders.DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappingsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e8fb11e6bcb93a3200cb5cb701d4ec140fde1e0125a8f24f4ff1d566714a5d98)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappingsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24953973a6d59f9e297e035ea59d8e6c41103ed763b53d7a9679ca6eee939950)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappingsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52ef097062a8c802a497848c8ce548d753813497a49e071cfdffbfc2b0576bbe)
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
            type_hints = typing.get_type_hints(_typecheckingstub__895b939688c34eb49dbaffeea4723131accd3d7ba2a1ef07a7bb60a789e2fd27)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c6c109c5a6f450454b1f76c62407a922936310e1630329cbdaab991f3c4a570b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappingsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasFederatedSettingsIdentityProviders.DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappingsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__45786812a0a5c2936475bed2b66075617fba77abc94399278b76dc0560616198)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="externalGroupName")
    def external_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "externalGroupName"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="roleAssignments")
    def role_assignments(
        self,
    ) -> "DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappingsRoleAssignmentsList":
        return typing.cast("DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappingsRoleAssignmentsList", jsii.get(self, "roleAssignments"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappings]:
        return typing.cast(typing.Optional[DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappings], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappings],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__549064ab5eba6a1fb884dee3c1fd90f20f44d8bfa28fe9e596d5f45dd6337178)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasFederatedSettingsIdentityProviders.DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappingsRoleAssignments",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappingsRoleAssignments:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappingsRoleAssignments(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappingsRoleAssignmentsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasFederatedSettingsIdentityProviders.DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappingsRoleAssignmentsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__55a9ab1eed9bd64098c446860a98def1563015d1b28b155344acafa16936117b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappingsRoleAssignmentsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26d0f63ecfb9522d5978e9cd21294eba780e352ed9d354e9ecf0add8d50f5d03)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappingsRoleAssignmentsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80d33380ceae994196baa88ab87bfa0a56b0237a742278e9f0242e8eb35af8f4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4ac8aec82e84d0ace19a83663f8e7cfc248833e37cb8cbfd674f5e7f3a20630e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e8c0e6b4f1a14eccc7c47bc4cf45edf0f097c28fd4f3f5bb87787fc69bdf6df9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappingsRoleAssignmentsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasFederatedSettingsIdentityProviders.DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappingsRoleAssignmentsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b03ae919ac289b3a9fd81811707e6ea3fe41f83204d1162c80f5c46f8c2398d9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="groupId")
    def group_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "groupId"))

    @builtins.property
    @jsii.member(jsii_name="orgId")
    def org_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "orgId"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "role"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappingsRoleAssignments]:
        return typing.cast(typing.Optional[DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappingsRoleAssignments], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappingsRoleAssignments],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b4f5e189f94342cf0a89afd58c874a3fb3ba330399721ea0c1aa8c988843cbc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasFederatedSettingsIdentityProviders.DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsUserConflicts",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsUserConflicts:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsUserConflicts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsUserConflictsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasFederatedSettingsIdentityProviders.DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsUserConflictsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f47b7511b057c46e7e7be14d7fb863a92e6a76a5f89d6ab4c7375ab2f9715b25)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsUserConflictsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbb750e75671ac21c4c50add0b2987fd316de5e02b8e64d7489e732f61d6efba)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsUserConflictsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__120b6b458cc5863d9f657668a10e86914e7d51109f9c490b8350eeecb1e32607)
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
            type_hints = typing.get_type_hints(_typecheckingstub__21aa1115e3db7e00114e22eca146482933a42fa29457c8d528b8179713d687e6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6817436201a366b8842eae8dcc2ef351f47c1885366e87ec5f33c145f8daf956)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsUserConflictsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasFederatedSettingsIdentityProviders.DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsUserConflictsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8fe47d8480ef96deabf7d04c28a8c976635d35b0d5322ef72443eea38bc73ca2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="emailAddress")
    def email_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailAddress"))

    @builtins.property
    @jsii.member(jsii_name="federationSettingsId")
    def federation_settings_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "federationSettingsId"))

    @builtins.property
    @jsii.member(jsii_name="firstName")
    def first_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "firstName"))

    @builtins.property
    @jsii.member(jsii_name="lastName")
    def last_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "lastName"))

    @builtins.property
    @jsii.member(jsii_name="userId")
    def user_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsUserConflicts]:
        return typing.cast(typing.Optional[DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsUserConflicts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsUserConflicts],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2911f975e7f16c58bf2e410c69d5448b5c1235b7abd2e262f87a59771996563)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataMongodbatlasFederatedSettingsIdentityProvidersResultsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasFederatedSettingsIdentityProviders.DataMongodbatlasFederatedSettingsIdentityProvidersResultsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1ad95cf1ef89c64eb021ece81d9169c81d5146c316d6da32c5044f270d11a7b2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataMongodbatlasFederatedSettingsIdentityProvidersResultsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__deab286218f9a6dacd3461b595bf63372aa5b265529fe5b6ad515d32af59c244)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataMongodbatlasFederatedSettingsIdentityProvidersResultsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fcd09f49a26f675c68833cad1bfdd698c60a8c8a5904a28a55342d719a9f2351)
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
            type_hints = typing.get_type_hints(_typecheckingstub__447358851319d3472d8515c02e5e5e431728a24efaec0980ef3af1cde822ca96)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6727f85845f62011d14b0c9df24fbc621b27a15de321379f33c6b48abf77f24c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataMongodbatlasFederatedSettingsIdentityProvidersResultsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasFederatedSettingsIdentityProviders.DataMongodbatlasFederatedSettingsIdentityProvidersResultsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fe93ea9a95087ff5e58c3027b1a0ca1d6d92e2400dd5ef265eef9bf0d789ac19)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="acsUrl")
    def acs_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "acsUrl"))

    @builtins.property
    @jsii.member(jsii_name="associatedDomains")
    def associated_domains(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "associatedDomains"))

    @builtins.property
    @jsii.member(jsii_name="associatedOrgs")
    def associated_orgs(
        self,
    ) -> DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsList:
        return typing.cast(DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsList, jsii.get(self, "associatedOrgs"))

    @builtins.property
    @jsii.member(jsii_name="audience")
    def audience(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "audience"))

    @builtins.property
    @jsii.member(jsii_name="audienceUri")
    def audience_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "audienceUri"))

    @builtins.property
    @jsii.member(jsii_name="authorizationType")
    def authorization_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authorizationType"))

    @builtins.property
    @jsii.member(jsii_name="clientId")
    def client_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientId"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="displayName")
    def display_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "displayName"))

    @builtins.property
    @jsii.member(jsii_name="groupsClaim")
    def groups_claim(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "groupsClaim"))

    @builtins.property
    @jsii.member(jsii_name="idpId")
    def idp_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "idpId"))

    @builtins.property
    @jsii.member(jsii_name="idpType")
    def idp_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "idpType"))

    @builtins.property
    @jsii.member(jsii_name="issuerUri")
    def issuer_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "issuerUri"))

    @builtins.property
    @jsii.member(jsii_name="oktaIdpId")
    def okta_idp_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oktaIdpId"))

    @builtins.property
    @jsii.member(jsii_name="pemFileInfo")
    def pem_file_info(
        self,
    ) -> "DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfoList":
        return typing.cast("DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfoList", jsii.get(self, "pemFileInfo"))

    @builtins.property
    @jsii.member(jsii_name="protocol")
    def protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "protocol"))

    @builtins.property
    @jsii.member(jsii_name="requestBinding")
    def request_binding(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "requestBinding"))

    @builtins.property
    @jsii.member(jsii_name="requestedScopes")
    def requested_scopes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "requestedScopes"))

    @builtins.property
    @jsii.member(jsii_name="responseSignatureAlgorithm")
    def response_signature_algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "responseSignatureAlgorithm"))

    @builtins.property
    @jsii.member(jsii_name="ssoDebugEnabled")
    def sso_debug_enabled(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "ssoDebugEnabled"))

    @builtins.property
    @jsii.member(jsii_name="ssoUrl")
    def sso_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ssoUrl"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property
    @jsii.member(jsii_name="userClaim")
    def user_claim(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userClaim"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataMongodbatlasFederatedSettingsIdentityProvidersResults]:
        return typing.cast(typing.Optional[DataMongodbatlasFederatedSettingsIdentityProvidersResults], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataMongodbatlasFederatedSettingsIdentityProvidersResults],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26cd2b3f2db4c0abb40f345ccf2e0288b1cd8c26867f88aae554181f6ab8641f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasFederatedSettingsIdentityProviders.DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfo",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfo:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfo(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasFederatedSettingsIdentityProviders.DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfoCertificates",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfoCertificates:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfoCertificates(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfoCertificatesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasFederatedSettingsIdentityProviders.DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfoCertificatesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0feefa61c813ce0847c74cbe32bbdcc107a999ded7a64bc57363719cdad5eec9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfoCertificatesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed7621efe6610b511003bf07ce051192b8c5e28d75b0e3105fcfa232e17fe344)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfoCertificatesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eda692ffda54f0e4b778686984754ee0ec88257df1760aa4e7ca7d89c5014312)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d188b102691dc481b4c2c7cca5ff3ffba15aaa590139424c23e008ccd7344d8b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c499b429077af32360c38a18e528e1bb2dc3c402cf69fa77d85f91996940af1a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfoCertificatesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasFederatedSettingsIdentityProviders.DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfoCertificatesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__00a240be86817d4ad08e22ffc68755fa32bd3c03f22beca427cf0acd468c7357)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="notAfter")
    def not_after(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notAfter"))

    @builtins.property
    @jsii.member(jsii_name="notBefore")
    def not_before(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notBefore"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfoCertificates]:
        return typing.cast(typing.Optional[DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfoCertificates], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfoCertificates],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55d97308437fcb0d8ac6dc7eb1897b911c27fcc68c57670497b035ed10282c75)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfoList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasFederatedSettingsIdentityProviders.DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfoList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e2883ea3b02e7f7b52f5a75c65e5de4aca4997b303310ead9b06fc3d37e452a3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfoOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1df4952be71c3fb54708630e782917af7827d369e7ebf88820652c7a8606c461)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfoOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__412047fabe261de4efd7b45eb9db83ff1c1742cbcf30eddc27460ab3dc7ed1d3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__dde65579b4b0ffbdf335ad954a31373e4124cc573109c6a8a743f96370b9c413)
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
            type_hints = typing.get_type_hints(_typecheckingstub__119b963fa438473b4e62cf263885c5dfa6067951bbf3d59770d1a03676cbee28)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfoOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.dataMongodbatlasFederatedSettingsIdentityProviders.DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfoOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__32b782f4c9df1199a7d3d7106ec862d58c34676841ff2e2452c71e0bf63b7d04)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="certificates")
    def certificates(
        self,
    ) -> DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfoCertificatesList:
        return typing.cast(DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfoCertificatesList, jsii.get(self, "certificates"))

    @builtins.property
    @jsii.member(jsii_name="fileName")
    def file_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileName"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfo]:
        return typing.cast(typing.Optional[DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfo], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfo],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e87ff71fe059676c99e37f4c38bdfdb0ddc041e773d9dad053d97fadcf49adde)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataMongodbatlasFederatedSettingsIdentityProviders",
    "DataMongodbatlasFederatedSettingsIdentityProvidersConfig",
    "DataMongodbatlasFederatedSettingsIdentityProvidersResults",
    "DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgs",
    "DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsList",
    "DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsOutputReference",
    "DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappings",
    "DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappingsList",
    "DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappingsOutputReference",
    "DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappingsRoleAssignments",
    "DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappingsRoleAssignmentsList",
    "DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappingsRoleAssignmentsOutputReference",
    "DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsUserConflicts",
    "DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsUserConflictsList",
    "DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsUserConflictsOutputReference",
    "DataMongodbatlasFederatedSettingsIdentityProvidersResultsList",
    "DataMongodbatlasFederatedSettingsIdentityProvidersResultsOutputReference",
    "DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfo",
    "DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfoCertificates",
    "DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfoCertificatesList",
    "DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfoCertificatesOutputReference",
    "DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfoList",
    "DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfoOutputReference",
]

publication.publish()

def _typecheckingstub__0e2bec59a71c9edac3c16c1e6e67fb67d38584f36de37ca4e37b2ee0845f1d2d(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    federation_settings_id: builtins.str,
    id: typing.Optional[builtins.str] = None,
    idp_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    protocols: typing.Optional[typing.Sequence[builtins.str]] = None,
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

def _typecheckingstub__2855b9c6d112d520f9988858e8ca1bba83ea91396ecfe18f5eb7bd4890129d50(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aad42e91ac376b1ab672247ec91c16523d0e55f382352ca21f86215f2b96bf31(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__915e0d0342bacc56200bae48f535e0fe01e98ff31c777d028c0ab72cb12eddc9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57a1764d2c4ca44a530835504663441154edcedbd769ff3542d4ff207b7c53ba(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e67d8f19b12619622bfb87793fed71df7e6a2be7e1276641ec9ac9565e8aaf7(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d73a159751fb946b4e80593e8ab2894520d49e74b5eddc68f8aedd540aa45ec(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    federation_settings_id: builtins.str,
    id: typing.Optional[builtins.str] = None,
    idp_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    protocols: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bdf1956342e75ef02482c125276e00f1cf1404529468d3f779e65cb5d5ebe0e0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c386e64a9c5e19ba34a6531ba0199f17fbfb1fe512e31eaab01b21976fad7276(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a5ec47aa75674e660bde81d34c13d3480dc845164cf6fa86df8970f34ee8e4f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab5766bd0d34cd2f52dae65d81655469feed191e50e64b2ba1bf9f5e420d0944(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__581572024f9b5d2dda9afe2907cfb7a3d2a71f3d9650e8fbdf9324408f4a7ad9(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92e1e3420d9e383522371160e6057ae2e7f91586849db768d3357d7fc3355714(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9595cbbc675c12a695ef706fcb20daff9a9e1f30b4022e74e00b8d893523e559(
    value: typing.Optional[DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgs],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8fb11e6bcb93a3200cb5cb701d4ec140fde1e0125a8f24f4ff1d566714a5d98(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24953973a6d59f9e297e035ea59d8e6c41103ed763b53d7a9679ca6eee939950(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52ef097062a8c802a497848c8ce548d753813497a49e071cfdffbfc2b0576bbe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__895b939688c34eb49dbaffeea4723131accd3d7ba2a1ef07a7bb60a789e2fd27(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6c109c5a6f450454b1f76c62407a922936310e1630329cbdaab991f3c4a570b(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45786812a0a5c2936475bed2b66075617fba77abc94399278b76dc0560616198(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__549064ab5eba6a1fb884dee3c1fd90f20f44d8bfa28fe9e596d5f45dd6337178(
    value: typing.Optional[DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappings],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55a9ab1eed9bd64098c446860a98def1563015d1b28b155344acafa16936117b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26d0f63ecfb9522d5978e9cd21294eba780e352ed9d354e9ecf0add8d50f5d03(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80d33380ceae994196baa88ab87bfa0a56b0237a742278e9f0242e8eb35af8f4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ac8aec82e84d0ace19a83663f8e7cfc248833e37cb8cbfd674f5e7f3a20630e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8c0e6b4f1a14eccc7c47bc4cf45edf0f097c28fd4f3f5bb87787fc69bdf6df9(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b03ae919ac289b3a9fd81811707e6ea3fe41f83204d1162c80f5c46f8c2398d9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b4f5e189f94342cf0a89afd58c874a3fb3ba330399721ea0c1aa8c988843cbc(
    value: typing.Optional[DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsRoleMappingsRoleAssignments],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f47b7511b057c46e7e7be14d7fb863a92e6a76a5f89d6ab4c7375ab2f9715b25(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbb750e75671ac21c4c50add0b2987fd316de5e02b8e64d7489e732f61d6efba(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__120b6b458cc5863d9f657668a10e86914e7d51109f9c490b8350eeecb1e32607(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21aa1115e3db7e00114e22eca146482933a42fa29457c8d528b8179713d687e6(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6817436201a366b8842eae8dcc2ef351f47c1885366e87ec5f33c145f8daf956(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8fe47d8480ef96deabf7d04c28a8c976635d35b0d5322ef72443eea38bc73ca2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2911f975e7f16c58bf2e410c69d5448b5c1235b7abd2e262f87a59771996563(
    value: typing.Optional[DataMongodbatlasFederatedSettingsIdentityProvidersResultsAssociatedOrgsUserConflicts],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ad95cf1ef89c64eb021ece81d9169c81d5146c316d6da32c5044f270d11a7b2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__deab286218f9a6dacd3461b595bf63372aa5b265529fe5b6ad515d32af59c244(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fcd09f49a26f675c68833cad1bfdd698c60a8c8a5904a28a55342d719a9f2351(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__447358851319d3472d8515c02e5e5e431728a24efaec0980ef3af1cde822ca96(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6727f85845f62011d14b0c9df24fbc621b27a15de321379f33c6b48abf77f24c(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe93ea9a95087ff5e58c3027b1a0ca1d6d92e2400dd5ef265eef9bf0d789ac19(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26cd2b3f2db4c0abb40f345ccf2e0288b1cd8c26867f88aae554181f6ab8641f(
    value: typing.Optional[DataMongodbatlasFederatedSettingsIdentityProvidersResults],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0feefa61c813ce0847c74cbe32bbdcc107a999ded7a64bc57363719cdad5eec9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed7621efe6610b511003bf07ce051192b8c5e28d75b0e3105fcfa232e17fe344(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eda692ffda54f0e4b778686984754ee0ec88257df1760aa4e7ca7d89c5014312(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d188b102691dc481b4c2c7cca5ff3ffba15aaa590139424c23e008ccd7344d8b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c499b429077af32360c38a18e528e1bb2dc3c402cf69fa77d85f91996940af1a(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00a240be86817d4ad08e22ffc68755fa32bd3c03f22beca427cf0acd468c7357(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55d97308437fcb0d8ac6dc7eb1897b911c27fcc68c57670497b035ed10282c75(
    value: typing.Optional[DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfoCertificates],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2883ea3b02e7f7b52f5a75c65e5de4aca4997b303310ead9b06fc3d37e452a3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1df4952be71c3fb54708630e782917af7827d369e7ebf88820652c7a8606c461(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__412047fabe261de4efd7b45eb9db83ff1c1742cbcf30eddc27460ab3dc7ed1d3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dde65579b4b0ffbdf335ad954a31373e4124cc573109c6a8a743f96370b9c413(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__119b963fa438473b4e62cf263885c5dfa6067951bbf3d59770d1a03676cbee28(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32b782f4c9df1199a7d3d7106ec862d58c34676841ff2e2452c71e0bf63b7d04(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e87ff71fe059676c99e37f4c38bdfdb0ddc041e773d9dad053d97fadcf49adde(
    value: typing.Optional[DataMongodbatlasFederatedSettingsIdentityProvidersResultsPemFileInfo],
) -> None:
    """Type checking stubs"""
    pass
