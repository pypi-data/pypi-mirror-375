r'''
# `mongodbatlas_federated_settings_identity_provider`

Refer to the Terraform Registry for docs: [`mongodbatlas_federated_settings_identity_provider`](https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider).
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


class FederatedSettingsIdentityProvider(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.federatedSettingsIdentityProvider.FederatedSettingsIdentityProvider",
):
    '''Represents a {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider mongodbatlas_federated_settings_identity_provider}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        federation_settings_id: builtins.str,
        issuer_uri: builtins.str,
        name: builtins.str,
        associated_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
        audience: typing.Optional[builtins.str] = None,
        authorization_type: typing.Optional[builtins.str] = None,
        client_id: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        groups_claim: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        idp_type: typing.Optional[builtins.str] = None,
        protocol: typing.Optional[builtins.str] = None,
        request_binding: typing.Optional[builtins.str] = None,
        requested_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
        response_signature_algorithm: typing.Optional[builtins.str] = None,
        sso_debug_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        sso_url: typing.Optional[builtins.str] = None,
        status: typing.Optional[builtins.str] = None,
        user_claim: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider mongodbatlas_federated_settings_identity_provider} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param federation_settings_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#federation_settings_id FederatedSettingsIdentityProvider#federation_settings_id}.
        :param issuer_uri: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#issuer_uri FederatedSettingsIdentityProvider#issuer_uri}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#name FederatedSettingsIdentityProvider#name}.
        :param associated_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#associated_domains FederatedSettingsIdentityProvider#associated_domains}.
        :param audience: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#audience FederatedSettingsIdentityProvider#audience}.
        :param authorization_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#authorization_type FederatedSettingsIdentityProvider#authorization_type}.
        :param client_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#client_id FederatedSettingsIdentityProvider#client_id}.
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#description FederatedSettingsIdentityProvider#description}.
        :param groups_claim: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#groups_claim FederatedSettingsIdentityProvider#groups_claim}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#id FederatedSettingsIdentityProvider#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param idp_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#idp_type FederatedSettingsIdentityProvider#idp_type}.
        :param protocol: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#protocol FederatedSettingsIdentityProvider#protocol}.
        :param request_binding: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#request_binding FederatedSettingsIdentityProvider#request_binding}.
        :param requested_scopes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#requested_scopes FederatedSettingsIdentityProvider#requested_scopes}.
        :param response_signature_algorithm: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#response_signature_algorithm FederatedSettingsIdentityProvider#response_signature_algorithm}.
        :param sso_debug_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#sso_debug_enabled FederatedSettingsIdentityProvider#sso_debug_enabled}.
        :param sso_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#sso_url FederatedSettingsIdentityProvider#sso_url}.
        :param status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#status FederatedSettingsIdentityProvider#status}.
        :param user_claim: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#user_claim FederatedSettingsIdentityProvider#user_claim}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17941229f54c7ceeceddec79fffa7c81243fabd0b62845a69d2db9f71579a4a4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = FederatedSettingsIdentityProviderConfig(
            federation_settings_id=federation_settings_id,
            issuer_uri=issuer_uri,
            name=name,
            associated_domains=associated_domains,
            audience=audience,
            authorization_type=authorization_type,
            client_id=client_id,
            description=description,
            groups_claim=groups_claim,
            id=id,
            idp_type=idp_type,
            protocol=protocol,
            request_binding=request_binding,
            requested_scopes=requested_scopes,
            response_signature_algorithm=response_signature_algorithm,
            sso_debug_enabled=sso_debug_enabled,
            sso_url=sso_url,
            status=status,
            user_claim=user_claim,
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
        '''Generates CDKTF code for importing a FederatedSettingsIdentityProvider resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the FederatedSettingsIdentityProvider to import.
        :param import_from_id: The id of the existing FederatedSettingsIdentityProvider that should be imported. Refer to the {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the FederatedSettingsIdentityProvider to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__031552dcd5367f02786ee3263415724104024e38b8492c379dfda6c7a1822dad)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAssociatedDomains")
    def reset_associated_domains(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAssociatedDomains", []))

    @jsii.member(jsii_name="resetAudience")
    def reset_audience(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAudience", []))

    @jsii.member(jsii_name="resetAuthorizationType")
    def reset_authorization_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthorizationType", []))

    @jsii.member(jsii_name="resetClientId")
    def reset_client_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientId", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetGroupsClaim")
    def reset_groups_claim(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGroupsClaim", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIdpType")
    def reset_idp_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdpType", []))

    @jsii.member(jsii_name="resetProtocol")
    def reset_protocol(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProtocol", []))

    @jsii.member(jsii_name="resetRequestBinding")
    def reset_request_binding(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequestBinding", []))

    @jsii.member(jsii_name="resetRequestedScopes")
    def reset_requested_scopes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequestedScopes", []))

    @jsii.member(jsii_name="resetResponseSignatureAlgorithm")
    def reset_response_signature_algorithm(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResponseSignatureAlgorithm", []))

    @jsii.member(jsii_name="resetSsoDebugEnabled")
    def reset_sso_debug_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSsoDebugEnabled", []))

    @jsii.member(jsii_name="resetSsoUrl")
    def reset_sso_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSsoUrl", []))

    @jsii.member(jsii_name="resetStatus")
    def reset_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatus", []))

    @jsii.member(jsii_name="resetUserClaim")
    def reset_user_claim(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserClaim", []))

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
    @jsii.member(jsii_name="idpId")
    def idp_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "idpId"))

    @builtins.property
    @jsii.member(jsii_name="oktaIdpId")
    def okta_idp_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "oktaIdpId"))

    @builtins.property
    @jsii.member(jsii_name="associatedDomainsInput")
    def associated_domains_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "associatedDomainsInput"))

    @builtins.property
    @jsii.member(jsii_name="audienceInput")
    def audience_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "audienceInput"))

    @builtins.property
    @jsii.member(jsii_name="authorizationTypeInput")
    def authorization_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authorizationTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="clientIdInput")
    def client_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientIdInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="federationSettingsIdInput")
    def federation_settings_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "federationSettingsIdInput"))

    @builtins.property
    @jsii.member(jsii_name="groupsClaimInput")
    def groups_claim_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "groupsClaimInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="idpTypeInput")
    def idp_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idpTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="issuerUriInput")
    def issuer_uri_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "issuerUriInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="protocolInput")
    def protocol_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "protocolInput"))

    @builtins.property
    @jsii.member(jsii_name="requestBindingInput")
    def request_binding_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "requestBindingInput"))

    @builtins.property
    @jsii.member(jsii_name="requestedScopesInput")
    def requested_scopes_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "requestedScopesInput"))

    @builtins.property
    @jsii.member(jsii_name="responseSignatureAlgorithmInput")
    def response_signature_algorithm_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "responseSignatureAlgorithmInput"))

    @builtins.property
    @jsii.member(jsii_name="ssoDebugEnabledInput")
    def sso_debug_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "ssoDebugEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="ssoUrlInput")
    def sso_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ssoUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="statusInput")
    def status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statusInput"))

    @builtins.property
    @jsii.member(jsii_name="userClaimInput")
    def user_claim_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userClaimInput"))

    @builtins.property
    @jsii.member(jsii_name="associatedDomains")
    def associated_domains(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "associatedDomains"))

    @associated_domains.setter
    def associated_domains(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__661e763dce3dd959f990476525ffe3f820266c8c1c70328921a59eab26aa0879)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "associatedDomains", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="audience")
    def audience(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "audience"))

    @audience.setter
    def audience(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__008bb797823a5d9c8405bdb3bf9e4acbe984f5213594f39438b2e46871f191a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "audience", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="authorizationType")
    def authorization_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authorizationType"))

    @authorization_type.setter
    def authorization_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56734162d19c3903a18a35953ddaf8ba309f949d272819cebe48a322f87d34ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authorizationType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clientId")
    def client_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientId"))

    @client_id.setter
    def client_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11d3c423baf75f609f1a7d534c795a49edc40c3a957ad4c072343caca6fd4955)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f43266ba92f904b99592025289f9c79e6b599a28907ea7bc654e27ca66c20b44)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="federationSettingsId")
    def federation_settings_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "federationSettingsId"))

    @federation_settings_id.setter
    def federation_settings_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5427f540d6b43d68eb26e46af3109238b9c620773fa09bf44b5b61f5f2c7d538)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "federationSettingsId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="groupsClaim")
    def groups_claim(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "groupsClaim"))

    @groups_claim.setter
    def groups_claim(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c36c019215a6dab1d4424a1117003d50ff12a6d5e5dfec87745b7cb85ae651f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "groupsClaim", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55b51c9064661b5352acd93a5235cc1c34de4c1700bde2c73de4608134e89a8c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="idpType")
    def idp_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "idpType"))

    @idp_type.setter
    def idp_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12a9ba28aaaf4c05a129026df14c9495c4a1146c52a57488153437af1a86294a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "idpType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="issuerUri")
    def issuer_uri(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "issuerUri"))

    @issuer_uri.setter
    def issuer_uri(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__688a0ede3ab273f8511e70d7cedadb085d49e76a4cd843b5a8fcd2945634802c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "issuerUri", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21fc45fedb7e6a32563cd33703e819a7a6faceb7b4c6e98e9ca3410373b62a88)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="protocol")
    def protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "protocol"))

    @protocol.setter
    def protocol(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0210feda8599d1102cfda438b489434096e6e16b07a96af4f161027774e605b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "protocol", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requestBinding")
    def request_binding(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "requestBinding"))

    @request_binding.setter
    def request_binding(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c08f02f1fd96ecc7ed9671987688a23e0500af175d6356ba531bbaf3e0c3a685)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requestBinding", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requestedScopes")
    def requested_scopes(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "requestedScopes"))

    @requested_scopes.setter
    def requested_scopes(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6a2a42a3248d29cca714c29af1ccce2a63171830d27644270ad72b0b61cbd4e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requestedScopes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="responseSignatureAlgorithm")
    def response_signature_algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "responseSignatureAlgorithm"))

    @response_signature_algorithm.setter
    def response_signature_algorithm(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d39e354ce62f9c9389c4dc06c79acbdb16ff38a2d570997fa73cd283a3ec4a01)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "responseSignatureAlgorithm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ssoDebugEnabled")
    def sso_debug_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "ssoDebugEnabled"))

    @sso_debug_enabled.setter
    def sso_debug_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd951848dda0858bde6f85505a5c95dd3e846d9cd858e0793fa7222fd8979063)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ssoDebugEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ssoUrl")
    def sso_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ssoUrl"))

    @sso_url.setter
    def sso_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44c73b3a57ea1ec172ac61c11b885bfd6678d126ec154873178ae90a6d5a1dec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ssoUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @status.setter
    def status(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__682894cfcce3aaebb259cdc36285e0e50cafc62824c48edd3bdd9f370ca2343a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "status", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userClaim")
    def user_claim(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userClaim"))

    @user_claim.setter
    def user_claim(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0f51aebbc69269f86662d2af0cdcb6411a5687e40def69dd2b31a0360502375)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userClaim", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.federatedSettingsIdentityProvider.FederatedSettingsIdentityProviderConfig",
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
        "issuer_uri": "issuerUri",
        "name": "name",
        "associated_domains": "associatedDomains",
        "audience": "audience",
        "authorization_type": "authorizationType",
        "client_id": "clientId",
        "description": "description",
        "groups_claim": "groupsClaim",
        "id": "id",
        "idp_type": "idpType",
        "protocol": "protocol",
        "request_binding": "requestBinding",
        "requested_scopes": "requestedScopes",
        "response_signature_algorithm": "responseSignatureAlgorithm",
        "sso_debug_enabled": "ssoDebugEnabled",
        "sso_url": "ssoUrl",
        "status": "status",
        "user_claim": "userClaim",
    },
)
class FederatedSettingsIdentityProviderConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        issuer_uri: builtins.str,
        name: builtins.str,
        associated_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
        audience: typing.Optional[builtins.str] = None,
        authorization_type: typing.Optional[builtins.str] = None,
        client_id: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        groups_claim: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        idp_type: typing.Optional[builtins.str] = None,
        protocol: typing.Optional[builtins.str] = None,
        request_binding: typing.Optional[builtins.str] = None,
        requested_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
        response_signature_algorithm: typing.Optional[builtins.str] = None,
        sso_debug_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        sso_url: typing.Optional[builtins.str] = None,
        status: typing.Optional[builtins.str] = None,
        user_claim: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param federation_settings_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#federation_settings_id FederatedSettingsIdentityProvider#federation_settings_id}.
        :param issuer_uri: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#issuer_uri FederatedSettingsIdentityProvider#issuer_uri}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#name FederatedSettingsIdentityProvider#name}.
        :param associated_domains: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#associated_domains FederatedSettingsIdentityProvider#associated_domains}.
        :param audience: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#audience FederatedSettingsIdentityProvider#audience}.
        :param authorization_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#authorization_type FederatedSettingsIdentityProvider#authorization_type}.
        :param client_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#client_id FederatedSettingsIdentityProvider#client_id}.
        :param description: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#description FederatedSettingsIdentityProvider#description}.
        :param groups_claim: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#groups_claim FederatedSettingsIdentityProvider#groups_claim}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#id FederatedSettingsIdentityProvider#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param idp_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#idp_type FederatedSettingsIdentityProvider#idp_type}.
        :param protocol: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#protocol FederatedSettingsIdentityProvider#protocol}.
        :param request_binding: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#request_binding FederatedSettingsIdentityProvider#request_binding}.
        :param requested_scopes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#requested_scopes FederatedSettingsIdentityProvider#requested_scopes}.
        :param response_signature_algorithm: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#response_signature_algorithm FederatedSettingsIdentityProvider#response_signature_algorithm}.
        :param sso_debug_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#sso_debug_enabled FederatedSettingsIdentityProvider#sso_debug_enabled}.
        :param sso_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#sso_url FederatedSettingsIdentityProvider#sso_url}.
        :param status: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#status FederatedSettingsIdentityProvider#status}.
        :param user_claim: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#user_claim FederatedSettingsIdentityProvider#user_claim}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__724d6f038136fd09e291f5dfb0b6551e08bfd4cce334e87342a45858976fc596)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument federation_settings_id", value=federation_settings_id, expected_type=type_hints["federation_settings_id"])
            check_type(argname="argument issuer_uri", value=issuer_uri, expected_type=type_hints["issuer_uri"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument associated_domains", value=associated_domains, expected_type=type_hints["associated_domains"])
            check_type(argname="argument audience", value=audience, expected_type=type_hints["audience"])
            check_type(argname="argument authorization_type", value=authorization_type, expected_type=type_hints["authorization_type"])
            check_type(argname="argument client_id", value=client_id, expected_type=type_hints["client_id"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument groups_claim", value=groups_claim, expected_type=type_hints["groups_claim"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument idp_type", value=idp_type, expected_type=type_hints["idp_type"])
            check_type(argname="argument protocol", value=protocol, expected_type=type_hints["protocol"])
            check_type(argname="argument request_binding", value=request_binding, expected_type=type_hints["request_binding"])
            check_type(argname="argument requested_scopes", value=requested_scopes, expected_type=type_hints["requested_scopes"])
            check_type(argname="argument response_signature_algorithm", value=response_signature_algorithm, expected_type=type_hints["response_signature_algorithm"])
            check_type(argname="argument sso_debug_enabled", value=sso_debug_enabled, expected_type=type_hints["sso_debug_enabled"])
            check_type(argname="argument sso_url", value=sso_url, expected_type=type_hints["sso_url"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
            check_type(argname="argument user_claim", value=user_claim, expected_type=type_hints["user_claim"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "federation_settings_id": federation_settings_id,
            "issuer_uri": issuer_uri,
            "name": name,
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
        if associated_domains is not None:
            self._values["associated_domains"] = associated_domains
        if audience is not None:
            self._values["audience"] = audience
        if authorization_type is not None:
            self._values["authorization_type"] = authorization_type
        if client_id is not None:
            self._values["client_id"] = client_id
        if description is not None:
            self._values["description"] = description
        if groups_claim is not None:
            self._values["groups_claim"] = groups_claim
        if id is not None:
            self._values["id"] = id
        if idp_type is not None:
            self._values["idp_type"] = idp_type
        if protocol is not None:
            self._values["protocol"] = protocol
        if request_binding is not None:
            self._values["request_binding"] = request_binding
        if requested_scopes is not None:
            self._values["requested_scopes"] = requested_scopes
        if response_signature_algorithm is not None:
            self._values["response_signature_algorithm"] = response_signature_algorithm
        if sso_debug_enabled is not None:
            self._values["sso_debug_enabled"] = sso_debug_enabled
        if sso_url is not None:
            self._values["sso_url"] = sso_url
        if status is not None:
            self._values["status"] = status
        if user_claim is not None:
            self._values["user_claim"] = user_claim

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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#federation_settings_id FederatedSettingsIdentityProvider#federation_settings_id}.'''
        result = self._values.get("federation_settings_id")
        assert result is not None, "Required property 'federation_settings_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def issuer_uri(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#issuer_uri FederatedSettingsIdentityProvider#issuer_uri}.'''
        result = self._values.get("issuer_uri")
        assert result is not None, "Required property 'issuer_uri' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#name FederatedSettingsIdentityProvider#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def associated_domains(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#associated_domains FederatedSettingsIdentityProvider#associated_domains}.'''
        result = self._values.get("associated_domains")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def audience(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#audience FederatedSettingsIdentityProvider#audience}.'''
        result = self._values.get("audience")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def authorization_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#authorization_type FederatedSettingsIdentityProvider#authorization_type}.'''
        result = self._values.get("authorization_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def client_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#client_id FederatedSettingsIdentityProvider#client_id}.'''
        result = self._values.get("client_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#description FederatedSettingsIdentityProvider#description}.'''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def groups_claim(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#groups_claim FederatedSettingsIdentityProvider#groups_claim}.'''
        result = self._values.get("groups_claim")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#id FederatedSettingsIdentityProvider#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def idp_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#idp_type FederatedSettingsIdentityProvider#idp_type}.'''
        result = self._values.get("idp_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def protocol(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#protocol FederatedSettingsIdentityProvider#protocol}.'''
        result = self._values.get("protocol")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def request_binding(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#request_binding FederatedSettingsIdentityProvider#request_binding}.'''
        result = self._values.get("request_binding")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def requested_scopes(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#requested_scopes FederatedSettingsIdentityProvider#requested_scopes}.'''
        result = self._values.get("requested_scopes")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def response_signature_algorithm(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#response_signature_algorithm FederatedSettingsIdentityProvider#response_signature_algorithm}.'''
        result = self._values.get("response_signature_algorithm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sso_debug_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#sso_debug_enabled FederatedSettingsIdentityProvider#sso_debug_enabled}.'''
        result = self._values.get("sso_debug_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def sso_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#sso_url FederatedSettingsIdentityProvider#sso_url}.'''
        result = self._values.get("sso_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def status(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#status FederatedSettingsIdentityProvider#status}.'''
        result = self._values.get("status")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_claim(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/federated_settings_identity_provider#user_claim FederatedSettingsIdentityProvider#user_claim}.'''
        result = self._values.get("user_claim")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "FederatedSettingsIdentityProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "FederatedSettingsIdentityProvider",
    "FederatedSettingsIdentityProviderConfig",
]

publication.publish()

def _typecheckingstub__17941229f54c7ceeceddec79fffa7c81243fabd0b62845a69d2db9f71579a4a4(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    federation_settings_id: builtins.str,
    issuer_uri: builtins.str,
    name: builtins.str,
    associated_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
    audience: typing.Optional[builtins.str] = None,
    authorization_type: typing.Optional[builtins.str] = None,
    client_id: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    groups_claim: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    idp_type: typing.Optional[builtins.str] = None,
    protocol: typing.Optional[builtins.str] = None,
    request_binding: typing.Optional[builtins.str] = None,
    requested_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
    response_signature_algorithm: typing.Optional[builtins.str] = None,
    sso_debug_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    sso_url: typing.Optional[builtins.str] = None,
    status: typing.Optional[builtins.str] = None,
    user_claim: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__031552dcd5367f02786ee3263415724104024e38b8492c379dfda6c7a1822dad(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__661e763dce3dd959f990476525ffe3f820266c8c1c70328921a59eab26aa0879(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__008bb797823a5d9c8405bdb3bf9e4acbe984f5213594f39438b2e46871f191a5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56734162d19c3903a18a35953ddaf8ba309f949d272819cebe48a322f87d34ce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11d3c423baf75f609f1a7d534c795a49edc40c3a957ad4c072343caca6fd4955(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f43266ba92f904b99592025289f9c79e6b599a28907ea7bc654e27ca66c20b44(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5427f540d6b43d68eb26e46af3109238b9c620773fa09bf44b5b61f5f2c7d538(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c36c019215a6dab1d4424a1117003d50ff12a6d5e5dfec87745b7cb85ae651f0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55b51c9064661b5352acd93a5235cc1c34de4c1700bde2c73de4608134e89a8c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12a9ba28aaaf4c05a129026df14c9495c4a1146c52a57488153437af1a86294a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__688a0ede3ab273f8511e70d7cedadb085d49e76a4cd843b5a8fcd2945634802c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21fc45fedb7e6a32563cd33703e819a7a6faceb7b4c6e98e9ca3410373b62a88(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0210feda8599d1102cfda438b489434096e6e16b07a96af4f161027774e605b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c08f02f1fd96ecc7ed9671987688a23e0500af175d6356ba531bbaf3e0c3a685(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6a2a42a3248d29cca714c29af1ccce2a63171830d27644270ad72b0b61cbd4e(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d39e354ce62f9c9389c4dc06c79acbdb16ff38a2d570997fa73cd283a3ec4a01(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd951848dda0858bde6f85505a5c95dd3e846d9cd858e0793fa7222fd8979063(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44c73b3a57ea1ec172ac61c11b885bfd6678d126ec154873178ae90a6d5a1dec(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__682894cfcce3aaebb259cdc36285e0e50cafc62824c48edd3bdd9f370ca2343a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0f51aebbc69269f86662d2af0cdcb6411a5687e40def69dd2b31a0360502375(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__724d6f038136fd09e291f5dfb0b6551e08bfd4cce334e87342a45858976fc596(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    federation_settings_id: builtins.str,
    issuer_uri: builtins.str,
    name: builtins.str,
    associated_domains: typing.Optional[typing.Sequence[builtins.str]] = None,
    audience: typing.Optional[builtins.str] = None,
    authorization_type: typing.Optional[builtins.str] = None,
    client_id: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    groups_claim: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    idp_type: typing.Optional[builtins.str] = None,
    protocol: typing.Optional[builtins.str] = None,
    request_binding: typing.Optional[builtins.str] = None,
    requested_scopes: typing.Optional[typing.Sequence[builtins.str]] = None,
    response_signature_algorithm: typing.Optional[builtins.str] = None,
    sso_debug_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    sso_url: typing.Optional[builtins.str] = None,
    status: typing.Optional[builtins.str] = None,
    user_claim: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
