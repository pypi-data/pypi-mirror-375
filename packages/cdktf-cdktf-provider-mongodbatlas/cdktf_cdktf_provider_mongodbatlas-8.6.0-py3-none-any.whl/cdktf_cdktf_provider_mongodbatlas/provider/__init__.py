r'''
# `provider`

Refer to the Terraform Registry for docs: [`mongodbatlas`](https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs).
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


class MongodbatlasProvider(
    _cdktf_9a9027ec.TerraformProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.provider.MongodbatlasProvider",
):
    '''Represents a {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs mongodbatlas}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        alias: typing.Optional[builtins.str] = None,
        assume_role: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["MongodbatlasProviderAssumeRole", typing.Dict[builtins.str, typing.Any]]]]] = None,
        aws_access_key_id: typing.Optional[builtins.str] = None,
        aws_secret_access_key: typing.Optional[builtins.str] = None,
        aws_session_token: typing.Optional[builtins.str] = None,
        base_url: typing.Optional[builtins.str] = None,
        is_mongodbgov_cloud: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        private_key: typing.Optional[builtins.str] = None,
        public_key: typing.Optional[builtins.str] = None,
        realm_base_url: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        secret_name: typing.Optional[builtins.str] = None,
        sts_endpoint: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs mongodbatlas} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param alias: Alias name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#alias MongodbatlasProvider#alias}
        :param assume_role: assume_role block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#assume_role MongodbatlasProvider#assume_role}
        :param aws_access_key_id: AWS API Access Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#aws_access_key_id MongodbatlasProvider#aws_access_key_id}
        :param aws_secret_access_key: AWS API Access Secret Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#aws_secret_access_key MongodbatlasProvider#aws_secret_access_key}
        :param aws_session_token: AWS Security Token Service provided session token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#aws_session_token MongodbatlasProvider#aws_session_token}
        :param base_url: MongoDB Atlas Base URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#base_url MongodbatlasProvider#base_url}
        :param is_mongodbgov_cloud: MongoDB Atlas Base URL default to gov. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#is_mongodbgov_cloud MongodbatlasProvider#is_mongodbgov_cloud}
        :param private_key: MongoDB Atlas Programmatic Private Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#private_key MongodbatlasProvider#private_key}
        :param public_key: MongoDB Atlas Programmatic Public Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#public_key MongodbatlasProvider#public_key}
        :param realm_base_url: MongoDB Realm Base URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#realm_base_url MongodbatlasProvider#realm_base_url}
        :param region: Region where secret is stored as part of AWS Secret Manager. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#region MongodbatlasProvider#region}
        :param secret_name: Name of secret stored in AWS Secret Manager. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#secret_name MongodbatlasProvider#secret_name}
        :param sts_endpoint: AWS Security Token Service endpoint. Required for cross-AWS region or cross-AWS account secrets. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#sts_endpoint MongodbatlasProvider#sts_endpoint}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5fe8533a5e73a3256028c820ce56824a41ae058e89737802f90e0ed37c147d56)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = MongodbatlasProviderConfig(
            alias=alias,
            assume_role=assume_role,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token,
            base_url=base_url,
            is_mongodbgov_cloud=is_mongodbgov_cloud,
            private_key=private_key,
            public_key=public_key,
            realm_base_url=realm_base_url,
            region=region,
            secret_name=secret_name,
            sts_endpoint=sts_endpoint,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a MongodbatlasProvider resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the MongodbatlasProvider to import.
        :param import_from_id: The id of the existing MongodbatlasProvider that should be imported. Refer to the {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the MongodbatlasProvider to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f65ff9398a872705a3440a3cc66c9482bd228795fb9a03cc90ade53fa95a6080)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAlias")
    def reset_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlias", []))

    @jsii.member(jsii_name="resetAssumeRole")
    def reset_assume_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAssumeRole", []))

    @jsii.member(jsii_name="resetAwsAccessKeyId")
    def reset_aws_access_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsAccessKeyId", []))

    @jsii.member(jsii_name="resetAwsSecretAccessKey")
    def reset_aws_secret_access_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsSecretAccessKey", []))

    @jsii.member(jsii_name="resetAwsSessionToken")
    def reset_aws_session_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsSessionToken", []))

    @jsii.member(jsii_name="resetBaseUrl")
    def reset_base_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBaseUrl", []))

    @jsii.member(jsii_name="resetIsMongodbgovCloud")
    def reset_is_mongodbgov_cloud(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsMongodbgovCloud", []))

    @jsii.member(jsii_name="resetPrivateKey")
    def reset_private_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrivateKey", []))

    @jsii.member(jsii_name="resetPublicKey")
    def reset_public_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPublicKey", []))

    @jsii.member(jsii_name="resetRealmBaseUrl")
    def reset_realm_base_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRealmBaseUrl", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @jsii.member(jsii_name="resetSecretName")
    def reset_secret_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecretName", []))

    @jsii.member(jsii_name="resetStsEndpoint")
    def reset_sts_endpoint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStsEndpoint", []))

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
    @jsii.member(jsii_name="aliasInput")
    def alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasInput"))

    @builtins.property
    @jsii.member(jsii_name="assumeRoleInput")
    def assume_role_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MongodbatlasProviderAssumeRole"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MongodbatlasProviderAssumeRole"]]], jsii.get(self, "assumeRoleInput"))

    @builtins.property
    @jsii.member(jsii_name="awsAccessKeyIdInput")
    def aws_access_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsAccessKeyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="awsSecretAccessKeyInput")
    def aws_secret_access_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsSecretAccessKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="awsSessionTokenInput")
    def aws_session_token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsSessionTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="baseUrlInput")
    def base_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "baseUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="isMongodbgovCloudInput")
    def is_mongodbgov_cloud_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isMongodbgovCloudInput"))

    @builtins.property
    @jsii.member(jsii_name="privateKeyInput")
    def private_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="publicKeyInput")
    def public_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "publicKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="realmBaseUrlInput")
    def realm_base_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "realmBaseUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="secretNameInput")
    def secret_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretNameInput"))

    @builtins.property
    @jsii.member(jsii_name="stsEndpointInput")
    def sts_endpoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stsEndpointInput"))

    @builtins.property
    @jsii.member(jsii_name="alias")
    def alias(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alias"))

    @alias.setter
    def alias(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7238d506530aec0e963be7466103e379c469f4a482941a82a99658b2ec5e6730)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alias", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="assumeRole")
    def assume_role(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MongodbatlasProviderAssumeRole"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MongodbatlasProviderAssumeRole"]]], jsii.get(self, "assumeRole"))

    @assume_role.setter
    def assume_role(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["MongodbatlasProviderAssumeRole"]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f8bc4370279e4aaabae8d701c5aa84b4e49bf8ca1ddaec13edc83d7176094bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "assumeRole", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="awsAccessKeyId")
    def aws_access_key_id(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsAccessKeyId"))

    @aws_access_key_id.setter
    def aws_access_key_id(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08e22095268e78625b1e05b24648498bc80b9bde524ba6a908942e422dfb5e1a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsAccessKeyId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="awsSecretAccessKey")
    def aws_secret_access_key(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsSecretAccessKey"))

    @aws_secret_access_key.setter
    def aws_secret_access_key(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7192ddb2886f35c0bad628f1c7d07991d03ca186324175ceedad8cbf661fe9e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsSecretAccessKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="awsSessionToken")
    def aws_session_token(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsSessionToken"))

    @aws_session_token.setter
    def aws_session_token(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__450c3f61d7f69231f69ee8fbe9c1368168994bd9a2f69797b8ce78aacebe7c0e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsSessionToken", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="baseUrl")
    def base_url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "baseUrl"))

    @base_url.setter
    def base_url(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e888a6723b68bf6e99274a38779755d5a6a374fd675eea3fc2546d7a3b31c7d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "baseUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isMongodbgovCloud")
    def is_mongodbgov_cloud(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isMongodbgovCloud"))

    @is_mongodbgov_cloud.setter
    def is_mongodbgov_cloud(
        self,
        value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be3803931eb6230987d2776e5a234474a876c8981775a77ca3135f616e040b09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isMongodbgovCloud", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="privateKey")
    def private_key(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "privateKey"))

    @private_key.setter
    def private_key(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b902bac3b33b8a18e3cb3ff2a69bb5a63ff9709e4b26edb1f1ce820ae8a2ef5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "privateKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="publicKey")
    def public_key(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "publicKey"))

    @public_key.setter
    def public_key(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__efc355fe737da42da99d81c240288c34bb0a37e1208e25ca0363661e1ebe8438)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "publicKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="realmBaseUrl")
    def realm_base_url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "realmBaseUrl"))

    @realm_base_url.setter
    def realm_base_url(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68c2d1010c5d14d5de57a1e5bb5bb54d6309bdf9ef0facbd6aeb2bffcc4c17b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "realmBaseUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "region"))

    @region.setter
    def region(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e83df8da7f55cc26dc3e0d2a07bbb1fed9bdb7e7f5ef2cf36f0afc74f2b98d4e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secretName")
    def secret_name(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretName"))

    @secret_name.setter
    def secret_name(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df5be10b3d5daddfecac0d98a37ca91a0a5c03f64b71cdf6fbc562076f7f28fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secretName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="stsEndpoint")
    def sts_endpoint(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stsEndpoint"))

    @sts_endpoint.setter
    def sts_endpoint(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41e504f445a52d25568cfd60b04732d720bd56366efcaa9799df29d0a7d8299b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "stsEndpoint", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.provider.MongodbatlasProviderAssumeRole",
    jsii_struct_bases=[],
    name_mapping={
        "duration": "duration",
        "external_id": "externalId",
        "policy": "policy",
        "policy_arns": "policyArns",
        "role_arn": "roleArn",
        "session_name": "sessionName",
        "source_identity": "sourceIdentity",
        "tags": "tags",
        "transitive_tag_keys": "transitiveTagKeys",
    },
)
class MongodbatlasProviderAssumeRole:
    def __init__(
        self,
        *,
        duration: typing.Optional[builtins.str] = None,
        external_id: typing.Optional[builtins.str] = None,
        policy: typing.Optional[builtins.str] = None,
        policy_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
        role_arn: typing.Optional[builtins.str] = None,
        session_name: typing.Optional[builtins.str] = None,
        source_identity: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        transitive_tag_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param duration: The duration, between 15 minutes and 12 hours, of the role session. Valid time units are ns, us (or µs), ms, s, h, or m. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#duration MongodbatlasProvider#duration}
        :param external_id: A unique identifier that might be required when you assume a role in another account. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#external_id MongodbatlasProvider#external_id}
        :param policy: IAM Policy JSON describing further restricting permissions for the IAM Role being assumed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#policy MongodbatlasProvider#policy}
        :param policy_arns: Amazon Resource Names (ARNs) of IAM Policies describing further restricting permissions for the IAM Role being assumed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#policy_arns MongodbatlasProvider#policy_arns}
        :param role_arn: Amazon Resource Name (ARN) of an IAM Role to assume prior to making API calls. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#role_arn MongodbatlasProvider#role_arn}
        :param session_name: An identifier for the assumed role session. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#session_name MongodbatlasProvider#session_name}
        :param source_identity: Source identity specified by the principal assuming the role. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#source_identity MongodbatlasProvider#source_identity}
        :param tags: Assume role session tags. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#tags MongodbatlasProvider#tags}
        :param transitive_tag_keys: Assume role session tag keys to pass to any subsequent sessions. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#transitive_tag_keys MongodbatlasProvider#transitive_tag_keys}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__deb1e1099f1ce0152e5c866578153213519cc377f0c1c9249f29371d2edd2386)
            check_type(argname="argument duration", value=duration, expected_type=type_hints["duration"])
            check_type(argname="argument external_id", value=external_id, expected_type=type_hints["external_id"])
            check_type(argname="argument policy", value=policy, expected_type=type_hints["policy"])
            check_type(argname="argument policy_arns", value=policy_arns, expected_type=type_hints["policy_arns"])
            check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
            check_type(argname="argument session_name", value=session_name, expected_type=type_hints["session_name"])
            check_type(argname="argument source_identity", value=source_identity, expected_type=type_hints["source_identity"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument transitive_tag_keys", value=transitive_tag_keys, expected_type=type_hints["transitive_tag_keys"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if duration is not None:
            self._values["duration"] = duration
        if external_id is not None:
            self._values["external_id"] = external_id
        if policy is not None:
            self._values["policy"] = policy
        if policy_arns is not None:
            self._values["policy_arns"] = policy_arns
        if role_arn is not None:
            self._values["role_arn"] = role_arn
        if session_name is not None:
            self._values["session_name"] = session_name
        if source_identity is not None:
            self._values["source_identity"] = source_identity
        if tags is not None:
            self._values["tags"] = tags
        if transitive_tag_keys is not None:
            self._values["transitive_tag_keys"] = transitive_tag_keys

    @builtins.property
    def duration(self) -> typing.Optional[builtins.str]:
        '''The duration, between 15 minutes and 12 hours, of the role session.

        Valid time units are ns, us (or µs), ms, s, h, or m.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#duration MongodbatlasProvider#duration}
        '''
        result = self._values.get("duration")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def external_id(self) -> typing.Optional[builtins.str]:
        '''A unique identifier that might be required when you assume a role in another account.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#external_id MongodbatlasProvider#external_id}
        '''
        result = self._values.get("external_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def policy(self) -> typing.Optional[builtins.str]:
        '''IAM Policy JSON describing further restricting permissions for the IAM Role being assumed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#policy MongodbatlasProvider#policy}
        '''
        result = self._values.get("policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def policy_arns(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Amazon Resource Names (ARNs) of IAM Policies describing further restricting permissions for the IAM Role being assumed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#policy_arns MongodbatlasProvider#policy_arns}
        '''
        result = self._values.get("policy_arns")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def role_arn(self) -> typing.Optional[builtins.str]:
        '''Amazon Resource Name (ARN) of an IAM Role to assume prior to making API calls.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#role_arn MongodbatlasProvider#role_arn}
        '''
        result = self._values.get("role_arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def session_name(self) -> typing.Optional[builtins.str]:
        '''An identifier for the assumed role session.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#session_name MongodbatlasProvider#session_name}
        '''
        result = self._values.get("session_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def source_identity(self) -> typing.Optional[builtins.str]:
        '''Source identity specified by the principal assuming the role.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#source_identity MongodbatlasProvider#source_identity}
        '''
        result = self._values.get("source_identity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Assume role session tags.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#tags MongodbatlasProvider#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def transitive_tag_keys(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Assume role session tag keys to pass to any subsequent sessions.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#transitive_tag_keys MongodbatlasProvider#transitive_tag_keys}
        '''
        result = self._values.get("transitive_tag_keys")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MongodbatlasProviderAssumeRole(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.provider.MongodbatlasProviderConfig",
    jsii_struct_bases=[],
    name_mapping={
        "alias": "alias",
        "assume_role": "assumeRole",
        "aws_access_key_id": "awsAccessKeyId",
        "aws_secret_access_key": "awsSecretAccessKey",
        "aws_session_token": "awsSessionToken",
        "base_url": "baseUrl",
        "is_mongodbgov_cloud": "isMongodbgovCloud",
        "private_key": "privateKey",
        "public_key": "publicKey",
        "realm_base_url": "realmBaseUrl",
        "region": "region",
        "secret_name": "secretName",
        "sts_endpoint": "stsEndpoint",
    },
)
class MongodbatlasProviderConfig:
    def __init__(
        self,
        *,
        alias: typing.Optional[builtins.str] = None,
        assume_role: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MongodbatlasProviderAssumeRole, typing.Dict[builtins.str, typing.Any]]]]] = None,
        aws_access_key_id: typing.Optional[builtins.str] = None,
        aws_secret_access_key: typing.Optional[builtins.str] = None,
        aws_session_token: typing.Optional[builtins.str] = None,
        base_url: typing.Optional[builtins.str] = None,
        is_mongodbgov_cloud: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        private_key: typing.Optional[builtins.str] = None,
        public_key: typing.Optional[builtins.str] = None,
        realm_base_url: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        secret_name: typing.Optional[builtins.str] = None,
        sts_endpoint: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param alias: Alias name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#alias MongodbatlasProvider#alias}
        :param assume_role: assume_role block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#assume_role MongodbatlasProvider#assume_role}
        :param aws_access_key_id: AWS API Access Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#aws_access_key_id MongodbatlasProvider#aws_access_key_id}
        :param aws_secret_access_key: AWS API Access Secret Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#aws_secret_access_key MongodbatlasProvider#aws_secret_access_key}
        :param aws_session_token: AWS Security Token Service provided session token. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#aws_session_token MongodbatlasProvider#aws_session_token}
        :param base_url: MongoDB Atlas Base URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#base_url MongodbatlasProvider#base_url}
        :param is_mongodbgov_cloud: MongoDB Atlas Base URL default to gov. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#is_mongodbgov_cloud MongodbatlasProvider#is_mongodbgov_cloud}
        :param private_key: MongoDB Atlas Programmatic Private Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#private_key MongodbatlasProvider#private_key}
        :param public_key: MongoDB Atlas Programmatic Public Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#public_key MongodbatlasProvider#public_key}
        :param realm_base_url: MongoDB Realm Base URL. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#realm_base_url MongodbatlasProvider#realm_base_url}
        :param region: Region where secret is stored as part of AWS Secret Manager. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#region MongodbatlasProvider#region}
        :param secret_name: Name of secret stored in AWS Secret Manager. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#secret_name MongodbatlasProvider#secret_name}
        :param sts_endpoint: AWS Security Token Service endpoint. Required for cross-AWS region or cross-AWS account secrets. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#sts_endpoint MongodbatlasProvider#sts_endpoint}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f1c6437c053fd97dacc33ed7f607ea706e0da1d2c5abbbbdcf28285101412b1)
            check_type(argname="argument alias", value=alias, expected_type=type_hints["alias"])
            check_type(argname="argument assume_role", value=assume_role, expected_type=type_hints["assume_role"])
            check_type(argname="argument aws_access_key_id", value=aws_access_key_id, expected_type=type_hints["aws_access_key_id"])
            check_type(argname="argument aws_secret_access_key", value=aws_secret_access_key, expected_type=type_hints["aws_secret_access_key"])
            check_type(argname="argument aws_session_token", value=aws_session_token, expected_type=type_hints["aws_session_token"])
            check_type(argname="argument base_url", value=base_url, expected_type=type_hints["base_url"])
            check_type(argname="argument is_mongodbgov_cloud", value=is_mongodbgov_cloud, expected_type=type_hints["is_mongodbgov_cloud"])
            check_type(argname="argument private_key", value=private_key, expected_type=type_hints["private_key"])
            check_type(argname="argument public_key", value=public_key, expected_type=type_hints["public_key"])
            check_type(argname="argument realm_base_url", value=realm_base_url, expected_type=type_hints["realm_base_url"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument secret_name", value=secret_name, expected_type=type_hints["secret_name"])
            check_type(argname="argument sts_endpoint", value=sts_endpoint, expected_type=type_hints["sts_endpoint"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if alias is not None:
            self._values["alias"] = alias
        if assume_role is not None:
            self._values["assume_role"] = assume_role
        if aws_access_key_id is not None:
            self._values["aws_access_key_id"] = aws_access_key_id
        if aws_secret_access_key is not None:
            self._values["aws_secret_access_key"] = aws_secret_access_key
        if aws_session_token is not None:
            self._values["aws_session_token"] = aws_session_token
        if base_url is not None:
            self._values["base_url"] = base_url
        if is_mongodbgov_cloud is not None:
            self._values["is_mongodbgov_cloud"] = is_mongodbgov_cloud
        if private_key is not None:
            self._values["private_key"] = private_key
        if public_key is not None:
            self._values["public_key"] = public_key
        if realm_base_url is not None:
            self._values["realm_base_url"] = realm_base_url
        if region is not None:
            self._values["region"] = region
        if secret_name is not None:
            self._values["secret_name"] = secret_name
        if sts_endpoint is not None:
            self._values["sts_endpoint"] = sts_endpoint

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Alias name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#alias MongodbatlasProvider#alias}
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def assume_role(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MongodbatlasProviderAssumeRole]]]:
        '''assume_role block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#assume_role MongodbatlasProvider#assume_role}
        '''
        result = self._values.get("assume_role")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MongodbatlasProviderAssumeRole]]], result)

    @builtins.property
    def aws_access_key_id(self) -> typing.Optional[builtins.str]:
        '''AWS API Access Key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#aws_access_key_id MongodbatlasProvider#aws_access_key_id}
        '''
        result = self._values.get("aws_access_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_secret_access_key(self) -> typing.Optional[builtins.str]:
        '''AWS API Access Secret Key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#aws_secret_access_key MongodbatlasProvider#aws_secret_access_key}
        '''
        result = self._values.get("aws_secret_access_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_session_token(self) -> typing.Optional[builtins.str]:
        '''AWS Security Token Service provided session token.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#aws_session_token MongodbatlasProvider#aws_session_token}
        '''
        result = self._values.get("aws_session_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def base_url(self) -> typing.Optional[builtins.str]:
        '''MongoDB Atlas Base URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#base_url MongodbatlasProvider#base_url}
        '''
        result = self._values.get("base_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def is_mongodbgov_cloud(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''MongoDB Atlas Base URL default to gov.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#is_mongodbgov_cloud MongodbatlasProvider#is_mongodbgov_cloud}
        '''
        result = self._values.get("is_mongodbgov_cloud")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def private_key(self) -> typing.Optional[builtins.str]:
        '''MongoDB Atlas Programmatic Private Key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#private_key MongodbatlasProvider#private_key}
        '''
        result = self._values.get("private_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def public_key(self) -> typing.Optional[builtins.str]:
        '''MongoDB Atlas Programmatic Public Key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#public_key MongodbatlasProvider#public_key}
        '''
        result = self._values.get("public_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def realm_base_url(self) -> typing.Optional[builtins.str]:
        '''MongoDB Realm Base URL.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#realm_base_url MongodbatlasProvider#realm_base_url}
        '''
        result = self._values.get("realm_base_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Region where secret is stored as part of AWS Secret Manager.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#region MongodbatlasProvider#region}
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secret_name(self) -> typing.Optional[builtins.str]:
        '''Name of secret stored in AWS Secret Manager.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#secret_name MongodbatlasProvider#secret_name}
        '''
        result = self._values.get("secret_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sts_endpoint(self) -> typing.Optional[builtins.str]:
        '''AWS Security Token Service endpoint. Required for cross-AWS region or cross-AWS account secrets.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs#sts_endpoint MongodbatlasProvider#sts_endpoint}
        '''
        result = self._values.get("sts_endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MongodbatlasProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "MongodbatlasProvider",
    "MongodbatlasProviderAssumeRole",
    "MongodbatlasProviderConfig",
]

publication.publish()

def _typecheckingstub__5fe8533a5e73a3256028c820ce56824a41ae058e89737802f90e0ed37c147d56(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    alias: typing.Optional[builtins.str] = None,
    assume_role: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MongodbatlasProviderAssumeRole, typing.Dict[builtins.str, typing.Any]]]]] = None,
    aws_access_key_id: typing.Optional[builtins.str] = None,
    aws_secret_access_key: typing.Optional[builtins.str] = None,
    aws_session_token: typing.Optional[builtins.str] = None,
    base_url: typing.Optional[builtins.str] = None,
    is_mongodbgov_cloud: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    private_key: typing.Optional[builtins.str] = None,
    public_key: typing.Optional[builtins.str] = None,
    realm_base_url: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    secret_name: typing.Optional[builtins.str] = None,
    sts_endpoint: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f65ff9398a872705a3440a3cc66c9482bd228795fb9a03cc90ade53fa95a6080(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7238d506530aec0e963be7466103e379c469f4a482941a82a99658b2ec5e6730(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f8bc4370279e4aaabae8d701c5aa84b4e49bf8ca1ddaec13edc83d7176094bc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[MongodbatlasProviderAssumeRole]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08e22095268e78625b1e05b24648498bc80b9bde524ba6a908942e422dfb5e1a(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7192ddb2886f35c0bad628f1c7d07991d03ca186324175ceedad8cbf661fe9e8(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__450c3f61d7f69231f69ee8fbe9c1368168994bd9a2f69797b8ce78aacebe7c0e(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e888a6723b68bf6e99274a38779755d5a6a374fd675eea3fc2546d7a3b31c7d(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be3803931eb6230987d2776e5a234474a876c8981775a77ca3135f616e040b09(
    value: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b902bac3b33b8a18e3cb3ff2a69bb5a63ff9709e4b26edb1f1ce820ae8a2ef5(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efc355fe737da42da99d81c240288c34bb0a37e1208e25ca0363661e1ebe8438(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68c2d1010c5d14d5de57a1e5bb5bb54d6309bdf9ef0facbd6aeb2bffcc4c17b0(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e83df8da7f55cc26dc3e0d2a07bbb1fed9bdb7e7f5ef2cf36f0afc74f2b98d4e(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df5be10b3d5daddfecac0d98a37ca91a0a5c03f64b71cdf6fbc562076f7f28fc(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41e504f445a52d25568cfd60b04732d720bd56366efcaa9799df29d0a7d8299b(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__deb1e1099f1ce0152e5c866578153213519cc377f0c1c9249f29371d2edd2386(
    *,
    duration: typing.Optional[builtins.str] = None,
    external_id: typing.Optional[builtins.str] = None,
    policy: typing.Optional[builtins.str] = None,
    policy_arns: typing.Optional[typing.Sequence[builtins.str]] = None,
    role_arn: typing.Optional[builtins.str] = None,
    session_name: typing.Optional[builtins.str] = None,
    source_identity: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    transitive_tag_keys: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f1c6437c053fd97dacc33ed7f607ea706e0da1d2c5abbbbdcf28285101412b1(
    *,
    alias: typing.Optional[builtins.str] = None,
    assume_role: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[MongodbatlasProviderAssumeRole, typing.Dict[builtins.str, typing.Any]]]]] = None,
    aws_access_key_id: typing.Optional[builtins.str] = None,
    aws_secret_access_key: typing.Optional[builtins.str] = None,
    aws_session_token: typing.Optional[builtins.str] = None,
    base_url: typing.Optional[builtins.str] = None,
    is_mongodbgov_cloud: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    private_key: typing.Optional[builtins.str] = None,
    public_key: typing.Optional[builtins.str] = None,
    realm_base_url: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    secret_name: typing.Optional[builtins.str] = None,
    sts_endpoint: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
