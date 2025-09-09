r'''
# `mongodbatlas_cloud_provider_access_authorization`

Refer to the Terraform Registry for docs: [`mongodbatlas_cloud_provider_access_authorization`](https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_provider_access_authorization).
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


class CloudProviderAccessAuthorization(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cloudProviderAccessAuthorization.CloudProviderAccessAuthorization",
):
    '''Represents a {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_provider_access_authorization mongodbatlas_cloud_provider_access_authorization}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        project_id: builtins.str,
        role_id: builtins.str,
        aws: typing.Optional[typing.Union["CloudProviderAccessAuthorizationAws", typing.Dict[builtins.str, typing.Any]]] = None,
        azure: typing.Optional[typing.Union["CloudProviderAccessAuthorizationAzure", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_provider_access_authorization mongodbatlas_cloud_provider_access_authorization} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_provider_access_authorization#project_id CloudProviderAccessAuthorization#project_id}.
        :param role_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_provider_access_authorization#role_id CloudProviderAccessAuthorization#role_id}.
        :param aws: aws block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_provider_access_authorization#aws CloudProviderAccessAuthorization#aws}
        :param azure: azure block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_provider_access_authorization#azure CloudProviderAccessAuthorization#azure}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_provider_access_authorization#id CloudProviderAccessAuthorization#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d2f428ff1c66e4cc35d759236213f1f5b4593047ca6adc46c541fa2ec5ef6f9)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = CloudProviderAccessAuthorizationConfig(
            project_id=project_id,
            role_id=role_id,
            aws=aws,
            azure=azure,
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
        '''Generates CDKTF code for importing a CloudProviderAccessAuthorization resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the CloudProviderAccessAuthorization to import.
        :param import_from_id: The id of the existing CloudProviderAccessAuthorization that should be imported. Refer to the {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_provider_access_authorization#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the CloudProviderAccessAuthorization to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8ff746530fb7b2c4cd88b8ba97b96cf390f47820dbc3ec66f297250335ca4ef)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putAws")
    def put_aws(self, *, iam_assumed_role_arn: builtins.str) -> None:
        '''
        :param iam_assumed_role_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_provider_access_authorization#iam_assumed_role_arn CloudProviderAccessAuthorization#iam_assumed_role_arn}.
        '''
        value = CloudProviderAccessAuthorizationAws(
            iam_assumed_role_arn=iam_assumed_role_arn
        )

        return typing.cast(None, jsii.invoke(self, "putAws", [value]))

    @jsii.member(jsii_name="putAzure")
    def put_azure(
        self,
        *,
        atlas_azure_app_id: builtins.str,
        service_principal_id: builtins.str,
        tenant_id: builtins.str,
    ) -> None:
        '''
        :param atlas_azure_app_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_provider_access_authorization#atlas_azure_app_id CloudProviderAccessAuthorization#atlas_azure_app_id}.
        :param service_principal_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_provider_access_authorization#service_principal_id CloudProviderAccessAuthorization#service_principal_id}.
        :param tenant_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_provider_access_authorization#tenant_id CloudProviderAccessAuthorization#tenant_id}.
        '''
        value = CloudProviderAccessAuthorizationAzure(
            atlas_azure_app_id=atlas_azure_app_id,
            service_principal_id=service_principal_id,
            tenant_id=tenant_id,
        )

        return typing.cast(None, jsii.invoke(self, "putAzure", [value]))

    @jsii.member(jsii_name="resetAws")
    def reset_aws(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAws", []))

    @jsii.member(jsii_name="resetAzure")
    def reset_azure(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzure", []))

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
    @jsii.member(jsii_name="authorizedDate")
    def authorized_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authorizedDate"))

    @builtins.property
    @jsii.member(jsii_name="aws")
    def aws(self) -> "CloudProviderAccessAuthorizationAwsOutputReference":
        return typing.cast("CloudProviderAccessAuthorizationAwsOutputReference", jsii.get(self, "aws"))

    @builtins.property
    @jsii.member(jsii_name="azure")
    def azure(self) -> "CloudProviderAccessAuthorizationAzureOutputReference":
        return typing.cast("CloudProviderAccessAuthorizationAzureOutputReference", jsii.get(self, "azure"))

    @builtins.property
    @jsii.member(jsii_name="featureUsages")
    def feature_usages(self) -> "CloudProviderAccessAuthorizationFeatureUsagesList":
        return typing.cast("CloudProviderAccessAuthorizationFeatureUsagesList", jsii.get(self, "featureUsages"))

    @builtins.property
    @jsii.member(jsii_name="gcp")
    def gcp(self) -> "CloudProviderAccessAuthorizationGcpList":
        return typing.cast("CloudProviderAccessAuthorizationGcpList", jsii.get(self, "gcp"))

    @builtins.property
    @jsii.member(jsii_name="awsInput")
    def aws_input(self) -> typing.Optional["CloudProviderAccessAuthorizationAws"]:
        return typing.cast(typing.Optional["CloudProviderAccessAuthorizationAws"], jsii.get(self, "awsInput"))

    @builtins.property
    @jsii.member(jsii_name="azureInput")
    def azure_input(self) -> typing.Optional["CloudProviderAccessAuthorizationAzure"]:
        return typing.cast(typing.Optional["CloudProviderAccessAuthorizationAzure"], jsii.get(self, "azureInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="roleIdInput")
    def role_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleIdInput"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67afc969768d3c2695c07698ec6a3c2c31fb9ae15ba94b239d979413d0a0ff42)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0132e54649d25dcabb05914a20364cfd07ee0b600ec21ec45fee995e441afde)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="roleId")
    def role_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleId"))

    @role_id.setter
    def role_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4501314b9d4bba71369fc586e38c4bf859b4a69b33dc6f0e55af9e70975118de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "roleId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.cloudProviderAccessAuthorization.CloudProviderAccessAuthorizationAws",
    jsii_struct_bases=[],
    name_mapping={"iam_assumed_role_arn": "iamAssumedRoleArn"},
)
class CloudProviderAccessAuthorizationAws:
    def __init__(self, *, iam_assumed_role_arn: builtins.str) -> None:
        '''
        :param iam_assumed_role_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_provider_access_authorization#iam_assumed_role_arn CloudProviderAccessAuthorization#iam_assumed_role_arn}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b428bfab4d01d5ff828aab268e8d5449a8219df76c1f9427c6652825dc626fe)
            check_type(argname="argument iam_assumed_role_arn", value=iam_assumed_role_arn, expected_type=type_hints["iam_assumed_role_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "iam_assumed_role_arn": iam_assumed_role_arn,
        }

    @builtins.property
    def iam_assumed_role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_provider_access_authorization#iam_assumed_role_arn CloudProviderAccessAuthorization#iam_assumed_role_arn}.'''
        result = self._values.get("iam_assumed_role_arn")
        assert result is not None, "Required property 'iam_assumed_role_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudProviderAccessAuthorizationAws(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudProviderAccessAuthorizationAwsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cloudProviderAccessAuthorization.CloudProviderAccessAuthorizationAwsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c1d1101b412da5f59d42ac17b6db7f433c0c61f96b6e44157c40bb89c7785af7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="iamAssumedRoleArnInput")
    def iam_assumed_role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "iamAssumedRoleArnInput"))

    @builtins.property
    @jsii.member(jsii_name="iamAssumedRoleArn")
    def iam_assumed_role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "iamAssumedRoleArn"))

    @iam_assumed_role_arn.setter
    def iam_assumed_role_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07b4593496df910618416861c8eb2e261f467103f7efdcfa7f61ea6013930175)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "iamAssumedRoleArn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CloudProviderAccessAuthorizationAws]:
        return typing.cast(typing.Optional[CloudProviderAccessAuthorizationAws], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudProviderAccessAuthorizationAws],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__570ff0c94846f42ed2e851dcd1efc82fe36bfe408e25ec211a0f4181b5e164e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.cloudProviderAccessAuthorization.CloudProviderAccessAuthorizationAzure",
    jsii_struct_bases=[],
    name_mapping={
        "atlas_azure_app_id": "atlasAzureAppId",
        "service_principal_id": "servicePrincipalId",
        "tenant_id": "tenantId",
    },
)
class CloudProviderAccessAuthorizationAzure:
    def __init__(
        self,
        *,
        atlas_azure_app_id: builtins.str,
        service_principal_id: builtins.str,
        tenant_id: builtins.str,
    ) -> None:
        '''
        :param atlas_azure_app_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_provider_access_authorization#atlas_azure_app_id CloudProviderAccessAuthorization#atlas_azure_app_id}.
        :param service_principal_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_provider_access_authorization#service_principal_id CloudProviderAccessAuthorization#service_principal_id}.
        :param tenant_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_provider_access_authorization#tenant_id CloudProviderAccessAuthorization#tenant_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__529fa85d9fc79c07f4d8f0791288952d42722de72fb3beb62995f2f63d8eb77f)
            check_type(argname="argument atlas_azure_app_id", value=atlas_azure_app_id, expected_type=type_hints["atlas_azure_app_id"])
            check_type(argname="argument service_principal_id", value=service_principal_id, expected_type=type_hints["service_principal_id"])
            check_type(argname="argument tenant_id", value=tenant_id, expected_type=type_hints["tenant_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "atlas_azure_app_id": atlas_azure_app_id,
            "service_principal_id": service_principal_id,
            "tenant_id": tenant_id,
        }

    @builtins.property
    def atlas_azure_app_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_provider_access_authorization#atlas_azure_app_id CloudProviderAccessAuthorization#atlas_azure_app_id}.'''
        result = self._values.get("atlas_azure_app_id")
        assert result is not None, "Required property 'atlas_azure_app_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def service_principal_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_provider_access_authorization#service_principal_id CloudProviderAccessAuthorization#service_principal_id}.'''
        result = self._values.get("service_principal_id")
        assert result is not None, "Required property 'service_principal_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tenant_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_provider_access_authorization#tenant_id CloudProviderAccessAuthorization#tenant_id}.'''
        result = self._values.get("tenant_id")
        assert result is not None, "Required property 'tenant_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudProviderAccessAuthorizationAzure(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudProviderAccessAuthorizationAzureOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cloudProviderAccessAuthorization.CloudProviderAccessAuthorizationAzureOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1d3b0c838a03c01e23b10fa397c7175fb8c8cb9502d8b1d14215f834da28f42d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="atlasAzureAppIdInput")
    def atlas_azure_app_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "atlasAzureAppIdInput"))

    @builtins.property
    @jsii.member(jsii_name="servicePrincipalIdInput")
    def service_principal_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "servicePrincipalIdInput"))

    @builtins.property
    @jsii.member(jsii_name="tenantIdInput")
    def tenant_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tenantIdInput"))

    @builtins.property
    @jsii.member(jsii_name="atlasAzureAppId")
    def atlas_azure_app_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "atlasAzureAppId"))

    @atlas_azure_app_id.setter
    def atlas_azure_app_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7bd2d0549412bcfc6d712637dfda51579a3fcca1bbb929f1a1beb52e57bb7f22)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "atlasAzureAppId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="servicePrincipalId")
    def service_principal_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "servicePrincipalId"))

    @service_principal_id.setter
    def service_principal_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10ca05b76ab8764d09cf84c769ec714f2e32e4790c43748a442b7479a4eeec32)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "servicePrincipalId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tenantId")
    def tenant_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tenantId"))

    @tenant_id.setter
    def tenant_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bca0b169847de3546e0f76674342b9105e43683b977b6293e9c02e6a7e0bdd10)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tenantId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CloudProviderAccessAuthorizationAzure]:
        return typing.cast(typing.Optional[CloudProviderAccessAuthorizationAzure], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudProviderAccessAuthorizationAzure],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d62d4d34355c76d82f1a3a0d22ada5ec865ad9fb7f8fa4236a30f69ec3cda7e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.cloudProviderAccessAuthorization.CloudProviderAccessAuthorizationConfig",
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
        "role_id": "roleId",
        "aws": "aws",
        "azure": "azure",
        "id": "id",
    },
)
class CloudProviderAccessAuthorizationConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        role_id: builtins.str,
        aws: typing.Optional[typing.Union[CloudProviderAccessAuthorizationAws, typing.Dict[builtins.str, typing.Any]]] = None,
        azure: typing.Optional[typing.Union[CloudProviderAccessAuthorizationAzure, typing.Dict[builtins.str, typing.Any]]] = None,
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
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_provider_access_authorization#project_id CloudProviderAccessAuthorization#project_id}.
        :param role_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_provider_access_authorization#role_id CloudProviderAccessAuthorization#role_id}.
        :param aws: aws block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_provider_access_authorization#aws CloudProviderAccessAuthorization#aws}
        :param azure: azure block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_provider_access_authorization#azure CloudProviderAccessAuthorization#azure}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_provider_access_authorization#id CloudProviderAccessAuthorization#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(aws, dict):
            aws = CloudProviderAccessAuthorizationAws(**aws)
        if isinstance(azure, dict):
            azure = CloudProviderAccessAuthorizationAzure(**azure)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__641672c0e373abe0939410edd23ffd3173c77e8ee53c193e3341686b487fb910)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument role_id", value=role_id, expected_type=type_hints["role_id"])
            check_type(argname="argument aws", value=aws, expected_type=type_hints["aws"])
            check_type(argname="argument azure", value=azure, expected_type=type_hints["azure"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "project_id": project_id,
            "role_id": role_id,
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
        if aws is not None:
            self._values["aws"] = aws
        if azure is not None:
            self._values["azure"] = azure
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
    def project_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_provider_access_authorization#project_id CloudProviderAccessAuthorization#project_id}.'''
        result = self._values.get("project_id")
        assert result is not None, "Required property 'project_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def role_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_provider_access_authorization#role_id CloudProviderAccessAuthorization#role_id}.'''
        result = self._values.get("role_id")
        assert result is not None, "Required property 'role_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def aws(self) -> typing.Optional[CloudProviderAccessAuthorizationAws]:
        '''aws block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_provider_access_authorization#aws CloudProviderAccessAuthorization#aws}
        '''
        result = self._values.get("aws")
        return typing.cast(typing.Optional[CloudProviderAccessAuthorizationAws], result)

    @builtins.property
    def azure(self) -> typing.Optional[CloudProviderAccessAuthorizationAzure]:
        '''azure block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_provider_access_authorization#azure CloudProviderAccessAuthorization#azure}
        '''
        result = self._values.get("azure")
        return typing.cast(typing.Optional[CloudProviderAccessAuthorizationAzure], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_provider_access_authorization#id CloudProviderAccessAuthorization#id}.

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
        return "CloudProviderAccessAuthorizationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.cloudProviderAccessAuthorization.CloudProviderAccessAuthorizationFeatureUsages",
    jsii_struct_bases=[],
    name_mapping={},
)
class CloudProviderAccessAuthorizationFeatureUsages:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudProviderAccessAuthorizationFeatureUsages(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudProviderAccessAuthorizationFeatureUsagesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cloudProviderAccessAuthorization.CloudProviderAccessAuthorizationFeatureUsagesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b5c47da0319e8241341350bad0fd14d341a0af866e711936e873bb16104ebaeb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "CloudProviderAccessAuthorizationFeatureUsagesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43df5383409215f38c893a3a71bd9077bb28fc2c4f3f134e44ce08ff3d7bf783)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("CloudProviderAccessAuthorizationFeatureUsagesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__726bd7f8ad7b37f6c1567434e56aee303a8b50802c7a271e8ee1afa3ebb7fd35)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9a828e350dd7958889781816eb2d8f846fd4a58290f59ffbcec7e33bc36b831f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1306441902123255fcae36cce2e3acfcf5475bb9af40972db962a20433f67204)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class CloudProviderAccessAuthorizationFeatureUsagesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cloudProviderAccessAuthorization.CloudProviderAccessAuthorizationFeatureUsagesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7748e34e14945b344d60c8196f1b55c98a8e1f95e642a8b0038908ac733f3855)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="featureId")
    def feature_id(self) -> _cdktf_9a9027ec.StringMap:
        return typing.cast(_cdktf_9a9027ec.StringMap, jsii.get(self, "featureId"))

    @builtins.property
    @jsii.member(jsii_name="featureType")
    def feature_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "featureType"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[CloudProviderAccessAuthorizationFeatureUsages]:
        return typing.cast(typing.Optional[CloudProviderAccessAuthorizationFeatureUsages], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudProviderAccessAuthorizationFeatureUsages],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6882749adcc5ef9c30722cab100dd47e73756fa71a0bafdf752a1ed54d624d73)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.cloudProviderAccessAuthorization.CloudProviderAccessAuthorizationGcp",
    jsii_struct_bases=[],
    name_mapping={},
)
class CloudProviderAccessAuthorizationGcp:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudProviderAccessAuthorizationGcp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudProviderAccessAuthorizationGcpList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cloudProviderAccessAuthorization.CloudProviderAccessAuthorizationGcpList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1a11b35f1fc6e0fc7fb5ef69be78008f1932335c46089f21d8e96d4f8a5039ed)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "CloudProviderAccessAuthorizationGcpOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba0681a102586d4d81d66e29f3868844523e6cb28e9efe32b2b41793677a0158)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("CloudProviderAccessAuthorizationGcpOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db5e1861bb516e4968fa214c25b680f76d1b1fd7fb64c27df5bbadd661157769)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8f23263fa4a42acdb30d6f5a3b5c986422bfa798d1f014008b809cbfed14e818)
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
            type_hints = typing.get_type_hints(_typecheckingstub__639af10747869300bf540312f1df1ecc85b2a2e6b9c20e4e8a9725612d3475e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class CloudProviderAccessAuthorizationGcpOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cloudProviderAccessAuthorization.CloudProviderAccessAuthorizationGcpOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__64304ee474eca27eecc408605eaa0ce44f40dc76c2e85e9e1b65c82caf13af33)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="serviceAccountForAtlas")
    def service_account_for_atlas(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceAccountForAtlas"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CloudProviderAccessAuthorizationGcp]:
        return typing.cast(typing.Optional[CloudProviderAccessAuthorizationGcp], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudProviderAccessAuthorizationGcp],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d82c1df017a6e79c941b0a8b726d9b38ec9ac65fb3dc3b5aa69b94508fa818e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "CloudProviderAccessAuthorization",
    "CloudProviderAccessAuthorizationAws",
    "CloudProviderAccessAuthorizationAwsOutputReference",
    "CloudProviderAccessAuthorizationAzure",
    "CloudProviderAccessAuthorizationAzureOutputReference",
    "CloudProviderAccessAuthorizationConfig",
    "CloudProviderAccessAuthorizationFeatureUsages",
    "CloudProviderAccessAuthorizationFeatureUsagesList",
    "CloudProviderAccessAuthorizationFeatureUsagesOutputReference",
    "CloudProviderAccessAuthorizationGcp",
    "CloudProviderAccessAuthorizationGcpList",
    "CloudProviderAccessAuthorizationGcpOutputReference",
]

