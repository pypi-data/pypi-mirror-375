r'''
# `mongodbatlas_federated_settings_org_config`

Refer to the Terraform Registry for docs: [`mongodbatlas_federated_settings_org_config`](https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_org_config).
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


class FederatedSettingsOrgConfig(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.federatedSettingsOrgConfig.FederatedSettingsOrgConfig",
):
    '''Represents a {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_org_config mongodbatlas_federated_settings_org_config}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        domain_restriction_enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        federation_settings_id: builtins.str,
        org_id: builtins.str,
        data_access_identity_provider_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        domain_allow_list: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        identity_provider_id: typing.Optional[builtins.str] = None,
        post_auth_role_grants: typing.Optional[typing.Sequence[builtins.str]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_org_config mongodbatlas_federated_settings_org_config} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param domain_restriction_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_org_config#domain_restriction_enabled FederatedSettingsOrgConfig#domain_restriction_enabled}.
        :param federation_settings_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_org_config#federation_settings_id FederatedSettingsOrgConfig#federation_settings_id}.
        :param org_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_org_config#org_id FederatedSettingsOrgConfig#org_id}.
        :param data_access_identity_provider_ids: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_org_config#data_access_identity_provider_ids FederatedSettingsOrgConfig#data_access_identity_provider_ids}.
        :param domain_allow_list: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_org_config#domain_allow_list FederatedSettingsOrgConfig#domain_allow_list}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_org_config#id FederatedSettingsOrgConfig#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_provider_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_org_config#identity_provider_id FederatedSettingsOrgConfig#identity_provider_id}.
        :param post_auth_role_grants: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_org_config#post_auth_role_grants FederatedSettingsOrgConfig#post_auth_role_grants}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7975a7c82604e939189ac9e46d4f53a20a69915113d8c330a79cbfd3862bdf07)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = FederatedSettingsOrgConfigConfig(
            domain_restriction_enabled=domain_restriction_enabled,
            federation_settings_id=federation_settings_id,
            org_id=org_id,
            data_access_identity_provider_ids=data_access_identity_provider_ids,
            domain_allow_list=domain_allow_list,
            id=id,
            identity_provider_id=identity_provider_id,
            post_auth_role_grants=post_auth_role_grants,
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
        '''Generates CDKTF code for importing a FederatedSettingsOrgConfig resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the FederatedSettingsOrgConfig to import.
        :param import_from_id: The id of the existing FederatedSettingsOrgConfig that should be imported. Refer to the {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_org_config#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the FederatedSettingsOrgConfig to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c4c1760b72a34139e8c976aac4d522ecd1ac7d50bd54650177c9a825fe7acb1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetDataAccessIdentityProviderIds")
    def reset_data_access_identity_provider_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataAccessIdentityProviderIds", []))

    @jsii.member(jsii_name="resetDomainAllowList")
    def reset_domain_allow_list(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDomainAllowList", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIdentityProviderId")
    def reset_identity_provider_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdentityProviderId", []))

    @jsii.member(jsii_name="resetPostAuthRoleGrants")
    def reset_post_auth_role_grants(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPostAuthRoleGrants", []))

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
    @jsii.member(jsii_name="userConflicts")
    def user_conflicts(self) -> "FederatedSettingsOrgConfigUserConflictsList":
        return typing.cast("FederatedSettingsOrgConfigUserConflictsList", jsii.get(self, "userConflicts"))

    @builtins.property
    @jsii.member(jsii_name="dataAccessIdentityProviderIdsInput")
    def data_access_identity_provider_ids_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "dataAccessIdentityProviderIdsInput"))

    @builtins.property
    @jsii.member(jsii_name="domainAllowListInput")
    def domain_allow_list_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "domainAllowListInput"))

    @builtins.property
    @jsii.member(jsii_name="domainRestrictionEnabledInput")
    def domain_restriction_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "domainRestrictionEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="federationSettingsIdInput")
    def federation_settings_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "federationSettingsIdInput"))

    @builtins.property
    @jsii.member(jsii_name="identityProviderIdInput")
    def identity_provider_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "identityProviderIdInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="orgIdInput")
    def org_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "orgIdInput"))

    @builtins.property
    @jsii.member(jsii_name="postAuthRoleGrantsInput")
    def post_auth_role_grants_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "postAuthRoleGrantsInput"))

    @builtins.property
    @jsii.member(jsii_name="dataAccessIdentityProviderIds")
    def data_access_identity_provider_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dataAccessIdentityProviderIds"))

    @data_access_identity_provider_ids.setter
    def data_access_identity_provider_ids(
        self,
        value: typing.List[builtins.str],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d310c7b60c2bc42b74b0e1f4d7d7aeb4e5c4a3abe5eea07183cc094b07966067)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataAccessIdentityProviderIds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="domainAllowList")
    def domain_allow_list(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "domainAllowList"))

    @domain_allow_list.setter
    def domain_allow_list(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80d3af02beb3c87d0be9dd126783a1647193c6332d599ba5ea41dadd12661e54)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "domainAllowList", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="domainRestrictionEnabled")
    def domain_restriction_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "domainRestrictionEnabled"))

    @domain_restriction_enabled.setter
    def domain_restriction_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__006026232e1bca1a1d7a3e96eb1f5bcf8f48d6754784de55343a83426d4feffd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "domainRestrictionEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="federationSettingsId")
    def federation_settings_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "federationSettingsId"))

    @federation_settings_id.setter
    def federation_settings_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0a077a0319c48d9e4a92cc70ae7ae11866c45b4aff365831f94dd9455904eca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "federationSettingsId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e260549aac8e40a7409b0854da26b183dcc04ff76a232a2cc57c20faf1991eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="identityProviderId")
    def identity_provider_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "identityProviderId"))

    @identity_provider_id.setter
    def identity_provider_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a4887e8da9c47c8dfa94a3b635e60f32677cf8930c9883391d5cb79fcc82be1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "identityProviderId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="orgId")
    def org_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "orgId"))

    @org_id.setter
    def org_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86f25ab2c5584eec9772aa09979aaddde55e76ac18a8f097dc222d0e6f2f6c8d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "orgId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="postAuthRoleGrants")
    def post_auth_role_grants(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "postAuthRoleGrants"))

    @post_auth_role_grants.setter
    def post_auth_role_grants(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b28729c0362fdadef2b1007d6b6610cf71f3eeb4399295ed9ec9e6884f5a501f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "postAuthRoleGrants", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.federatedSettingsOrgConfig.FederatedSettingsOrgConfigConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "domain_restriction_enabled": "domainRestrictionEnabled",
        "federation_settings_id": "federationSettingsId",
        "org_id": "orgId",
        "data_access_identity_provider_ids": "dataAccessIdentityProviderIds",
        "domain_allow_list": "domainAllowList",
        "id": "id",
        "identity_provider_id": "identityProviderId",
        "post_auth_role_grants": "postAuthRoleGrants",
    },
)
class FederatedSettingsOrgConfigConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        domain_restriction_enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        federation_settings_id: builtins.str,
        org_id: builtins.str,
        data_access_identity_provider_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        domain_allow_list: typing.Optional[typing.Sequence[builtins.str]] = None,
        id: typing.Optional[builtins.str] = None,
        identity_provider_id: typing.Optional[builtins.str] = None,
        post_auth_role_grants: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param domain_restriction_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_org_config#domain_restriction_enabled FederatedSettingsOrgConfig#domain_restriction_enabled}.
        :param federation_settings_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_org_config#federation_settings_id FederatedSettingsOrgConfig#federation_settings_id}.
        :param org_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_org_config#org_id FederatedSettingsOrgConfig#org_id}.
        :param data_access_identity_provider_ids: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_org_config#data_access_identity_provider_ids FederatedSettingsOrgConfig#data_access_identity_provider_ids}.
        :param domain_allow_list: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_org_config#domain_allow_list FederatedSettingsOrgConfig#domain_allow_list}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_org_config#id FederatedSettingsOrgConfig#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param identity_provider_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_org_config#identity_provider_id FederatedSettingsOrgConfig#identity_provider_id}.
        :param post_auth_role_grants: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_org_config#post_auth_role_grants FederatedSettingsOrgConfig#post_auth_role_grants}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fdf7076518c08a3b815ec415b2043794641120fc9319f0be1ab93dc5defb7b81)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument domain_restriction_enabled", value=domain_restriction_enabled, expected_type=type_hints["domain_restriction_enabled"])
            check_type(argname="argument federation_settings_id", value=federation_settings_id, expected_type=type_hints["federation_settings_id"])
            check_type(argname="argument org_id", value=org_id, expected_type=type_hints["org_id"])
            check_type(argname="argument data_access_identity_provider_ids", value=data_access_identity_provider_ids, expected_type=type_hints["data_access_identity_provider_ids"])
            check_type(argname="argument domain_allow_list", value=domain_allow_list, expected_type=type_hints["domain_allow_list"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument identity_provider_id", value=identity_provider_id, expected_type=type_hints["identity_provider_id"])
            check_type(argname="argument post_auth_role_grants", value=post_auth_role_grants, expected_type=type_hints["post_auth_role_grants"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "domain_restriction_enabled": domain_restriction_enabled,
            "federation_settings_id": federation_settings_id,
            "org_id": org_id,
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
        if data_access_identity_provider_ids is not None:
            self._values["data_access_identity_provider_ids"] = data_access_identity_provider_ids
        if domain_allow_list is not None:
            self._values["domain_allow_list"] = domain_allow_list
        if id is not None:
            self._values["id"] = id
        if identity_provider_id is not None:
            self._values["identity_provider_id"] = identity_provider_id
        if post_auth_role_grants is not None:
            self._values["post_auth_role_grants"] = post_auth_role_grants

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
    def domain_restriction_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_org_config#domain_restriction_enabled FederatedSettingsOrgConfig#domain_restriction_enabled}.'''
        result = self._values.get("domain_restriction_enabled")
        assert result is not None, "Required property 'domain_restriction_enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def federation_settings_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_org_config#federation_settings_id FederatedSettingsOrgConfig#federation_settings_id}.'''
        result = self._values.get("federation_settings_id")
        assert result is not None, "Required property 'federation_settings_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def org_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_org_config#org_id FederatedSettingsOrgConfig#org_id}.'''
        result = self._values.get("org_id")
        assert result is not None, "Required property 'org_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def data_access_identity_provider_ids(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_org_config#data_access_identity_provider_ids FederatedSettingsOrgConfig#data_access_identity_provider_ids}.'''
        result = self._values.get("data_access_identity_provider_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def domain_allow_list(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_org_config#domain_allow_list FederatedSettingsOrgConfig#domain_allow_list}.'''
        result = self._values.get("domain_allow_list")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_org_config#id FederatedSettingsOrgConfig#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def identity_provider_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_org_config#identity_provider_id FederatedSettingsOrgConfig#identity_provider_id}.'''
        result = self._values.get("identity_provider_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def post_auth_role_grants(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_org_config#post_auth_role_grants FederatedSettingsOrgConfig#post_auth_role_grants}.'''
        result = self._values.get("post_auth_role_grants")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FederatedSettingsOrgConfigConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.federatedSettingsOrgConfig.FederatedSettingsOrgConfigUserConflicts",
    jsii_struct_bases=[],
    name_mapping={},
)
class FederatedSettingsOrgConfigUserConflicts:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FederatedSettingsOrgConfigUserConflicts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class FederatedSettingsOrgConfigUserConflictsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.federatedSettingsOrgConfig.FederatedSettingsOrgConfigUserConflictsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__daf62af4de619bd262ade5e53a5fde7171d852e02f43039e0dff6a24d7dd9c4b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "FederatedSettingsOrgConfigUserConflictsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8b801a8bc220ea4ed757b30855247023b82368c757cc21a71552d0c1eea7d4e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("FederatedSettingsOrgConfigUserConflictsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca2d116848393230e94c7173a974b4af941c7a11cfe758611412987cf7342ced)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8c8949eeab9eeadf61e47a114c65ea6b6f6b700f30d2c1ba3d2c1ef92cf0f0b2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7b8bcc5de2970d50e1fe68cc68463460d7f3ea2553b51b7607d3b2e1fc4a48f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class FederatedSettingsOrgConfigUserConflictsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.federatedSettingsOrgConfig.FederatedSettingsOrgConfigUserConflictsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7a3a303f1cce25180ad1b3efd98cb54a4c901734219d80642c434fa5c3a2a093)
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
    ) -> typing.Optional[FederatedSettingsOrgConfigUserConflicts]:
        return typing.cast(typing.Optional[FederatedSettingsOrgConfigUserConflicts], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[FederatedSettingsOrgConfigUserConflicts],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51d313826ded5dc1f623b1024184bca2c1e0e226246dfce2795b777976325000)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "FederatedSettingsOrgConfig",
    "FederatedSettingsOrgConfigConfig",
    "FederatedSettingsOrgConfigUserConflicts",
    "FederatedSettingsOrgConfigUserConflictsList",
    "FederatedSettingsOrgConfigUserConflictsOutputReference",
]

