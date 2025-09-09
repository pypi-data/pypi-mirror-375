r'''
# `mongodbatlas_encryption_at_rest`

Refer to the Terraform Registry for docs: [`mongodbatlas_encryption_at_rest`](https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest).
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


class EncryptionAtRest(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.encryptionAtRest.EncryptionAtRest",
):
    '''Represents a {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest mongodbatlas_encryption_at_rest}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        project_id: builtins.str,
        aws_kms_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["EncryptionAtRestAwsKmsConfig", typing.Dict[builtins.str, typing.Any]]]]] = None,
        azure_key_vault_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["EncryptionAtRestAzureKeyVaultConfig", typing.Dict[builtins.str, typing.Any]]]]] = None,
        enabled_for_search_nodes: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        google_cloud_kms_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["EncryptionAtRestGoogleCloudKmsConfig", typing.Dict[builtins.str, typing.Any]]]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest mongodbatlas_encryption_at_rest} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param project_id: Unique 24-hexadecimal digit string that identifies your project. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#project_id EncryptionAtRest#project_id}
        :param aws_kms_config: aws_kms_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#aws_kms_config EncryptionAtRest#aws_kms_config}
        :param azure_key_vault_config: azure_key_vault_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#azure_key_vault_config EncryptionAtRest#azure_key_vault_config}
        :param enabled_for_search_nodes: Flag that indicates whether Encryption at Rest for Dedicated Search Nodes is enabled in the specified project. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#enabled_for_search_nodes EncryptionAtRest#enabled_for_search_nodes}
        :param google_cloud_kms_config: google_cloud_kms_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#google_cloud_kms_config EncryptionAtRest#google_cloud_kms_config}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8a749241b9925e4e5575c33df78a5f4c547da582518cff88d990656dedbacb8)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = EncryptionAtRestConfig(
            project_id=project_id,
            aws_kms_config=aws_kms_config,
            azure_key_vault_config=azure_key_vault_config,
            enabled_for_search_nodes=enabled_for_search_nodes,
            google_cloud_kms_config=google_cloud_kms_config,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
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
        '''Generates CDKTF code for importing a EncryptionAtRest resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the EncryptionAtRest to import.
        :param import_from_id: The id of the existing EncryptionAtRest that should be imported. Refer to the {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the EncryptionAtRest to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0887d0ce6555a9a21ffd924e77d97c4894149f23e37ab964208596aaddea5227)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putAwsKmsConfig")
    def put_aws_kms_config(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["EncryptionAtRestAwsKmsConfig", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ab175d06a6cd6850af7e956be9fb54e498f63da7944692ffe2f50c8c63eea48)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAwsKmsConfig", [value]))

    @jsii.member(jsii_name="putAzureKeyVaultConfig")
    def put_azure_key_vault_config(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["EncryptionAtRestAzureKeyVaultConfig", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fcbe79c853e765df94d595f867f3e5dc6e922eb18d04c8ee4d6f6b6659187a76)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAzureKeyVaultConfig", [value]))

    @jsii.member(jsii_name="putGoogleCloudKmsConfig")
    def put_google_cloud_kms_config(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["EncryptionAtRestGoogleCloudKmsConfig", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8479a46703edc2e36b4019d7a26f0fdb3aff818a81e5405ac620d9a3d75f5076)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putGoogleCloudKmsConfig", [value]))

    @jsii.member(jsii_name="resetAwsKmsConfig")
    def reset_aws_kms_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsKmsConfig", []))

    @jsii.member(jsii_name="resetAzureKeyVaultConfig")
    def reset_azure_key_vault_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureKeyVaultConfig", []))

    @jsii.member(jsii_name="resetEnabledForSearchNodes")
    def reset_enabled_for_search_nodes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabledForSearchNodes", []))

    @jsii.member(jsii_name="resetGoogleCloudKmsConfig")
    def reset_google_cloud_kms_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGoogleCloudKmsConfig", []))

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
    @jsii.member(jsii_name="awsKmsConfig")
    def aws_kms_config(self) -> "EncryptionAtRestAwsKmsConfigList":
        return typing.cast("EncryptionAtRestAwsKmsConfigList", jsii.get(self, "awsKmsConfig"))

    @builtins.property
    @jsii.member(jsii_name="azureKeyVaultConfig")
    def azure_key_vault_config(self) -> "EncryptionAtRestAzureKeyVaultConfigList":
        return typing.cast("EncryptionAtRestAzureKeyVaultConfigList", jsii.get(self, "azureKeyVaultConfig"))

    @builtins.property
    @jsii.member(jsii_name="googleCloudKmsConfig")
    def google_cloud_kms_config(self) -> "EncryptionAtRestGoogleCloudKmsConfigList":
        return typing.cast("EncryptionAtRestGoogleCloudKmsConfigList", jsii.get(self, "googleCloudKmsConfig"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="awsKmsConfigInput")
    def aws_kms_config_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["EncryptionAtRestAwsKmsConfig"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["EncryptionAtRestAwsKmsConfig"]]], jsii.get(self, "awsKmsConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="azureKeyVaultConfigInput")
    def azure_key_vault_config_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["EncryptionAtRestAzureKeyVaultConfig"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["EncryptionAtRestAzureKeyVaultConfig"]]], jsii.get(self, "azureKeyVaultConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledForSearchNodesInput")
    def enabled_for_search_nodes_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledForSearchNodesInput"))

    @builtins.property
    @jsii.member(jsii_name="googleCloudKmsConfigInput")
    def google_cloud_kms_config_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["EncryptionAtRestGoogleCloudKmsConfig"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["EncryptionAtRestGoogleCloudKmsConfig"]]], jsii.get(self, "googleCloudKmsConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledForSearchNodes")
    def enabled_for_search_nodes(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enabledForSearchNodes"))

    @enabled_for_search_nodes.setter
    def enabled_for_search_nodes(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab3b1c104b8e90d0f8f5801db0f4254893c0147af355363c7bb5821e5a4f165e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabledForSearchNodes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9439e0e2caad1419ef55c3bce2d0e9762828a700c38e7fc4c0c6df694a3d7f9c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.encryptionAtRest.EncryptionAtRestAwsKmsConfig",
    jsii_struct_bases=[],
    name_mapping={
        "access_key_id": "accessKeyId",
        "customer_master_key_id": "customerMasterKeyId",
        "enabled": "enabled",
        "region": "region",
        "require_private_networking": "requirePrivateNetworking",
        "role_id": "roleId",
        "secret_access_key": "secretAccessKey",
    },
)
class EncryptionAtRestAwsKmsConfig:
    def __init__(
        self,
        *,
        access_key_id: typing.Optional[builtins.str] = None,
        customer_master_key_id: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        region: typing.Optional[builtins.str] = None,
        require_private_networking: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        role_id: typing.Optional[builtins.str] = None,
        secret_access_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param access_key_id: Unique alphanumeric string that identifies an Identity and Access Management (IAM) access key with permissions required to access your Amazon Web Services (AWS) Customer Master Key (CMK). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#access_key_id EncryptionAtRest#access_key_id}
        :param customer_master_key_id: Unique alphanumeric string that identifies the Amazon Web Services (AWS) Customer Master Key (CMK) you used to encrypt and decrypt the MongoDB master keys. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#customer_master_key_id EncryptionAtRest#customer_master_key_id}
        :param enabled: Flag that indicates whether someone enabled encryption at rest for the specified project through Amazon Web Services (AWS) Key Management Service (KMS). To disable encryption at rest using customer key management and remove the configuration details, pass only this parameter with a value of ``false``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#enabled EncryptionAtRest#enabled}
        :param region: Physical location where MongoDB Atlas deploys your AWS-hosted MongoDB cluster nodes. The region you choose can affect network latency for clients accessing your databases. When MongoDB Cloud deploys a dedicated cluster, it checks if a VPC or VPC connection exists for that provider and region. If not, MongoDB Atlas creates them as part of the deployment. MongoDB Atlas assigns the VPC a CIDR block. To limit a new VPC peering connection to one CIDR block and region, create the connection first. Deploy the cluster after the connection starts. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#region EncryptionAtRest#region}
        :param require_private_networking: Enable connection to your Amazon Web Services (AWS) Key Management Service (KMS) over private networking. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#require_private_networking EncryptionAtRest#require_private_networking}
        :param role_id: Unique 24-hexadecimal digit string that identifies an Amazon Web Services (AWS) Identity and Access Management (IAM) role. This IAM role has the permissions required to manage your AWS customer master key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#role_id EncryptionAtRest#role_id}
        :param secret_access_key: Human-readable label of the Identity and Access Management (IAM) secret access key with permissions required to access your Amazon Web Services (AWS) customer master key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#secret_access_key EncryptionAtRest#secret_access_key}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1dd6569dc4b956383c6698bba19ed570923e21ab1bcc7247a726669fa55ccaa1)
            check_type(argname="argument access_key_id", value=access_key_id, expected_type=type_hints["access_key_id"])
            check_type(argname="argument customer_master_key_id", value=customer_master_key_id, expected_type=type_hints["customer_master_key_id"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument require_private_networking", value=require_private_networking, expected_type=type_hints["require_private_networking"])
            check_type(argname="argument role_id", value=role_id, expected_type=type_hints["role_id"])
            check_type(argname="argument secret_access_key", value=secret_access_key, expected_type=type_hints["secret_access_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if access_key_id is not None:
            self._values["access_key_id"] = access_key_id
        if customer_master_key_id is not None:
            self._values["customer_master_key_id"] = customer_master_key_id
        if enabled is not None:
            self._values["enabled"] = enabled
        if region is not None:
            self._values["region"] = region
        if require_private_networking is not None:
            self._values["require_private_networking"] = require_private_networking
        if role_id is not None:
            self._values["role_id"] = role_id
        if secret_access_key is not None:
            self._values["secret_access_key"] = secret_access_key

    @builtins.property
    def access_key_id(self) -> typing.Optional[builtins.str]:
        '''Unique alphanumeric string that identifies an Identity and Access Management (IAM) access key with permissions required to access your Amazon Web Services (AWS) Customer Master Key (CMK).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#access_key_id EncryptionAtRest#access_key_id}
        '''
        result = self._values.get("access_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def customer_master_key_id(self) -> typing.Optional[builtins.str]:
        '''Unique alphanumeric string that identifies the Amazon Web Services (AWS) Customer Master Key (CMK) you used to encrypt and decrypt the MongoDB master keys.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#customer_master_key_id EncryptionAtRest#customer_master_key_id}
        '''
        result = self._values.get("customer_master_key_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag that indicates whether someone enabled encryption at rest for the specified project through Amazon Web Services (AWS) Key Management Service (KMS).

        To disable encryption at rest using customer key management and remove the configuration details, pass only this parameter with a value of ``false``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#enabled EncryptionAtRest#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Physical location where MongoDB Atlas deploys your AWS-hosted MongoDB cluster nodes.

        The region you choose can affect network latency for clients accessing your databases. When MongoDB Cloud deploys a dedicated cluster, it checks if a VPC or VPC connection exists for that provider and region. If not, MongoDB Atlas creates them as part of the deployment. MongoDB Atlas assigns the VPC a CIDR block. To limit a new VPC peering connection to one CIDR block and region, create the connection first. Deploy the cluster after the connection starts.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#region EncryptionAtRest#region}
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def require_private_networking(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable connection to your Amazon Web Services (AWS) Key Management Service (KMS) over private networking.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#require_private_networking EncryptionAtRest#require_private_networking}
        '''
        result = self._values.get("require_private_networking")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def role_id(self) -> typing.Optional[builtins.str]:
        '''Unique 24-hexadecimal digit string that identifies an Amazon Web Services (AWS) Identity and Access Management (IAM) role.

        This IAM role has the permissions required to manage your AWS customer master key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#role_id EncryptionAtRest#role_id}
        '''
        result = self._values.get("role_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secret_access_key(self) -> typing.Optional[builtins.str]:
        '''Human-readable label of the Identity and Access Management (IAM) secret access key with permissions required to access your Amazon Web Services (AWS) customer master key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#secret_access_key EncryptionAtRest#secret_access_key}
        '''
        result = self._values.get("secret_access_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EncryptionAtRestAwsKmsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EncryptionAtRestAwsKmsConfigList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.encryptionAtRest.EncryptionAtRestAwsKmsConfigList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__71bba9fad89034da21963c9d5581adff67a3ae39a798ba4c726bc651440791ff)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "EncryptionAtRestAwsKmsConfigOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15a99ec2f3a2165f907a8b34efaf2fefe187d004fd96a46b4865a30df66f5a38)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("EncryptionAtRestAwsKmsConfigOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4747692202e89f24ad14c084044254dedac368c8636a2c6669c527e720c11f9d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9836710b7f0c86c12b31ef837330f169cb1cd913d787ac8a57ceda3a4206eb20)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d0e8ed67f1da1579d6dde30f2386ab9673bc1b7ffd90212bce4224b582582ba8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[EncryptionAtRestAwsKmsConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[EncryptionAtRestAwsKmsConfig]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[EncryptionAtRestAwsKmsConfig]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74b1018c28aa003a6f495a944bea27669e7e5441ae4af397a5132a1b2591675a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class EncryptionAtRestAwsKmsConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.encryptionAtRest.EncryptionAtRestAwsKmsConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__58d2d3a567c0bf664f2b33d6fad122cea199f1c4af389e2ced9e5038115d59e5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetAccessKeyId")
    def reset_access_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccessKeyId", []))

    @jsii.member(jsii_name="resetCustomerMasterKeyId")
    def reset_customer_master_key_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCustomerMasterKeyId", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @jsii.member(jsii_name="resetRequirePrivateNetworking")
    def reset_require_private_networking(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequirePrivateNetworking", []))

    @jsii.member(jsii_name="resetRoleId")
    def reset_role_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRoleId", []))

    @jsii.member(jsii_name="resetSecretAccessKey")
    def reset_secret_access_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecretAccessKey", []))

    @builtins.property
    @jsii.member(jsii_name="valid")
    def valid(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "valid"))

    @builtins.property
    @jsii.member(jsii_name="accessKeyIdInput")
    def access_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accessKeyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="customerMasterKeyIdInput")
    def customer_master_key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "customerMasterKeyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="requirePrivateNetworkingInput")
    def require_private_networking_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "requirePrivateNetworkingInput"))

    @builtins.property
    @jsii.member(jsii_name="roleIdInput")
    def role_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleIdInput"))

    @builtins.property
    @jsii.member(jsii_name="secretAccessKeyInput")
    def secret_access_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretAccessKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="accessKeyId")
    def access_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accessKeyId"))

    @access_key_id.setter
    def access_key_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f51b399a6b218c7cfaeda67a1bfe310fbffe2656af726f28bb6fd28a95df29c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accessKeyId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="customerMasterKeyId")
    def customer_master_key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "customerMasterKeyId"))

    @customer_master_key_id.setter
    def customer_master_key_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4361390b0e55e1cfd4f404c68d2fe4d747847ff2b16fd45d24d959a0abca2c9a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "customerMasterKeyId", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__eb2e8075f14e443d096f05767a14288428c6d1f96c44b927d083871cb521f851)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef4c80bc4747c81dba5c780f7c052b1dac12f90d2c983d89f17e1f0197cb6fcb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requirePrivateNetworking")
    def require_private_networking(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "requirePrivateNetworking"))

    @require_private_networking.setter
    def require_private_networking(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b7946425a45549560570c792bdca31abbc5b7b6c6fa05218fcf1aff68cd374b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requirePrivateNetworking", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="roleId")
    def role_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleId"))

    @role_id.setter
    def role_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55081dbc7a44d12c1a56eb8949356b1da8be074cf5a8ff28b995922027d106f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "roleId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secretAccessKey")
    def secret_access_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretAccessKey"))

    @secret_access_key.setter
    def secret_access_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12b709f63a750640efb8dbb285fc46e321a400ce0739ab0f311b94519db83ea0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secretAccessKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, EncryptionAtRestAwsKmsConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, EncryptionAtRestAwsKmsConfig]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, EncryptionAtRestAwsKmsConfig]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2837550a221a143ba84f9f8051c03a38e6cdc75bf63b452e090b383c89e59814)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.encryptionAtRest.EncryptionAtRestAzureKeyVaultConfig",
    jsii_struct_bases=[],
    name_mapping={
        "azure_environment": "azureEnvironment",
        "client_id": "clientId",
        "enabled": "enabled",
        "key_identifier": "keyIdentifier",
        "key_vault_name": "keyVaultName",
        "require_private_networking": "requirePrivateNetworking",
        "resource_group_name": "resourceGroupName",
        "secret": "secret",
        "subscription_id": "subscriptionId",
        "tenant_id": "tenantId",
    },
)
class EncryptionAtRestAzureKeyVaultConfig:
    def __init__(
        self,
        *,
        azure_environment: typing.Optional[builtins.str] = None,
        client_id: typing.Optional[builtins.str] = None,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        key_identifier: typing.Optional[builtins.str] = None,
        key_vault_name: typing.Optional[builtins.str] = None,
        require_private_networking: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        resource_group_name: typing.Optional[builtins.str] = None,
        secret: typing.Optional[builtins.str] = None,
        subscription_id: typing.Optional[builtins.str] = None,
        tenant_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param azure_environment: Azure environment in which your account credentials reside. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#azure_environment EncryptionAtRest#azure_environment}
        :param client_id: Unique 36-hexadecimal character string that identifies an Azure application associated with your Azure Active Directory tenant. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#client_id EncryptionAtRest#client_id}
        :param enabled: Flag that indicates whether someone enabled encryption at rest for the specified project. To disable encryption at rest using customer key management and remove the configuration details, pass only this parameter with a value of ``false``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#enabled EncryptionAtRest#enabled}
        :param key_identifier: Web address with a unique key that identifies for your Azure Key Vault. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#key_identifier EncryptionAtRest#key_identifier}
        :param key_vault_name: Unique string that identifies the Azure Key Vault that contains your key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#key_vault_name EncryptionAtRest#key_vault_name}
        :param require_private_networking: Enable connection to your Azure Key Vault over private networking. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#require_private_networking EncryptionAtRest#require_private_networking}
        :param resource_group_name: Name of the Azure resource group that contains your Azure Key Vault. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#resource_group_name EncryptionAtRest#resource_group_name}
        :param secret: Private data that you need secured and that belongs to the specified Azure Key Vault (AKV) tenant (**azureKeyVault.tenantID**). This data can include any type of sensitive data such as passwords, database connection strings, API keys, and the like. AKV stores this information as encrypted binary data. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#secret EncryptionAtRest#secret}
        :param subscription_id: Unique 36-hexadecimal character string that identifies your Azure subscription. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#subscription_id EncryptionAtRest#subscription_id}
        :param tenant_id: Unique 36-hexadecimal character string that identifies the Azure Active Directory tenant within your Azure subscription. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#tenant_id EncryptionAtRest#tenant_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af1862db25e54c77985632a2ac72a3a22ffc755c82b8d516e11b4c05257a8c22)
            check_type(argname="argument azure_environment", value=azure_environment, expected_type=type_hints["azure_environment"])
            check_type(argname="argument client_id", value=client_id, expected_type=type_hints["client_id"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument key_identifier", value=key_identifier, expected_type=type_hints["key_identifier"])
            check_type(argname="argument key_vault_name", value=key_vault_name, expected_type=type_hints["key_vault_name"])
            check_type(argname="argument require_private_networking", value=require_private_networking, expected_type=type_hints["require_private_networking"])
            check_type(argname="argument resource_group_name", value=resource_group_name, expected_type=type_hints["resource_group_name"])
            check_type(argname="argument secret", value=secret, expected_type=type_hints["secret"])
            check_type(argname="argument subscription_id", value=subscription_id, expected_type=type_hints["subscription_id"])
            check_type(argname="argument tenant_id", value=tenant_id, expected_type=type_hints["tenant_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if azure_environment is not None:
            self._values["azure_environment"] = azure_environment
        if client_id is not None:
            self._values["client_id"] = client_id
        if enabled is not None:
            self._values["enabled"] = enabled
        if key_identifier is not None:
            self._values["key_identifier"] = key_identifier
        if key_vault_name is not None:
            self._values["key_vault_name"] = key_vault_name
        if require_private_networking is not None:
            self._values["require_private_networking"] = require_private_networking
        if resource_group_name is not None:
            self._values["resource_group_name"] = resource_group_name
        if secret is not None:
            self._values["secret"] = secret
        if subscription_id is not None:
            self._values["subscription_id"] = subscription_id
        if tenant_id is not None:
            self._values["tenant_id"] = tenant_id

    @builtins.property
    def azure_environment(self) -> typing.Optional[builtins.str]:
        '''Azure environment in which your account credentials reside.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#azure_environment EncryptionAtRest#azure_environment}
        '''
        result = self._values.get("azure_environment")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def client_id(self) -> typing.Optional[builtins.str]:
        '''Unique 36-hexadecimal character string that identifies an Azure application associated with your Azure Active Directory tenant.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#client_id EncryptionAtRest#client_id}
        '''
        result = self._values.get("client_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag that indicates whether someone enabled encryption at rest for the specified  project.

        To disable encryption at rest using customer key management and remove the configuration details, pass only this parameter with a value of ``false``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#enabled EncryptionAtRest#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def key_identifier(self) -> typing.Optional[builtins.str]:
        '''Web address with a unique key that identifies for your Azure Key Vault.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#key_identifier EncryptionAtRest#key_identifier}
        '''
        result = self._values.get("key_identifier")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_vault_name(self) -> typing.Optional[builtins.str]:
        '''Unique string that identifies the Azure Key Vault that contains your key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#key_vault_name EncryptionAtRest#key_vault_name}
        '''
        result = self._values.get("key_vault_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def require_private_networking(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable connection to your Azure Key Vault over private networking.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#require_private_networking EncryptionAtRest#require_private_networking}
        '''
        result = self._values.get("require_private_networking")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def resource_group_name(self) -> typing.Optional[builtins.str]:
        '''Name of the Azure resource group that contains your Azure Key Vault.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#resource_group_name EncryptionAtRest#resource_group_name}
        '''
        result = self._values.get("resource_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secret(self) -> typing.Optional[builtins.str]:
        '''Private data that you need secured and that belongs to the specified Azure Key Vault (AKV) tenant (**azureKeyVault.tenantID**). This data can include any type of sensitive data such as passwords, database connection strings, API keys, and the like. AKV stores this information as encrypted binary data.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#secret EncryptionAtRest#secret}
        '''
        result = self._values.get("secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def subscription_id(self) -> typing.Optional[builtins.str]:
        '''Unique 36-hexadecimal character string that identifies your Azure subscription.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#subscription_id EncryptionAtRest#subscription_id}
        '''
        result = self._values.get("subscription_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tenant_id(self) -> typing.Optional[builtins.str]:
        '''Unique 36-hexadecimal character string that identifies the Azure Active Directory tenant within your Azure subscription.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#tenant_id EncryptionAtRest#tenant_id}
        '''
        result = self._values.get("tenant_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EncryptionAtRestAzureKeyVaultConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EncryptionAtRestAzureKeyVaultConfigList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.encryptionAtRest.EncryptionAtRestAzureKeyVaultConfigList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b65f917655edecc4fd483b4736a241d35ecb4f8b16e5d9bb849f74a9590b9b9d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "EncryptionAtRestAzureKeyVaultConfigOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__483ac7e07d7aee9a92db5da6c91918e5be00ec81e8f22c69c8797812aba887ed)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("EncryptionAtRestAzureKeyVaultConfigOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f77f7239e66d6ae02f80a1de297371b71578a28bb40888a697fd8f7d7b6df75c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__079739d967c244af514a787f875fda623de185cfa593f7a678e7ec9061ddcb8b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__18b295844cec8398cea52481056efbb87c8531582af6be92efb08317ff2c139f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[EncryptionAtRestAzureKeyVaultConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[EncryptionAtRestAzureKeyVaultConfig]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[EncryptionAtRestAzureKeyVaultConfig]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6551790ef766f38c41d00f290668eb5d1ab46058404772d63afb0183258a0ee2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class EncryptionAtRestAzureKeyVaultConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.encryptionAtRest.EncryptionAtRestAzureKeyVaultConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7cf936d70031c0e28dd3de0139428b13036a86d3a0a83edaf6d7843d6466149b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetAzureEnvironment")
    def reset_azure_environment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureEnvironment", []))

    @jsii.member(jsii_name="resetClientId")
    def reset_client_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClientId", []))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetKeyIdentifier")
    def reset_key_identifier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyIdentifier", []))

    @jsii.member(jsii_name="resetKeyVaultName")
    def reset_key_vault_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyVaultName", []))

    @jsii.member(jsii_name="resetRequirePrivateNetworking")
    def reset_require_private_networking(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequirePrivateNetworking", []))

    @jsii.member(jsii_name="resetResourceGroupName")
    def reset_resource_group_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceGroupName", []))

    @jsii.member(jsii_name="resetSecret")
    def reset_secret(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecret", []))

    @jsii.member(jsii_name="resetSubscriptionId")
    def reset_subscription_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubscriptionId", []))

    @jsii.member(jsii_name="resetTenantId")
    def reset_tenant_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTenantId", []))

    @builtins.property
    @jsii.member(jsii_name="valid")
    def valid(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "valid"))

    @builtins.property
    @jsii.member(jsii_name="azureEnvironmentInput")
    def azure_environment_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "azureEnvironmentInput"))

    @builtins.property
    @jsii.member(jsii_name="clientIdInput")
    def client_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clientIdInput"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="keyIdentifierInput")
    def key_identifier_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyIdentifierInput"))

    @builtins.property
    @jsii.member(jsii_name="keyVaultNameInput")
    def key_vault_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyVaultNameInput"))

    @builtins.property
    @jsii.member(jsii_name="requirePrivateNetworkingInput")
    def require_private_networking_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "requirePrivateNetworkingInput"))

    @builtins.property
    @jsii.member(jsii_name="resourceGroupNameInput")
    def resource_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceGroupNameInput"))

    @builtins.property
    @jsii.member(jsii_name="secretInput")
    def secret_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretInput"))

    @builtins.property
    @jsii.member(jsii_name="subscriptionIdInput")
    def subscription_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "subscriptionIdInput"))

    @builtins.property
    @jsii.member(jsii_name="tenantIdInput")
    def tenant_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tenantIdInput"))

    @builtins.property
    @jsii.member(jsii_name="azureEnvironment")
    def azure_environment(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "azureEnvironment"))

    @azure_environment.setter
    def azure_environment(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a5080be53a162314178eb3d5a5754dcdf9af36d5bbeb8a5d7f68acba1b4af2e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureEnvironment", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clientId")
    def client_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clientId"))

    @client_id.setter
    def client_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ae7fda14c6d425af21fb6567e49233b21a590ccbf3d8fcf8b7e85a73d07ed20)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clientId", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__e3645fc98a9ddbe83aa53926f7f7c8e634518f2c97af7ec68b934366e3d3d4e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyIdentifier")
    def key_identifier(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyIdentifier"))

    @key_identifier.setter
    def key_identifier(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4db41b5d2b0af428972a4e9f72116499c0eecc581aef510b14e1f4f416428977)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyIdentifier", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyVaultName")
    def key_vault_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyVaultName"))

    @key_vault_name.setter
    def key_vault_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7c134ac3f2fb59beced0dce92b78bfc1f797c12d48e6488f9e3c144fa1f703a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyVaultName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requirePrivateNetworking")
    def require_private_networking(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "requirePrivateNetworking"))

    @require_private_networking.setter
    def require_private_networking(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__912cd3c621f4eb15824d6d2067d7d3a0544969b8780b8c663df5099ce29c661a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requirePrivateNetworking", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resourceGroupName")
    def resource_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceGroupName"))

    @resource_group_name.setter
    def resource_group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48748e519eea9ea85d698ac8f416d359ab2181ce066b5f34a58f177d2e5bcd32)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceGroupName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secret")
    def secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secret"))

    @secret.setter
    def secret(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__315e7d884e7ee505be7de1fc076a66df982f3ef2ee62a2ea8346b01ad7ae9eb4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secret", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="subscriptionId")
    def subscription_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "subscriptionId"))

    @subscription_id.setter
    def subscription_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__030dbb056efbe20837256ce43acbbf3f0a042338f7eaf584d5da97a966f1ade6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subscriptionId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tenantId")
    def tenant_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tenantId"))

    @tenant_id.setter
    def tenant_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b10d03016237213b406fbea0c0234c896b5432234d76f29390df77058785a79)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tenantId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, EncryptionAtRestAzureKeyVaultConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, EncryptionAtRestAzureKeyVaultConfig]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, EncryptionAtRestAzureKeyVaultConfig]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52199317422413f9c082734d0a9af04626b6ff66474a6ada6d72c26b41e7d7ab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.encryptionAtRest.EncryptionAtRestConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "project_id": "projectId",
        "aws_kms_config": "awsKmsConfig",
        "azure_key_vault_config": "azureKeyVaultConfig",
        "enabled_for_search_nodes": "enabledForSearchNodes",
        "google_cloud_kms_config": "googleCloudKmsConfig",
    },
)
class EncryptionAtRestConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        project_id: builtins.str,
        aws_kms_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[EncryptionAtRestAwsKmsConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
        azure_key_vault_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[EncryptionAtRestAzureKeyVaultConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
        enabled_for_search_nodes: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        google_cloud_kms_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["EncryptionAtRestGoogleCloudKmsConfig", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param project_id: Unique 24-hexadecimal digit string that identifies your project. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#project_id EncryptionAtRest#project_id}
        :param aws_kms_config: aws_kms_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#aws_kms_config EncryptionAtRest#aws_kms_config}
        :param azure_key_vault_config: azure_key_vault_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#azure_key_vault_config EncryptionAtRest#azure_key_vault_config}
        :param enabled_for_search_nodes: Flag that indicates whether Encryption at Rest for Dedicated Search Nodes is enabled in the specified project. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#enabled_for_search_nodes EncryptionAtRest#enabled_for_search_nodes}
        :param google_cloud_kms_config: google_cloud_kms_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#google_cloud_kms_config EncryptionAtRest#google_cloud_kms_config}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8fd0d6cbf8a84a372487ec153ba2f3813d8498010cc8bebed82e6cb3a5bb07f8)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument aws_kms_config", value=aws_kms_config, expected_type=type_hints["aws_kms_config"])
            check_type(argname="argument azure_key_vault_config", value=azure_key_vault_config, expected_type=type_hints["azure_key_vault_config"])
            check_type(argname="argument enabled_for_search_nodes", value=enabled_for_search_nodes, expected_type=type_hints["enabled_for_search_nodes"])
            check_type(argname="argument google_cloud_kms_config", value=google_cloud_kms_config, expected_type=type_hints["google_cloud_kms_config"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
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
        if aws_kms_config is not None:
            self._values["aws_kms_config"] = aws_kms_config
        if azure_key_vault_config is not None:
            self._values["azure_key_vault_config"] = azure_key_vault_config
        if enabled_for_search_nodes is not None:
            self._values["enabled_for_search_nodes"] = enabled_for_search_nodes
        if google_cloud_kms_config is not None:
            self._values["google_cloud_kms_config"] = google_cloud_kms_config

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
    def project_id(self) -> builtins.str:
        '''Unique 24-hexadecimal digit string that identifies your project.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#project_id EncryptionAtRest#project_id}
        '''
        result = self._values.get("project_id")
        assert result is not None, "Required property 'project_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def aws_kms_config(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[EncryptionAtRestAwsKmsConfig]]]:
        '''aws_kms_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#aws_kms_config EncryptionAtRest#aws_kms_config}
        '''
        result = self._values.get("aws_kms_config")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[EncryptionAtRestAwsKmsConfig]]], result)

    @builtins.property
    def azure_key_vault_config(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[EncryptionAtRestAzureKeyVaultConfig]]]:
        '''azure_key_vault_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#azure_key_vault_config EncryptionAtRest#azure_key_vault_config}
        '''
        result = self._values.get("azure_key_vault_config")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[EncryptionAtRestAzureKeyVaultConfig]]], result)

    @builtins.property
    def enabled_for_search_nodes(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag that indicates whether Encryption at Rest for Dedicated Search Nodes is enabled in the specified project.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#enabled_for_search_nodes EncryptionAtRest#enabled_for_search_nodes}
        '''
        result = self._values.get("enabled_for_search_nodes")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def google_cloud_kms_config(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["EncryptionAtRestGoogleCloudKmsConfig"]]]:
        '''google_cloud_kms_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#google_cloud_kms_config EncryptionAtRest#google_cloud_kms_config}
        '''
        result = self._values.get("google_cloud_kms_config")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["EncryptionAtRestGoogleCloudKmsConfig"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EncryptionAtRestConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.encryptionAtRest.EncryptionAtRestGoogleCloudKmsConfig",
    jsii_struct_bases=[],
    name_mapping={
        "enabled": "enabled",
        "key_version_resource_id": "keyVersionResourceId",
        "role_id": "roleId",
        "service_account_key": "serviceAccountKey",
    },
)
class EncryptionAtRestGoogleCloudKmsConfig:
    def __init__(
        self,
        *,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        key_version_resource_id: typing.Optional[builtins.str] = None,
        role_id: typing.Optional[builtins.str] = None,
        service_account_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param enabled: Flag that indicates whether someone enabled encryption at rest for the specified project. To disable encryption at rest using customer key management and remove the configuration details, pass only this parameter with a value of ``false``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#enabled EncryptionAtRest#enabled}
        :param key_version_resource_id: Resource path that displays the key version resource ID for your Google Cloud KMS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#key_version_resource_id EncryptionAtRest#key_version_resource_id}
        :param role_id: Unique 24-hexadecimal digit string that identifies the Google Cloud Provider Access Role that MongoDB Cloud uses to access the Google Cloud KMS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#role_id EncryptionAtRest#role_id}
        :param service_account_key: JavaScript Object Notation (JSON) object that contains the Google Cloud Key Management Service (KMS). Format the JSON as a string and not as an object. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#service_account_key EncryptionAtRest#service_account_key}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aedb02119e179d4089eb0d364bb17330a58560982b3605a6181f3239dd678184)
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument key_version_resource_id", value=key_version_resource_id, expected_type=type_hints["key_version_resource_id"])
            check_type(argname="argument role_id", value=role_id, expected_type=type_hints["role_id"])
            check_type(argname="argument service_account_key", value=service_account_key, expected_type=type_hints["service_account_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if enabled is not None:
            self._values["enabled"] = enabled
        if key_version_resource_id is not None:
            self._values["key_version_resource_id"] = key_version_resource_id
        if role_id is not None:
            self._values["role_id"] = role_id
        if service_account_key is not None:
            self._values["service_account_key"] = service_account_key

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Flag that indicates whether someone enabled encryption at rest for the specified  project.

        To disable encryption at rest using customer key management and remove the configuration details, pass only this parameter with a value of ``false``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#enabled EncryptionAtRest#enabled}
        '''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def key_version_resource_id(self) -> typing.Optional[builtins.str]:
        '''Resource path that displays the key version resource ID for your Google Cloud KMS.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#key_version_resource_id EncryptionAtRest#key_version_resource_id}
        '''
        result = self._values.get("key_version_resource_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def role_id(self) -> typing.Optional[builtins.str]:
        '''Unique 24-hexadecimal digit string that identifies the Google Cloud Provider Access Role that MongoDB Cloud uses to access the Google Cloud KMS.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#role_id EncryptionAtRest#role_id}
        '''
        result = self._values.get("role_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service_account_key(self) -> typing.Optional[builtins.str]:
        '''JavaScript Object Notation (JSON) object that contains the Google Cloud Key Management Service (KMS).

        Format the JSON as a string and not as an object.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/encryption_at_rest#service_account_key EncryptionAtRest#service_account_key}
        '''
        result = self._values.get("service_account_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EncryptionAtRestGoogleCloudKmsConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EncryptionAtRestGoogleCloudKmsConfigList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.encryptionAtRest.EncryptionAtRestGoogleCloudKmsConfigList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c97d93bbd78001b479c9ad336596cc63e49acc32a59a817fe4d1abb29d071d59)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "EncryptionAtRestGoogleCloudKmsConfigOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ab3d7903196fa94f0d70b20b2cde4124141803b978aa4feac932f79e11e40de)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("EncryptionAtRestGoogleCloudKmsConfigOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e17ad80db1bcb411a58bbeda0201e2234e2e3aebe0092a417c792b725555499b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bcb580c2ea19a0dac1ef250dfb775a0365d78a6aa71878a0606b2f66c51dda35)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e7b5b795373629513a737716bdadc81e055283ec69aaa716c59a492e419e9638)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[EncryptionAtRestGoogleCloudKmsConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[EncryptionAtRestGoogleCloudKmsConfig]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[EncryptionAtRestGoogleCloudKmsConfig]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__589e31b4ad940228cb05726a41d966dab4f3a6afd30c5418474c227a8290852d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class EncryptionAtRestGoogleCloudKmsConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.encryptionAtRest.EncryptionAtRestGoogleCloudKmsConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4bfaca90c3f6809a2826ed8c38a1a8a7f49dbd6808ffe0e60b27580a2d2a466d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetKeyVersionResourceId")
    def reset_key_version_resource_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyVersionResourceId", []))

    @jsii.member(jsii_name="resetRoleId")
    def reset_role_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRoleId", []))

    @jsii.member(jsii_name="resetServiceAccountKey")
    def reset_service_account_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceAccountKey", []))

    @builtins.property
    @jsii.member(jsii_name="valid")
    def valid(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "valid"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="keyVersionResourceIdInput")
    def key_version_resource_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyVersionResourceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="roleIdInput")
    def role_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleIdInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceAccountKeyInput")
    def service_account_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceAccountKeyInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__52eeed5634eae91d25dda8d5f7fe8806b117f3485f1b87f00fbf14b0a0d12ddb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="keyVersionResourceId")
    def key_version_resource_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyVersionResourceId"))

    @key_version_resource_id.setter
    def key_version_resource_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b348720d95ed8204a70c897eee20442ba668247f32f91cab8899640b9f38dfd6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyVersionResourceId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="roleId")
    def role_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleId"))

    @role_id.setter
    def role_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45cb3b3166b9c9cd5a14ccb75f37284f070dc2222c03c7a1ffe6b296e6abb63b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "roleId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serviceAccountKey")
    def service_account_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceAccountKey"))

    @service_account_key.setter
    def service_account_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4346f8a20f517ffa99b4e5995f3f8146c333c2319ef9b7d2338e2109a11b41de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceAccountKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, EncryptionAtRestGoogleCloudKmsConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, EncryptionAtRestGoogleCloudKmsConfig]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, EncryptionAtRestGoogleCloudKmsConfig]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__685dfa2d5d6e4991e48f4f73402afbfe5534a824ecc445c8046945ff7b7410e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "EncryptionAtRest",
    "EncryptionAtRestAwsKmsConfig",
    "EncryptionAtRestAwsKmsConfigList",
    "EncryptionAtRestAwsKmsConfigOutputReference",
    "EncryptionAtRestAzureKeyVaultConfig",
    "EncryptionAtRestAzureKeyVaultConfigList",
    "EncryptionAtRestAzureKeyVaultConfigOutputReference",
    "EncryptionAtRestConfig",
    "EncryptionAtRestGoogleCloudKmsConfig",
    "EncryptionAtRestGoogleCloudKmsConfigList",
    "EncryptionAtRestGoogleCloudKmsConfigOutputReference",
]

publication.publish()

def _typecheckingstub__b8a749241b9925e4e5575c33df78a5f4c547da582518cff88d990656dedbacb8(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    project_id: builtins.str,
    aws_kms_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[EncryptionAtRestAwsKmsConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
    azure_key_vault_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[EncryptionAtRestAzureKeyVaultConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
    enabled_for_search_nodes: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    google_cloud_kms_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[EncryptionAtRestGoogleCloudKmsConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
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

def _typecheckingstub__0887d0ce6555a9a21ffd924e77d97c4894149f23e37ab964208596aaddea5227(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ab175d06a6cd6850af7e956be9fb54e498f63da7944692ffe2f50c8c63eea48(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[EncryptionAtRestAwsKmsConfig, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fcbe79c853e765df94d595f867f3e5dc6e922eb18d04c8ee4d6f6b6659187a76(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[EncryptionAtRestAzureKeyVaultConfig, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8479a46703edc2e36b4019d7a26f0fdb3aff818a81e5405ac620d9a3d75f5076(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[EncryptionAtRestGoogleCloudKmsConfig, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab3b1c104b8e90d0f8f5801db0f4254893c0147af355363c7bb5821e5a4f165e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9439e0e2caad1419ef55c3bce2d0e9762828a700c38e7fc4c0c6df694a3d7f9c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1dd6569dc4b956383c6698bba19ed570923e21ab1bcc7247a726669fa55ccaa1(
    *,
    access_key_id: typing.Optional[builtins.str] = None,
    customer_master_key_id: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    region: typing.Optional[builtins.str] = None,
    require_private_networking: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    role_id: typing.Optional[builtins.str] = None,
    secret_access_key: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71bba9fad89034da21963c9d5581adff67a3ae39a798ba4c726bc651440791ff(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15a99ec2f3a2165f907a8b34efaf2fefe187d004fd96a46b4865a30df66f5a38(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4747692202e89f24ad14c084044254dedac368c8636a2c6669c527e720c11f9d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9836710b7f0c86c12b31ef837330f169cb1cd913d787ac8a57ceda3a4206eb20(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d0e8ed67f1da1579d6dde30f2386ab9673bc1b7ffd90212bce4224b582582ba8(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74b1018c28aa003a6f495a944bea27669e7e5441ae4af397a5132a1b2591675a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[EncryptionAtRestAwsKmsConfig]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58d2d3a567c0bf664f2b33d6fad122cea199f1c4af389e2ced9e5038115d59e5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f51b399a6b218c7cfaeda67a1bfe310fbffe2656af726f28bb6fd28a95df29c0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4361390b0e55e1cfd4f404c68d2fe4d747847ff2b16fd45d24d959a0abca2c9a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb2e8075f14e443d096f05767a14288428c6d1f96c44b927d083871cb521f851(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef4c80bc4747c81dba5c780f7c052b1dac12f90d2c983d89f17e1f0197cb6fcb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b7946425a45549560570c792bdca31abbc5b7b6c6fa05218fcf1aff68cd374b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55081dbc7a44d12c1a56eb8949356b1da8be074cf5a8ff28b995922027d106f1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12b709f63a750640efb8dbb285fc46e321a400ce0739ab0f311b94519db83ea0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2837550a221a143ba84f9f8051c03a38e6cdc75bf63b452e090b383c89e59814(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, EncryptionAtRestAwsKmsConfig]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af1862db25e54c77985632a2ac72a3a22ffc755c82b8d516e11b4c05257a8c22(
    *,
    azure_environment: typing.Optional[builtins.str] = None,
    client_id: typing.Optional[builtins.str] = None,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    key_identifier: typing.Optional[builtins.str] = None,
    key_vault_name: typing.Optional[builtins.str] = None,
    require_private_networking: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    resource_group_name: typing.Optional[builtins.str] = None,
    secret: typing.Optional[builtins.str] = None,
    subscription_id: typing.Optional[builtins.str] = None,
    tenant_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b65f917655edecc4fd483b4736a241d35ecb4f8b16e5d9bb849f74a9590b9b9d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__483ac7e07d7aee9a92db5da6c91918e5be00ec81e8f22c69c8797812aba887ed(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f77f7239e66d6ae02f80a1de297371b71578a28bb40888a697fd8f7d7b6df75c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__079739d967c244af514a787f875fda623de185cfa593f7a678e7ec9061ddcb8b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18b295844cec8398cea52481056efbb87c8531582af6be92efb08317ff2c139f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6551790ef766f38c41d00f290668eb5d1ab46058404772d63afb0183258a0ee2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[EncryptionAtRestAzureKeyVaultConfig]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7cf936d70031c0e28dd3de0139428b13036a86d3a0a83edaf6d7843d6466149b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a5080be53a162314178eb3d5a5754dcdf9af36d5bbeb8a5d7f68acba1b4af2e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ae7fda14c6d425af21fb6567e49233b21a590ccbf3d8fcf8b7e85a73d07ed20(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3645fc98a9ddbe83aa53926f7f7c8e634518f2c97af7ec68b934366e3d3d4e6(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4db41b5d2b0af428972a4e9f72116499c0eecc581aef510b14e1f4f416428977(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7c134ac3f2fb59beced0dce92b78bfc1f797c12d48e6488f9e3c144fa1f703a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__912cd3c621f4eb15824d6d2067d7d3a0544969b8780b8c663df5099ce29c661a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48748e519eea9ea85d698ac8f416d359ab2181ce066b5f34a58f177d2e5bcd32(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__315e7d884e7ee505be7de1fc076a66df982f3ef2ee62a2ea8346b01ad7ae9eb4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__030dbb056efbe20837256ce43acbbf3f0a042338f7eaf584d5da97a966f1ade6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b10d03016237213b406fbea0c0234c896b5432234d76f29390df77058785a79(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52199317422413f9c082734d0a9af04626b6ff66474a6ada6d72c26b41e7d7ab(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, EncryptionAtRestAzureKeyVaultConfig]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8fd0d6cbf8a84a372487ec153ba2f3813d8498010cc8bebed82e6cb3a5bb07f8(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    project_id: builtins.str,
    aws_kms_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[EncryptionAtRestAwsKmsConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
    azure_key_vault_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[EncryptionAtRestAzureKeyVaultConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
    enabled_for_search_nodes: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    google_cloud_kms_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[EncryptionAtRestGoogleCloudKmsConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aedb02119e179d4089eb0d364bb17330a58560982b3605a6181f3239dd678184(
    *,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    key_version_resource_id: typing.Optional[builtins.str] = None,
    role_id: typing.Optional[builtins.str] = None,
    service_account_key: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c97d93bbd78001b479c9ad336596cc63e49acc32a59a817fe4d1abb29d071d59(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ab3d7903196fa94f0d70b20b2cde4124141803b978aa4feac932f79e11e40de(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e17ad80db1bcb411a58bbeda0201e2234e2e3aebe0092a417c792b725555499b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcb580c2ea19a0dac1ef250dfb775a0365d78a6aa71878a0606b2f66c51dda35(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7b5b795373629513a737716bdadc81e055283ec69aaa716c59a492e419e9638(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__589e31b4ad940228cb05726a41d966dab4f3a6afd30c5418474c227a8290852d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[EncryptionAtRestGoogleCloudKmsConfig]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4bfaca90c3f6809a2826ed8c38a1a8a7f49dbd6808ffe0e60b27580a2d2a466d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52eeed5634eae91d25dda8d5f7fe8806b117f3485f1b87f00fbf14b0a0d12ddb(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b348720d95ed8204a70c897eee20442ba668247f32f91cab8899640b9f38dfd6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45cb3b3166b9c9cd5a14ccb75f37284f070dc2222c03c7a1ffe6b296e6abb63b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4346f8a20f517ffa99b4e5995f3f8146c333c2319ef9b7d2338e2109a11b41de(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__685dfa2d5d6e4991e48f4f73402afbfe5534a824ecc445c8046945ff7b7410e8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, EncryptionAtRestGoogleCloudKmsConfig]],
) -> None:
    """Type checking stubs"""
    pass
