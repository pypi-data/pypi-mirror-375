r'''
# `mongodbatlas_stream_connection`

Refer to the Terraform Registry for docs: [`mongodbatlas_stream_connection`](https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection).
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


class StreamConnection(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.streamConnection.StreamConnection",
):
    '''Represents a {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection mongodbatlas_stream_connection}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        connection_name: builtins.str,
        instance_name: builtins.str,
        project_id: builtins.str,
        type: builtins.str,
        authentication: typing.Optional[typing.Union["StreamConnectionAuthentication", typing.Dict[builtins.str, typing.Any]]] = None,
        aws: typing.Optional[typing.Union["StreamConnectionAws", typing.Dict[builtins.str, typing.Any]]] = None,
        bootstrap_servers: typing.Optional[builtins.str] = None,
        cluster_name: typing.Optional[builtins.str] = None,
        cluster_project_id: typing.Optional[builtins.str] = None,
        config: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        db_role_to_execute: typing.Optional[typing.Union["StreamConnectionDbRoleToExecute", typing.Dict[builtins.str, typing.Any]]] = None,
        headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        networking: typing.Optional[typing.Union["StreamConnectionNetworking", typing.Dict[builtins.str, typing.Any]]] = None,
        security: typing.Optional[typing.Union["StreamConnectionSecurity", typing.Dict[builtins.str, typing.Any]]] = None,
        url: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection mongodbatlas_stream_connection} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param connection_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#connection_name StreamConnection#connection_name}.
        :param instance_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#instance_name StreamConnection#instance_name}.
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#project_id StreamConnection#project_id}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#type StreamConnection#type}.
        :param authentication: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#authentication StreamConnection#authentication}.
        :param aws: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#aws StreamConnection#aws}.
        :param bootstrap_servers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#bootstrap_servers StreamConnection#bootstrap_servers}.
        :param cluster_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#cluster_name StreamConnection#cluster_name}.
        :param cluster_project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#cluster_project_id StreamConnection#cluster_project_id}.
        :param config: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#config StreamConnection#config}.
        :param db_role_to_execute: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#db_role_to_execute StreamConnection#db_role_to_execute}.
        :param headers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#headers StreamConnection#headers}.
        :param networking: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#networking StreamConnection#networking}.
        :param security: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#security StreamConnection#security}.
        :param url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#url StreamConnection#url}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28b3e1dfe2ef9abae429e4bd723ed4a042b4c6e73da94e37438fafb69ee66d2e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config_ = StreamConnectionConfig(
            connection_name=connection_name,
            instance_name=instance_name,
            project_id=project_id,
            type=type,
            authentication=authentication,
            aws=aws,
            bootstrap_servers=bootstrap_servers,
            cluster_name=cluster_name,
            cluster_project_id=cluster_project_id,
            config=config,
            db_role_to_execute=db_role_to_execute,
            headers=headers,
            networking=networking,
            security=security,
            url=url,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id, config_])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a StreamConnection resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the StreamConnection to import.
        :param import_from_id: The id of the existing StreamConnection that should be imported. Refer to the {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the StreamConnection to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e1f63bcc8dc2a5e71275140421a0f3ce3bee47c7cefd9f52d6493e7e3abbb4b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putAuthentication")
    def put_authentication(
        self,
        *,
        mechanism: typing.Optional[builtins.str] = None,
        password: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param mechanism: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#mechanism StreamConnection#mechanism}.
        :param password: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#password StreamConnection#password}.
        :param username: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#username StreamConnection#username}.
        '''
        value = StreamConnectionAuthentication(
            mechanism=mechanism, password=password, username=username
        )

        return typing.cast(None, jsii.invoke(self, "putAuthentication", [value]))

    @jsii.member(jsii_name="putAws")
    def put_aws(self, *, role_arn: builtins.str) -> None:
        '''
        :param role_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#role_arn StreamConnection#role_arn}.
        '''
        value = StreamConnectionAws(role_arn=role_arn)

        return typing.cast(None, jsii.invoke(self, "putAws", [value]))

    @jsii.member(jsii_name="putDbRoleToExecute")
    def put_db_role_to_execute(self, *, role: builtins.str, type: builtins.str) -> None:
        '''
        :param role: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#role StreamConnection#role}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#type StreamConnection#type}.
        '''
        value = StreamConnectionDbRoleToExecute(role=role, type=type)

        return typing.cast(None, jsii.invoke(self, "putDbRoleToExecute", [value]))

    @jsii.member(jsii_name="putNetworking")
    def put_networking(
        self,
        *,
        access: typing.Union["StreamConnectionNetworkingAccess", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param access: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#access StreamConnection#access}.
        '''
        value = StreamConnectionNetworking(access=access)

        return typing.cast(None, jsii.invoke(self, "putNetworking", [value]))

    @jsii.member(jsii_name="putSecurity")
    def put_security(
        self,
        *,
        broker_public_certificate: typing.Optional[builtins.str] = None,
        protocol: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param broker_public_certificate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#broker_public_certificate StreamConnection#broker_public_certificate}.
        :param protocol: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#protocol StreamConnection#protocol}.
        '''
        value = StreamConnectionSecurity(
            broker_public_certificate=broker_public_certificate, protocol=protocol
        )

        return typing.cast(None, jsii.invoke(self, "putSecurity", [value]))

    @jsii.member(jsii_name="resetAuthentication")
    def reset_authentication(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthentication", []))

    @jsii.member(jsii_name="resetAws")
    def reset_aws(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAws", []))

    @jsii.member(jsii_name="resetBootstrapServers")
    def reset_bootstrap_servers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBootstrapServers", []))

    @jsii.member(jsii_name="resetClusterName")
    def reset_cluster_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterName", []))

    @jsii.member(jsii_name="resetClusterProjectId")
    def reset_cluster_project_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterProjectId", []))

    @jsii.member(jsii_name="resetConfig")
    def reset_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfig", []))

    @jsii.member(jsii_name="resetDbRoleToExecute")
    def reset_db_role_to_execute(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDbRoleToExecute", []))

    @jsii.member(jsii_name="resetHeaders")
    def reset_headers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHeaders", []))

    @jsii.member(jsii_name="resetNetworking")
    def reset_networking(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworking", []))

    @jsii.member(jsii_name="resetSecurity")
    def reset_security(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecurity", []))

    @jsii.member(jsii_name="resetUrl")
    def reset_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrl", []))

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
    @jsii.member(jsii_name="authentication")
    def authentication(self) -> "StreamConnectionAuthenticationOutputReference":
        return typing.cast("StreamConnectionAuthenticationOutputReference", jsii.get(self, "authentication"))

    @builtins.property
    @jsii.member(jsii_name="aws")
    def aws(self) -> "StreamConnectionAwsOutputReference":
        return typing.cast("StreamConnectionAwsOutputReference", jsii.get(self, "aws"))

    @builtins.property
    @jsii.member(jsii_name="dbRoleToExecute")
    def db_role_to_execute(self) -> "StreamConnectionDbRoleToExecuteOutputReference":
        return typing.cast("StreamConnectionDbRoleToExecuteOutputReference", jsii.get(self, "dbRoleToExecute"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="networking")
    def networking(self) -> "StreamConnectionNetworkingOutputReference":
        return typing.cast("StreamConnectionNetworkingOutputReference", jsii.get(self, "networking"))

    @builtins.property
    @jsii.member(jsii_name="security")
    def security(self) -> "StreamConnectionSecurityOutputReference":
        return typing.cast("StreamConnectionSecurityOutputReference", jsii.get(self, "security"))

    @builtins.property
    @jsii.member(jsii_name="authenticationInput")
    def authentication_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "StreamConnectionAuthentication"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "StreamConnectionAuthentication"]], jsii.get(self, "authenticationInput"))

    @builtins.property
    @jsii.member(jsii_name="awsInput")
    def aws_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "StreamConnectionAws"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "StreamConnectionAws"]], jsii.get(self, "awsInput"))

    @builtins.property
    @jsii.member(jsii_name="bootstrapServersInput")
    def bootstrap_servers_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bootstrapServersInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterNameInput")
    def cluster_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterNameInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterProjectIdInput")
    def cluster_project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterProjectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="configInput")
    def config_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "configInput"))

    @builtins.property
    @jsii.member(jsii_name="connectionNameInput")
    def connection_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectionNameInput"))

    @builtins.property
    @jsii.member(jsii_name="dbRoleToExecuteInput")
    def db_role_to_execute_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "StreamConnectionDbRoleToExecute"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "StreamConnectionDbRoleToExecute"]], jsii.get(self, "dbRoleToExecuteInput"))

    @builtins.property
    @jsii.member(jsii_name="headersInput")
    def headers_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "headersInput"))

    @builtins.property
    @jsii.member(jsii_name="instanceNameInput")
    def instance_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceNameInput"))

    @builtins.property
    @jsii.member(jsii_name="networkingInput")
    def networking_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "StreamConnectionNetworking"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "StreamConnectionNetworking"]], jsii.get(self, "networkingInput"))

    @builtins.property
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="securityInput")
    def security_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "StreamConnectionSecurity"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "StreamConnectionSecurity"]], jsii.get(self, "securityInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property
    @jsii.member(jsii_name="bootstrapServers")
    def bootstrap_servers(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bootstrapServers"))

    @bootstrap_servers.setter
    def bootstrap_servers(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38e0ea4083c6c66a0604999a05c20d9a0dc7626d4070c237d92e09eb32082299)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bootstrapServers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterName"))

    @cluster_name.setter
    def cluster_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0431b40ce2e31e46c3b401cf8722b61312c74291e9e6cd6e8be21f6d648ffd2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clusterProjectId")
    def cluster_project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterProjectId"))

    @cluster_project_id.setter
    def cluster_project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67c29fd041608e2d1e1932811cafca40aa8bf20c3482f3cb23f7baa986d4ed45)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterProjectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "config"))

    @config.setter
    def config(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1869a8d1f406161b62d21eba8cdd4728e63ed4d369316a717d727701669da3f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "config", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="connectionName")
    def connection_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connectionName"))

    @connection_name.setter
    def connection_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__885802f9c0be20ad482706271cfae884384368800df2d9d21e0c23ade9634aa1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="headers")
    def headers(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "headers"))

    @headers.setter
    def headers(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db3466ebd61c87d25f0be301f2f4f934eead725667df2f78b50d96660948433c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "headers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instanceName")
    def instance_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceName"))

    @instance_name.setter
    def instance_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a94e177e77b9f1763b87ed8d7c8a03c3da883b58fcceb4217a57cbac58b68df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e956465c592c4ec3b18d1cdc8b76415795e8ebec4ce50fc357a7c63efaa9de35)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7107f687c1d86cdd8f874556d90efaf9f58a66d06d27b6dfea41a3aac7d0591)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9fd174b745874dce9e547beff40f0f1667e251ed2b1033069381fb25ecc45653)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.streamConnection.StreamConnectionAuthentication",
    jsii_struct_bases=[],
    name_mapping={
        "mechanism": "mechanism",
        "password": "password",
        "username": "username",
    },
)
class StreamConnectionAuthentication:
    def __init__(
        self,
        *,
        mechanism: typing.Optional[builtins.str] = None,
        password: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param mechanism: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#mechanism StreamConnection#mechanism}.
        :param password: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#password StreamConnection#password}.
        :param username: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#username StreamConnection#username}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad1156f255d28f4ea5fc6ea3db9048acb9494a12c2debbb6551ee6b1c466cf02)
            check_type(argname="argument mechanism", value=mechanism, expected_type=type_hints["mechanism"])
            check_type(argname="argument password", value=password, expected_type=type_hints["password"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if mechanism is not None:
            self._values["mechanism"] = mechanism
        if password is not None:
            self._values["password"] = password
        if username is not None:
            self._values["username"] = username

    @builtins.property
    def mechanism(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#mechanism StreamConnection#mechanism}.'''
        result = self._values.get("mechanism")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def password(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#password StreamConnection#password}.'''
        result = self._values.get("password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#username StreamConnection#username}.'''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StreamConnectionAuthentication(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StreamConnectionAuthenticationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.streamConnection.StreamConnectionAuthenticationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__718516eb0b9c6fabeba20609b2b9f09b09da06d062e11aa91ecc609c78e2fa7c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMechanism")
    def reset_mechanism(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMechanism", []))

    @jsii.member(jsii_name="resetPassword")
    def reset_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPassword", []))

    @jsii.member(jsii_name="resetUsername")
    def reset_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsername", []))

    @builtins.property
    @jsii.member(jsii_name="mechanismInput")
    def mechanism_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mechanismInput"))

    @builtins.property
    @jsii.member(jsii_name="passwordInput")
    def password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "passwordInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property
    @jsii.member(jsii_name="mechanism")
    def mechanism(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mechanism"))

    @mechanism.setter
    def mechanism(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6e9ce019911bca552847ec6994847dd9d0d0e0240aa900b00128a5f5c1efe84)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mechanism", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="password")
    def password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "password"))

    @password.setter
    def password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20f0d3c6888b380e7e4ed45d557bfa8bf1d5eff6d8283c340ce5d70f0daa35a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "password", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__006eecdf34219c7298dfcc3a51df3b038cfb1de0341de83308632169f0f38574)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StreamConnectionAuthentication]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StreamConnectionAuthentication]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StreamConnectionAuthentication]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a3c880098554f6fa680ac1b0721ba22f6806459d3e85633464190ad91c4f3c2d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.streamConnection.StreamConnectionAws",
    jsii_struct_bases=[],
    name_mapping={"role_arn": "roleArn"},
)
class StreamConnectionAws:
    def __init__(self, *, role_arn: builtins.str) -> None:
        '''
        :param role_arn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#role_arn StreamConnection#role_arn}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__094daccfc60b251b7a31874f5643254bf1cbd295c5baa085a9420cfc83ee3c75)
            check_type(argname="argument role_arn", value=role_arn, expected_type=type_hints["role_arn"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "role_arn": role_arn,
        }

    @builtins.property
    def role_arn(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#role_arn StreamConnection#role_arn}.'''
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StreamConnectionAws(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StreamConnectionAwsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.streamConnection.StreamConnectionAwsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d105186216e80355bb72c3e247e173655abc46970c1d5b2b1c2f70b7545b6122)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="roleArnInput")
    def role_arn_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleArnInput"))

    @builtins.property
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "roleArn"))

    @role_arn.setter
    def role_arn(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c6c3f27cef2a0cd15f011ac8d40a5970a8bca2e05bb6232851c351948e08d5b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "roleArn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StreamConnectionAws]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StreamConnectionAws]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StreamConnectionAws]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52c57fd630efb599edae445b3ee7779e5eefdea0cc30dd8fa18a1ca78c0328e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.streamConnection.StreamConnectionConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "connection_name": "connectionName",
        "instance_name": "instanceName",
        "project_id": "projectId",
        "type": "type",
        "authentication": "authentication",
        "aws": "aws",
        "bootstrap_servers": "bootstrapServers",
        "cluster_name": "clusterName",
        "cluster_project_id": "clusterProjectId",
        "config": "config",
        "db_role_to_execute": "dbRoleToExecute",
        "headers": "headers",
        "networking": "networking",
        "security": "security",
        "url": "url",
    },
)
class StreamConnectionConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        connection_name: builtins.str,
        instance_name: builtins.str,
        project_id: builtins.str,
        type: builtins.str,
        authentication: typing.Optional[typing.Union[StreamConnectionAuthentication, typing.Dict[builtins.str, typing.Any]]] = None,
        aws: typing.Optional[typing.Union[StreamConnectionAws, typing.Dict[builtins.str, typing.Any]]] = None,
        bootstrap_servers: typing.Optional[builtins.str] = None,
        cluster_name: typing.Optional[builtins.str] = None,
        cluster_project_id: typing.Optional[builtins.str] = None,
        config: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        db_role_to_execute: typing.Optional[typing.Union["StreamConnectionDbRoleToExecute", typing.Dict[builtins.str, typing.Any]]] = None,
        headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        networking: typing.Optional[typing.Union["StreamConnectionNetworking", typing.Dict[builtins.str, typing.Any]]] = None,
        security: typing.Optional[typing.Union["StreamConnectionSecurity", typing.Dict[builtins.str, typing.Any]]] = None,
        url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param connection_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#connection_name StreamConnection#connection_name}.
        :param instance_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#instance_name StreamConnection#instance_name}.
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#project_id StreamConnection#project_id}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#type StreamConnection#type}.
        :param authentication: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#authentication StreamConnection#authentication}.
        :param aws: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#aws StreamConnection#aws}.
        :param bootstrap_servers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#bootstrap_servers StreamConnection#bootstrap_servers}.
        :param cluster_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#cluster_name StreamConnection#cluster_name}.
        :param cluster_project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#cluster_project_id StreamConnection#cluster_project_id}.
        :param config: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#config StreamConnection#config}.
        :param db_role_to_execute: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#db_role_to_execute StreamConnection#db_role_to_execute}.
        :param headers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#headers StreamConnection#headers}.
        :param networking: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#networking StreamConnection#networking}.
        :param security: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#security StreamConnection#security}.
        :param url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#url StreamConnection#url}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(authentication, dict):
            authentication = StreamConnectionAuthentication(**authentication)
        if isinstance(aws, dict):
            aws = StreamConnectionAws(**aws)
        if isinstance(db_role_to_execute, dict):
            db_role_to_execute = StreamConnectionDbRoleToExecute(**db_role_to_execute)
        if isinstance(networking, dict):
            networking = StreamConnectionNetworking(**networking)
        if isinstance(security, dict):
            security = StreamConnectionSecurity(**security)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10d27355744698a7d7990f6c999249cb18cf326b82c61556dd3f8d8ec2bef813)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument connection_name", value=connection_name, expected_type=type_hints["connection_name"])
            check_type(argname="argument instance_name", value=instance_name, expected_type=type_hints["instance_name"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument authentication", value=authentication, expected_type=type_hints["authentication"])
            check_type(argname="argument aws", value=aws, expected_type=type_hints["aws"])
            check_type(argname="argument bootstrap_servers", value=bootstrap_servers, expected_type=type_hints["bootstrap_servers"])
            check_type(argname="argument cluster_name", value=cluster_name, expected_type=type_hints["cluster_name"])
            check_type(argname="argument cluster_project_id", value=cluster_project_id, expected_type=type_hints["cluster_project_id"])
            check_type(argname="argument config", value=config, expected_type=type_hints["config"])
            check_type(argname="argument db_role_to_execute", value=db_role_to_execute, expected_type=type_hints["db_role_to_execute"])
            check_type(argname="argument headers", value=headers, expected_type=type_hints["headers"])
            check_type(argname="argument networking", value=networking, expected_type=type_hints["networking"])
            check_type(argname="argument security", value=security, expected_type=type_hints["security"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "connection_name": connection_name,
            "instance_name": instance_name,
            "project_id": project_id,
            "type": type,
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
        if authentication is not None:
            self._values["authentication"] = authentication
        if aws is not None:
            self._values["aws"] = aws
        if bootstrap_servers is not None:
            self._values["bootstrap_servers"] = bootstrap_servers
        if cluster_name is not None:
            self._values["cluster_name"] = cluster_name
        if cluster_project_id is not None:
            self._values["cluster_project_id"] = cluster_project_id
        if config is not None:
            self._values["config"] = config
        if db_role_to_execute is not None:
            self._values["db_role_to_execute"] = db_role_to_execute
        if headers is not None:
            self._values["headers"] = headers
        if networking is not None:
            self._values["networking"] = networking
        if security is not None:
            self._values["security"] = security
        if url is not None:
            self._values["url"] = url

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
    def connection_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#connection_name StreamConnection#connection_name}.'''
        result = self._values.get("connection_name")
        assert result is not None, "Required property 'connection_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def instance_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#instance_name StreamConnection#instance_name}.'''
        result = self._values.get("instance_name")
        assert result is not None, "Required property 'instance_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def project_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#project_id StreamConnection#project_id}.'''
        result = self._values.get("project_id")
        assert result is not None, "Required property 'project_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#type StreamConnection#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def authentication(self) -> typing.Optional[StreamConnectionAuthentication]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#authentication StreamConnection#authentication}.'''
        result = self._values.get("authentication")
        return typing.cast(typing.Optional[StreamConnectionAuthentication], result)

    @builtins.property
    def aws(self) -> typing.Optional[StreamConnectionAws]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#aws StreamConnection#aws}.'''
        result = self._values.get("aws")
        return typing.cast(typing.Optional[StreamConnectionAws], result)

    @builtins.property
    def bootstrap_servers(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#bootstrap_servers StreamConnection#bootstrap_servers}.'''
        result = self._values.get("bootstrap_servers")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#cluster_name StreamConnection#cluster_name}.'''
        result = self._values.get("cluster_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cluster_project_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#cluster_project_id StreamConnection#cluster_project_id}.'''
        result = self._values.get("cluster_project_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def config(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#config StreamConnection#config}.'''
        result = self._values.get("config")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def db_role_to_execute(self) -> typing.Optional["StreamConnectionDbRoleToExecute"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#db_role_to_execute StreamConnection#db_role_to_execute}.'''
        result = self._values.get("db_role_to_execute")
        return typing.cast(typing.Optional["StreamConnectionDbRoleToExecute"], result)

    @builtins.property
    def headers(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#headers StreamConnection#headers}.'''
        result = self._values.get("headers")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def networking(self) -> typing.Optional["StreamConnectionNetworking"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#networking StreamConnection#networking}.'''
        result = self._values.get("networking")
        return typing.cast(typing.Optional["StreamConnectionNetworking"], result)

    @builtins.property
    def security(self) -> typing.Optional["StreamConnectionSecurity"]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#security StreamConnection#security}.'''
        result = self._values.get("security")
        return typing.cast(typing.Optional["StreamConnectionSecurity"], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#url StreamConnection#url}.'''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StreamConnectionConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.streamConnection.StreamConnectionDbRoleToExecute",
    jsii_struct_bases=[],
    name_mapping={"role": "role", "type": "type"},
)
class StreamConnectionDbRoleToExecute:
    def __init__(self, *, role: builtins.str, type: builtins.str) -> None:
        '''
        :param role: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#role StreamConnection#role}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#type StreamConnection#type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0153a6ae22ff26d065f248b9f19491b075b063f5af5afbe8ea7c0280ae6863fb)
            check_type(argname="argument role", value=role, expected_type=type_hints["role"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "role": role,
            "type": type,
        }

    @builtins.property
    def role(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#role StreamConnection#role}.'''
        result = self._values.get("role")
        assert result is not None, "Required property 'role' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#type StreamConnection#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StreamConnectionDbRoleToExecute(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StreamConnectionDbRoleToExecuteOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.streamConnection.StreamConnectionDbRoleToExecuteOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__925ccfa4d50d1fc72bf3aa37b4a937adbda6148c82388ecf8259301cba9f0bf7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="roleInput")
    def role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "roleInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="role")
    def role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "role"))

    @role.setter
    def role(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0487b5ca4d1a84d553e779f2b71d158ca5b9ac8312c2a48be70aa2df68c969a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "role", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e46a3b03a65119d41ac3e64ccebf24ea4bd59c44ceec6dfb9717cf0e8dc7245)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StreamConnectionDbRoleToExecute]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StreamConnectionDbRoleToExecute]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StreamConnectionDbRoleToExecute]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__32a869e6e2619c8b331e01d8a4e7c358ff85243b366a959941fc736ebcc9b3a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.streamConnection.StreamConnectionNetworking",
    jsii_struct_bases=[],
    name_mapping={"access": "access"},
)
class StreamConnectionNetworking:
    def __init__(
        self,
        *,
        access: typing.Union["StreamConnectionNetworkingAccess", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param access: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#access StreamConnection#access}.
        '''
        if isinstance(access, dict):
            access = StreamConnectionNetworkingAccess(**access)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__632805963a70a65500dd36427898bed46b68cd9452325157c608911b7205f80b)
            check_type(argname="argument access", value=access, expected_type=type_hints["access"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "access": access,
        }

    @builtins.property
    def access(self) -> "StreamConnectionNetworkingAccess":
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#access StreamConnection#access}.'''
        result = self._values.get("access")
        assert result is not None, "Required property 'access' is missing"
        return typing.cast("StreamConnectionNetworkingAccess", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StreamConnectionNetworking(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.streamConnection.StreamConnectionNetworkingAccess",
    jsii_struct_bases=[],
    name_mapping={"type": "type", "connection_id": "connectionId"},
)
class StreamConnectionNetworkingAccess:
    def __init__(
        self,
        *,
        type: builtins.str,
        connection_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#type StreamConnection#type}.
        :param connection_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#connection_id StreamConnection#connection_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23b0c791200abc258294a46dcf6a574b273bcd0932647f4c080504dffb0d8d6e)
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument connection_id", value=connection_id, expected_type=type_hints["connection_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "type": type,
        }
        if connection_id is not None:
            self._values["connection_id"] = connection_id

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#type StreamConnection#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def connection_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#connection_id StreamConnection#connection_id}.'''
        result = self._values.get("connection_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StreamConnectionNetworkingAccess(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StreamConnectionNetworkingAccessOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.streamConnection.StreamConnectionNetworkingAccessOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0b6479cc41989481aecf362233cf53c42a5cd5dc4838f43e06d4f9bda60b8b5b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetConnectionId")
    def reset_connection_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectionId", []))

    @builtins.property
    @jsii.member(jsii_name="connectionIdInput")
    def connection_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectionIdInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="connectionId")
    def connection_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connectionId"))

    @connection_id.setter
    def connection_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba23f7986f0a66b47c91255499332bd2bc9f9aa1bf4368ea47fa278ddd21b215)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectionId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12e209fe8be067ae443dbc36b2ad5aa9b2079132a218a49b3a175d1ca8494499)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[StreamConnectionNetworkingAccess]:
        return typing.cast(typing.Optional[StreamConnectionNetworkingAccess], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[StreamConnectionNetworkingAccess],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aecfb2c797d0f39584962c37b79ddb5a3d245960cf0e74061e5b15fee53a7e89)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class StreamConnectionNetworkingOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.streamConnection.StreamConnectionNetworkingOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f6a256680f35e6dabaffe7b93aab6d587cc148b2a1b7609c22ec0b6546a002be)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAccess")
    def put_access(
        self,
        *,
        type: builtins.str,
        connection_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#type StreamConnection#type}.
        :param connection_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#connection_id StreamConnection#connection_id}.
        '''
        value = StreamConnectionNetworkingAccess(
            type=type, connection_id=connection_id
        )

        return typing.cast(None, jsii.invoke(self, "putAccess", [value]))

    @builtins.property
    @jsii.member(jsii_name="access")
    def access(self) -> StreamConnectionNetworkingAccessOutputReference:
        return typing.cast(StreamConnectionNetworkingAccessOutputReference, jsii.get(self, "access"))

    @builtins.property
    @jsii.member(jsii_name="accessInput")
    def access_input(self) -> typing.Optional[StreamConnectionNetworkingAccess]:
        return typing.cast(typing.Optional[StreamConnectionNetworkingAccess], jsii.get(self, "accessInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StreamConnectionNetworking]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StreamConnectionNetworking]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StreamConnectionNetworking]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37cd309adb792de987f38746deb10e0ecb864a07bb975c884077fbc68ed3a5fb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.streamConnection.StreamConnectionSecurity",
    jsii_struct_bases=[],
    name_mapping={
        "broker_public_certificate": "brokerPublicCertificate",
        "protocol": "protocol",
    },
)
class StreamConnectionSecurity:
    def __init__(
        self,
        *,
        broker_public_certificate: typing.Optional[builtins.str] = None,
        protocol: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param broker_public_certificate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#broker_public_certificate StreamConnection#broker_public_certificate}.
        :param protocol: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#protocol StreamConnection#protocol}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ed9d9770b6655d130453faaf7b371552ef3af3e196902ac5817ee46b42e645a)
            check_type(argname="argument broker_public_certificate", value=broker_public_certificate, expected_type=type_hints["broker_public_certificate"])
            check_type(argname="argument protocol", value=protocol, expected_type=type_hints["protocol"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if broker_public_certificate is not None:
            self._values["broker_public_certificate"] = broker_public_certificate
        if protocol is not None:
            self._values["protocol"] = protocol

    @builtins.property
    def broker_public_certificate(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#broker_public_certificate StreamConnection#broker_public_certificate}.'''
        result = self._values.get("broker_public_certificate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def protocol(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_connection#protocol StreamConnection#protocol}.'''
        result = self._values.get("protocol")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StreamConnectionSecurity(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StreamConnectionSecurityOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.streamConnection.StreamConnectionSecurityOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2748cc785aea62e1e3f3f6c5b9ed78a3303a02a17ebdff2e04bb705f40deda50)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetBrokerPublicCertificate")
    def reset_broker_public_certificate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBrokerPublicCertificate", []))

    @jsii.member(jsii_name="resetProtocol")
    def reset_protocol(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProtocol", []))

    @builtins.property
    @jsii.member(jsii_name="brokerPublicCertificateInput")
    def broker_public_certificate_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "brokerPublicCertificateInput"))

    @builtins.property
    @jsii.member(jsii_name="protocolInput")
    def protocol_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "protocolInput"))

    @builtins.property
    @jsii.member(jsii_name="brokerPublicCertificate")
    def broker_public_certificate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "brokerPublicCertificate"))

    @broker_public_certificate.setter
    def broker_public_certificate(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfef17e85c2794c411ce1a8cfd76f4b61126ef6f351b3865d7ffa2b974d3aac2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "brokerPublicCertificate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="protocol")
    def protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "protocol"))

    @protocol.setter
    def protocol(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__666402ec37b7f8e81363357bc09ec4ea738f06165f4586ddccb0a52ee9fc33ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "protocol", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StreamConnectionSecurity]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StreamConnectionSecurity]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StreamConnectionSecurity]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c8bead477af010fe45e796cb464a03e03a77bfd3a247503e1c8331299cd2caa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "StreamConnection",
    "StreamConnectionAuthentication",
    "StreamConnectionAuthenticationOutputReference",
    "StreamConnectionAws",
    "StreamConnectionAwsOutputReference",
    "StreamConnectionConfig",
    "StreamConnectionDbRoleToExecute",
    "StreamConnectionDbRoleToExecuteOutputReference",
    "StreamConnectionNetworking",
    "StreamConnectionNetworkingAccess",
    "StreamConnectionNetworkingAccessOutputReference",
    "StreamConnectionNetworkingOutputReference",
    "StreamConnectionSecurity",
    "StreamConnectionSecurityOutputReference",
]

