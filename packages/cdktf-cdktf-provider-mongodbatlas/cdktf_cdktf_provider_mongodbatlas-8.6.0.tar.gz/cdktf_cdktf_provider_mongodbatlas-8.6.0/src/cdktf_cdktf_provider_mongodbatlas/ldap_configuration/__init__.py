r'''
# `mongodbatlas_ldap_configuration`

Refer to the Terraform Registry for docs: [`mongodbatlas_ldap_configuration`](https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration).
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


class LdapConfiguration(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.ldapConfiguration.LdapConfiguration",
):
    '''Represents a {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration mongodbatlas_ldap_configuration}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        authentication_enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        bind_password: builtins.str,
        bind_username: builtins.str,
        hostname: builtins.str,
        project_id: builtins.str,
        authorization_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        authz_query_template: typing.Optional[builtins.str] = None,
        ca_certificate: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        user_to_dn_mapping: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["LdapConfigurationUserToDnMapping", typing.Dict[builtins.str, typing.Any]]]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration mongodbatlas_ldap_configuration} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param authentication_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#authentication_enabled LdapConfiguration#authentication_enabled}.
        :param bind_password: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#bind_password LdapConfiguration#bind_password}.
        :param bind_username: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#bind_username LdapConfiguration#bind_username}.
        :param hostname: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#hostname LdapConfiguration#hostname}.
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#project_id LdapConfiguration#project_id}.
        :param authorization_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#authorization_enabled LdapConfiguration#authorization_enabled}.
        :param authz_query_template: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#authz_query_template LdapConfiguration#authz_query_template}.
        :param ca_certificate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#ca_certificate LdapConfiguration#ca_certificate}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#id LdapConfiguration#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param port: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#port LdapConfiguration#port}.
        :param user_to_dn_mapping: user_to_dn_mapping block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#user_to_dn_mapping LdapConfiguration#user_to_dn_mapping}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b82a60dccf54cfeb6530de7b490b661acd8d6bf604e28b44852916afb36e392)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = LdapConfigurationConfig(
            authentication_enabled=authentication_enabled,
            bind_password=bind_password,
            bind_username=bind_username,
            hostname=hostname,
            project_id=project_id,
            authorization_enabled=authorization_enabled,
            authz_query_template=authz_query_template,
            ca_certificate=ca_certificate,
            id=id,
            port=port,
            user_to_dn_mapping=user_to_dn_mapping,
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
        '''Generates CDKTF code for importing a LdapConfiguration resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the LdapConfiguration to import.
        :param import_from_id: The id of the existing LdapConfiguration that should be imported. Refer to the {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the LdapConfiguration to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26d5f31dd81d33542df08d9f8cc19007ac5eeb0e332e6c817f2180e8029b7212)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putUserToDnMapping")
    def put_user_to_dn_mapping(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["LdapConfigurationUserToDnMapping", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__204462ced710a89f729ae022df3bca57b3f1481942588ac734176f9e04e22fcb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putUserToDnMapping", [value]))

    @jsii.member(jsii_name="resetAuthorizationEnabled")
    def reset_authorization_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthorizationEnabled", []))

    @jsii.member(jsii_name="resetAuthzQueryTemplate")
    def reset_authz_query_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthzQueryTemplate", []))

    @jsii.member(jsii_name="resetCaCertificate")
    def reset_ca_certificate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCaCertificate", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetPort")
    def reset_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPort", []))

    @jsii.member(jsii_name="resetUserToDnMapping")
    def reset_user_to_dn_mapping(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserToDnMapping", []))

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
    @jsii.member(jsii_name="userToDnMapping")
    def user_to_dn_mapping(self) -> "LdapConfigurationUserToDnMappingList":
        return typing.cast("LdapConfigurationUserToDnMappingList", jsii.get(self, "userToDnMapping"))

    @builtins.property
    @jsii.member(jsii_name="authenticationEnabledInput")
    def authentication_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "authenticationEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="authorizationEnabledInput")
    def authorization_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "authorizationEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="authzQueryTemplateInput")
    def authz_query_template_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authzQueryTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="bindPasswordInput")
    def bind_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bindPasswordInput"))

    @builtins.property
    @jsii.member(jsii_name="bindUsernameInput")
    def bind_username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bindUsernameInput"))

    @builtins.property
    @jsii.member(jsii_name="caCertificateInput")
    def ca_certificate_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "caCertificateInput"))

    @builtins.property
    @jsii.member(jsii_name="hostnameInput")
    def hostname_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hostnameInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="userToDnMappingInput")
    def user_to_dn_mapping_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["LdapConfigurationUserToDnMapping"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["LdapConfigurationUserToDnMapping"]]], jsii.get(self, "userToDnMappingInput"))

    @builtins.property
    @jsii.member(jsii_name="authenticationEnabled")
    def authentication_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "authenticationEnabled"))

    @authentication_enabled.setter
    def authentication_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a605879eeffc3ccf764f895bac19f1d7a15349d227130405cb5fc56d9b97c092)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authenticationEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="authorizationEnabled")
    def authorization_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "authorizationEnabled"))

    @authorization_enabled.setter
    def authorization_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc1d267817db3766bd3a95c33d3fa990a77ebd2c5527ce82db5f5a3b870adbd8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authorizationEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="authzQueryTemplate")
    def authz_query_template(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authzQueryTemplate"))

    @authz_query_template.setter
    def authz_query_template(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40057708291a7842c00c93591bda5c1a8911d7a01abc43741361e1679f2adc2c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authzQueryTemplate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bindPassword")
    def bind_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bindPassword"))

    @bind_password.setter
    def bind_password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f687cd579ce211dcb5d2d48031a4d657a0e82d309d3f76e162ab37f11ab6a9c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bindPassword", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bindUsername")
    def bind_username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bindUsername"))

    @bind_username.setter
    def bind_username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6e730404354936be6d5f6ce19bbfd90828395992f358067d062b60b26a18dc0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bindUsername", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="caCertificate")
    def ca_certificate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "caCertificate"))

    @ca_certificate.setter
    def ca_certificate(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6922a85e0a9913e53805738967e706ea0c8910fd4d06663cbcc03b86984be4b8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "caCertificate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hostname")
    def hostname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hostname"))

    @hostname.setter
    def hostname(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61b954a075ca2e788339eb14fa3ddf6f8666d39062aaeda19aa11804c023ab96)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hostname", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9c88d64d4c85ccdf7ba53ba7ee8f41218639da57399a14f4053fc3a54a8d03b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6d47a86f0a97de8821c126d7d6916f84b06bab2a2dac02c8bf9c0b9145280d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c95740785e63e421c126145e72170c6cf0b0199232357d4ed756231d4641d1d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.ldapConfiguration.LdapConfigurationConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "authentication_enabled": "authenticationEnabled",
        "bind_password": "bindPassword",
        "bind_username": "bindUsername",
        "hostname": "hostname",
        "project_id": "projectId",
        "authorization_enabled": "authorizationEnabled",
        "authz_query_template": "authzQueryTemplate",
        "ca_certificate": "caCertificate",
        "id": "id",
        "port": "port",
        "user_to_dn_mapping": "userToDnMapping",
    },
)
class LdapConfigurationConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        authentication_enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
        bind_password: builtins.str,
        bind_username: builtins.str,
        hostname: builtins.str,
        project_id: builtins.str,
        authorization_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        authz_query_template: typing.Optional[builtins.str] = None,
        ca_certificate: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        port: typing.Optional[jsii.Number] = None,
        user_to_dn_mapping: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["LdapConfigurationUserToDnMapping", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param authentication_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#authentication_enabled LdapConfiguration#authentication_enabled}.
        :param bind_password: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#bind_password LdapConfiguration#bind_password}.
        :param bind_username: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#bind_username LdapConfiguration#bind_username}.
        :param hostname: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#hostname LdapConfiguration#hostname}.
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#project_id LdapConfiguration#project_id}.
        :param authorization_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#authorization_enabled LdapConfiguration#authorization_enabled}.
        :param authz_query_template: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#authz_query_template LdapConfiguration#authz_query_template}.
        :param ca_certificate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#ca_certificate LdapConfiguration#ca_certificate}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#id LdapConfiguration#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param port: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#port LdapConfiguration#port}.
        :param user_to_dn_mapping: user_to_dn_mapping block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#user_to_dn_mapping LdapConfiguration#user_to_dn_mapping}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d92e71ab63bcf274bcfbdddecaebd971124b0e18dc69520d6feb53b4262f9ebd)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument authentication_enabled", value=authentication_enabled, expected_type=type_hints["authentication_enabled"])
            check_type(argname="argument bind_password", value=bind_password, expected_type=type_hints["bind_password"])
            check_type(argname="argument bind_username", value=bind_username, expected_type=type_hints["bind_username"])
            check_type(argname="argument hostname", value=hostname, expected_type=type_hints["hostname"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument authorization_enabled", value=authorization_enabled, expected_type=type_hints["authorization_enabled"])
            check_type(argname="argument authz_query_template", value=authz_query_template, expected_type=type_hints["authz_query_template"])
            check_type(argname="argument ca_certificate", value=ca_certificate, expected_type=type_hints["ca_certificate"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument user_to_dn_mapping", value=user_to_dn_mapping, expected_type=type_hints["user_to_dn_mapping"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "authentication_enabled": authentication_enabled,
            "bind_password": bind_password,
            "bind_username": bind_username,
            "hostname": hostname,
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
        if authorization_enabled is not None:
            self._values["authorization_enabled"] = authorization_enabled
        if authz_query_template is not None:
            self._values["authz_query_template"] = authz_query_template
        if ca_certificate is not None:
            self._values["ca_certificate"] = ca_certificate
        if id is not None:
            self._values["id"] = id
        if port is not None:
            self._values["port"] = port
        if user_to_dn_mapping is not None:
            self._values["user_to_dn_mapping"] = user_to_dn_mapping

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
    def authentication_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#authentication_enabled LdapConfiguration#authentication_enabled}.'''
        result = self._values.get("authentication_enabled")
        assert result is not None, "Required property 'authentication_enabled' is missing"
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], result)

    @builtins.property
    def bind_password(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#bind_password LdapConfiguration#bind_password}.'''
        result = self._values.get("bind_password")
        assert result is not None, "Required property 'bind_password' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def bind_username(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#bind_username LdapConfiguration#bind_username}.'''
        result = self._values.get("bind_username")
        assert result is not None, "Required property 'bind_username' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def hostname(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#hostname LdapConfiguration#hostname}.'''
        result = self._values.get("hostname")
        assert result is not None, "Required property 'hostname' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def project_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#project_id LdapConfiguration#project_id}.'''
        result = self._values.get("project_id")
        assert result is not None, "Required property 'project_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def authorization_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#authorization_enabled LdapConfiguration#authorization_enabled}.'''
        result = self._values.get("authorization_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def authz_query_template(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#authz_query_template LdapConfiguration#authz_query_template}.'''
        result = self._values.get("authz_query_template")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ca_certificate(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#ca_certificate LdapConfiguration#ca_certificate}.'''
        result = self._values.get("ca_certificate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#id LdapConfiguration#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#port LdapConfiguration#port}.'''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def user_to_dn_mapping(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["LdapConfigurationUserToDnMapping"]]]:
        '''user_to_dn_mapping block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#user_to_dn_mapping LdapConfiguration#user_to_dn_mapping}
        '''
        result = self._values.get("user_to_dn_mapping")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["LdapConfigurationUserToDnMapping"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LdapConfigurationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.ldapConfiguration.LdapConfigurationUserToDnMapping",
    jsii_struct_bases=[],
    name_mapping={
        "ldap_query": "ldapQuery",
        "match": "match",
        "substitution": "substitution",
    },
)
class LdapConfigurationUserToDnMapping:
    def __init__(
        self,
        *,
        ldap_query: typing.Optional[builtins.str] = None,
        match: typing.Optional[builtins.str] = None,
        substitution: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param ldap_query: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#ldap_query LdapConfiguration#ldap_query}.
        :param match: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#match LdapConfiguration#match}.
        :param substitution: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#substitution LdapConfiguration#substitution}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47aacd4c6f34948f9ebafaa5f055a4987200f1f5f4a908b1d94526d62a1eb66b)
            check_type(argname="argument ldap_query", value=ldap_query, expected_type=type_hints["ldap_query"])
            check_type(argname="argument match", value=match, expected_type=type_hints["match"])
            check_type(argname="argument substitution", value=substitution, expected_type=type_hints["substitution"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if ldap_query is not None:
            self._values["ldap_query"] = ldap_query
        if match is not None:
            self._values["match"] = match
        if substitution is not None:
            self._values["substitution"] = substitution

    @builtins.property
    def ldap_query(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#ldap_query LdapConfiguration#ldap_query}.'''
        result = self._values.get("ldap_query")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def match(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#match LdapConfiguration#match}.'''
        result = self._values.get("match")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def substitution(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/ldap_configuration#substitution LdapConfiguration#substitution}.'''
        result = self._values.get("substitution")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LdapConfigurationUserToDnMapping(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LdapConfigurationUserToDnMappingList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.ldapConfiguration.LdapConfigurationUserToDnMappingList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f698ae0b1766c8f34c5d8c06ff1614f93ae0dd36bd8f150e8084918e146df031)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "LdapConfigurationUserToDnMappingOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f90f58ec8d9c6f071dfa171a978021766f07c2601e65965779412b5708b6b50)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("LdapConfigurationUserToDnMappingOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d92cdd1db6ae5bbc34c622bfbe0c3ba933380c33351c5edd565d07400a23e266)
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
            type_hints = typing.get_type_hints(_typecheckingstub__40e5e1e6a4762c3cc6eeff0cf4369b45cbf719a4daf36eb4d232df7b12ea68a3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9c0fd7ed03a8df958fd9b0b2a9ad231e89e98a440c8b77632952f15da4b58d9e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[LdapConfigurationUserToDnMapping]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[LdapConfigurationUserToDnMapping]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[LdapConfigurationUserToDnMapping]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6908c9dbd35f8cf2006d98e557b9b6015308448cce78325da59e4ddb7be11335)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class LdapConfigurationUserToDnMappingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.ldapConfiguration.LdapConfigurationUserToDnMappingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3803591eaf0ff064d82ead4990e7e41a5d1dc98fdee68f3923757a306772a700)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetLdapQuery")
    def reset_ldap_query(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLdapQuery", []))

    @jsii.member(jsii_name="resetMatch")
    def reset_match(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMatch", []))

    @jsii.member(jsii_name="resetSubstitution")
    def reset_substitution(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubstitution", []))

    @builtins.property
    @jsii.member(jsii_name="ldapQueryInput")
    def ldap_query_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ldapQueryInput"))

    @builtins.property
    @jsii.member(jsii_name="matchInput")
    def match_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "matchInput"))

    @builtins.property
    @jsii.member(jsii_name="substitutionInput")
    def substitution_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "substitutionInput"))

    @builtins.property
    @jsii.member(jsii_name="ldapQuery")
    def ldap_query(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ldapQuery"))

    @ldap_query.setter
    def ldap_query(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e14f050f94ab16acca57c7d50d6d2e839e397469b529cde2718ad3238f6af04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ldapQuery", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="match")
    def match(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "match"))

    @match.setter
    def match(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5fa5613296e636c34155d31098c5b215e0e3115965c0f2b84761227e0f72bfaa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "match", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="substitution")
    def substitution(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "substitution"))

    @substitution.setter
    def substitution(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a04ee02ecbb9b1856177913793bec1bcb2372f8b2c94843c3cface9ae5096566)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "substitution", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LdapConfigurationUserToDnMapping]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LdapConfigurationUserToDnMapping]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LdapConfigurationUserToDnMapping]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28da381c0b2fd8b1512d1ff78f06a2957e35bb2ab709e3818b04a98554490ae8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "LdapConfiguration",
    "LdapConfigurationConfig",
    "LdapConfigurationUserToDnMapping",
    "LdapConfigurationUserToDnMappingList",
    "LdapConfigurationUserToDnMappingOutputReference",
]

publication.publish()

def _typecheckingstub__7b82a60dccf54cfeb6530de7b490b661acd8d6bf604e28b44852916afb36e392(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    authentication_enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    bind_password: builtins.str,
    bind_username: builtins.str,
    hostname: builtins.str,
    project_id: builtins.str,
    authorization_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    authz_query_template: typing.Optional[builtins.str] = None,
    ca_certificate: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    port: typing.Optional[jsii.Number] = None,
    user_to_dn_mapping: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[LdapConfigurationUserToDnMapping, typing.Dict[builtins.str, typing.Any]]]]] = None,
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

def _typecheckingstub__26d5f31dd81d33542df08d9f8cc19007ac5eeb0e332e6c817f2180e8029b7212(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__204462ced710a89f729ae022df3bca57b3f1481942588ac734176f9e04e22fcb(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[LdapConfigurationUserToDnMapping, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a605879eeffc3ccf764f895bac19f1d7a15349d227130405cb5fc56d9b97c092(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc1d267817db3766bd3a95c33d3fa990a77ebd2c5527ce82db5f5a3b870adbd8(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40057708291a7842c00c93591bda5c1a8911d7a01abc43741361e1679f2adc2c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f687cd579ce211dcb5d2d48031a4d657a0e82d309d3f76e162ab37f11ab6a9c3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6e730404354936be6d5f6ce19bbfd90828395992f358067d062b60b26a18dc0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6922a85e0a9913e53805738967e706ea0c8910fd4d06663cbcc03b86984be4b8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61b954a075ca2e788339eb14fa3ddf6f8666d39062aaeda19aa11804c023ab96(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9c88d64d4c85ccdf7ba53ba7ee8f41218639da57399a14f4053fc3a54a8d03b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6d47a86f0a97de8821c126d7d6916f84b06bab2a2dac02c8bf9c0b9145280d4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c95740785e63e421c126145e72170c6cf0b0199232357d4ed756231d4641d1d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d92e71ab63bcf274bcfbdddecaebd971124b0e18dc69520d6feb53b4262f9ebd(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    authentication_enabled: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    bind_password: builtins.str,
    bind_username: builtins.str,
    hostname: builtins.str,
    project_id: builtins.str,
    authorization_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    authz_query_template: typing.Optional[builtins.str] = None,
    ca_certificate: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    port: typing.Optional[jsii.Number] = None,
    user_to_dn_mapping: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[LdapConfigurationUserToDnMapping, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47aacd4c6f34948f9ebafaa5f055a4987200f1f5f4a908b1d94526d62a1eb66b(
    *,
    ldap_query: typing.Optional[builtins.str] = None,
    match: typing.Optional[builtins.str] = None,
    substitution: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f698ae0b1766c8f34c5d8c06ff1614f93ae0dd36bd8f150e8084918e146df031(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f90f58ec8d9c6f071dfa171a978021766f07c2601e65965779412b5708b6b50(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d92cdd1db6ae5bbc34c622bfbe0c3ba933380c33351c5edd565d07400a23e266(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40e5e1e6a4762c3cc6eeff0cf4369b45cbf719a4daf36eb4d232df7b12ea68a3(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c0fd7ed03a8df958fd9b0b2a9ad231e89e98a440c8b77632952f15da4b58d9e(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6908c9dbd35f8cf2006d98e557b9b6015308448cce78325da59e4ddb7be11335(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[LdapConfigurationUserToDnMapping]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3803591eaf0ff064d82ead4990e7e41a5d1dc98fdee68f3923757a306772a700(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e14f050f94ab16acca57c7d50d6d2e839e397469b529cde2718ad3238f6af04(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fa5613296e636c34155d31098c5b215e0e3115965c0f2b84761227e0f72bfaa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a04ee02ecbb9b1856177913793bec1bcb2372f8b2c94843c3cface9ae5096566(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28da381c0b2fd8b1512d1ff78f06a2957e35bb2ab709e3818b04a98554490ae8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LdapConfigurationUserToDnMapping]],
) -> None:
    """Type checking stubs"""
    pass
