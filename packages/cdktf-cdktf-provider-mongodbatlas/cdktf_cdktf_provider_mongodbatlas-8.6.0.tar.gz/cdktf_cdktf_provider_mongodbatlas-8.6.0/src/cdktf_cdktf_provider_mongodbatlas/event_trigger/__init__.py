r'''
# `mongodbatlas_event_trigger`

Refer to the Terraform Registry for docs: [`mongodbatlas_event_trigger`](https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger).
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


class EventTrigger(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.eventTrigger.EventTrigger",
):
    '''Represents a {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger mongodbatlas_event_trigger}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        app_id: builtins.str,
        name: builtins.str,
        project_id: builtins.str,
        type: builtins.str,
        config_collection: typing.Optional[builtins.str] = None,
        config_database: typing.Optional[builtins.str] = None,
        config_full_document: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        config_full_document_before: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        config_match: typing.Optional[builtins.str] = None,
        config_operation_type: typing.Optional[builtins.str] = None,
        config_operation_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        config_project: typing.Optional[builtins.str] = None,
        config_providers: typing.Optional[typing.Sequence[builtins.str]] = None,
        config_schedule: typing.Optional[builtins.str] = None,
        config_service_id: typing.Optional[builtins.str] = None,
        disabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        event_processors: typing.Optional[typing.Union["EventTriggerEventProcessors", typing.Dict[builtins.str, typing.Any]]] = None,
        function_id: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        unordered: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger mongodbatlas_event_trigger} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param app_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#app_id EventTrigger#app_id}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#name EventTrigger#name}.
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#project_id EventTrigger#project_id}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#type EventTrigger#type}.
        :param config_collection: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_collection EventTrigger#config_collection}.
        :param config_database: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_database EventTrigger#config_database}.
        :param config_full_document: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_full_document EventTrigger#config_full_document}.
        :param config_full_document_before: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_full_document_before EventTrigger#config_full_document_before}.
        :param config_match: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_match EventTrigger#config_match}.
        :param config_operation_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_operation_type EventTrigger#config_operation_type}.
        :param config_operation_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_operation_types EventTrigger#config_operation_types}.
        :param config_project: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_project EventTrigger#config_project}.
        :param config_providers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_providers EventTrigger#config_providers}.
        :param config_schedule: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_schedule EventTrigger#config_schedule}.
        :param config_service_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_service_id EventTrigger#config_service_id}.
        :param disabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#disabled EventTrigger#disabled}.
        :param event_processors: event_processors block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#event_processors EventTrigger#event_processors}
        :param function_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#function_id EventTrigger#function_id}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#id EventTrigger#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param unordered: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#unordered EventTrigger#unordered}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17d3332aed0f8331f133eea2b5dcbd3f7d5aa449d882e1a1ec4b9756c88b7907)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = EventTriggerConfig(
            app_id=app_id,
            name=name,
            project_id=project_id,
            type=type,
            config_collection=config_collection,
            config_database=config_database,
            config_full_document=config_full_document,
            config_full_document_before=config_full_document_before,
            config_match=config_match,
            config_operation_type=config_operation_type,
            config_operation_types=config_operation_types,
            config_project=config_project,
            config_providers=config_providers,
            config_schedule=config_schedule,
            config_service_id=config_service_id,
            disabled=disabled,
            event_processors=event_processors,
            function_id=function_id,
            id=id,
            unordered=unordered,
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
        '''Generates CDKTF code for importing a EventTrigger resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the EventTrigger to import.
        :param import_from_id: The id of the existing EventTrigger that should be imported. Refer to the {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the EventTrigger to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf71514d99385648ae092ecb2097d4df04079bced06164a1b1cb28bd796bd8cd)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putEventProcessors")
    def put_event_processors(
        self,
        *,
        aws_eventbridge: typing.Optional[typing.Union["EventTriggerEventProcessorsAwsEventbridge", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param aws_eventbridge: aws_eventbridge block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#aws_eventbridge EventTrigger#aws_eventbridge}
        '''
        value = EventTriggerEventProcessors(aws_eventbridge=aws_eventbridge)

        return typing.cast(None, jsii.invoke(self, "putEventProcessors", [value]))

    @jsii.member(jsii_name="resetConfigCollection")
    def reset_config_collection(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfigCollection", []))

    @jsii.member(jsii_name="resetConfigDatabase")
    def reset_config_database(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfigDatabase", []))

    @jsii.member(jsii_name="resetConfigFullDocument")
    def reset_config_full_document(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfigFullDocument", []))

    @jsii.member(jsii_name="resetConfigFullDocumentBefore")
    def reset_config_full_document_before(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfigFullDocumentBefore", []))

    @jsii.member(jsii_name="resetConfigMatch")
    def reset_config_match(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfigMatch", []))

    @jsii.member(jsii_name="resetConfigOperationType")
    def reset_config_operation_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfigOperationType", []))

    @jsii.member(jsii_name="resetConfigOperationTypes")
    def reset_config_operation_types(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfigOperationTypes", []))

    @jsii.member(jsii_name="resetConfigProject")
    def reset_config_project(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfigProject", []))

    @jsii.member(jsii_name="resetConfigProviders")
    def reset_config_providers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfigProviders", []))

    @jsii.member(jsii_name="resetConfigSchedule")
    def reset_config_schedule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfigSchedule", []))

    @jsii.member(jsii_name="resetConfigServiceId")
    def reset_config_service_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfigServiceId", []))

    @jsii.member(jsii_name="resetDisabled")
    def reset_disabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisabled", []))

    @jsii.member(jsii_name="resetEventProcessors")
    def reset_event_processors(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEventProcessors", []))

    @jsii.member(jsii_name="resetFunctionId")
    def reset_function_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFunctionId", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetUnordered")
    def reset_unordered(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUnordered", []))

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
    @jsii.member(jsii_name="configScheduleType")
    def config_schedule_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configScheduleType"))

    @builtins.property
    @jsii.member(jsii_name="eventProcessors")
    def event_processors(self) -> "EventTriggerEventProcessorsOutputReference":
        return typing.cast("EventTriggerEventProcessorsOutputReference", jsii.get(self, "eventProcessors"))

    @builtins.property
    @jsii.member(jsii_name="functionName")
    def function_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "functionName"))

    @builtins.property
    @jsii.member(jsii_name="triggerId")
    def trigger_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "triggerId"))

    @builtins.property
    @jsii.member(jsii_name="appIdInput")
    def app_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "appIdInput"))

    @builtins.property
    @jsii.member(jsii_name="configCollectionInput")
    def config_collection_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "configCollectionInput"))

    @builtins.property
    @jsii.member(jsii_name="configDatabaseInput")
    def config_database_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "configDatabaseInput"))

    @builtins.property
    @jsii.member(jsii_name="configFullDocumentBeforeInput")
    def config_full_document_before_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "configFullDocumentBeforeInput"))

    @builtins.property
    @jsii.member(jsii_name="configFullDocumentInput")
    def config_full_document_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "configFullDocumentInput"))

    @builtins.property
    @jsii.member(jsii_name="configMatchInput")
    def config_match_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "configMatchInput"))

    @builtins.property
    @jsii.member(jsii_name="configOperationTypeInput")
    def config_operation_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "configOperationTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="configOperationTypesInput")
    def config_operation_types_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "configOperationTypesInput"))

    @builtins.property
    @jsii.member(jsii_name="configProjectInput")
    def config_project_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "configProjectInput"))

    @builtins.property
    @jsii.member(jsii_name="configProvidersInput")
    def config_providers_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "configProvidersInput"))

    @builtins.property
    @jsii.member(jsii_name="configScheduleInput")
    def config_schedule_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "configScheduleInput"))

    @builtins.property
    @jsii.member(jsii_name="configServiceIdInput")
    def config_service_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "configServiceIdInput"))

    @builtins.property
    @jsii.member(jsii_name="disabledInput")
    def disabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disabledInput"))

    @builtins.property
    @jsii.member(jsii_name="eventProcessorsInput")
    def event_processors_input(self) -> typing.Optional["EventTriggerEventProcessors"]:
        return typing.cast(typing.Optional["EventTriggerEventProcessors"], jsii.get(self, "eventProcessorsInput"))

    @builtins.property
    @jsii.member(jsii_name="functionIdInput")
    def function_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "functionIdInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="unorderedInput")
    def unordered_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "unorderedInput"))

    @builtins.property
    @jsii.member(jsii_name="appId")
    def app_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "appId"))

    @app_id.setter
    def app_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3595d6b251d5983e1bd5e7392c6fdbc774d8594660c5eb32505a60647b4ac39e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "appId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="configCollection")
    def config_collection(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configCollection"))

    @config_collection.setter
    def config_collection(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81b46f87e392acc6fea38599e1ce3679dc23592841b12daa5116e1e46d317ed3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "configCollection", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="configDatabase")
    def config_database(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configDatabase"))

    @config_database.setter
    def config_database(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85f47bec517a0d0113156f7bfa02dc0449869c1a774c4715b45132c23c12fa23)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "configDatabase", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="configFullDocument")
    def config_full_document(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "configFullDocument"))

    @config_full_document.setter
    def config_full_document(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8abaceafc04393ecdab561c8f87c3801bfc640323e2d2f0c40c511717f946377)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "configFullDocument", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="configFullDocumentBefore")
    def config_full_document_before(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "configFullDocumentBefore"))

    @config_full_document_before.setter
    def config_full_document_before(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__501f139b805e731de1ec3820fab96197e0c0297d0a53d5ffca9c7590c06d37d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "configFullDocumentBefore", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="configMatch")
    def config_match(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configMatch"))

    @config_match.setter
    def config_match(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fa8bb715d4bff64ea016552cee01963f9a7178a812d9523c9d6b00c786e1fe4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "configMatch", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="configOperationType")
    def config_operation_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configOperationType"))

    @config_operation_type.setter
    def config_operation_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__200a4ed0e4aa6fb6fa61f6f530d1ab39c19b92c8670b531cf944e7bd32b0ee83)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "configOperationType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="configOperationTypes")
    def config_operation_types(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "configOperationTypes"))

    @config_operation_types.setter
    def config_operation_types(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3d430549e75e5401d81dc8bdd8d3e67af012eee8297341910792346f634f0d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "configOperationTypes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="configProject")
    def config_project(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configProject"))

    @config_project.setter
    def config_project(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68854a3d0a857de060e3b9b067a6ec1eb3d5175ba36dc625f3f99a4c7d1153c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "configProject", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="configProviders")
    def config_providers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "configProviders"))

    @config_providers.setter
    def config_providers(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd3e465dbea3d3ac003edeb64eecc5d9bc62c9b27e6a6695af0bace64c26c84c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "configProviders", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="configSchedule")
    def config_schedule(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configSchedule"))

    @config_schedule.setter
    def config_schedule(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a313862363506ea896b01a7c41cd4279f2eafce7959015d3ea7dca8baa474737)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "configSchedule", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="configServiceId")
    def config_service_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configServiceId"))

    @config_service_id.setter
    def config_service_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9851e6ed669265177d187f1b89fb749e8fd750d13a43e16351f76620554929af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "configServiceId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="disabled")
    def disabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "disabled"))

    @disabled.setter
    def disabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6a945d4b203cb5ed3a2895465005559f195bc4355920d86b96a5e3b616a2036)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="functionId")
    def function_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "functionId"))

    @function_id.setter
    def function_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8995d91cbf8eb52bedc1a7621f20f4b8242000698692e75a7389d1a50c8facb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "functionId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d93be735b54cd6c703c21d7860fb088bc1c0d8e43e6237b6f52f63f36f0e1075)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b52be3e091f9890f160cbd57d6ebacabb75fce8224ed54f81ad76a71d96facc1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c86f61328459ec39fe2575e0277567b93c8c5fe1070611ceb507ba527e885e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9627d9500f830f695def82ab9a81112ea7ee546bfdfef266d6dc31548f707a77)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="unordered")
    def unordered(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "unordered"))

    @unordered.setter
    def unordered(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fbe57ad8b5848ccda8795bc9fd8acb4207f44a0e794e4545bba0e2ecd4258013)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unordered", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.eventTrigger.EventTriggerConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "app_id": "appId",
        "name": "name",
        "project_id": "projectId",
        "type": "type",
        "config_collection": "configCollection",
        "config_database": "configDatabase",
        "config_full_document": "configFullDocument",
        "config_full_document_before": "configFullDocumentBefore",
        "config_match": "configMatch",
        "config_operation_type": "configOperationType",
        "config_operation_types": "configOperationTypes",
        "config_project": "configProject",
        "config_providers": "configProviders",
        "config_schedule": "configSchedule",
        "config_service_id": "configServiceId",
        "disabled": "disabled",
        "event_processors": "eventProcessors",
        "function_id": "functionId",
        "id": "id",
        "unordered": "unordered",
    },
)
class EventTriggerConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        app_id: builtins.str,
        name: builtins.str,
        project_id: builtins.str,
        type: builtins.str,
        config_collection: typing.Optional[builtins.str] = None,
        config_database: typing.Optional[builtins.str] = None,
        config_full_document: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        config_full_document_before: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        config_match: typing.Optional[builtins.str] = None,
        config_operation_type: typing.Optional[builtins.str] = None,
        config_operation_types: typing.Optional[typing.Sequence[builtins.str]] = None,
        config_project: typing.Optional[builtins.str] = None,
        config_providers: typing.Optional[typing.Sequence[builtins.str]] = None,
        config_schedule: typing.Optional[builtins.str] = None,
        config_service_id: typing.Optional[builtins.str] = None,
        disabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        event_processors: typing.Optional[typing.Union["EventTriggerEventProcessors", typing.Dict[builtins.str, typing.Any]]] = None,
        function_id: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        unordered: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param app_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#app_id EventTrigger#app_id}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#name EventTrigger#name}.
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#project_id EventTrigger#project_id}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#type EventTrigger#type}.
        :param config_collection: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_collection EventTrigger#config_collection}.
        :param config_database: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_database EventTrigger#config_database}.
        :param config_full_document: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_full_document EventTrigger#config_full_document}.
        :param config_full_document_before: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_full_document_before EventTrigger#config_full_document_before}.
        :param config_match: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_match EventTrigger#config_match}.
        :param config_operation_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_operation_type EventTrigger#config_operation_type}.
        :param config_operation_types: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_operation_types EventTrigger#config_operation_types}.
        :param config_project: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_project EventTrigger#config_project}.
        :param config_providers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_providers EventTrigger#config_providers}.
        :param config_schedule: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_schedule EventTrigger#config_schedule}.
        :param config_service_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_service_id EventTrigger#config_service_id}.
        :param disabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#disabled EventTrigger#disabled}.
        :param event_processors: event_processors block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#event_processors EventTrigger#event_processors}
        :param function_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#function_id EventTrigger#function_id}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#id EventTrigger#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param unordered: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#unordered EventTrigger#unordered}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(event_processors, dict):
            event_processors = EventTriggerEventProcessors(**event_processors)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d59f9b1046b25c198fa9be526af0111fd8ecdb34793a9fdacdc3798b636a93e)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument app_id", value=app_id, expected_type=type_hints["app_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument config_collection", value=config_collection, expected_type=type_hints["config_collection"])
            check_type(argname="argument config_database", value=config_database, expected_type=type_hints["config_database"])
            check_type(argname="argument config_full_document", value=config_full_document, expected_type=type_hints["config_full_document"])
            check_type(argname="argument config_full_document_before", value=config_full_document_before, expected_type=type_hints["config_full_document_before"])
            check_type(argname="argument config_match", value=config_match, expected_type=type_hints["config_match"])
            check_type(argname="argument config_operation_type", value=config_operation_type, expected_type=type_hints["config_operation_type"])
            check_type(argname="argument config_operation_types", value=config_operation_types, expected_type=type_hints["config_operation_types"])
            check_type(argname="argument config_project", value=config_project, expected_type=type_hints["config_project"])
            check_type(argname="argument config_providers", value=config_providers, expected_type=type_hints["config_providers"])
            check_type(argname="argument config_schedule", value=config_schedule, expected_type=type_hints["config_schedule"])
            check_type(argname="argument config_service_id", value=config_service_id, expected_type=type_hints["config_service_id"])
            check_type(argname="argument disabled", value=disabled, expected_type=type_hints["disabled"])
            check_type(argname="argument event_processors", value=event_processors, expected_type=type_hints["event_processors"])
            check_type(argname="argument function_id", value=function_id, expected_type=type_hints["function_id"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument unordered", value=unordered, expected_type=type_hints["unordered"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "app_id": app_id,
            "name": name,
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
        if config_collection is not None:
            self._values["config_collection"] = config_collection
        if config_database is not None:
            self._values["config_database"] = config_database
        if config_full_document is not None:
            self._values["config_full_document"] = config_full_document
        if config_full_document_before is not None:
            self._values["config_full_document_before"] = config_full_document_before
        if config_match is not None:
            self._values["config_match"] = config_match
        if config_operation_type is not None:
            self._values["config_operation_type"] = config_operation_type
        if config_operation_types is not None:
            self._values["config_operation_types"] = config_operation_types
        if config_project is not None:
            self._values["config_project"] = config_project
        if config_providers is not None:
            self._values["config_providers"] = config_providers
        if config_schedule is not None:
            self._values["config_schedule"] = config_schedule
        if config_service_id is not None:
            self._values["config_service_id"] = config_service_id
        if disabled is not None:
            self._values["disabled"] = disabled
        if event_processors is not None:
            self._values["event_processors"] = event_processors
        if function_id is not None:
            self._values["function_id"] = function_id
        if id is not None:
            self._values["id"] = id
        if unordered is not None:
            self._values["unordered"] = unordered

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
    def app_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#app_id EventTrigger#app_id}.'''
        result = self._values.get("app_id")
        assert result is not None, "Required property 'app_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#name EventTrigger#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def project_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#project_id EventTrigger#project_id}.'''
        result = self._values.get("project_id")
        assert result is not None, "Required property 'project_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#type EventTrigger#type}.'''
        result = self._values.get("type")
        assert result is not None, "Required property 'type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def config_collection(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_collection EventTrigger#config_collection}.'''
        result = self._values.get("config_collection")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def config_database(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_database EventTrigger#config_database}.'''
        result = self._values.get("config_database")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def config_full_document(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_full_document EventTrigger#config_full_document}.'''
        result = self._values.get("config_full_document")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def config_full_document_before(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_full_document_before EventTrigger#config_full_document_before}.'''
        result = self._values.get("config_full_document_before")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def config_match(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_match EventTrigger#config_match}.'''
        result = self._values.get("config_match")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def config_operation_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_operation_type EventTrigger#config_operation_type}.'''
        result = self._values.get("config_operation_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def config_operation_types(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_operation_types EventTrigger#config_operation_types}.'''
        result = self._values.get("config_operation_types")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def config_project(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_project EventTrigger#config_project}.'''
        result = self._values.get("config_project")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def config_providers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_providers EventTrigger#config_providers}.'''
        result = self._values.get("config_providers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def config_schedule(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_schedule EventTrigger#config_schedule}.'''
        result = self._values.get("config_schedule")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def config_service_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_service_id EventTrigger#config_service_id}.'''
        result = self._values.get("config_service_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#disabled EventTrigger#disabled}.'''
        result = self._values.get("disabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def event_processors(self) -> typing.Optional["EventTriggerEventProcessors"]:
        '''event_processors block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#event_processors EventTrigger#event_processors}
        '''
        result = self._values.get("event_processors")
        return typing.cast(typing.Optional["EventTriggerEventProcessors"], result)

    @builtins.property
    def function_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#function_id EventTrigger#function_id}.'''
        result = self._values.get("function_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#id EventTrigger#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def unordered(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#unordered EventTrigger#unordered}.'''
        result = self._values.get("unordered")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EventTriggerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.eventTrigger.EventTriggerEventProcessors",
    jsii_struct_bases=[],
    name_mapping={"aws_eventbridge": "awsEventbridge"},
)
class EventTriggerEventProcessors:
    def __init__(
        self,
        *,
        aws_eventbridge: typing.Optional[typing.Union["EventTriggerEventProcessorsAwsEventbridge", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param aws_eventbridge: aws_eventbridge block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#aws_eventbridge EventTrigger#aws_eventbridge}
        '''
        if isinstance(aws_eventbridge, dict):
            aws_eventbridge = EventTriggerEventProcessorsAwsEventbridge(**aws_eventbridge)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df141f053379494f8796e2877b4f61738ac41085bf28acd1546479b1c1d7abe3)
            check_type(argname="argument aws_eventbridge", value=aws_eventbridge, expected_type=type_hints["aws_eventbridge"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if aws_eventbridge is not None:
            self._values["aws_eventbridge"] = aws_eventbridge

    @builtins.property
    def aws_eventbridge(
        self,
    ) -> typing.Optional["EventTriggerEventProcessorsAwsEventbridge"]:
        '''aws_eventbridge block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#aws_eventbridge EventTrigger#aws_eventbridge}
        '''
        result = self._values.get("aws_eventbridge")
        return typing.cast(typing.Optional["EventTriggerEventProcessorsAwsEventbridge"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EventTriggerEventProcessors(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.eventTrigger.EventTriggerEventProcessorsAwsEventbridge",
    jsii_struct_bases=[],
    name_mapping={
        "config_account_id": "configAccountId",
        "config_region": "configRegion",
    },
)
class EventTriggerEventProcessorsAwsEventbridge:
    def __init__(
        self,
        *,
        config_account_id: typing.Optional[builtins.str] = None,
        config_region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param config_account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_account_id EventTrigger#config_account_id}.
        :param config_region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_region EventTrigger#config_region}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e382faf7eec345596efd6fb8c3d241291625fbea10a383193634923829d1d240)
            check_type(argname="argument config_account_id", value=config_account_id, expected_type=type_hints["config_account_id"])
            check_type(argname="argument config_region", value=config_region, expected_type=type_hints["config_region"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if config_account_id is not None:
            self._values["config_account_id"] = config_account_id
        if config_region is not None:
            self._values["config_region"] = config_region

    @builtins.property
    def config_account_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_account_id EventTrigger#config_account_id}.'''
        result = self._values.get("config_account_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def config_region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_region EventTrigger#config_region}.'''
        result = self._values.get("config_region")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EventTriggerEventProcessorsAwsEventbridge(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class EventTriggerEventProcessorsAwsEventbridgeOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.eventTrigger.EventTriggerEventProcessorsAwsEventbridgeOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ea9b1401b9b627d4ee2044692c4c4ae573c8c2b2ab99d42cbfac5eaf4e790c59)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetConfigAccountId")
    def reset_config_account_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfigAccountId", []))

    @jsii.member(jsii_name="resetConfigRegion")
    def reset_config_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfigRegion", []))

    @builtins.property
    @jsii.member(jsii_name="configAccountIdInput")
    def config_account_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "configAccountIdInput"))

    @builtins.property
    @jsii.member(jsii_name="configRegionInput")
    def config_region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "configRegionInput"))

    @builtins.property
    @jsii.member(jsii_name="configAccountId")
    def config_account_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configAccountId"))

    @config_account_id.setter
    def config_account_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8dd98a827da160d01c89f3796fc428e014ec8b49af6cb7ccb17fc3133239300c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "configAccountId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="configRegion")
    def config_region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "configRegion"))

    @config_region.setter
    def config_region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9ae2155d9780f00e957e8e91db6c6732755f217b75e3fb7a6808c954dfb19a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "configRegion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[EventTriggerEventProcessorsAwsEventbridge]:
        return typing.cast(typing.Optional[EventTriggerEventProcessorsAwsEventbridge], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[EventTriggerEventProcessorsAwsEventbridge],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f386971b155b751f80e2d06fa28aa3531b54704077ad5d93d88263b19e42c47)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class EventTriggerEventProcessorsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.eventTrigger.EventTriggerEventProcessorsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1c5b61066018571a15cdbd319e9dc9c8e66d8bad8a4b62f9738494a8f9d2d6fa)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putAwsEventbridge")
    def put_aws_eventbridge(
        self,
        *,
        config_account_id: typing.Optional[builtins.str] = None,
        config_region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param config_account_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_account_id EventTrigger#config_account_id}.
        :param config_region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/event_trigger#config_region EventTrigger#config_region}.
        '''
        value = EventTriggerEventProcessorsAwsEventbridge(
            config_account_id=config_account_id, config_region=config_region
        )

        return typing.cast(None, jsii.invoke(self, "putAwsEventbridge", [value]))

    @jsii.member(jsii_name="resetAwsEventbridge")
    def reset_aws_eventbridge(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAwsEventbridge", []))

    @builtins.property
    @jsii.member(jsii_name="awsEventbridge")
    def aws_eventbridge(
        self,
    ) -> EventTriggerEventProcessorsAwsEventbridgeOutputReference:
        return typing.cast(EventTriggerEventProcessorsAwsEventbridgeOutputReference, jsii.get(self, "awsEventbridge"))

    @builtins.property
    @jsii.member(jsii_name="awsEventbridgeInput")
    def aws_eventbridge_input(
        self,
    ) -> typing.Optional[EventTriggerEventProcessorsAwsEventbridge]:
        return typing.cast(typing.Optional[EventTriggerEventProcessorsAwsEventbridge], jsii.get(self, "awsEventbridgeInput"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[EventTriggerEventProcessors]:
        return typing.cast(typing.Optional[EventTriggerEventProcessors], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[EventTriggerEventProcessors],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a38c4c1ca02dc6a43456e2a60cd51efc5c89b071369395b6f499f1cb4dad217e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "EventTrigger",
    "EventTriggerConfig",
    "EventTriggerEventProcessors",
    "EventTriggerEventProcessorsAwsEventbridge",
    "EventTriggerEventProcessorsAwsEventbridgeOutputReference",
    "EventTriggerEventProcessorsOutputReference",
]

publication.publish()

def _typecheckingstub__17d3332aed0f8331f133eea2b5dcbd3f7d5aa449d882e1a1ec4b9756c88b7907(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    app_id: builtins.str,
    name: builtins.str,
    project_id: builtins.str,
    type: builtins.str,
    config_collection: typing.Optional[builtins.str] = None,
    config_database: typing.Optional[builtins.str] = None,
    config_full_document: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    config_full_document_before: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    config_match: typing.Optional[builtins.str] = None,
    config_operation_type: typing.Optional[builtins.str] = None,
    config_operation_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    config_project: typing.Optional[builtins.str] = None,
    config_providers: typing.Optional[typing.Sequence[builtins.str]] = None,
    config_schedule: typing.Optional[builtins.str] = None,
    config_service_id: typing.Optional[builtins.str] = None,
    disabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    event_processors: typing.Optional[typing.Union[EventTriggerEventProcessors, typing.Dict[builtins.str, typing.Any]]] = None,
    function_id: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    unordered: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__bf71514d99385648ae092ecb2097d4df04079bced06164a1b1cb28bd796bd8cd(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3595d6b251d5983e1bd5e7392c6fdbc774d8594660c5eb32505a60647b4ac39e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81b46f87e392acc6fea38599e1ce3679dc23592841b12daa5116e1e46d317ed3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85f47bec517a0d0113156f7bfa02dc0449869c1a774c4715b45132c23c12fa23(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8abaceafc04393ecdab561c8f87c3801bfc640323e2d2f0c40c511717f946377(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__501f139b805e731de1ec3820fab96197e0c0297d0a53d5ffca9c7590c06d37d1(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fa8bb715d4bff64ea016552cee01963f9a7178a812d9523c9d6b00c786e1fe4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__200a4ed0e4aa6fb6fa61f6f530d1ab39c19b92c8670b531cf944e7bd32b0ee83(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3d430549e75e5401d81dc8bdd8d3e67af012eee8297341910792346f634f0d3(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68854a3d0a857de060e3b9b067a6ec1eb3d5175ba36dc625f3f99a4c7d1153c0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd3e465dbea3d3ac003edeb64eecc5d9bc62c9b27e6a6695af0bace64c26c84c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a313862363506ea896b01a7c41cd4279f2eafce7959015d3ea7dca8baa474737(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9851e6ed669265177d187f1b89fb749e8fd750d13a43e16351f76620554929af(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6a945d4b203cb5ed3a2895465005559f195bc4355920d86b96a5e3b616a2036(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8995d91cbf8eb52bedc1a7621f20f4b8242000698692e75a7389d1a50c8facb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d93be735b54cd6c703c21d7860fb088bc1c0d8e43e6237b6f52f63f36f0e1075(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b52be3e091f9890f160cbd57d6ebacabb75fce8224ed54f81ad76a71d96facc1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c86f61328459ec39fe2575e0277567b93c8c5fe1070611ceb507ba527e885e0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9627d9500f830f695def82ab9a81112ea7ee546bfdfef266d6dc31548f707a77(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fbe57ad8b5848ccda8795bc9fd8acb4207f44a0e794e4545bba0e2ecd4258013(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d59f9b1046b25c198fa9be526af0111fd8ecdb34793a9fdacdc3798b636a93e(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    app_id: builtins.str,
    name: builtins.str,
    project_id: builtins.str,
    type: builtins.str,
    config_collection: typing.Optional[builtins.str] = None,
    config_database: typing.Optional[builtins.str] = None,
    config_full_document: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    config_full_document_before: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    config_match: typing.Optional[builtins.str] = None,
    config_operation_type: typing.Optional[builtins.str] = None,
    config_operation_types: typing.Optional[typing.Sequence[builtins.str]] = None,
    config_project: typing.Optional[builtins.str] = None,
    config_providers: typing.Optional[typing.Sequence[builtins.str]] = None,
    config_schedule: typing.Optional[builtins.str] = None,
    config_service_id: typing.Optional[builtins.str] = None,
    disabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    event_processors: typing.Optional[typing.Union[EventTriggerEventProcessors, typing.Dict[builtins.str, typing.Any]]] = None,
    function_id: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    unordered: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df141f053379494f8796e2877b4f61738ac41085bf28acd1546479b1c1d7abe3(
    *,
    aws_eventbridge: typing.Optional[typing.Union[EventTriggerEventProcessorsAwsEventbridge, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e382faf7eec345596efd6fb8c3d241291625fbea10a383193634923829d1d240(
    *,
    config_account_id: typing.Optional[builtins.str] = None,
    config_region: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea9b1401b9b627d4ee2044692c4c4ae573c8c2b2ab99d42cbfac5eaf4e790c59(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8dd98a827da160d01c89f3796fc428e014ec8b49af6cb7ccb17fc3133239300c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9ae2155d9780f00e957e8e91db6c6732755f217b75e3fb7a6808c954dfb19a6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f386971b155b751f80e2d06fa28aa3531b54704077ad5d93d88263b19e42c47(
    value: typing.Optional[EventTriggerEventProcessorsAwsEventbridge],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c5b61066018571a15cdbd319e9dc9c8e66d8bad8a4b62f9738494a8f9d2d6fa(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a38c4c1ca02dc6a43456e2a60cd51efc5c89b071369395b6f499f1cb4dad217e(
    value: typing.Optional[EventTriggerEventProcessors],
) -> None:
    """Type checking stubs"""
    pass
