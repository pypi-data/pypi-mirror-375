r'''
# `mongodbatlas_stream_privatelink_endpoint`

Refer to the Terraform Registry for docs: [`mongodbatlas_stream_privatelink_endpoint`](https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_privatelink_endpoint).
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


class StreamPrivatelinkEndpoint(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.streamPrivatelinkEndpoint.StreamPrivatelinkEndpoint",
):
    '''Represents a {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_privatelink_endpoint mongodbatlas_stream_privatelink_endpoint}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        project_id: builtins.str,
        provider_name: builtins.str,
        vendor: builtins.str,
        arn: typing.Optional[builtins.str] = None,
        dns_domain: typing.Optional[builtins.str] = None,
        dns_sub_domain: typing.Optional[typing.Sequence[builtins.str]] = None,
        region: typing.Optional[builtins.str] = None,
        service_endpoint_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_privatelink_endpoint mongodbatlas_stream_privatelink_endpoint} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param project_id: Unique 24-hexadecimal digit string that identifies your project. Use the `/groups <#tag/Projects/operation/listProjects>`_ endpoint to retrieve all projects to which the authenticated user has access.**NOTE**: Groups and projects are synonymous terms. Your group id is the same as your project id. For existing groups, your group or project id remains the same. The resource and corresponding endpoints use the term groups. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_privatelink_endpoint#project_id StreamPrivatelinkEndpoint#project_id}
        :param provider_name: Provider where the endpoint is deployed. Valid values are AWS and AZURE. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_privatelink_endpoint#provider_name StreamPrivatelinkEndpoint#provider_name}
        :param vendor: Vendor that manages the endpoint. The following are the vendor values per provider:. - **AWS**: MSK, CONFLUENT, and S3 - **Azure**: EVENTHUB and CONFLUENT Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_privatelink_endpoint#vendor StreamPrivatelinkEndpoint#vendor}
        :param arn: Amazon Resource Name (ARN). Required for AWS Provider and MSK vendor. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_privatelink_endpoint#arn StreamPrivatelinkEndpoint#arn}
        :param dns_domain: The domain hostname. Required for the following provider and vendor combinations: * AWS provider with CONFLUENT vendor. - AZURE provider with EVENTHUB or CONFLUENT vendor. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_privatelink_endpoint#dns_domain StreamPrivatelinkEndpoint#dns_domain}
        :param dns_sub_domain: Sub-Domain name of Confluent cluster. These are typically your availability zones. Required for AWS Provider and CONFLUENT vendor. If your AWS CONFLUENT cluster doesn't use subdomains, you must set this to the empty array []. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_privatelink_endpoint#dns_sub_domain StreamPrivatelinkEndpoint#dns_sub_domain}
        :param region: The region of the Provider’s cluster. See `AZURE <https://www.mongodb.com/docs/atlas/reference/microsoft-azure/#stream-processing-instances>`_ and `AWS <https://www.mongodb.com/docs/atlas/reference/amazon-aws/#stream-processing-instances>`_ supported regions. When the vendor is ``CONFLUENT``, this is the domain name of Confluent cluster. When the vendor is ``MSK``, this is computed by the API from the provided ``arn``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_privatelink_endpoint#region StreamPrivatelinkEndpoint#region}
        :param service_endpoint_id: For AZURE EVENTHUB, this is the `namespace endpoint ID <https://learn.microsoft.com/en-us/rest/api/eventhub/namespaces/get>`_. For AWS CONFLUENT cluster, this is the `VPC Endpoint service name <https://docs.confluent.io/cloud/current/networking/private-links/aws-privatelink.html>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_privatelink_endpoint#service_endpoint_id StreamPrivatelinkEndpoint#service_endpoint_id}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db9574bdec04b91b4228009acfa6bd62b24dfb08c611ed5d5dfe2cc726da4114)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = StreamPrivatelinkEndpointConfig(
            project_id=project_id,
            provider_name=provider_name,
            vendor=vendor,
            arn=arn,
            dns_domain=dns_domain,
            dns_sub_domain=dns_sub_domain,
            region=region,
            service_endpoint_id=service_endpoint_id,
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
        '''Generates CDKTF code for importing a StreamPrivatelinkEndpoint resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the StreamPrivatelinkEndpoint to import.
        :param import_from_id: The id of the existing StreamPrivatelinkEndpoint that should be imported. Refer to the {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_privatelink_endpoint#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the StreamPrivatelinkEndpoint to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b53c05d8ae6ec8cc6c19fd53f5472a7c2006597be05e573a175af10efab393b0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetArn")
    def reset_arn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetArn", []))

    @jsii.member(jsii_name="resetDnsDomain")
    def reset_dns_domain(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDnsDomain", []))

    @jsii.member(jsii_name="resetDnsSubDomain")
    def reset_dns_sub_domain(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDnsSubDomain", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @jsii.member(jsii_name="resetServiceEndpointId")
    def reset_service_endpoint_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceEndpointId", []))

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
    @jsii.member(jsii_name="errorMessage")
    def error_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "errorMessage"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="interfaceEndpointId")
    def interface_endpoint_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "interfaceEndpointId"))

    @builtins.property
    @jsii.member(jsii_name="interfaceEndpointName")
    def interface_endpoint_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "interfaceEndpointName"))

    @builtins.property
    @jsii.member(jsii_name="providerAccountId")
    def provider_account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "providerAccountId"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="arnInput")
    def arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "arnInput"))

    @builtins.property
    @jsii.member(jsii_name="dnsDomainInput")
    def dns_domain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dnsDomainInput"))

    @builtins.property
    @jsii.member(jsii_name="dnsSubDomainInput")
    def dns_sub_domain_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "dnsSubDomainInput"))

    @builtins.property
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="providerNameInput")
    def provider_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "providerNameInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceEndpointIdInput")
    def service_endpoint_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceEndpointIdInput"))

    @builtins.property
    @jsii.member(jsii_name="vendorInput")
    def vendor_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vendorInput"))

    @builtins.property
    @jsii.member(jsii_name="arn")
    def arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "arn"))

    @arn.setter
    def arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44bf223a87a73c5c46ede8b48807c551b49b73fc379a6362a85c581056794e10)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "arn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dnsDomain")
    def dns_domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dnsDomain"))

    @dns_domain.setter
    def dns_domain(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5d2f7536e6a715a484f0b11af7da39408f1c864681cd085f169649a37179930)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dnsDomain", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dnsSubDomain")
    def dns_sub_domain(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dnsSubDomain"))

    @dns_sub_domain.setter
    def dns_sub_domain(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__847cc7af3d64a890d631e76d231d337357acb3d55b839fbcd20dbd5a65a4319b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dnsSubDomain", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ca61a897064be25829ebdedbade055fb7603b1b0411f550def3861330d18e2e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="providerName")
    def provider_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "providerName"))

    @provider_name.setter
    def provider_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__822d8cc3c7526d113b49979b7cfefad1936b49e0a0dfb7c0c4de80d70be9d68c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "providerName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb752c50c41b3a1321775c0a338ee7b43a83b48c654a53c0c1e580fc84f151c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serviceEndpointId")
    def service_endpoint_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceEndpointId"))

    @service_endpoint_id.setter
    def service_endpoint_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a49ab4f782293370e5107bdcf3ed24e8cd2f61072a5bc76f28d154a885a0b73)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceEndpointId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vendor")
    def vendor(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vendor"))

    @vendor.setter
    def vendor(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19d05be4dcf17eea6ef7a834c2b5ea5aa0f2ecbb77cc406ec9c8614cf7d863cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vendor", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.streamPrivatelinkEndpoint.StreamPrivatelinkEndpointConfig",
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
        "provider_name": "providerName",
        "vendor": "vendor",
        "arn": "arn",
        "dns_domain": "dnsDomain",
        "dns_sub_domain": "dnsSubDomain",
        "region": "region",
        "service_endpoint_id": "serviceEndpointId",
    },
)
class StreamPrivatelinkEndpointConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        provider_name: builtins.str,
        vendor: builtins.str,
        arn: typing.Optional[builtins.str] = None,
        dns_domain: typing.Optional[builtins.str] = None,
        dns_sub_domain: typing.Optional[typing.Sequence[builtins.str]] = None,
        region: typing.Optional[builtins.str] = None,
        service_endpoint_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param project_id: Unique 24-hexadecimal digit string that identifies your project. Use the `/groups <#tag/Projects/operation/listProjects>`_ endpoint to retrieve all projects to which the authenticated user has access.**NOTE**: Groups and projects are synonymous terms. Your group id is the same as your project id. For existing groups, your group or project id remains the same. The resource and corresponding endpoints use the term groups. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_privatelink_endpoint#project_id StreamPrivatelinkEndpoint#project_id}
        :param provider_name: Provider where the endpoint is deployed. Valid values are AWS and AZURE. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_privatelink_endpoint#provider_name StreamPrivatelinkEndpoint#provider_name}
        :param vendor: Vendor that manages the endpoint. The following are the vendor values per provider:. - **AWS**: MSK, CONFLUENT, and S3 - **Azure**: EVENTHUB and CONFLUENT Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_privatelink_endpoint#vendor StreamPrivatelinkEndpoint#vendor}
        :param arn: Amazon Resource Name (ARN). Required for AWS Provider and MSK vendor. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_privatelink_endpoint#arn StreamPrivatelinkEndpoint#arn}
        :param dns_domain: The domain hostname. Required for the following provider and vendor combinations: * AWS provider with CONFLUENT vendor. - AZURE provider with EVENTHUB or CONFLUENT vendor. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_privatelink_endpoint#dns_domain StreamPrivatelinkEndpoint#dns_domain}
        :param dns_sub_domain: Sub-Domain name of Confluent cluster. These are typically your availability zones. Required for AWS Provider and CONFLUENT vendor. If your AWS CONFLUENT cluster doesn't use subdomains, you must set this to the empty array []. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_privatelink_endpoint#dns_sub_domain StreamPrivatelinkEndpoint#dns_sub_domain}
        :param region: The region of the Provider’s cluster. See `AZURE <https://www.mongodb.com/docs/atlas/reference/microsoft-azure/#stream-processing-instances>`_ and `AWS <https://www.mongodb.com/docs/atlas/reference/amazon-aws/#stream-processing-instances>`_ supported regions. When the vendor is ``CONFLUENT``, this is the domain name of Confluent cluster. When the vendor is ``MSK``, this is computed by the API from the provided ``arn``. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_privatelink_endpoint#region StreamPrivatelinkEndpoint#region}
        :param service_endpoint_id: For AZURE EVENTHUB, this is the `namespace endpoint ID <https://learn.microsoft.com/en-us/rest/api/eventhub/namespaces/get>`_. For AWS CONFLUENT cluster, this is the `VPC Endpoint service name <https://docs.confluent.io/cloud/current/networking/private-links/aws-privatelink.html>`_. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_privatelink_endpoint#service_endpoint_id StreamPrivatelinkEndpoint#service_endpoint_id}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd1357d7a8f0093cb26a4273bab16f4bd3c3dd812dfad7530728ed4b2d944c78)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument provider_name", value=provider_name, expected_type=type_hints["provider_name"])
            check_type(argname="argument vendor", value=vendor, expected_type=type_hints["vendor"])
            check_type(argname="argument arn", value=arn, expected_type=type_hints["arn"])
            check_type(argname="argument dns_domain", value=dns_domain, expected_type=type_hints["dns_domain"])
            check_type(argname="argument dns_sub_domain", value=dns_sub_domain, expected_type=type_hints["dns_sub_domain"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument service_endpoint_id", value=service_endpoint_id, expected_type=type_hints["service_endpoint_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "project_id": project_id,
            "provider_name": provider_name,
            "vendor": vendor,
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
        if arn is not None:
            self._values["arn"] = arn
        if dns_domain is not None:
            self._values["dns_domain"] = dns_domain
        if dns_sub_domain is not None:
            self._values["dns_sub_domain"] = dns_sub_domain
        if region is not None:
            self._values["region"] = region
        if service_endpoint_id is not None:
            self._values["service_endpoint_id"] = service_endpoint_id

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

        Use the `/groups <#tag/Projects/operation/listProjects>`_ endpoint to retrieve all projects to which the authenticated user has access.**NOTE**: Groups and projects are synonymous terms. Your group id is the same as your project id. For existing groups, your group or project id remains the same. The resource and corresponding endpoints use the term groups.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_privatelink_endpoint#project_id StreamPrivatelinkEndpoint#project_id}
        '''
        result = self._values.get("project_id")
        assert result is not None, "Required property 'project_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def provider_name(self) -> builtins.str:
        '''Provider where the endpoint is deployed. Valid values are AWS and AZURE.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_privatelink_endpoint#provider_name StreamPrivatelinkEndpoint#provider_name}
        '''
        result = self._values.get("provider_name")
        assert result is not None, "Required property 'provider_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vendor(self) -> builtins.str:
        '''Vendor that manages the endpoint. The following are the vendor values per provider:.

        - **AWS**: MSK, CONFLUENT, and S3

          - **Azure**: EVENTHUB and CONFLUENT

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_privatelink_endpoint#vendor StreamPrivatelinkEndpoint#vendor}
        '''
        result = self._values.get("vendor")
        assert result is not None, "Required property 'vendor' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def arn(self) -> typing.Optional[builtins.str]:
        '''Amazon Resource Name (ARN). Required for AWS Provider and MSK vendor.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_privatelink_endpoint#arn StreamPrivatelinkEndpoint#arn}
        '''
        result = self._values.get("arn")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dns_domain(self) -> typing.Optional[builtins.str]:
        '''The domain hostname. Required for the following provider and vendor combinations: 				 	* AWS provider with CONFLUENT vendor.

        - AZURE provider with EVENTHUB or CONFLUENT vendor.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_privatelink_endpoint#dns_domain StreamPrivatelinkEndpoint#dns_domain}
        '''
        result = self._values.get("dns_domain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def dns_sub_domain(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Sub-Domain name of Confluent cluster.

        These are typically your availability zones. Required for AWS Provider and CONFLUENT vendor. If your AWS CONFLUENT cluster doesn't use subdomains, you must set this to the empty array [].

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_privatelink_endpoint#dns_sub_domain StreamPrivatelinkEndpoint#dns_sub_domain}
        '''
        result = self._values.get("dns_sub_domain")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''The region of the Provider’s cluster.

        See `AZURE <https://www.mongodb.com/docs/atlas/reference/microsoft-azure/#stream-processing-instances>`_ and `AWS <https://www.mongodb.com/docs/atlas/reference/amazon-aws/#stream-processing-instances>`_ supported regions. When the vendor is ``CONFLUENT``, this is the domain name of Confluent cluster. When the vendor is ``MSK``, this is computed by the API from the provided ``arn``.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_privatelink_endpoint#region StreamPrivatelinkEndpoint#region}
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def service_endpoint_id(self) -> typing.Optional[builtins.str]:
        '''For AZURE EVENTHUB, this is the `namespace endpoint ID <https://learn.microsoft.com/en-us/rest/api/eventhub/namespaces/get>`_. For AWS CONFLUENT cluster, this is the `VPC Endpoint service name <https://docs.confluent.io/cloud/current/networking/private-links/aws-privatelink.html>`_.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_privatelink_endpoint#service_endpoint_id StreamPrivatelinkEndpoint#service_endpoint_id}
        '''
        result = self._values.get("service_endpoint_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StreamPrivatelinkEndpointConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "StreamPrivatelinkEndpoint",
    "StreamPrivatelinkEndpointConfig",
]

publication.publish()

def _typecheckingstub__db9574bdec04b91b4228009acfa6bd62b24dfb08c611ed5d5dfe2cc726da4114(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    project_id: builtins.str,
    provider_name: builtins.str,
    vendor: builtins.str,
    arn: typing.Optional[builtins.str] = None,
    dns_domain: typing.Optional[builtins.str] = None,
    dns_sub_domain: typing.Optional[typing.Sequence[builtins.str]] = None,
    region: typing.Optional[builtins.str] = None,
    service_endpoint_id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__b53c05d8ae6ec8cc6c19fd53f5472a7c2006597be05e573a175af10efab393b0(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44bf223a87a73c5c46ede8b48807c551b49b73fc379a6362a85c581056794e10(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5d2f7536e6a715a484f0b11af7da39408f1c864681cd085f169649a37179930(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__847cc7af3d64a890d631e76d231d337357acb3d55b839fbcd20dbd5a65a4319b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ca61a897064be25829ebdedbade055fb7603b1b0411f550def3861330d18e2e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__822d8cc3c7526d113b49979b7cfefad1936b49e0a0dfb7c0c4de80d70be9d68c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb752c50c41b3a1321775c0a338ee7b43a83b48c654a53c0c1e580fc84f151c4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a49ab4f782293370e5107bdcf3ed24e8cd2f61072a5bc76f28d154a885a0b73(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19d05be4dcf17eea6ef7a834c2b5ea5aa0f2ecbb77cc406ec9c8614cf7d863cc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd1357d7a8f0093cb26a4273bab16f4bd3c3dd812dfad7530728ed4b2d944c78(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    project_id: builtins.str,
    provider_name: builtins.str,
    vendor: builtins.str,
    arn: typing.Optional[builtins.str] = None,
    dns_domain: typing.Optional[builtins.str] = None,
    dns_sub_domain: typing.Optional[typing.Sequence[builtins.str]] = None,
    region: typing.Optional[builtins.str] = None,
    service_endpoint_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
