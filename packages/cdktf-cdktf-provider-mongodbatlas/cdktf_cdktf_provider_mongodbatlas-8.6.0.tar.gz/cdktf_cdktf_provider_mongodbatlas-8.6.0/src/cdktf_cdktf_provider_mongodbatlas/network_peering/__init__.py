r'''
# `mongodbatlas_network_peering`

Refer to the Terraform Registry for docs: [`mongodbatlas_network_peering`](https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering).
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


class NetworkPeering(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.networkPeering.NetworkPeering",
):
    '''Represents a {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering mongodbatlas_network_peering}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        container_id: builtins.str,
        project_id: builtins.str,
        provider_name: builtins.str,
        accepter_region_name: typing.Optional[builtins.str] = None,
        atlas_cidr_block: typing.Optional[builtins.str] = None,
        atlas_gcp_project_id: typing.Optional[builtins.str] = None,
        atlas_vpc_name: typing.Optional[builtins.str] = None,
        aws_account_id: typing.Optional[builtins.str] = None,
        azure_directory_id: typing.Optional[builtins.str] = None,
        azure_subscription_id: typing.Optional[builtins.str] = None,
        gcp_project_id: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        network_name: typing.Optional[builtins.str] = None,
        resource_group_name: typing.Optional[builtins.str] = None,
        route_table_cidr_block: typing.Optional[builtins.str] = None,
        vnet_name: typing.Optional[builtins.str] = None,
        vpc_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering mongodbatlas_network_peering} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param container_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#container_id NetworkPeering#container_id}.
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#project_id NetworkPeering#project_id}.
        :param provider_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#provider_name NetworkPeering#provider_name}.
        :param accepter_region_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#accepter_region_name NetworkPeering#accepter_region_name}.
        :param atlas_cidr_block: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#atlas_cidr_block NetworkPeering#atlas_cidr_block}.
        :param atlas_gcp_project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#atlas_gcp_project_id NetworkPeering#atlas_gcp_project_id}.
        :param atlas_vpc_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#atlas_vpc_name NetworkPeering#atlas_vpc_name}.
        :param aws_account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#aws_account_id NetworkPeering#aws_account_id}.
        :param azure_directory_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#azure_directory_id NetworkPeering#azure_directory_id}.
        :param azure_subscription_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#azure_subscription_id NetworkPeering#azure_subscription_id}.
        :param gcp_project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#gcp_project_id NetworkPeering#gcp_project_id}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#id NetworkPeering#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param network_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#network_name NetworkPeering#network_name}.
        :param resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#resource_group_name NetworkPeering#resource_group_name}.
        :param route_table_cidr_block: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#route_table_cidr_block NetworkPeering#route_table_cidr_block}.
        :param vnet_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#vnet_name NetworkPeering#vnet_name}.
        :param vpc_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#vpc_id NetworkPeering#vpc_id}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__971ccb4fc9d210efd4be0df9263bd9aa0194866eb45a100a1ce3240e6c4b31a2)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = NetworkPeeringConfig(
            container_id=container_id,
            project_id=project_id,
            provider_name=provider_name,
            accepter_region_name=accepter_region_name,
            atlas_cidr_block=atlas_cidr_block,
            atlas_gcp_project_id=atlas_gcp_project_id,
            atlas_vpc_name=atlas_vpc_name,
            aws_account_id=aws_account_id,
            azure_directory_id=azure_directory_id,
            azure_subscription_id=azure_subscription_id,
            gcp_project_id=gcp_project_id,
            id=id,
            network_name=network_name,
            resource_group_name=resource_group_name,
            route_table_cidr_block=route_table_cidr_block,
            vnet_name=vnet_name,
            vpc_id=vpc_id,
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
        '''Generates CDKTF code for importing a NetworkPeering resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the NetworkPeering to import.
        :param import_from_id: The id of the existing NetworkPeering that should be imported. Refer to the {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the NetworkPeering to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b5d82d6800f791615616b598b120585699af9be3febb1ee2be3405fbf71b4985)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAccepterRegionName")
    def reset_accepter_region_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAccepterRegionName", []))

    @jsii.member(jsii_name="resetAtlasCidrBlock")
    def reset_atlas_cidr_block(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAtlasCidrBlock", []))

    @jsii.member(jsii_name="resetAtlasGcpProjectId")
    def reset_atlas_gcp_project_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAtlasGcpProjectId", []))

    @jsii.member(jsii_name="resetAtlasVpcName")
    def reset_atlas_vpc_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAtlasVpcName", []))

    @jsii.member(jsii_name="resetAwsAccountId")
    def reset_aws_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsAccountId", []))

    @jsii.member(jsii_name="resetAzureDirectoryId")
    def reset_azure_directory_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureDirectoryId", []))

    @jsii.member(jsii_name="resetAzureSubscriptionId")
    def reset_azure_subscription_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAzureSubscriptionId", []))

    @jsii.member(jsii_name="resetGcpProjectId")
    def reset_gcp_project_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGcpProjectId", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetNetworkName")
    def reset_network_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkName", []))

    @jsii.member(jsii_name="resetResourceGroupName")
    def reset_resource_group_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResourceGroupName", []))

    @jsii.member(jsii_name="resetRouteTableCidrBlock")
    def reset_route_table_cidr_block(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRouteTableCidrBlock", []))

    @jsii.member(jsii_name="resetVnetName")
    def reset_vnet_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVnetName", []))

    @jsii.member(jsii_name="resetVpcId")
    def reset_vpc_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVpcId", []))

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
    @jsii.member(jsii_name="atlasId")
    def atlas_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "atlasId"))

    @builtins.property
    @jsii.member(jsii_name="connectionId")
    def connection_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connectionId"))

    @builtins.property
    @jsii.member(jsii_name="errorMessage")
    def error_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "errorMessage"))

    @builtins.property
    @jsii.member(jsii_name="errorState")
    def error_state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "errorState"))

    @builtins.property
    @jsii.member(jsii_name="errorStateName")
    def error_state_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "errorStateName"))

    @builtins.property
    @jsii.member(jsii_name="peerId")
    def peer_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "peerId"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property
    @jsii.member(jsii_name="statusName")
    def status_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "statusName"))

    @builtins.property
    @jsii.member(jsii_name="accepterRegionNameInput")
    def accepter_region_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accepterRegionNameInput"))

    @builtins.property
    @jsii.member(jsii_name="atlasCidrBlockInput")
    def atlas_cidr_block_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "atlasCidrBlockInput"))

    @builtins.property
    @jsii.member(jsii_name="atlasGcpProjectIdInput")
    def atlas_gcp_project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "atlasGcpProjectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="atlasVpcNameInput")
    def atlas_vpc_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "atlasVpcNameInput"))

    @builtins.property
    @jsii.member(jsii_name="awsAccountIdInput")
    def aws_account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "awsAccountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="azureDirectoryIdInput")
    def azure_directory_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "azureDirectoryIdInput"))

    @builtins.property
    @jsii.member(jsii_name="azureSubscriptionIdInput")
    def azure_subscription_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "azureSubscriptionIdInput"))

    @builtins.property
    @jsii.member(jsii_name="containerIdInput")
    def container_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "containerIdInput"))

    @builtins.property
    @jsii.member(jsii_name="gcpProjectIdInput")
    def gcp_project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "gcpProjectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="networkNameInput")
    def network_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkNameInput"))

    @builtins.property
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="providerNameInput")
    def provider_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "providerNameInput"))

    @builtins.property
    @jsii.member(jsii_name="resourceGroupNameInput")
    def resource_group_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "resourceGroupNameInput"))

    @builtins.property
    @jsii.member(jsii_name="routeTableCidrBlockInput")
    def route_table_cidr_block_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "routeTableCidrBlockInput"))

    @builtins.property
    @jsii.member(jsii_name="vnetNameInput")
    def vnet_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vnetNameInput"))

    @builtins.property
    @jsii.member(jsii_name="vpcIdInput")
    def vpc_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vpcIdInput"))

    @builtins.property
    @jsii.member(jsii_name="accepterRegionName")
    def accepter_region_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accepterRegionName"))

    @accepter_region_name.setter
    def accepter_region_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93620c954c99ac961562a6e1b459d7cb0f9d0f94b8adb1b0e52c053316884ac9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accepterRegionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="atlasCidrBlock")
    def atlas_cidr_block(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "atlasCidrBlock"))

    @atlas_cidr_block.setter
    def atlas_cidr_block(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d87efc3b5d038a26847fa28ad72ac1f91d093a0800db9116c7a832a5a570a93)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "atlasCidrBlock", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="atlasGcpProjectId")
    def atlas_gcp_project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "atlasGcpProjectId"))

    @atlas_gcp_project_id.setter
    def atlas_gcp_project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5382d3515169d6d9aa32ad43970ecbcc50a2674b2a0d4f73b131cedc1e0394bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "atlasGcpProjectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="atlasVpcName")
    def atlas_vpc_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "atlasVpcName"))

    @atlas_vpc_name.setter
    def atlas_vpc_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c0b4e836eb8e0be44db042a634e0089b1d9ba6d4958af08006ec76ba8484af76)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "atlasVpcName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="awsAccountId")
    def aws_account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "awsAccountId"))

    @aws_account_id.setter
    def aws_account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0f06b10b925ff776b45f4a4f2e60323448fddde395928169a0d9ecad1821233)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "awsAccountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="azureDirectoryId")
    def azure_directory_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "azureDirectoryId"))

    @azure_directory_id.setter
    def azure_directory_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72cdaad7f315d335ba3d6eaa09e57df7e1bc5e37b82cffadf3a552380db0fd5d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureDirectoryId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="azureSubscriptionId")
    def azure_subscription_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "azureSubscriptionId"))

    @azure_subscription_id.setter
    def azure_subscription_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5529b6f81a18e1d4933f0c4fe38b01f56d4099533af66de7ada221dc1a95e291)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "azureSubscriptionId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="containerId")
    def container_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "containerId"))

    @container_id.setter
    def container_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70207cb79277f0c47b77f550542eb428743ee8026b50e5bb9a7819de09145fdf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "containerId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="gcpProjectId")
    def gcp_project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "gcpProjectId"))

    @gcp_project_id.setter
    def gcp_project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d6d4b15c318f845eecc52dba16b6ad7426ce30e6acb30a70ce775bc580fb19b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "gcpProjectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4417cbbbcd100c6fa816cf81f5346f7d691b0240408ad70a6e060485c6ae81a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networkName")
    def network_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkName"))

    @network_name.setter
    def network_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2c7ce80bbd478010270ab4f12a78aa79ab697e77066bd2cfb163de0bf97d6aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce41fb3adf49d76de5a16b6b81c04b89f8e68801f238ae95aaa91fcf9178c10b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="providerName")
    def provider_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "providerName"))

    @provider_name.setter
    def provider_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5708a22964febd885f696b88d8ded2fa82707996ba26e642152cfdecb3a1c25)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "providerName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="resourceGroupName")
    def resource_group_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "resourceGroupName"))

    @resource_group_name.setter
    def resource_group_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00fd795df8fecd3ab64cf434ebb093c3b790d6ebf06edcd86091795c6c753572)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "resourceGroupName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="routeTableCidrBlock")
    def route_table_cidr_block(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "routeTableCidrBlock"))

    @route_table_cidr_block.setter
    def route_table_cidr_block(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ec18346e7d869d84dc15563f3ad84188b097df444ba582c77ac08ce8df3949d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "routeTableCidrBlock", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vnetName")
    def vnet_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vnetName"))

    @vnet_name.setter
    def vnet_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a92d82f8d0fa36efb46d142ea09a4dd477d81a6dd76cb68bce43bbed73c13968)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vnetName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vpcId")
    def vpc_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcId"))

    @vpc_id.setter
    def vpc_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd2c309a8e9c6337fa30cf0a038e9992bd5100cd1f3cdec0bd1afb56f6ed4794)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vpcId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.networkPeering.NetworkPeeringConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "container_id": "containerId",
        "project_id": "projectId",
        "provider_name": "providerName",
        "accepter_region_name": "accepterRegionName",
        "atlas_cidr_block": "atlasCidrBlock",
        "atlas_gcp_project_id": "atlasGcpProjectId",
        "atlas_vpc_name": "atlasVpcName",
        "aws_account_id": "awsAccountId",
        "azure_directory_id": "azureDirectoryId",
        "azure_subscription_id": "azureSubscriptionId",
        "gcp_project_id": "gcpProjectId",
        "id": "id",
        "network_name": "networkName",
        "resource_group_name": "resourceGroupName",
        "route_table_cidr_block": "routeTableCidrBlock",
        "vnet_name": "vnetName",
        "vpc_id": "vpcId",
    },
)
class NetworkPeeringConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        container_id: builtins.str,
        project_id: builtins.str,
        provider_name: builtins.str,
        accepter_region_name: typing.Optional[builtins.str] = None,
        atlas_cidr_block: typing.Optional[builtins.str] = None,
        atlas_gcp_project_id: typing.Optional[builtins.str] = None,
        atlas_vpc_name: typing.Optional[builtins.str] = None,
        aws_account_id: typing.Optional[builtins.str] = None,
        azure_directory_id: typing.Optional[builtins.str] = None,
        azure_subscription_id: typing.Optional[builtins.str] = None,
        gcp_project_id: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        network_name: typing.Optional[builtins.str] = None,
        resource_group_name: typing.Optional[builtins.str] = None,
        route_table_cidr_block: typing.Optional[builtins.str] = None,
        vnet_name: typing.Optional[builtins.str] = None,
        vpc_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param container_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#container_id NetworkPeering#container_id}.
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#project_id NetworkPeering#project_id}.
        :param provider_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#provider_name NetworkPeering#provider_name}.
        :param accepter_region_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#accepter_region_name NetworkPeering#accepter_region_name}.
        :param atlas_cidr_block: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#atlas_cidr_block NetworkPeering#atlas_cidr_block}.
        :param atlas_gcp_project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#atlas_gcp_project_id NetworkPeering#atlas_gcp_project_id}.
        :param atlas_vpc_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#atlas_vpc_name NetworkPeering#atlas_vpc_name}.
        :param aws_account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#aws_account_id NetworkPeering#aws_account_id}.
        :param azure_directory_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#azure_directory_id NetworkPeering#azure_directory_id}.
        :param azure_subscription_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#azure_subscription_id NetworkPeering#azure_subscription_id}.
        :param gcp_project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#gcp_project_id NetworkPeering#gcp_project_id}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#id NetworkPeering#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param network_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#network_name NetworkPeering#network_name}.
        :param resource_group_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#resource_group_name NetworkPeering#resource_group_name}.
        :param route_table_cidr_block: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#route_table_cidr_block NetworkPeering#route_table_cidr_block}.
        :param vnet_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#vnet_name NetworkPeering#vnet_name}.
        :param vpc_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#vpc_id NetworkPeering#vpc_id}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1174bd019f995ab934658219f070340aa11fdb3809c46bca021e2d42d5b37607)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument container_id", value=container_id, expected_type=type_hints["container_id"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument provider_name", value=provider_name, expected_type=type_hints["provider_name"])
            check_type(argname="argument accepter_region_name", value=accepter_region_name, expected_type=type_hints["accepter_region_name"])
            check_type(argname="argument atlas_cidr_block", value=atlas_cidr_block, expected_type=type_hints["atlas_cidr_block"])
            check_type(argname="argument atlas_gcp_project_id", value=atlas_gcp_project_id, expected_type=type_hints["atlas_gcp_project_id"])
            check_type(argname="argument atlas_vpc_name", value=atlas_vpc_name, expected_type=type_hints["atlas_vpc_name"])
            check_type(argname="argument aws_account_id", value=aws_account_id, expected_type=type_hints["aws_account_id"])
            check_type(argname="argument azure_directory_id", value=azure_directory_id, expected_type=type_hints["azure_directory_id"])
            check_type(argname="argument azure_subscription_id", value=azure_subscription_id, expected_type=type_hints["azure_subscription_id"])
            check_type(argname="argument gcp_project_id", value=gcp_project_id, expected_type=type_hints["gcp_project_id"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument network_name", value=network_name, expected_type=type_hints["network_name"])
            check_type(argname="argument resource_group_name", value=resource_group_name, expected_type=type_hints["resource_group_name"])
            check_type(argname="argument route_table_cidr_block", value=route_table_cidr_block, expected_type=type_hints["route_table_cidr_block"])
            check_type(argname="argument vnet_name", value=vnet_name, expected_type=type_hints["vnet_name"])
            check_type(argname="argument vpc_id", value=vpc_id, expected_type=type_hints["vpc_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "container_id": container_id,
            "project_id": project_id,
            "provider_name": provider_name,
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
        if accepter_region_name is not None:
            self._values["accepter_region_name"] = accepter_region_name
        if atlas_cidr_block is not None:
            self._values["atlas_cidr_block"] = atlas_cidr_block
        if atlas_gcp_project_id is not None:
            self._values["atlas_gcp_project_id"] = atlas_gcp_project_id
        if atlas_vpc_name is not None:
            self._values["atlas_vpc_name"] = atlas_vpc_name
        if aws_account_id is not None:
            self._values["aws_account_id"] = aws_account_id
        if azure_directory_id is not None:
            self._values["azure_directory_id"] = azure_directory_id
        if azure_subscription_id is not None:
            self._values["azure_subscription_id"] = azure_subscription_id
        if gcp_project_id is not None:
            self._values["gcp_project_id"] = gcp_project_id
        if id is not None:
            self._values["id"] = id
        if network_name is not None:
            self._values["network_name"] = network_name
        if resource_group_name is not None:
            self._values["resource_group_name"] = resource_group_name
        if route_table_cidr_block is not None:
            self._values["route_table_cidr_block"] = route_table_cidr_block
        if vnet_name is not None:
            self._values["vnet_name"] = vnet_name
        if vpc_id is not None:
            self._values["vpc_id"] = vpc_id

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
    def container_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#container_id NetworkPeering#container_id}.'''
        result = self._values.get("container_id")
        assert result is not None, "Required property 'container_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def project_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#project_id NetworkPeering#project_id}.'''
        result = self._values.get("project_id")
        assert result is not None, "Required property 'project_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def provider_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#provider_name NetworkPeering#provider_name}.'''
        result = self._values.get("provider_name")
        assert result is not None, "Required property 'provider_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def accepter_region_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#accepter_region_name NetworkPeering#accepter_region_name}.'''
        result = self._values.get("accepter_region_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def atlas_cidr_block(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#atlas_cidr_block NetworkPeering#atlas_cidr_block}.'''
        result = self._values.get("atlas_cidr_block")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def atlas_gcp_project_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#atlas_gcp_project_id NetworkPeering#atlas_gcp_project_id}.'''
        result = self._values.get("atlas_gcp_project_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def atlas_vpc_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#atlas_vpc_name NetworkPeering#atlas_vpc_name}.'''
        result = self._values.get("atlas_vpc_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def aws_account_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#aws_account_id NetworkPeering#aws_account_id}.'''
        result = self._values.get("aws_account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def azure_directory_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#azure_directory_id NetworkPeering#azure_directory_id}.'''
        result = self._values.get("azure_directory_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def azure_subscription_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#azure_subscription_id NetworkPeering#azure_subscription_id}.'''
        result = self._values.get("azure_subscription_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def gcp_project_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#gcp_project_id NetworkPeering#gcp_project_id}.'''
        result = self._values.get("gcp_project_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#id NetworkPeering#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def network_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#network_name NetworkPeering#network_name}.'''
        result = self._values.get("network_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def resource_group_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#resource_group_name NetworkPeering#resource_group_name}.'''
        result = self._values.get("resource_group_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def route_table_cidr_block(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#route_table_cidr_block NetworkPeering#route_table_cidr_block}.'''
        result = self._values.get("route_table_cidr_block")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vnet_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#vnet_name NetworkPeering#vnet_name}.'''
        result = self._values.get("vnet_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/network_peering#vpc_id NetworkPeering#vpc_id}.'''
        result = self._values.get("vpc_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "NetworkPeeringConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "NetworkPeering",
    "NetworkPeeringConfig",
]

publication.publish()

def _typecheckingstub__971ccb4fc9d210efd4be0df9263bd9aa0194866eb45a100a1ce3240e6c4b31a2(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    container_id: builtins.str,
    project_id: builtins.str,
    provider_name: builtins.str,
    accepter_region_name: typing.Optional[builtins.str] = None,
    atlas_cidr_block: typing.Optional[builtins.str] = None,
    atlas_gcp_project_id: typing.Optional[builtins.str] = None,
    atlas_vpc_name: typing.Optional[builtins.str] = None,
    aws_account_id: typing.Optional[builtins.str] = None,
    azure_directory_id: typing.Optional[builtins.str] = None,
    azure_subscription_id: typing.Optional[builtins.str] = None,
    gcp_project_id: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    network_name: typing.Optional[builtins.str] = None,
    resource_group_name: typing.Optional[builtins.str] = None,
    route_table_cidr_block: typing.Optional[builtins.str] = None,
    vnet_name: typing.Optional[builtins.str] = None,
    vpc_id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__b5d82d6800f791615616b598b120585699af9be3febb1ee2be3405fbf71b4985(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93620c954c99ac961562a6e1b459d7cb0f9d0f94b8adb1b0e52c053316884ac9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d87efc3b5d038a26847fa28ad72ac1f91d093a0800db9116c7a832a5a570a93(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5382d3515169d6d9aa32ad43970ecbcc50a2674b2a0d4f73b131cedc1e0394bc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c0b4e836eb8e0be44db042a634e0089b1d9ba6d4958af08006ec76ba8484af76(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0f06b10b925ff776b45f4a4f2e60323448fddde395928169a0d9ecad1821233(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72cdaad7f315d335ba3d6eaa09e57df7e1bc5e37b82cffadf3a552380db0fd5d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5529b6f81a18e1d4933f0c4fe38b01f56d4099533af66de7ada221dc1a95e291(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70207cb79277f0c47b77f550542eb428743ee8026b50e5bb9a7819de09145fdf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d6d4b15c318f845eecc52dba16b6ad7426ce30e6acb30a70ce775bc580fb19b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4417cbbbcd100c6fa816cf81f5346f7d691b0240408ad70a6e060485c6ae81a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2c7ce80bbd478010270ab4f12a78aa79ab697e77066bd2cfb163de0bf97d6aa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce41fb3adf49d76de5a16b6b81c04b89f8e68801f238ae95aaa91fcf9178c10b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5708a22964febd885f696b88d8ded2fa82707996ba26e642152cfdecb3a1c25(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00fd795df8fecd3ab64cf434ebb093c3b790d6ebf06edcd86091795c6c753572(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ec18346e7d869d84dc15563f3ad84188b097df444ba582c77ac08ce8df3949d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a92d82f8d0fa36efb46d142ea09a4dd477d81a6dd76cb68bce43bbed73c13968(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd2c309a8e9c6337fa30cf0a038e9992bd5100cd1f3cdec0bd1afb56f6ed4794(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1174bd019f995ab934658219f070340aa11fdb3809c46bca021e2d42d5b37607(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    container_id: builtins.str,
    project_id: builtins.str,
    provider_name: builtins.str,
    accepter_region_name: typing.Optional[builtins.str] = None,
    atlas_cidr_block: typing.Optional[builtins.str] = None,
    atlas_gcp_project_id: typing.Optional[builtins.str] = None,
    atlas_vpc_name: typing.Optional[builtins.str] = None,
    aws_account_id: typing.Optional[builtins.str] = None,
    azure_directory_id: typing.Optional[builtins.str] = None,
    azure_subscription_id: typing.Optional[builtins.str] = None,
    gcp_project_id: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    network_name: typing.Optional[builtins.str] = None,
    resource_group_name: typing.Optional[builtins.str] = None,
    route_table_cidr_block: typing.Optional[builtins.str] = None,
    vnet_name: typing.Optional[builtins.str] = None,
    vpc_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