publication.publish()

def _typecheckingstub__7975a7c82604e939189ac9e46d4f53a20a69915113d8c330a79cbfd3862bdf07(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    domain_restriction_enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    federation_settings_id: builtins.str,
    org_id: builtins.str,
    data_access_identity_provider_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    domain_allow_list: typing.Optional[typing.Sequence[builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    identity_provider_id: typing.Optional[builtins.str] = None,
    post_auth_role_grants: typing.Optional[typing.Sequence[builtins.str]] = None,
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

def _typecheckingstub__8c4c1760b72a34139e8c976aac4d522ecd1ac7d50bd54650177c9a825fe7acb1(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d310c7b60c2bc42b74b0e1f4d7d7aeb4e5c4a3abe5eea07183cc094b07966067(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80d3af02beb3c87d0be9dd126783a1647193c6332d599ba5ea41dadd12661e54(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__006026232e1bca1a1d7a3e96eb1f5bcf8f48d6754784de55343a83426d4feffd(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0a077a0319c48d9e4a92cc70ae7ae11866c45b4aff365831f94dd9455904eca(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e260549aac8e40a7409b0854da26b183dcc04ff76a232a2cc57c20faf1991eb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a4887e8da9c47c8dfa94a3b635e60f32677cf8930c9883391d5cb79fcc82be1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86f25ab2c5584eec9772aa09979aaddde55e76ac18a8f097dc222d0e6f2f6c8d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b28729c0362fdadef2b1007d6b6610cf71f3eeb4399295ed9ec9e6884f5a501f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdf7076518c08a3b815ec415b2043794641120fc9319f0be1ab93dc5defb7b81(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    domain_restriction_enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    federation_settings_id: builtins.str,
    org_id: builtins.str,
    data_access_identity_provider_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    domain_allow_list: typing.Optional[typing.Sequence[builtins.str]] = None,
    id: typing.Optional[builtins.str] = None,
    identity_provider_id: typing.Optional[builtins.str] = None,
    post_auth_role_grants: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__daf62af4de619bd262ade5e53a5fde7171d852e02f43039e0dff6a24d7dd9c4b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8b801a8bc220ea4ed757b30855247023b82368c757cc21a71552d0c1eea7d4e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca2d116848393230e94c7173a974b4af941c7a11cfe758611412987cf7342ced(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c8949eeab9eeadf61e47a114c65ea6b6f6b700f30d2c1ba3d2c1ef92cf0f0b2(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b8bcc5de2970d50e1fe68cc68463460d7f3ea2553b51b7607d3b2e1fc4a48f3(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a3a303f1cce25180ad1b3efd98cb54a4c901734219d80642c434fa5c3a2a093(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51d313826ded5dc1f623b1024184bca2c1e0e226246dfce2795b777976325000(
    value: typing.Optional[FederatedSettingsOrgConfigUserConflicts],
) -> None:
    """Type checking stubs"""
    pass