publication.publish()

def _typecheckingstub__1d2f428ff1c66e4cc35d759236213f1f5b4593047ca6adc46c541fa2ec5ef6f9(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    project_id: builtins.str,
    role_id: builtins.str,
    aws: typing.Optional[typing.Union[CloudProviderAccessAuthorizationAws, typing.Dict[builtins.str, typing.Any]]] = None,
    azure: typing.Optional[typing.Union[CloudProviderAccessAuthorizationAzure, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__a8ff746530fb7b2c4cd88b8ba97b96cf390f47820dbc3ec66f297250335ca4ef(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67afc969768d3c2695c07698ec6a3c2c31fb9ae15ba94b239d979413d0a0ff42(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0132e54649d25dcabb05914a20364cfd07ee0b600ec21ec45fee995e441afde(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4501314b9d4bba71369fc586e38c4bf859b4a69b33dc6f0e55af9e70975118de(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b428bfab4d01d5ff828aab268e8d5449a8219df76c1f9427c6652825dc626fe(
    *,
    iam_assumed_role_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1d1101b412da5f59d42ac17b6db7f433c0c61f96b6e44157c40bb89c7785af7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07b4593496df910618416861c8eb2e261f467103f7efdcfa7f61ea6013930175(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__570ff0c94846f42ed2e851dcd1efc82fe36bfe408e25ec211a0f4181b5e164e1(
    value: typing.Optional[CloudProviderAccessAuthorizationAws],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__529fa85d9fc79c07f4d8f0791288952d42722de72fb3beb62995f2f63d8eb77f(
    *,
    atlas_azure_app_id: builtins.str,
    service_principal_id: builtins.str,
    tenant_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d3b0c838a03c01e23b10fa397c7175fb8c8cb9502d8b1d14215f834da28f42d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7bd2d0549412bcfc6d712637dfda51579a3fcca1bbb929f1a1beb52e57bb7f22(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10ca05b76ab8764d09cf84c769ec714f2e32e4790c43748a442b7479a4eeec32(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bca0b169847de3546e0f76674342b9105e43683b977b6293e9c02e6a7e0bdd10(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d62d4d34355c76d82f1a3a0d22ada5ec865ad9fb7f8fa4236a30f69ec3cda7e(
    value: typing.Optional[CloudProviderAccessAuthorizationAzure],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__641672c0e373abe0939410edd23ffd3173c77e8ee53c193e3341686b487fb910(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    project_id: builtins.str,
    role_id: builtins.str,
    aws: typing.Optional[typing.Union[CloudProviderAccessAuthorizationAws, typing.Dict[builtins.str, typing.Any]]] = None,
    azure: typing.Optional[typing.Union[CloudProviderAccessAuthorizationAzure, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b5c47da0319e8241341350bad0fd14d341a0af866e711936e873bb16104ebaeb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43df5383409215f38c893a3a71bd9077bb28fc2c4f3f134e44ce08ff3d7bf783(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__726bd7f8ad7b37f6c1567434e56aee303a8b50802c7a271e8ee1afa3ebb7fd35(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a828e350dd7958889781816eb2d8f846fd4a58290f59ffbcec7e33bc36b831f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1306441902123255fcae36cce2e3acfcf5475bb9af40972db962a20433f67204(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7748e34e14945b344d60c8196f1b55c98a8e1f95e642a8b0038908ac733f3855(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6882749adcc5ef9c30722cab100dd47e73756fa71a0bafdf752a1ed54d624d73(
    value: typing.Optional[CloudProviderAccessAuthorizationFeatureUsages],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a11b35f1fc6e0fc7fb5ef69be78008f1932335c46089f21d8e96d4f8a5039ed(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba0681a102586d4d81d66e29f3868844523e6cb28e9efe32b2b41793677a0158(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db5e1861bb516e4968fa214c25b680f76d1b1fd7fb64c27df5bbadd661157769(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f23263fa4a42acdb30d6f5a3b5c986422bfa798d1f014008b809cbfed14e818(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__639af10747869300bf540312f1df1ecc85b2a2e6b9c20e4e8a9725612d3475e0(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64304ee474eca27eecc408605eaa0ce44f40dc76c2e85e9e1b65c82caf13af33(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d82c1df017a6e79c941b0a8b726d9b38ec9ac65fb3dc3b5aa69b94508fa818e8(
    value: typing.Optional[CloudProviderAccessAuthorizationGcp],
) -> None:
    """Type checking stubs"""
    pass