publication.publish()

def _typecheckingstub__28b3e1dfe2ef9abae429e4bd723ed4a042b4c6e73da94e37438fafb69ee66d2e(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    connection_name: builtins.str,
    instance_name: builtins.str,
    project_id: builtins.str,
    type: builtins.str,
    authentication: typing.Optional[typing.Union[StreamConnectionAuthentication, typing.Dict[builtins.str, typing.Any]]] = None,
    aws: typing.Optional[typing.Union[StreamConnectionAws, typing.Dict[builtins.str, typing.Any]]] = None,
    bootstrap_servers: typing.Optional[builtins.str] = None,
    cluster_name: typing.Optional[builtins.str] = None,
    cluster_project_id: typing.Optional[builtins.str] = None,
    config: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    db_role_to_execute: typing.Optional[typing.Union[StreamConnectionDbRoleToExecute, typing.Dict[builtins.str, typing.Any]]] = None,
    headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    networking: typing.Optional[typing.Union[StreamConnectionNetworking, typing.Dict[builtins.str, typing.Any]]] = None,
    security: typing.Optional[typing.Union[StreamConnectionSecurity, typing.Dict[builtins.str, typing.Any]]] = None,
    url: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__6e1f63bcc8dc2a5e71275140421a0f3ce3bee47c7cefd9f52d6493e7e3abbb4b(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38e0ea4083c6c66a0604999a05c20d9a0dc7626d4070c237d92e09eb32082299(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0431b40ce2e31e46c3b401cf8722b61312c74291e9e6cd6e8be21f6d648ffd2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67c29fd041608e2d1e1932811cafca40aa8bf20c3482f3cb23f7baa986d4ed45(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1869a8d1f406161b62d21eba8cdd4728e63ed4d369316a717d727701669da3f9(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__885802f9c0be20ad482706271cfae884384368800df2d9d21e0c23ade9634aa1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db3466ebd61c87d25f0be301f2f4f934eead725667df2f78b50d96660948433c(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a94e177e77b9f1763b87ed8d7c8a03c3da883b58fcceb4217a57cbac58b68df(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e956465c592c4ec3b18d1cdc8b76415795e8ebec4ce50fc357a7c63efaa9de35(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7107f687c1d86cdd8f874556d90efaf9f58a66d06d27b6dfea41a3aac7d0591(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fd174b745874dce9e547beff40f0f1667e251ed2b1033069381fb25ecc45653(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad1156f255d28f4ea5fc6ea3db9048acb9494a12c2debbb6551ee6b1c466cf02(
    *,
    mechanism: typing.Optional[builtins.str] = None,
    password: typing.Optional[builtins.str] = None,
    username: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__718516eb0b9c6fabeba20609b2b9f09b09da06d062e11aa91ecc609c78e2fa7c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6e9ce019911bca552847ec6994847dd9d0d0e0240aa900b00128a5f5c1efe84(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20f0d3c6888b380e7e4ed45d557bfa8bf1d5eff6d8283c340ce5d70f0daa35a0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__006eecdf34219c7298dfcc3a51df3b038cfb1de0341de83308632169f0f38574(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a3c880098554f6fa680ac1b0721ba22f6806459d3e85633464190ad91c4f3c2d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StreamConnectionAuthentication]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__094daccfc60b251b7a31874f5643254bf1cbd295c5baa085a9420cfc83ee3c75(
    *,
    role_arn: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d105186216e80355bb72c3e247e173655abc46970c1d5b2b1c2f70b7545b6122(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c6c3f27cef2a0cd15f011ac8d40a5970a8bca2e05bb6232851c351948e08d5b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52c57fd630efb599edae445b3ee7779e5eefdea0cc30dd8fa18a1ca78c0328e0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StreamConnectionAws]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10d27355744698a7d7990f6c999249cb18cf326b82c61556dd3f8d8ec2bef813(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    connection_name: builtins.str,
    instance_name: builtins.str,
    project_id: builtins.str,
    type: builtins.str,
    authentication: typing.Optional[typing.Union[StreamConnectionAuthentication, typing.Dict[builtins.str, typing.Any]]] = None,
    aws: typing.Optional[typing.Union[StreamConnectionAws, typing.Dict[builtins.str, typing.Any]]] = None,
    bootstrap_servers: typing.Optional[builtins.str] = None,
    cluster_name: typing.Optional[builtins.str] = None,
    cluster_project_id: typing.Optional[builtins.str] = None,
    config: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    db_role_to_execute: typing.Optional[typing.Union[StreamConnectionDbRoleToExecute, typing.Dict[builtins.str, typing.Any]]] = None,
    headers: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    networking: typing.Optional[typing.Union[StreamConnectionNetworking, typing.Dict[builtins.str, typing.Any]]] = None,
    security: typing.Optional[typing.Union[StreamConnectionSecurity, typing.Dict[builtins.str, typing.Any]]] = None,
    url: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0153a6ae22ff26d065f248b9f19491b075b063f5af5afbe8ea7c0280ae6863fb(
    *,
    role: builtins.str,
    type: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__925ccfa4d50d1fc72bf3aa37b4a937adbda6148c82388ecf8259301cba9f0bf7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0487b5ca4d1a84d553e779f2b71d158ca5b9ac8312c2a48be70aa2df68c969a3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e46a3b03a65119d41ac3e64ccebf24ea4bd59c44ceec6dfb9717cf0e8dc7245(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32a869e6e2619c8b331e01d8a4e7c358ff85243b366a959941fc736ebcc9b3a3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StreamConnectionDbRoleToExecute]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__632805963a70a65500dd36427898bed46b68cd9452325157c608911b7205f80b(
    *,
    access: typing.Union[StreamConnectionNetworkingAccess, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23b0c791200abc258294a46dcf6a574b273bcd0932647f4c080504dffb0d8d6e(
    *,
    type: builtins.str,
    connection_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b6479cc41989481aecf362233cf53c42a5cd5dc4838f43e06d4f9bda60b8b5b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba23f7986f0a66b47c91255499332bd2bc9f9aa1bf4368ea47fa278ddd21b215(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12e209fe8be067ae443dbc36b2ad5aa9b2079132a218a49b3a175d1ca8494499(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aecfb2c797d0f39584962c37b79ddb5a3d245960cf0e74061e5b15fee53a7e89(
    value: typing.Optional[StreamConnectionNetworkingAccess],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f6a256680f35e6dabaffe7b93aab6d587cc148b2a1b7609c22ec0b6546a002be(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37cd309adb792de987f38746deb10e0ecb864a07bb975c884077fbc68ed3a5fb(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StreamConnectionNetworking]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ed9d9770b6655d130453faaf7b371552ef3af3e196902ac5817ee46b42e645a(
    *,
    broker_public_certificate: typing.Optional[builtins.str] = None,
    protocol: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2748cc785aea62e1e3f3f6c5b9ed78a3303a02a17ebdff2e04bb705f40deda50(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfef17e85c2794c411ce1a8cfd76f4b61126ef6f351b3865d7ffa2b974d3aac2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__666402ec37b7f8e81363357bc09ec4ea738f06165f4586ddccb0a52ee9fc33ec(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c8bead477af010fe45e796cb464a03e03a77bfd3a247503e1c8331299cd2caa(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StreamConnectionSecurity]],
) -> None:
    """Type checking stubs"""
    pass
