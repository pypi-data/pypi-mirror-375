r'''
# `mongodbatlas_stream_processor`

Refer to the Terraform Registry for docs: [`mongodbatlas_stream_processor`](https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_processor).
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


class StreamProcessor(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.streamProcessor.StreamProcessor",
):
    '''Represents a {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_processor mongodbatlas_stream_processor}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        instance_name: builtins.str,
        pipeline: builtins.str,
        processor_name: builtins.str,
        project_id: builtins.str,
        options: typing.Optional[typing.Union["StreamProcessorOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        state: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_processor mongodbatlas_stream_processor} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param instance_name: Human-readable label that identifies the stream instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_processor#instance_name StreamProcessor#instance_name}
        :param pipeline: Stream aggregation pipeline you want to apply to your streaming data. `MongoDB Atlas Docs <https://www.mongodb.com/docs/atlas/atlas-stream-processing/stream-aggregation/#std-label-stream-aggregation>`_ contain more information. Using `jsonencode <https://developer.hashicorp.com/terraform/language/functions/jsonencode>`_ is recommended when setting this attribute. For more details see the `Aggregation Pipelines Documentation <https://www.mongodb.com/docs/atlas/atlas-stream-processing/stream-aggregation/>`_ Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_processor#pipeline StreamProcessor#pipeline}
        :param processor_name: Human-readable label that identifies the stream processor. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_processor#processor_name StreamProcessor#processor_name}
        :param project_id: Unique 24-hexadecimal digit string that identifies your project. Use the `/groups <#tag/Projects/operation/listProjects>`_ endpoint to retrieve all projects to which the authenticated user has access. **NOTE**: Groups and projects are synonymous terms. Your group id is the same as your project id. For existing groups, your group/project id remains the same. The resource and corresponding endpoints use the term groups. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_processor#project_id StreamProcessor#project_id}
        :param options: Optional configuration for the stream processor. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_processor#options StreamProcessor#options}
        :param state: The state of the stream processor. Commonly occurring states are 'CREATED', 'STARTED', 'STOPPED' and 'FAILED'. Used to start or stop the Stream Processor. Valid values are ``CREATED``, ``STARTED`` or ``STOPPED``. When a Stream Processor is created without specifying the state, it will default to ``CREATED`` state. When a Stream Processor is updated without specifying the state, it will default to the Previous state. **NOTE** When a Stream Processor is updated without specifying the state, it is stopped and then restored to previous state upon update completion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_processor#state StreamProcessor#state}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__98c1d5f90e8922253bb596f53637a4763be76a6ecac4837b68521ecadf57eb72)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = StreamProcessorConfig(
            instance_name=instance_name,
            pipeline=pipeline,
            processor_name=processor_name,
            project_id=project_id,
            options=options,
            state=state,
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
        '''Generates CDKTF code for importing a StreamProcessor resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the StreamProcessor to import.
        :param import_from_id: The id of the existing StreamProcessor that should be imported. Refer to the {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_processor#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the StreamProcessor to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2fe047fd35ba07d0791e9c6af5cc89632159c120d7f234bb52ce245add780f03)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putOptions")
    def put_options(
        self,
        *,
        dlq: typing.Union["StreamProcessorOptionsDlq", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param dlq: Dead letter queue for the stream processor. Refer to the `MongoDB Atlas Docs <https://www.mongodb.com/docs/atlas/reference/glossary/#std-term-dead-letter-queue>`_ for more information. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_processor#dlq StreamProcessor#dlq}
        '''
        value = StreamProcessorOptions(dlq=dlq)

        return typing.cast(None, jsii.invoke(self, "putOptions", [value]))

    @jsii.member(jsii_name="resetOptions")
    def reset_options(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOptions", []))

    @jsii.member(jsii_name="resetState")
    def reset_state(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetState", []))

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
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="options")
    def options(self) -> "StreamProcessorOptionsOutputReference":
        return typing.cast("StreamProcessorOptionsOutputReference", jsii.get(self, "options"))

    @builtins.property
    @jsii.member(jsii_name="stats")
    def stats(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "stats"))

    @builtins.property
    @jsii.member(jsii_name="instanceNameInput")
    def instance_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instanceNameInput"))

    @builtins.property
    @jsii.member(jsii_name="optionsInput")
    def options_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "StreamProcessorOptions"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "StreamProcessorOptions"]], jsii.get(self, "optionsInput"))

    @builtins.property
    @jsii.member(jsii_name="pipelineInput")
    def pipeline_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pipelineInput"))

    @builtins.property
    @jsii.member(jsii_name="processorNameInput")
    def processor_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "processorNameInput"))

    @builtins.property
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="stateInput")
    def state_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "stateInput"))

    @builtins.property
    @jsii.member(jsii_name="instanceName")
    def instance_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instanceName"))

    @instance_name.setter
    def instance_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36bb2ab355b61255afd4029ed125799cdc87f2d28fde6a598ce393ded5cd3796)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instanceName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pipeline")
    def pipeline(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pipeline"))

    @pipeline.setter
    def pipeline(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8912a7597eba1d29c61465120daf9e69943c681127c4d9b77b2451fb505756c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pipeline", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="processorName")
    def processor_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "processorName"))

    @processor_name.setter
    def processor_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bad63cb3f4dabb3d41aa09552aec84b58bab9805b507616ee97a557ac4685792)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "processorName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21419f870bfc40ba9bd6b072137823c2b9a013b526b17c590fb8afc100261995)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @state.setter
    def state(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9cde6715e112f8e5fb7b55c6bf01dee35b83c3ee54a5e7b77be34549b165dc70)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "state", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.streamProcessor.StreamProcessorConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "instance_name": "instanceName",
        "pipeline": "pipeline",
        "processor_name": "processorName",
        "project_id": "projectId",
        "options": "options",
        "state": "state",
    },
)
class StreamProcessorConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        instance_name: builtins.str,
        pipeline: builtins.str,
        processor_name: builtins.str,
        project_id: builtins.str,
        options: typing.Optional[typing.Union["StreamProcessorOptions", typing.Dict[builtins.str, typing.Any]]] = None,
        state: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param instance_name: Human-readable label that identifies the stream instance. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_processor#instance_name StreamProcessor#instance_name}
        :param pipeline: Stream aggregation pipeline you want to apply to your streaming data. `MongoDB Atlas Docs <https://www.mongodb.com/docs/atlas/atlas-stream-processing/stream-aggregation/#std-label-stream-aggregation>`_ contain more information. Using `jsonencode <https://developer.hashicorp.com/terraform/language/functions/jsonencode>`_ is recommended when setting this attribute. For more details see the `Aggregation Pipelines Documentation <https://www.mongodb.com/docs/atlas/atlas-stream-processing/stream-aggregation/>`_ Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_processor#pipeline StreamProcessor#pipeline}
        :param processor_name: Human-readable label that identifies the stream processor. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_processor#processor_name StreamProcessor#processor_name}
        :param project_id: Unique 24-hexadecimal digit string that identifies your project. Use the `/groups <#tag/Projects/operation/listProjects>`_ endpoint to retrieve all projects to which the authenticated user has access. **NOTE**: Groups and projects are synonymous terms. Your group id is the same as your project id. For existing groups, your group/project id remains the same. The resource and corresponding endpoints use the term groups. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_processor#project_id StreamProcessor#project_id}
        :param options: Optional configuration for the stream processor. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_processor#options StreamProcessor#options}
        :param state: The state of the stream processor. Commonly occurring states are 'CREATED', 'STARTED', 'STOPPED' and 'FAILED'. Used to start or stop the Stream Processor. Valid values are ``CREATED``, ``STARTED`` or ``STOPPED``. When a Stream Processor is created without specifying the state, it will default to ``CREATED`` state. When a Stream Processor is updated without specifying the state, it will default to the Previous state. **NOTE** When a Stream Processor is updated without specifying the state, it is stopped and then restored to previous state upon update completion. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_processor#state StreamProcessor#state}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(options, dict):
            options = StreamProcessorOptions(**options)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6201f82c1f95ef9fcdddd667187a7fb78fcbc8387a8d43582a705ee34fed3a5)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument instance_name", value=instance_name, expected_type=type_hints["instance_name"])
            check_type(argname="argument pipeline", value=pipeline, expected_type=type_hints["pipeline"])
            check_type(argname="argument processor_name", value=processor_name, expected_type=type_hints["processor_name"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument options", value=options, expected_type=type_hints["options"])
            check_type(argname="argument state", value=state, expected_type=type_hints["state"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "instance_name": instance_name,
            "pipeline": pipeline,
            "processor_name": processor_name,
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
        if options is not None:
            self._values["options"] = options
        if state is not None:
            self._values["state"] = state

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
    def instance_name(self) -> builtins.str:
        '''Human-readable label that identifies the stream instance.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_processor#instance_name StreamProcessor#instance_name}
        '''
        result = self._values.get("instance_name")
        assert result is not None, "Required property 'instance_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def pipeline(self) -> builtins.str:
        '''Stream aggregation pipeline you want to apply to your streaming data.

        `MongoDB Atlas Docs <https://www.mongodb.com/docs/atlas/atlas-stream-processing/stream-aggregation/#std-label-stream-aggregation>`_ contain more information. Using `jsonencode <https://developer.hashicorp.com/terraform/language/functions/jsonencode>`_ is recommended when setting this attribute. For more details see the `Aggregation Pipelines Documentation <https://www.mongodb.com/docs/atlas/atlas-stream-processing/stream-aggregation/>`_

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_processor#pipeline StreamProcessor#pipeline}
        '''
        result = self._values.get("pipeline")
        assert result is not None, "Required property 'pipeline' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def processor_name(self) -> builtins.str:
        '''Human-readable label that identifies the stream processor.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_processor#processor_name StreamProcessor#processor_name}
        '''
        result = self._values.get("processor_name")
        assert result is not None, "Required property 'processor_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def project_id(self) -> builtins.str:
        '''Unique 24-hexadecimal digit string that identifies your project.

        Use the `/groups <#tag/Projects/operation/listProjects>`_ endpoint to retrieve all projects to which the authenticated user has access.

        **NOTE**: Groups and projects are synonymous terms. Your group id is the same as your project id. For existing groups, your group/project id remains the same. The resource and corresponding endpoints use the term groups.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_processor#project_id StreamProcessor#project_id}
        '''
        result = self._values.get("project_id")
        assert result is not None, "Required property 'project_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def options(self) -> typing.Optional["StreamProcessorOptions"]:
        '''Optional configuration for the stream processor.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_processor#options StreamProcessor#options}
        '''
        result = self._values.get("options")
        return typing.cast(typing.Optional["StreamProcessorOptions"], result)

    @builtins.property
    def state(self) -> typing.Optional[builtins.str]:
        '''The state of the stream processor.

        Commonly occurring states are 'CREATED', 'STARTED', 'STOPPED' and 'FAILED'. Used to start or stop the Stream Processor. Valid values are ``CREATED``, ``STARTED`` or ``STOPPED``. When a Stream Processor is created without specifying the state, it will default to ``CREATED`` state. When a Stream Processor is updated without specifying the state, it will default to the Previous state.

        **NOTE** When a Stream Processor is updated without specifying the state, it is stopped and then restored to previous state upon update completion.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_processor#state StreamProcessor#state}
        '''
        result = self._values.get("state")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StreamProcessorConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.streamProcessor.StreamProcessorOptions",
    jsii_struct_bases=[],
    name_mapping={"dlq": "dlq"},
)
class StreamProcessorOptions:
    def __init__(
        self,
        *,
        dlq: typing.Union["StreamProcessorOptionsDlq", typing.Dict[builtins.str, typing.Any]],
    ) -> None:
        '''
        :param dlq: Dead letter queue for the stream processor. Refer to the `MongoDB Atlas Docs <https://www.mongodb.com/docs/atlas/reference/glossary/#std-term-dead-letter-queue>`_ for more information. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_processor#dlq StreamProcessor#dlq}
        '''
        if isinstance(dlq, dict):
            dlq = StreamProcessorOptionsDlq(**dlq)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2abfea6f6789c37d6c8dda5742299b9161caa6d8fea74d8c0200c1987b390913)
            check_type(argname="argument dlq", value=dlq, expected_type=type_hints["dlq"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "dlq": dlq,
        }

    @builtins.property
    def dlq(self) -> "StreamProcessorOptionsDlq":
        '''Dead letter queue for the stream processor. Refer to the `MongoDB Atlas Docs <https://www.mongodb.com/docs/atlas/reference/glossary/#std-term-dead-letter-queue>`_ for more information.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_processor#dlq StreamProcessor#dlq}
        '''
        result = self._values.get("dlq")
        assert result is not None, "Required property 'dlq' is missing"
        return typing.cast("StreamProcessorOptionsDlq", result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StreamProcessorOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.streamProcessor.StreamProcessorOptionsDlq",
    jsii_struct_bases=[],
    name_mapping={"coll": "coll", "connection_name": "connectionName", "db": "db"},
)
class StreamProcessorOptionsDlq:
    def __init__(
        self,
        *,
        coll: builtins.str,
        connection_name: builtins.str,
        db: builtins.str,
    ) -> None:
        '''
        :param coll: Name of the collection to use for the DLQ. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_processor#coll StreamProcessor#coll}
        :param connection_name: Name of the connection to write DLQ messages to. Must be an Atlas connection. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_processor#connection_name StreamProcessor#connection_name}
        :param db: Name of the database to use for the DLQ. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_processor#db StreamProcessor#db}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b4a5901f751812bda76950f5332eef56afa9252a10e67b7c2910535a6c2898a3)
            check_type(argname="argument coll", value=coll, expected_type=type_hints["coll"])
            check_type(argname="argument connection_name", value=connection_name, expected_type=type_hints["connection_name"])
            check_type(argname="argument db", value=db, expected_type=type_hints["db"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "coll": coll,
            "connection_name": connection_name,
            "db": db,
        }

    @builtins.property
    def coll(self) -> builtins.str:
        '''Name of the collection to use for the DLQ.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_processor#coll StreamProcessor#coll}
        '''
        result = self._values.get("coll")
        assert result is not None, "Required property 'coll' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def connection_name(self) -> builtins.str:
        '''Name of the connection to write DLQ messages to. Must be an Atlas connection.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_processor#connection_name StreamProcessor#connection_name}
        '''
        result = self._values.get("connection_name")
        assert result is not None, "Required property 'connection_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def db(self) -> builtins.str:
        '''Name of the database to use for the DLQ.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_processor#db StreamProcessor#db}
        '''
        result = self._values.get("db")
        assert result is not None, "Required property 'db' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "StreamProcessorOptionsDlq(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class StreamProcessorOptionsDlqOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.streamProcessor.StreamProcessorOptionsDlqOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__78c7b2cf36fabdd4544c491a5c180900b7e85cae241d8d7a9c9e79f067dda0e0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="collInput")
    def coll_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "collInput"))

    @builtins.property
    @jsii.member(jsii_name="connectionNameInput")
    def connection_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "connectionNameInput"))

    @builtins.property
    @jsii.member(jsii_name="dbInput")
    def db_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dbInput"))

    @builtins.property
    @jsii.member(jsii_name="coll")
    def coll(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "coll"))

    @coll.setter
    def coll(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fc23d9e86e81860998695d5c56faf1636851dba066ff490e5c0de6c3d4aee9b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "coll", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="connectionName")
    def connection_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "connectionName"))

    @connection_name.setter
    def connection_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b94b970f87cff89933597b7ac1a5d22dba9e32f34b9b0a904a9ecece899aad0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="db")
    def db(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "db"))

    @db.setter
    def db(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__515563d31cf1c78d22dd7aa4b0a302c83d5c4bfec1c5d72576343651d2bdd11a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "db", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StreamProcessorOptionsDlq]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StreamProcessorOptionsDlq]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StreamProcessorOptionsDlq]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ee52fa619ca554eb30edc312563e9ba4625977d4c04598e6cac471e824c0287)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class StreamProcessorOptionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.streamProcessor.StreamProcessorOptionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__78a9c8548489c9121070af8674a907f080736c487cf5fbdfa92b06548ecba8ac)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putDlq")
    def put_dlq(
        self,
        *,
        coll: builtins.str,
        connection_name: builtins.str,
        db: builtins.str,
    ) -> None:
        '''
        :param coll: Name of the collection to use for the DLQ. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_processor#coll StreamProcessor#coll}
        :param connection_name: Name of the connection to write DLQ messages to. Must be an Atlas connection. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_processor#connection_name StreamProcessor#connection_name}
        :param db: Name of the database to use for the DLQ. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/stream_processor#db StreamProcessor#db}
        '''
        value = StreamProcessorOptionsDlq(
            coll=coll, connection_name=connection_name, db=db
        )

        return typing.cast(None, jsii.invoke(self, "putDlq", [value]))

    @builtins.property
    @jsii.member(jsii_name="dlq")
    def dlq(self) -> StreamProcessorOptionsDlqOutputReference:
        return typing.cast(StreamProcessorOptionsDlqOutputReference, jsii.get(self, "dlq"))

    @builtins.property
    @jsii.member(jsii_name="dlqInput")
    def dlq_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StreamProcessorOptionsDlq]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StreamProcessorOptionsDlq]], jsii.get(self, "dlqInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StreamProcessorOptions]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StreamProcessorOptions]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StreamProcessorOptions]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de46325d76947ef4cde6057351f4cceac0bf56caa2996488c65dcdb3e38657a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "StreamProcessor",
    "StreamProcessorConfig",
    "StreamProcessorOptions",
    "StreamProcessorOptionsDlq",
    "StreamProcessorOptionsDlqOutputReference",
    "StreamProcessorOptionsOutputReference",
]

publication.publish()

def _typecheckingstub__98c1d5f90e8922253bb596f53637a4763be76a6ecac4837b68521ecadf57eb72(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    instance_name: builtins.str,
    pipeline: builtins.str,
    processor_name: builtins.str,
    project_id: builtins.str,
    options: typing.Optional[typing.Union[StreamProcessorOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    state: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__2fe047fd35ba07d0791e9c6af5cc89632159c120d7f234bb52ce245add780f03(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__36bb2ab355b61255afd4029ed125799cdc87f2d28fde6a598ce393ded5cd3796(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8912a7597eba1d29c61465120daf9e69943c681127c4d9b77b2451fb505756c4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bad63cb3f4dabb3d41aa09552aec84b58bab9805b507616ee97a557ac4685792(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21419f870bfc40ba9bd6b072137823c2b9a013b526b17c590fb8afc100261995(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9cde6715e112f8e5fb7b55c6bf01dee35b83c3ee54a5e7b77be34549b165dc70(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6201f82c1f95ef9fcdddd667187a7fb78fcbc8387a8d43582a705ee34fed3a5(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    instance_name: builtins.str,
    pipeline: builtins.str,
    processor_name: builtins.str,
    project_id: builtins.str,
    options: typing.Optional[typing.Union[StreamProcessorOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    state: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2abfea6f6789c37d6c8dda5742299b9161caa6d8fea74d8c0200c1987b390913(
    *,
    dlq: typing.Union[StreamProcessorOptionsDlq, typing.Dict[builtins.str, typing.Any]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b4a5901f751812bda76950f5332eef56afa9252a10e67b7c2910535a6c2898a3(
    *,
    coll: builtins.str,
    connection_name: builtins.str,
    db: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78c7b2cf36fabdd4544c491a5c180900b7e85cae241d8d7a9c9e79f067dda0e0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fc23d9e86e81860998695d5c56faf1636851dba066ff490e5c0de6c3d4aee9b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b94b970f87cff89933597b7ac1a5d22dba9e32f34b9b0a904a9ecece899aad0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__515563d31cf1c78d22dd7aa4b0a302c83d5c4bfec1c5d72576343651d2bdd11a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ee52fa619ca554eb30edc312563e9ba4625977d4c04598e6cac471e824c0287(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StreamProcessorOptionsDlq]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78a9c8548489c9121070af8674a907f080736c487cf5fbdfa92b06548ecba8ac(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de46325d76947ef4cde6057351f4cceac0bf56caa2996488c65dcdb3e38657a3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, StreamProcessorOptions]],
) -> None:
    """Type checking stubs"""
    pass
