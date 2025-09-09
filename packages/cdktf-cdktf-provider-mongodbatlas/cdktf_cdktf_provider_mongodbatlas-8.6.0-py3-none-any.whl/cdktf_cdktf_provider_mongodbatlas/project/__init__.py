r'''
# `mongodbatlas_project`

Refer to the Terraform Registry for docs: [`mongodbatlas_project`](https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project).
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


class Project(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.project.Project",
):
    '''Represents a {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project mongodbatlas_project}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        name: builtins.str,
        org_id: builtins.str,
        is_collect_database_specifics_statistics_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        is_data_explorer_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        is_extended_storage_sizes_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        is_performance_advisor_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        is_realtime_performance_panel_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        is_schema_advisor_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        is_slow_operation_thresholding_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        limits: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ProjectLimits", typing.Dict[builtins.str, typing.Any]]]]] = None,
        project_owner_id: typing.Optional[builtins.str] = None,
        region_usage_restrictions: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        teams: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ProjectTeams", typing.Dict[builtins.str, typing.Any]]]]] = None,
        with_default_alerts_settings: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project mongodbatlas_project} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#name Project#name}.
        :param org_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#org_id Project#org_id}.
        :param is_collect_database_specifics_statistics_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#is_collect_database_specifics_statistics_enabled Project#is_collect_database_specifics_statistics_enabled}.
        :param is_data_explorer_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#is_data_explorer_enabled Project#is_data_explorer_enabled}.
        :param is_extended_storage_sizes_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#is_extended_storage_sizes_enabled Project#is_extended_storage_sizes_enabled}.
        :param is_performance_advisor_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#is_performance_advisor_enabled Project#is_performance_advisor_enabled}.
        :param is_realtime_performance_panel_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#is_realtime_performance_panel_enabled Project#is_realtime_performance_panel_enabled}.
        :param is_schema_advisor_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#is_schema_advisor_enabled Project#is_schema_advisor_enabled}.
        :param is_slow_operation_thresholding_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#is_slow_operation_thresholding_enabled Project#is_slow_operation_thresholding_enabled}.
        :param limits: limits block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#limits Project#limits}
        :param project_owner_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#project_owner_id Project#project_owner_id}.
        :param region_usage_restrictions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#region_usage_restrictions Project#region_usage_restrictions}.
        :param tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#tags Project#tags}.
        :param teams: teams block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#teams Project#teams}
        :param with_default_alerts_settings: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#with_default_alerts_settings Project#with_default_alerts_settings}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d7a170c16ee3d7749a2e1a1597ff9942a4f15acab9c14e51e3e2c98f32c7ccd)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = ProjectConfig(
            name=name,
            org_id=org_id,
            is_collect_database_specifics_statistics_enabled=is_collect_database_specifics_statistics_enabled,
            is_data_explorer_enabled=is_data_explorer_enabled,
            is_extended_storage_sizes_enabled=is_extended_storage_sizes_enabled,
            is_performance_advisor_enabled=is_performance_advisor_enabled,
            is_realtime_performance_panel_enabled=is_realtime_performance_panel_enabled,
            is_schema_advisor_enabled=is_schema_advisor_enabled,
            is_slow_operation_thresholding_enabled=is_slow_operation_thresholding_enabled,
            limits=limits,
            project_owner_id=project_owner_id,
            region_usage_restrictions=region_usage_restrictions,
            tags=tags,
            teams=teams,
            with_default_alerts_settings=with_default_alerts_settings,
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
        '''Generates CDKTF code for importing a Project resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the Project to import.
        :param import_from_id: The id of the existing Project that should be imported. Refer to the {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the Project to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8dfb33ef2f1bc1e18aea988d0f7a8b337ad7b85ec9bc1940ff1af6447850f66b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putLimits")
    def put_limits(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ProjectLimits", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4042a529353ed63629e6a3b4be106c8fcae0bc9712fe2549a6f56505e74fc6b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putLimits", [value]))

    @jsii.member(jsii_name="putTeams")
    def put_teams(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ProjectTeams", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62db4d9da517db2e656400e303bb2208dca445fbd3b89005ab2ff7b77edadfb7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTeams", [value]))

    @jsii.member(jsii_name="resetIsCollectDatabaseSpecificsStatisticsEnabled")
    def reset_is_collect_database_specifics_statistics_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsCollectDatabaseSpecificsStatisticsEnabled", []))

    @jsii.member(jsii_name="resetIsDataExplorerEnabled")
    def reset_is_data_explorer_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsDataExplorerEnabled", []))

    @jsii.member(jsii_name="resetIsExtendedStorageSizesEnabled")
    def reset_is_extended_storage_sizes_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsExtendedStorageSizesEnabled", []))

    @jsii.member(jsii_name="resetIsPerformanceAdvisorEnabled")
    def reset_is_performance_advisor_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsPerformanceAdvisorEnabled", []))

    @jsii.member(jsii_name="resetIsRealtimePerformancePanelEnabled")
    def reset_is_realtime_performance_panel_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsRealtimePerformancePanelEnabled", []))

    @jsii.member(jsii_name="resetIsSchemaAdvisorEnabled")
    def reset_is_schema_advisor_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsSchemaAdvisorEnabled", []))

    @jsii.member(jsii_name="resetIsSlowOperationThresholdingEnabled")
    def reset_is_slow_operation_thresholding_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsSlowOperationThresholdingEnabled", []))

    @jsii.member(jsii_name="resetLimits")
    def reset_limits(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLimits", []))

    @jsii.member(jsii_name="resetProjectOwnerId")
    def reset_project_owner_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProjectOwnerId", []))

    @jsii.member(jsii_name="resetRegionUsageRestrictions")
    def reset_region_usage_restrictions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegionUsageRestrictions", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTeams")
    def reset_teams(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTeams", []))

    @jsii.member(jsii_name="resetWithDefaultAlertsSettings")
    def reset_with_default_alerts_settings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWithDefaultAlertsSettings", []))

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
    @jsii.member(jsii_name="clusterCount")
    def cluster_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "clusterCount"))

    @builtins.property
    @jsii.member(jsii_name="created")
    def created(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "created"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="ipAddresses")
    def ip_addresses(self) -> "ProjectIpAddressesOutputReference":
        return typing.cast("ProjectIpAddressesOutputReference", jsii.get(self, "ipAddresses"))

    @builtins.property
    @jsii.member(jsii_name="limits")
    def limits(self) -> "ProjectLimitsList":
        return typing.cast("ProjectLimitsList", jsii.get(self, "limits"))

    @builtins.property
    @jsii.member(jsii_name="teams")
    def teams(self) -> "ProjectTeamsList":
        return typing.cast("ProjectTeamsList", jsii.get(self, "teams"))

    @builtins.property
    @jsii.member(jsii_name="isCollectDatabaseSpecificsStatisticsEnabledInput")
    def is_collect_database_specifics_statistics_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isCollectDatabaseSpecificsStatisticsEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="isDataExplorerEnabledInput")
    def is_data_explorer_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isDataExplorerEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="isExtendedStorageSizesEnabledInput")
    def is_extended_storage_sizes_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isExtendedStorageSizesEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="isPerformanceAdvisorEnabledInput")
    def is_performance_advisor_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isPerformanceAdvisorEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="isRealtimePerformancePanelEnabledInput")
    def is_realtime_performance_panel_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isRealtimePerformancePanelEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="isSchemaAdvisorEnabledInput")
    def is_schema_advisor_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isSchemaAdvisorEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="isSlowOperationThresholdingEnabledInput")
    def is_slow_operation_thresholding_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isSlowOperationThresholdingEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="limitsInput")
    def limits_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ProjectLimits"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ProjectLimits"]]], jsii.get(self, "limitsInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="orgIdInput")
    def org_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "orgIdInput"))

    @builtins.property
    @jsii.member(jsii_name="projectOwnerIdInput")
    def project_owner_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectOwnerIdInput"))

    @builtins.property
    @jsii.member(jsii_name="regionUsageRestrictionsInput")
    def region_usage_restrictions_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionUsageRestrictionsInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="teamsInput")
    def teams_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ProjectTeams"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ProjectTeams"]]], jsii.get(self, "teamsInput"))

    @builtins.property
    @jsii.member(jsii_name="withDefaultAlertsSettingsInput")
    def with_default_alerts_settings_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "withDefaultAlertsSettingsInput"))

    @builtins.property
    @jsii.member(jsii_name="isCollectDatabaseSpecificsStatisticsEnabled")
    def is_collect_database_specifics_statistics_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isCollectDatabaseSpecificsStatisticsEnabled"))

    @is_collect_database_specifics_statistics_enabled.setter
    def is_collect_database_specifics_statistics_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ed13b0c82fcbccc5f42317472fd6d38dd0564b0e676e0d4dbe7099d325c1279)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isCollectDatabaseSpecificsStatisticsEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isDataExplorerEnabled")
    def is_data_explorer_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isDataExplorerEnabled"))

    @is_data_explorer_enabled.setter
    def is_data_explorer_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b427bc1254e9875ed52737e822e9e5d4f117331f3e5f0203e09133789aa56f2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isDataExplorerEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isExtendedStorageSizesEnabled")
    def is_extended_storage_sizes_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isExtendedStorageSizesEnabled"))

    @is_extended_storage_sizes_enabled.setter
    def is_extended_storage_sizes_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__490821c1c18f14abad6b4807a2714eaedf8cf4e08ccdb0afeb6d7e89667ff21c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isExtendedStorageSizesEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isPerformanceAdvisorEnabled")
    def is_performance_advisor_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isPerformanceAdvisorEnabled"))

    @is_performance_advisor_enabled.setter
    def is_performance_advisor_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53fd1f0422b4b11af7c55db4e45bfdad07101563662d39829d18a9d61e2a185e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isPerformanceAdvisorEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isRealtimePerformancePanelEnabled")
    def is_realtime_performance_panel_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isRealtimePerformancePanelEnabled"))

    @is_realtime_performance_panel_enabled.setter
    def is_realtime_performance_panel_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a74741c03e52ff9f498c35e6d1efcabe03e14de861fda5409657fb75b487c66)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isRealtimePerformancePanelEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isSchemaAdvisorEnabled")
    def is_schema_advisor_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isSchemaAdvisorEnabled"))

    @is_schema_advisor_enabled.setter
    def is_schema_advisor_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2bebb280cb7cc531b4fe8d979dd24e0f9b86ba62f0235d71ff9bc7cb12b8c1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isSchemaAdvisorEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isSlowOperationThresholdingEnabled")
    def is_slow_operation_thresholding_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isSlowOperationThresholdingEnabled"))

    @is_slow_operation_thresholding_enabled.setter
    def is_slow_operation_thresholding_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a321c7289ae683901f5e2a069fecb6b558fc6ad5c5eb7b7b82d2d6f83af9a1a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isSlowOperationThresholdingEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9877c6d3de9b197338f85827372f832a76310c1cb3d1bde1200389329ce270c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="orgId")
    def org_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "orgId"))

    @org_id.setter
    def org_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56fa63757c44a2d36b14586e0c85f6b8e2b3a4a5d3f1ef7927bd9a9e8322302a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "orgId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectOwnerId")
    def project_owner_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectOwnerId"))

    @project_owner_id.setter
    def project_owner_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c17a62eb55e28fcf1d83f41eff2be9d9238606ead3c76bcd004c709a5df2be8b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectOwnerId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="regionUsageRestrictions")
    def region_usage_restrictions(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "regionUsageRestrictions"))

    @region_usage_restrictions.setter
    def region_usage_restrictions(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a95b780805ec47b6f1f798a4705b303527259dbbbe62e7907fb6f4e01f9eedf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "regionUsageRestrictions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8461b5b0666b7d4d31ce3884ddcbacf73e9ae860cb1908cc4b1551a64bb25949)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="withDefaultAlertsSettings")
    def with_default_alerts_settings(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "withDefaultAlertsSettings"))

    @with_default_alerts_settings.setter
    def with_default_alerts_settings(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35fa76ee4131e5c94898039410519ebaab4f5160f78c144f28b2f9250aab0240)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "withDefaultAlertsSettings", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.project.ProjectConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "name": "name",
        "org_id": "orgId",
        "is_collect_database_specifics_statistics_enabled": "isCollectDatabaseSpecificsStatisticsEnabled",
        "is_data_explorer_enabled": "isDataExplorerEnabled",
        "is_extended_storage_sizes_enabled": "isExtendedStorageSizesEnabled",
        "is_performance_advisor_enabled": "isPerformanceAdvisorEnabled",
        "is_realtime_performance_panel_enabled": "isRealtimePerformancePanelEnabled",
        "is_schema_advisor_enabled": "isSchemaAdvisorEnabled",
        "is_slow_operation_thresholding_enabled": "isSlowOperationThresholdingEnabled",
        "limits": "limits",
        "project_owner_id": "projectOwnerId",
        "region_usage_restrictions": "regionUsageRestrictions",
        "tags": "tags",
        "teams": "teams",
        "with_default_alerts_settings": "withDefaultAlertsSettings",
    },
)
class ProjectConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        name: builtins.str,
        org_id: builtins.str,
        is_collect_database_specifics_statistics_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        is_data_explorer_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        is_extended_storage_sizes_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        is_performance_advisor_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        is_realtime_performance_panel_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        is_schema_advisor_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        is_slow_operation_thresholding_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        limits: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ProjectLimits", typing.Dict[builtins.str, typing.Any]]]]] = None,
        project_owner_id: typing.Optional[builtins.str] = None,
        region_usage_restrictions: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        teams: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["ProjectTeams", typing.Dict[builtins.str, typing.Any]]]]] = None,
        with_default_alerts_settings: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#name Project#name}.
        :param org_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#org_id Project#org_id}.
        :param is_collect_database_specifics_statistics_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#is_collect_database_specifics_statistics_enabled Project#is_collect_database_specifics_statistics_enabled}.
        :param is_data_explorer_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#is_data_explorer_enabled Project#is_data_explorer_enabled}.
        :param is_extended_storage_sizes_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#is_extended_storage_sizes_enabled Project#is_extended_storage_sizes_enabled}.
        :param is_performance_advisor_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#is_performance_advisor_enabled Project#is_performance_advisor_enabled}.
        :param is_realtime_performance_panel_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#is_realtime_performance_panel_enabled Project#is_realtime_performance_panel_enabled}.
        :param is_schema_advisor_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#is_schema_advisor_enabled Project#is_schema_advisor_enabled}.
        :param is_slow_operation_thresholding_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#is_slow_operation_thresholding_enabled Project#is_slow_operation_thresholding_enabled}.
        :param limits: limits block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#limits Project#limits}
        :param project_owner_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#project_owner_id Project#project_owner_id}.
        :param region_usage_restrictions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#region_usage_restrictions Project#region_usage_restrictions}.
        :param tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#tags Project#tags}.
        :param teams: teams block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#teams Project#teams}
        :param with_default_alerts_settings: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#with_default_alerts_settings Project#with_default_alerts_settings}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf13e3da8485dd62c5423ed6934179902dd00b10349679ad3b25dba465581cf5)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument org_id", value=org_id, expected_type=type_hints["org_id"])
            check_type(argname="argument is_collect_database_specifics_statistics_enabled", value=is_collect_database_specifics_statistics_enabled, expected_type=type_hints["is_collect_database_specifics_statistics_enabled"])
            check_type(argname="argument is_data_explorer_enabled", value=is_data_explorer_enabled, expected_type=type_hints["is_data_explorer_enabled"])
            check_type(argname="argument is_extended_storage_sizes_enabled", value=is_extended_storage_sizes_enabled, expected_type=type_hints["is_extended_storage_sizes_enabled"])
            check_type(argname="argument is_performance_advisor_enabled", value=is_performance_advisor_enabled, expected_type=type_hints["is_performance_advisor_enabled"])
            check_type(argname="argument is_realtime_performance_panel_enabled", value=is_realtime_performance_panel_enabled, expected_type=type_hints["is_realtime_performance_panel_enabled"])
            check_type(argname="argument is_schema_advisor_enabled", value=is_schema_advisor_enabled, expected_type=type_hints["is_schema_advisor_enabled"])
            check_type(argname="argument is_slow_operation_thresholding_enabled", value=is_slow_operation_thresholding_enabled, expected_type=type_hints["is_slow_operation_thresholding_enabled"])
            check_type(argname="argument limits", value=limits, expected_type=type_hints["limits"])
            check_type(argname="argument project_owner_id", value=project_owner_id, expected_type=type_hints["project_owner_id"])
            check_type(argname="argument region_usage_restrictions", value=region_usage_restrictions, expected_type=type_hints["region_usage_restrictions"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument teams", value=teams, expected_type=type_hints["teams"])
            check_type(argname="argument with_default_alerts_settings", value=with_default_alerts_settings, expected_type=type_hints["with_default_alerts_settings"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "org_id": org_id,
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
        if is_collect_database_specifics_statistics_enabled is not None:
            self._values["is_collect_database_specifics_statistics_enabled"] = is_collect_database_specifics_statistics_enabled
        if is_data_explorer_enabled is not None:
            self._values["is_data_explorer_enabled"] = is_data_explorer_enabled
        if is_extended_storage_sizes_enabled is not None:
            self._values["is_extended_storage_sizes_enabled"] = is_extended_storage_sizes_enabled
        if is_performance_advisor_enabled is not None:
            self._values["is_performance_advisor_enabled"] = is_performance_advisor_enabled
        if is_realtime_performance_panel_enabled is not None:
            self._values["is_realtime_performance_panel_enabled"] = is_realtime_performance_panel_enabled
        if is_schema_advisor_enabled is not None:
            self._values["is_schema_advisor_enabled"] = is_schema_advisor_enabled
        if is_slow_operation_thresholding_enabled is not None:
            self._values["is_slow_operation_thresholding_enabled"] = is_slow_operation_thresholding_enabled
        if limits is not None:
            self._values["limits"] = limits
        if project_owner_id is not None:
            self._values["project_owner_id"] = project_owner_id
        if region_usage_restrictions is not None:
            self._values["region_usage_restrictions"] = region_usage_restrictions
        if tags is not None:
            self._values["tags"] = tags
        if teams is not None:
            self._values["teams"] = teams
        if with_default_alerts_settings is not None:
            self._values["with_default_alerts_settings"] = with_default_alerts_settings

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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#name Project#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def org_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#org_id Project#org_id}.'''
        result = self._values.get("org_id")
        assert result is not None, "Required property 'org_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def is_collect_database_specifics_statistics_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#is_collect_database_specifics_statistics_enabled Project#is_collect_database_specifics_statistics_enabled}.'''
        result = self._values.get("is_collect_database_specifics_statistics_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def is_data_explorer_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#is_data_explorer_enabled Project#is_data_explorer_enabled}.'''
        result = self._values.get("is_data_explorer_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def is_extended_storage_sizes_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#is_extended_storage_sizes_enabled Project#is_extended_storage_sizes_enabled}.'''
        result = self._values.get("is_extended_storage_sizes_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def is_performance_advisor_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#is_performance_advisor_enabled Project#is_performance_advisor_enabled}.'''
        result = self._values.get("is_performance_advisor_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def is_realtime_performance_panel_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#is_realtime_performance_panel_enabled Project#is_realtime_performance_panel_enabled}.'''
        result = self._values.get("is_realtime_performance_panel_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def is_schema_advisor_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#is_schema_advisor_enabled Project#is_schema_advisor_enabled}.'''
        result = self._values.get("is_schema_advisor_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def is_slow_operation_thresholding_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#is_slow_operation_thresholding_enabled Project#is_slow_operation_thresholding_enabled}.'''
        result = self._values.get("is_slow_operation_thresholding_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def limits(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ProjectLimits"]]]:
        '''limits block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#limits Project#limits}
        '''
        result = self._values.get("limits")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ProjectLimits"]]], result)

    @builtins.property
    def project_owner_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#project_owner_id Project#project_owner_id}.'''
        result = self._values.get("project_owner_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region_usage_restrictions(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#region_usage_restrictions Project#region_usage_restrictions}.'''
        result = self._values.get("region_usage_restrictions")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#tags Project#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def teams(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ProjectTeams"]]]:
        '''teams block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#teams Project#teams}
        '''
        result = self._values.get("teams")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["ProjectTeams"]]], result)

    @builtins.property
    def with_default_alerts_settings(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#with_default_alerts_settings Project#with_default_alerts_settings}.'''
        result = self._values.get("with_default_alerts_settings")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProjectConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.project.ProjectIpAddresses",
    jsii_struct_bases=[],
    name_mapping={},
)
class ProjectIpAddresses:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProjectIpAddresses(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ProjectIpAddressesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.project.ProjectIpAddressesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b755cafec7d5850eb5e9d171c0a72a07741d8f0edf2ab47035dbc1108d5203c3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="services")
    def services(self) -> "ProjectIpAddressesServicesOutputReference":
        return typing.cast("ProjectIpAddressesServicesOutputReference", jsii.get(self, "services"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ProjectIpAddresses]:
        return typing.cast(typing.Optional[ProjectIpAddresses], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[ProjectIpAddresses]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18b27802b64c80c60732dbf2a15721bc6c4cfa6d05deb395217a796703bd7308)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.project.ProjectIpAddressesServices",
    jsii_struct_bases=[],
    name_mapping={},
)
class ProjectIpAddressesServices:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProjectIpAddressesServices(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.project.ProjectIpAddressesServicesClusters",
    jsii_struct_bases=[],
    name_mapping={},
)
class ProjectIpAddressesServicesClusters:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProjectIpAddressesServicesClusters(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ProjectIpAddressesServicesClustersList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.project.ProjectIpAddressesServicesClustersList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6c7baec34b1c25a3349c7aa1c3809af65f868ffb37594835ec948ba2f15d7400)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "ProjectIpAddressesServicesClustersOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77153031f4589680b08b00df6c2438eee0b2d1464862280a0ef934684600c086)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ProjectIpAddressesServicesClustersOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96a5280ff67ac364d7e58e4f44b351a704c01ec231b5bf9d8b8b40646aac6097)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fc26941dd16ed54cbe1c5e5b017397e16ec49cc8205eabfb6578b4df481fa039)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d93a9f46a71cf1c6d3c351f02a8b2e6c6554b712b12c3edfb8746835bb5e7fd8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class ProjectIpAddressesServicesClustersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.project.ProjectIpAddressesServicesClustersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__61284f80ff3314d7ab21e4122adf6b97615d0951266d1c8346a0deb37aaeca1b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterName"))

    @builtins.property
    @jsii.member(jsii_name="inbound")
    def inbound(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "inbound"))

    @builtins.property
    @jsii.member(jsii_name="outbound")
    def outbound(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "outbound"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ProjectIpAddressesServicesClusters]:
        return typing.cast(typing.Optional[ProjectIpAddressesServicesClusters], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ProjectIpAddressesServicesClusters],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95fb59097b05aa4c76e3d0f010ca8ce230fdedd15ec07ecb220e6e3494aa5d01)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ProjectIpAddressesServicesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.project.ProjectIpAddressesServicesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3c3c3e5a475fb309317c318187d7eaf3ce53d3b69ce262c28395a5d61bf6888c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="clusters")
    def clusters(self) -> ProjectIpAddressesServicesClustersList:
        return typing.cast(ProjectIpAddressesServicesClustersList, jsii.get(self, "clusters"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[ProjectIpAddressesServices]:
        return typing.cast(typing.Optional[ProjectIpAddressesServices], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[ProjectIpAddressesServices],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc1c78a8a36a25f0e00583a59f51f7997be4e15b2fc6b884b64a812658e2d2bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.project.ProjectLimits",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "value": "value"},
)
class ProjectLimits:
    def __init__(self, *, name: builtins.str, value: jsii.Number) -> None:
        '''
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#name Project#name}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#value Project#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b31de542bca9ec216d822020e457deae35f120659d6270fe9769e7c6bb094ae8)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
            "value": value,
        }

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#name Project#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#value Project#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProjectLimits(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ProjectLimitsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.project.ProjectLimitsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0d489cd1be9581e3893a41adc27aed9cb9b14eec547338dfa114305970e4070b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ProjectLimitsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1552fe3207c1518047ff8d0c9381f238715ad53c1aa85be7bc939af6f9558d5)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ProjectLimitsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68fec6840b4fd742d8e9c50061cc1afab5d84293b2486e5015d175588a36c363)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2179d369fe80a00189b0477aff1baf60c4f64bf5abb1ac23f1cf67b7014f4fdf)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cac4852751304ad8468b466fafd6ed4512aed5091dbd1e92ef43ccd3f6b150e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ProjectLimits]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ProjectLimits]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ProjectLimits]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfeaebf0d147d8f2857477c11a971af3b5f49ce300cc4e583fd2a1a977a4c596)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ProjectLimitsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.project.ProjectLimitsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__753efb8bf428e3cdca25a8983757172f978248061bf2ff4d89c50edfbb5274bd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="currentUsage")
    def current_usage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "currentUsage"))

    @builtins.property
    @jsii.member(jsii_name="defaultLimit")
    def default_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "defaultLimit"))

    @builtins.property
    @jsii.member(jsii_name="maximumLimit")
    def maximum_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maximumLimit"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c4b7509144bf795ffd19cb9f4c7f2deea8b509232945925e8580782c3b01c08)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "value"))

    @value.setter
    def value(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__325357285c9434f36cbb173f2ce31fb4b4bafccea9b20ba6385245c457913f8c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ProjectLimits]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ProjectLimits]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ProjectLimits]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e5e649e22904b3ce9a90139020abb8486194c942c1b484669a61755acbfc05de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.project.ProjectTeams",
    jsii_struct_bases=[],
    name_mapping={"role_names": "roleNames", "team_id": "teamId"},
)
class ProjectTeams:
    def __init__(
        self,
        *,
        role_names: typing.Sequence[builtins.str],
        team_id: builtins.str,
    ) -> None:
        '''
        :param role_names: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#role_names Project#role_names}.
        :param team_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#team_id Project#team_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce41930cf839a0737fb23d79189594a8fac75bf267949ddb55ec67141b3f293f)
            check_type(argname="argument role_names", value=role_names, expected_type=type_hints["role_names"])
            check_type(argname="argument team_id", value=team_id, expected_type=type_hints["team_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "role_names": role_names,
            "team_id": team_id,
        }

    @builtins.property
    def role_names(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#role_names Project#role_names}.'''
        result = self._values.get("role_names")
        assert result is not None, "Required property 'role_names' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def team_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/project#team_id Project#team_id}.'''
        result = self._values.get("team_id")
        assert result is not None, "Required property 'team_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ProjectTeams(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class ProjectTeamsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.project.ProjectTeamsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e32a9b286007d51f936d4285652c877b5e27743d30496a35c3f91a8127e7af05)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "ProjectTeamsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b7b46ac6533125045a512953f5eb31f692ddf3ffa431d6d5d060a367e859f33e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("ProjectTeamsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60275064266cfe5ddf284d123b690718ff4c34fa7f620193cb7c03ff1ae4dfbd)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e3722e8092c49e69acdf2817656cb9efabb9deebb214abbbcf48773e71331a2c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0213c5db4458923d82ca1226f07621ef223bfc584ac4d7c2df5e7d4a2dad8208)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ProjectTeams]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ProjectTeams]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ProjectTeams]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b136d533a3e072dbb8723fd0ba7720d58b9399a78e9c4df74e81411ed9e9c6bc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class ProjectTeamsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.project.ProjectTeamsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__48788858743b2f4f84d47ccc4a3e1ad2e56d97403aab5543c123cac30714974d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="roleNamesInput")
    def role_names_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "roleNamesInput"))

    @builtins.property
    @jsii.member(jsii_name="teamIdInput")
    def team_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "teamIdInput"))

    @builtins.property
    @jsii.member(jsii_name="roleNames")
    def role_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "roleNames"))

    @role_names.setter
    def role_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f2dcbb7f00862d79c33529d3a7e8e5656c6127516bb1373d52d69359bfbbe010)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "roleNames", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="teamId")
    def team_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "teamId"))

    @team_id.setter
    def team_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__03b9d00a63f63cac3574aff0fb9aea85fbaa4ee172e1b5d087e0bbbc199507de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "teamId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ProjectTeams]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ProjectTeams]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ProjectTeams]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c097efe0e029bb66d1f350cf0995c3998162dafebe9154970b041b531374933e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "Project",
    "ProjectConfig",
    "ProjectIpAddresses",
    "ProjectIpAddressesOutputReference",
    "ProjectIpAddressesServices",
    "ProjectIpAddressesServicesClusters",
    "ProjectIpAddressesServicesClustersList",
    "ProjectIpAddressesServicesClustersOutputReference",
    "ProjectIpAddressesServicesOutputReference",
    "ProjectLimits",
    "ProjectLimitsList",
    "ProjectLimitsOutputReference",
    "ProjectTeams",
    "ProjectTeamsList",
    "ProjectTeamsOutputReference",
]

publication.publish()

def _typecheckingstub__9d7a170c16ee3d7749a2e1a1597ff9942a4f15acab9c14e51e3e2c98f32c7ccd(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    name: builtins.str,
    org_id: builtins.str,
    is_collect_database_specifics_statistics_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    is_data_explorer_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    is_extended_storage_sizes_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    is_performance_advisor_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    is_realtime_performance_panel_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    is_schema_advisor_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    is_slow_operation_thresholding_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    limits: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ProjectLimits, typing.Dict[builtins.str, typing.Any]]]]] = None,
    project_owner_id: typing.Optional[builtins.str] = None,
    region_usage_restrictions: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    teams: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ProjectTeams, typing.Dict[builtins.str, typing.Any]]]]] = None,
    with_default_alerts_settings: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__8dfb33ef2f1bc1e18aea988d0f7a8b337ad7b85ec9bc1940ff1af6447850f66b(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4042a529353ed63629e6a3b4be106c8fcae0bc9712fe2549a6f56505e74fc6b(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ProjectLimits, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62db4d9da517db2e656400e303bb2208dca445fbd3b89005ab2ff7b77edadfb7(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ProjectTeams, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ed13b0c82fcbccc5f42317472fd6d38dd0564b0e676e0d4dbe7099d325c1279(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b427bc1254e9875ed52737e822e9e5d4f117331f3e5f0203e09133789aa56f2(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__490821c1c18f14abad6b4807a2714eaedf8cf4e08ccdb0afeb6d7e89667ff21c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53fd1f0422b4b11af7c55db4e45bfdad07101563662d39829d18a9d61e2a185e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a74741c03e52ff9f498c35e6d1efcabe03e14de861fda5409657fb75b487c66(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2bebb280cb7cc531b4fe8d979dd24e0f9b86ba62f0235d71ff9bc7cb12b8c1c(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a321c7289ae683901f5e2a069fecb6b558fc6ad5c5eb7b7b82d2d6f83af9a1a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9877c6d3de9b197338f85827372f832a76310c1cb3d1bde1200389329ce270c7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56fa63757c44a2d36b14586e0c85f6b8e2b3a4a5d3f1ef7927bd9a9e8322302a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c17a62eb55e28fcf1d83f41eff2be9d9238606ead3c76bcd004c709a5df2be8b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a95b780805ec47b6f1f798a4705b303527259dbbbe62e7907fb6f4e01f9eedf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8461b5b0666b7d4d31ce3884ddcbacf73e9ae860cb1908cc4b1551a64bb25949(
    value: typing.Mapping[builtins.str, builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35fa76ee4131e5c94898039410519ebaab4f5160f78c144f28b2f9250aab0240(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf13e3da8485dd62c5423ed6934179902dd00b10349679ad3b25dba465581cf5(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    org_id: builtins.str,
    is_collect_database_specifics_statistics_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    is_data_explorer_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    is_extended_storage_sizes_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    is_performance_advisor_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    is_realtime_performance_panel_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    is_schema_advisor_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    is_slow_operation_thresholding_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    limits: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ProjectLimits, typing.Dict[builtins.str, typing.Any]]]]] = None,
    project_owner_id: typing.Optional[builtins.str] = None,
    region_usage_restrictions: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    teams: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[ProjectTeams, typing.Dict[builtins.str, typing.Any]]]]] = None,
    with_default_alerts_settings: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b755cafec7d5850eb5e9d171c0a72a07741d8f0edf2ab47035dbc1108d5203c3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18b27802b64c80c60732dbf2a15721bc6c4cfa6d05deb395217a796703bd7308(
    value: typing.Optional[ProjectIpAddresses],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c7baec34b1c25a3349c7aa1c3809af65f868ffb37594835ec948ba2f15d7400(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77153031f4589680b08b00df6c2438eee0b2d1464862280a0ef934684600c086(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96a5280ff67ac364d7e58e4f44b351a704c01ec231b5bf9d8b8b40646aac6097(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc26941dd16ed54cbe1c5e5b017397e16ec49cc8205eabfb6578b4df481fa039(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d93a9f46a71cf1c6d3c351f02a8b2e6c6554b712b12c3edfb8746835bb5e7fd8(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61284f80ff3314d7ab21e4122adf6b97615d0951266d1c8346a0deb37aaeca1b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95fb59097b05aa4c76e3d0f010ca8ce230fdedd15ec07ecb220e6e3494aa5d01(
    value: typing.Optional[ProjectIpAddressesServicesClusters],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c3c3e5a475fb309317c318187d7eaf3ce53d3b69ce262c28395a5d61bf6888c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc1c78a8a36a25f0e00583a59f51f7997be4e15b2fc6b884b64a812658e2d2bf(
    value: typing.Optional[ProjectIpAddressesServices],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b31de542bca9ec216d822020e457deae35f120659d6270fe9769e7c6bb094ae8(
    *,
    name: builtins.str,
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d489cd1be9581e3893a41adc27aed9cb9b14eec547338dfa114305970e4070b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1552fe3207c1518047ff8d0c9381f238715ad53c1aa85be7bc939af6f9558d5(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68fec6840b4fd742d8e9c50061cc1afab5d84293b2486e5015d175588a36c363(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2179d369fe80a00189b0477aff1baf60c4f64bf5abb1ac23f1cf67b7014f4fdf(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cac4852751304ad8468b466fafd6ed4512aed5091dbd1e92ef43ccd3f6b150e0(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfeaebf0d147d8f2857477c11a971af3b5f49ce300cc4e583fd2a1a977a4c596(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ProjectLimits]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__753efb8bf428e3cdca25a8983757172f978248061bf2ff4d89c50edfbb5274bd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c4b7509144bf795ffd19cb9f4c7f2deea8b509232945925e8580782c3b01c08(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__325357285c9434f36cbb173f2ce31fb4b4bafccea9b20ba6385245c457913f8c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e5e649e22904b3ce9a90139020abb8486194c942c1b484669a61755acbfc05de(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ProjectLimits]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce41930cf839a0737fb23d79189594a8fac75bf267949ddb55ec67141b3f293f(
    *,
    role_names: typing.Sequence[builtins.str],
    team_id: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e32a9b286007d51f936d4285652c877b5e27743d30496a35c3f91a8127e7af05(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7b46ac6533125045a512953f5eb31f692ddf3ffa431d6d5d060a367e859f33e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60275064266cfe5ddf284d123b690718ff4c34fa7f620193cb7c03ff1ae4dfbd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3722e8092c49e69acdf2817656cb9efabb9deebb214abbbcf48773e71331a2c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0213c5db4458923d82ca1226f07621ef223bfc584ac4d7c2df5e7d4a2dad8208(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b136d533a3e072dbb8723fd0ba7720d58b9399a78e9c4df74e81411ed9e9c6bc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[ProjectTeams]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48788858743b2f4f84d47ccc4a3e1ad2e56d97403aab5543c123cac30714974d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2dcbb7f00862d79c33529d3a7e8e5656c6127516bb1373d52d69359bfbbe010(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__03b9d00a63f63cac3574aff0fb9aea85fbaa4ee172e1b5d087e0bbbc199507de(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c097efe0e029bb66d1f350cf0995c3998162dafebe9154970b041b531374933e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, ProjectTeams]],
) -> None:
    """Type checking stubs"""
    pass
