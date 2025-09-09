r'''
# `mongodbatlas_cloud_backup_schedule`

Refer to the Terraform Registry for docs: [`mongodbatlas_cloud_backup_schedule`](https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule).
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


class CloudBackupSchedule(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cloudBackupSchedule.CloudBackupSchedule",
):
    '''Represents a {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule mongodbatlas_cloud_backup_schedule}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        cluster_name: builtins.str,
        project_id: builtins.str,
        auto_export_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        copy_settings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CloudBackupScheduleCopySettings", typing.Dict[builtins.str, typing.Any]]]]] = None,
        export: typing.Optional[typing.Union["CloudBackupScheduleExport", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        policy_item_daily: typing.Optional[typing.Union["CloudBackupSchedulePolicyItemDaily", typing.Dict[builtins.str, typing.Any]]] = None,
        policy_item_hourly: typing.Optional[typing.Union["CloudBackupSchedulePolicyItemHourly", typing.Dict[builtins.str, typing.Any]]] = None,
        policy_item_monthly: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CloudBackupSchedulePolicyItemMonthly", typing.Dict[builtins.str, typing.Any]]]]] = None,
        policy_item_weekly: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CloudBackupSchedulePolicyItemWeekly", typing.Dict[builtins.str, typing.Any]]]]] = None,
        policy_item_yearly: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CloudBackupSchedulePolicyItemYearly", typing.Dict[builtins.str, typing.Any]]]]] = None,
        reference_hour_of_day: typing.Optional[jsii.Number] = None,
        reference_minute_of_hour: typing.Optional[jsii.Number] = None,
        restore_window_days: typing.Optional[jsii.Number] = None,
        update_snapshots: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        use_org_and_group_names_in_export_prefix: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule mongodbatlas_cloud_backup_schedule} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#cluster_name CloudBackupSchedule#cluster_name}.
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#project_id CloudBackupSchedule#project_id}.
        :param auto_export_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#auto_export_enabled CloudBackupSchedule#auto_export_enabled}.
        :param copy_settings: copy_settings block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#copy_settings CloudBackupSchedule#copy_settings}
        :param export: export block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#export CloudBackupSchedule#export}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#id CloudBackupSchedule#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param policy_item_daily: policy_item_daily block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#policy_item_daily CloudBackupSchedule#policy_item_daily}
        :param policy_item_hourly: policy_item_hourly block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#policy_item_hourly CloudBackupSchedule#policy_item_hourly}
        :param policy_item_monthly: policy_item_monthly block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#policy_item_monthly CloudBackupSchedule#policy_item_monthly}
        :param policy_item_weekly: policy_item_weekly block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#policy_item_weekly CloudBackupSchedule#policy_item_weekly}
        :param policy_item_yearly: policy_item_yearly block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#policy_item_yearly CloudBackupSchedule#policy_item_yearly}
        :param reference_hour_of_day: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#reference_hour_of_day CloudBackupSchedule#reference_hour_of_day}.
        :param reference_minute_of_hour: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#reference_minute_of_hour CloudBackupSchedule#reference_minute_of_hour}.
        :param restore_window_days: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#restore_window_days CloudBackupSchedule#restore_window_days}.
        :param update_snapshots: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#update_snapshots CloudBackupSchedule#update_snapshots}.
        :param use_org_and_group_names_in_export_prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#use_org_and_group_names_in_export_prefix CloudBackupSchedule#use_org_and_group_names_in_export_prefix}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__344c5fd4696fda75905f5944497f97382441a465f6e49e9285991c716c152716)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = CloudBackupScheduleConfig(
            cluster_name=cluster_name,
            project_id=project_id,
            auto_export_enabled=auto_export_enabled,
            copy_settings=copy_settings,
            export=export,
            id=id,
            policy_item_daily=policy_item_daily,
            policy_item_hourly=policy_item_hourly,
            policy_item_monthly=policy_item_monthly,
            policy_item_weekly=policy_item_weekly,
            policy_item_yearly=policy_item_yearly,
            reference_hour_of_day=reference_hour_of_day,
            reference_minute_of_hour=reference_minute_of_hour,
            restore_window_days=restore_window_days,
            update_snapshots=update_snapshots,
            use_org_and_group_names_in_export_prefix=use_org_and_group_names_in_export_prefix,
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
        '''Generates CDKTF code for importing a CloudBackupSchedule resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the CloudBackupSchedule to import.
        :param import_from_id: The id of the existing CloudBackupSchedule that should be imported. Refer to the {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the CloudBackupSchedule to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bcc6444f5cde1813546bc6f4bc06fc1f6100117f2811c23678a02adc83794e91)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putCopySettings")
    def put_copy_settings(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CloudBackupScheduleCopySettings", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b108240c1e5259379f0749ec3a296b8944a55d4ae4a263b081c77174b4969eef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putCopySettings", [value]))

    @jsii.member(jsii_name="putExport")
    def put_export(
        self,
        *,
        export_bucket_id: typing.Optional[builtins.str] = None,
        frequency_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param export_bucket_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#export_bucket_id CloudBackupSchedule#export_bucket_id}.
        :param frequency_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#frequency_type CloudBackupSchedule#frequency_type}.
        '''
        value = CloudBackupScheduleExport(
            export_bucket_id=export_bucket_id, frequency_type=frequency_type
        )

        return typing.cast(None, jsii.invoke(self, "putExport", [value]))

    @jsii.member(jsii_name="putPolicyItemDaily")
    def put_policy_item_daily(
        self,
        *,
        frequency_interval: jsii.Number,
        retention_unit: builtins.str,
        retention_value: jsii.Number,
    ) -> None:
        '''
        :param frequency_interval: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#frequency_interval CloudBackupSchedule#frequency_interval}.
        :param retention_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#retention_unit CloudBackupSchedule#retention_unit}.
        :param retention_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#retention_value CloudBackupSchedule#retention_value}.
        '''
        value = CloudBackupSchedulePolicyItemDaily(
            frequency_interval=frequency_interval,
            retention_unit=retention_unit,
            retention_value=retention_value,
        )

        return typing.cast(None, jsii.invoke(self, "putPolicyItemDaily", [value]))

    @jsii.member(jsii_name="putPolicyItemHourly")
    def put_policy_item_hourly(
        self,
        *,
        frequency_interval: jsii.Number,
        retention_unit: builtins.str,
        retention_value: jsii.Number,
    ) -> None:
        '''
        :param frequency_interval: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#frequency_interval CloudBackupSchedule#frequency_interval}.
        :param retention_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#retention_unit CloudBackupSchedule#retention_unit}.
        :param retention_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#retention_value CloudBackupSchedule#retention_value}.
        '''
        value = CloudBackupSchedulePolicyItemHourly(
            frequency_interval=frequency_interval,
            retention_unit=retention_unit,
            retention_value=retention_value,
        )

        return typing.cast(None, jsii.invoke(self, "putPolicyItemHourly", [value]))

    @jsii.member(jsii_name="putPolicyItemMonthly")
    def put_policy_item_monthly(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CloudBackupSchedulePolicyItemMonthly", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__abbf5ebe8b71f98c41aff3ce4766c5aff025adf99f95694749d9cc0fcdc92bd8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putPolicyItemMonthly", [value]))

    @jsii.member(jsii_name="putPolicyItemWeekly")
    def put_policy_item_weekly(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CloudBackupSchedulePolicyItemWeekly", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1c74326e3323660a93ef253615da67dc0f2032f3eccdc9f32f69d8673b998ce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putPolicyItemWeekly", [value]))

    @jsii.member(jsii_name="putPolicyItemYearly")
    def put_policy_item_yearly(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CloudBackupSchedulePolicyItemYearly", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3ae06564c667812d33e81b3ff5c34011e45ce6bdd5824405b72635966332ea0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putPolicyItemYearly", [value]))

    @jsii.member(jsii_name="resetAutoExportEnabled")
    def reset_auto_export_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoExportEnabled", []))

    @jsii.member(jsii_name="resetCopySettings")
    def reset_copy_settings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCopySettings", []))

    @jsii.member(jsii_name="resetExport")
    def reset_export(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExport", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetPolicyItemDaily")
    def reset_policy_item_daily(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicyItemDaily", []))

    @jsii.member(jsii_name="resetPolicyItemHourly")
    def reset_policy_item_hourly(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicyItemHourly", []))

    @jsii.member(jsii_name="resetPolicyItemMonthly")
    def reset_policy_item_monthly(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicyItemMonthly", []))

    @jsii.member(jsii_name="resetPolicyItemWeekly")
    def reset_policy_item_weekly(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicyItemWeekly", []))

    @jsii.member(jsii_name="resetPolicyItemYearly")
    def reset_policy_item_yearly(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPolicyItemYearly", []))

    @jsii.member(jsii_name="resetReferenceHourOfDay")
    def reset_reference_hour_of_day(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReferenceHourOfDay", []))

    @jsii.member(jsii_name="resetReferenceMinuteOfHour")
    def reset_reference_minute_of_hour(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReferenceMinuteOfHour", []))

    @jsii.member(jsii_name="resetRestoreWindowDays")
    def reset_restore_window_days(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRestoreWindowDays", []))

    @jsii.member(jsii_name="resetUpdateSnapshots")
    def reset_update_snapshots(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUpdateSnapshots", []))

    @jsii.member(jsii_name="resetUseOrgAndGroupNamesInExportPrefix")
    def reset_use_org_and_group_names_in_export_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUseOrgAndGroupNamesInExportPrefix", []))

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
    @jsii.member(jsii_name="clusterId")
    def cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterId"))

    @builtins.property
    @jsii.member(jsii_name="copySettings")
    def copy_settings(self) -> "CloudBackupScheduleCopySettingsList":
        return typing.cast("CloudBackupScheduleCopySettingsList", jsii.get(self, "copySettings"))

    @builtins.property
    @jsii.member(jsii_name="export")
    def export(self) -> "CloudBackupScheduleExportOutputReference":
        return typing.cast("CloudBackupScheduleExportOutputReference", jsii.get(self, "export"))

    @builtins.property
    @jsii.member(jsii_name="idPolicy")
    def id_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "idPolicy"))

    @builtins.property
    @jsii.member(jsii_name="nextSnapshot")
    def next_snapshot(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "nextSnapshot"))

    @builtins.property
    @jsii.member(jsii_name="policyItemDaily")
    def policy_item_daily(self) -> "CloudBackupSchedulePolicyItemDailyOutputReference":
        return typing.cast("CloudBackupSchedulePolicyItemDailyOutputReference", jsii.get(self, "policyItemDaily"))

    @builtins.property
    @jsii.member(jsii_name="policyItemHourly")
    def policy_item_hourly(
        self,
    ) -> "CloudBackupSchedulePolicyItemHourlyOutputReference":
        return typing.cast("CloudBackupSchedulePolicyItemHourlyOutputReference", jsii.get(self, "policyItemHourly"))

    @builtins.property
    @jsii.member(jsii_name="policyItemMonthly")
    def policy_item_monthly(self) -> "CloudBackupSchedulePolicyItemMonthlyList":
        return typing.cast("CloudBackupSchedulePolicyItemMonthlyList", jsii.get(self, "policyItemMonthly"))

    @builtins.property
    @jsii.member(jsii_name="policyItemWeekly")
    def policy_item_weekly(self) -> "CloudBackupSchedulePolicyItemWeeklyList":
        return typing.cast("CloudBackupSchedulePolicyItemWeeklyList", jsii.get(self, "policyItemWeekly"))

    @builtins.property
    @jsii.member(jsii_name="policyItemYearly")
    def policy_item_yearly(self) -> "CloudBackupSchedulePolicyItemYearlyList":
        return typing.cast("CloudBackupSchedulePolicyItemYearlyList", jsii.get(self, "policyItemYearly"))

    @builtins.property
    @jsii.member(jsii_name="autoExportEnabledInput")
    def auto_export_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "autoExportEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterNameInput")
    def cluster_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterNameInput"))

    @builtins.property
    @jsii.member(jsii_name="copySettingsInput")
    def copy_settings_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CloudBackupScheduleCopySettings"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CloudBackupScheduleCopySettings"]]], jsii.get(self, "copySettingsInput"))

    @builtins.property
    @jsii.member(jsii_name="exportInput")
    def export_input(self) -> typing.Optional["CloudBackupScheduleExport"]:
        return typing.cast(typing.Optional["CloudBackupScheduleExport"], jsii.get(self, "exportInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="policyItemDailyInput")
    def policy_item_daily_input(
        self,
    ) -> typing.Optional["CloudBackupSchedulePolicyItemDaily"]:
        return typing.cast(typing.Optional["CloudBackupSchedulePolicyItemDaily"], jsii.get(self, "policyItemDailyInput"))

    @builtins.property
    @jsii.member(jsii_name="policyItemHourlyInput")
    def policy_item_hourly_input(
        self,
    ) -> typing.Optional["CloudBackupSchedulePolicyItemHourly"]:
        return typing.cast(typing.Optional["CloudBackupSchedulePolicyItemHourly"], jsii.get(self, "policyItemHourlyInput"))

    @builtins.property
    @jsii.member(jsii_name="policyItemMonthlyInput")
    def policy_item_monthly_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CloudBackupSchedulePolicyItemMonthly"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CloudBackupSchedulePolicyItemMonthly"]]], jsii.get(self, "policyItemMonthlyInput"))

    @builtins.property
    @jsii.member(jsii_name="policyItemWeeklyInput")
    def policy_item_weekly_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CloudBackupSchedulePolicyItemWeekly"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CloudBackupSchedulePolicyItemWeekly"]]], jsii.get(self, "policyItemWeeklyInput"))

    @builtins.property
    @jsii.member(jsii_name="policyItemYearlyInput")
    def policy_item_yearly_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CloudBackupSchedulePolicyItemYearly"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CloudBackupSchedulePolicyItemYearly"]]], jsii.get(self, "policyItemYearlyInput"))

    @builtins.property
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="referenceHourOfDayInput")
    def reference_hour_of_day_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "referenceHourOfDayInput"))

    @builtins.property
    @jsii.member(jsii_name="referenceMinuteOfHourInput")
    def reference_minute_of_hour_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "referenceMinuteOfHourInput"))

    @builtins.property
    @jsii.member(jsii_name="restoreWindowDaysInput")
    def restore_window_days_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "restoreWindowDaysInput"))

    @builtins.property
    @jsii.member(jsii_name="updateSnapshotsInput")
    def update_snapshots_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "updateSnapshotsInput"))

    @builtins.property
    @jsii.member(jsii_name="useOrgAndGroupNamesInExportPrefixInput")
    def use_org_and_group_names_in_export_prefix_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "useOrgAndGroupNamesInExportPrefixInput"))

    @builtins.property
    @jsii.member(jsii_name="autoExportEnabled")
    def auto_export_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "autoExportEnabled"))

    @auto_export_enabled.setter
    def auto_export_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81c18efeb5ceac87365ac18c191c76193df2442f5188b6e6f58c0e64c8686266)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoExportEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterName"))

    @cluster_name.setter
    def cluster_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a149919bf5352a1cbf3ec42e2aeec0dd454c57c8d42432f02feda9ad18c2ac8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dd49cb83afc70ba00b9a283a05a297f4a2192737a62e6853bf0cf6ce84dbcce0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16ddcc0dc620ebb7c4bc5e93c4dfa367b6c52ba00efc0dece18ae0b1d1e9c467)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="referenceHourOfDay")
    def reference_hour_of_day(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "referenceHourOfDay"))

    @reference_hour_of_day.setter
    def reference_hour_of_day(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fab4d307e33ff79a4954fc0dbf53536b931186cc30324b2d2c00d83c65b83799)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "referenceHourOfDay", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="referenceMinuteOfHour")
    def reference_minute_of_hour(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "referenceMinuteOfHour"))

    @reference_minute_of_hour.setter
    def reference_minute_of_hour(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b408a68f7e5565bf9e3032d53951984b135ce12837c3096decf9a41215f3b05)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "referenceMinuteOfHour", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="restoreWindowDays")
    def restore_window_days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "restoreWindowDays"))

    @restore_window_days.setter
    def restore_window_days(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b302cabad0c11f12432d965a9932b583759d6561034e1159153bc3b85b424ab7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "restoreWindowDays", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="updateSnapshots")
    def update_snapshots(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "updateSnapshots"))

    @update_snapshots.setter
    def update_snapshots(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a05a7af7eef426c8333ce833d9e93614e248877bcf404c11fd08fb6494d6aa63)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "updateSnapshots", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="useOrgAndGroupNamesInExportPrefix")
    def use_org_and_group_names_in_export_prefix(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "useOrgAndGroupNamesInExportPrefix"))

    @use_org_and_group_names_in_export_prefix.setter
    def use_org_and_group_names_in_export_prefix(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61142b778b457438aa0b1af973246df6a895eb4508bd7f3672395eae0392292d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "useOrgAndGroupNamesInExportPrefix", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.cloudBackupSchedule.CloudBackupScheduleConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "cluster_name": "clusterName",
        "project_id": "projectId",
        "auto_export_enabled": "autoExportEnabled",
        "copy_settings": "copySettings",
        "export": "export",
        "id": "id",
        "policy_item_daily": "policyItemDaily",
        "policy_item_hourly": "policyItemHourly",
        "policy_item_monthly": "policyItemMonthly",
        "policy_item_weekly": "policyItemWeekly",
        "policy_item_yearly": "policyItemYearly",
        "reference_hour_of_day": "referenceHourOfDay",
        "reference_minute_of_hour": "referenceMinuteOfHour",
        "restore_window_days": "restoreWindowDays",
        "update_snapshots": "updateSnapshots",
        "use_org_and_group_names_in_export_prefix": "useOrgAndGroupNamesInExportPrefix",
    },
)
class CloudBackupScheduleConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        cluster_name: builtins.str,
        project_id: builtins.str,
        auto_export_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        copy_settings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CloudBackupScheduleCopySettings", typing.Dict[builtins.str, typing.Any]]]]] = None,
        export: typing.Optional[typing.Union["CloudBackupScheduleExport", typing.Dict[builtins.str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        policy_item_daily: typing.Optional[typing.Union["CloudBackupSchedulePolicyItemDaily", typing.Dict[builtins.str, typing.Any]]] = None,
        policy_item_hourly: typing.Optional[typing.Union["CloudBackupSchedulePolicyItemHourly", typing.Dict[builtins.str, typing.Any]]] = None,
        policy_item_monthly: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CloudBackupSchedulePolicyItemMonthly", typing.Dict[builtins.str, typing.Any]]]]] = None,
        policy_item_weekly: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CloudBackupSchedulePolicyItemWeekly", typing.Dict[builtins.str, typing.Any]]]]] = None,
        policy_item_yearly: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["CloudBackupSchedulePolicyItemYearly", typing.Dict[builtins.str, typing.Any]]]]] = None,
        reference_hour_of_day: typing.Optional[jsii.Number] = None,
        reference_minute_of_hour: typing.Optional[jsii.Number] = None,
        restore_window_days: typing.Optional[jsii.Number] = None,
        update_snapshots: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        use_org_and_group_names_in_export_prefix: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param cluster_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#cluster_name CloudBackupSchedule#cluster_name}.
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#project_id CloudBackupSchedule#project_id}.
        :param auto_export_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#auto_export_enabled CloudBackupSchedule#auto_export_enabled}.
        :param copy_settings: copy_settings block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#copy_settings CloudBackupSchedule#copy_settings}
        :param export: export block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#export CloudBackupSchedule#export}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#id CloudBackupSchedule#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param policy_item_daily: policy_item_daily block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#policy_item_daily CloudBackupSchedule#policy_item_daily}
        :param policy_item_hourly: policy_item_hourly block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#policy_item_hourly CloudBackupSchedule#policy_item_hourly}
        :param policy_item_monthly: policy_item_monthly block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#policy_item_monthly CloudBackupSchedule#policy_item_monthly}
        :param policy_item_weekly: policy_item_weekly block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#policy_item_weekly CloudBackupSchedule#policy_item_weekly}
        :param policy_item_yearly: policy_item_yearly block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#policy_item_yearly CloudBackupSchedule#policy_item_yearly}
        :param reference_hour_of_day: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#reference_hour_of_day CloudBackupSchedule#reference_hour_of_day}.
        :param reference_minute_of_hour: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#reference_minute_of_hour CloudBackupSchedule#reference_minute_of_hour}.
        :param restore_window_days: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#restore_window_days CloudBackupSchedule#restore_window_days}.
        :param update_snapshots: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#update_snapshots CloudBackupSchedule#update_snapshots}.
        :param use_org_and_group_names_in_export_prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#use_org_and_group_names_in_export_prefix CloudBackupSchedule#use_org_and_group_names_in_export_prefix}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(export, dict):
            export = CloudBackupScheduleExport(**export)
        if isinstance(policy_item_daily, dict):
            policy_item_daily = CloudBackupSchedulePolicyItemDaily(**policy_item_daily)
        if isinstance(policy_item_hourly, dict):
            policy_item_hourly = CloudBackupSchedulePolicyItemHourly(**policy_item_hourly)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4dc71990a56b772b3bd536feea273f3f9584f44b01a9a6517b02e0efc74bb7f)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument cluster_name", value=cluster_name, expected_type=type_hints["cluster_name"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument auto_export_enabled", value=auto_export_enabled, expected_type=type_hints["auto_export_enabled"])
            check_type(argname="argument copy_settings", value=copy_settings, expected_type=type_hints["copy_settings"])
            check_type(argname="argument export", value=export, expected_type=type_hints["export"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument policy_item_daily", value=policy_item_daily, expected_type=type_hints["policy_item_daily"])
            check_type(argname="argument policy_item_hourly", value=policy_item_hourly, expected_type=type_hints["policy_item_hourly"])
            check_type(argname="argument policy_item_monthly", value=policy_item_monthly, expected_type=type_hints["policy_item_monthly"])
            check_type(argname="argument policy_item_weekly", value=policy_item_weekly, expected_type=type_hints["policy_item_weekly"])
            check_type(argname="argument policy_item_yearly", value=policy_item_yearly, expected_type=type_hints["policy_item_yearly"])
            check_type(argname="argument reference_hour_of_day", value=reference_hour_of_day, expected_type=type_hints["reference_hour_of_day"])
            check_type(argname="argument reference_minute_of_hour", value=reference_minute_of_hour, expected_type=type_hints["reference_minute_of_hour"])
            check_type(argname="argument restore_window_days", value=restore_window_days, expected_type=type_hints["restore_window_days"])
            check_type(argname="argument update_snapshots", value=update_snapshots, expected_type=type_hints["update_snapshots"])
            check_type(argname="argument use_org_and_group_names_in_export_prefix", value=use_org_and_group_names_in_export_prefix, expected_type=type_hints["use_org_and_group_names_in_export_prefix"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cluster_name": cluster_name,
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
        if auto_export_enabled is not None:
            self._values["auto_export_enabled"] = auto_export_enabled
        if copy_settings is not None:
            self._values["copy_settings"] = copy_settings
        if export is not None:
            self._values["export"] = export
        if id is not None:
            self._values["id"] = id
        if policy_item_daily is not None:
            self._values["policy_item_daily"] = policy_item_daily
        if policy_item_hourly is not None:
            self._values["policy_item_hourly"] = policy_item_hourly
        if policy_item_monthly is not None:
            self._values["policy_item_monthly"] = policy_item_monthly
        if policy_item_weekly is not None:
            self._values["policy_item_weekly"] = policy_item_weekly
        if policy_item_yearly is not None:
            self._values["policy_item_yearly"] = policy_item_yearly
        if reference_hour_of_day is not None:
            self._values["reference_hour_of_day"] = reference_hour_of_day
        if reference_minute_of_hour is not None:
            self._values["reference_minute_of_hour"] = reference_minute_of_hour
        if restore_window_days is not None:
            self._values["restore_window_days"] = restore_window_days
        if update_snapshots is not None:
            self._values["update_snapshots"] = update_snapshots
        if use_org_and_group_names_in_export_prefix is not None:
            self._values["use_org_and_group_names_in_export_prefix"] = use_org_and_group_names_in_export_prefix

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
    def cluster_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#cluster_name CloudBackupSchedule#cluster_name}.'''
        result = self._values.get("cluster_name")
        assert result is not None, "Required property 'cluster_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def project_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#project_id CloudBackupSchedule#project_id}.'''
        result = self._values.get("project_id")
        assert result is not None, "Required property 'project_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auto_export_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#auto_export_enabled CloudBackupSchedule#auto_export_enabled}.'''
        result = self._values.get("auto_export_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def copy_settings(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CloudBackupScheduleCopySettings"]]]:
        '''copy_settings block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#copy_settings CloudBackupSchedule#copy_settings}
        '''
        result = self._values.get("copy_settings")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CloudBackupScheduleCopySettings"]]], result)

    @builtins.property
    def export(self) -> typing.Optional["CloudBackupScheduleExport"]:
        '''export block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#export CloudBackupSchedule#export}
        '''
        result = self._values.get("export")
        return typing.cast(typing.Optional["CloudBackupScheduleExport"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#id CloudBackupSchedule#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def policy_item_daily(
        self,
    ) -> typing.Optional["CloudBackupSchedulePolicyItemDaily"]:
        '''policy_item_daily block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#policy_item_daily CloudBackupSchedule#policy_item_daily}
        '''
        result = self._values.get("policy_item_daily")
        return typing.cast(typing.Optional["CloudBackupSchedulePolicyItemDaily"], result)

    @builtins.property
    def policy_item_hourly(
        self,
    ) -> typing.Optional["CloudBackupSchedulePolicyItemHourly"]:
        '''policy_item_hourly block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#policy_item_hourly CloudBackupSchedule#policy_item_hourly}
        '''
        result = self._values.get("policy_item_hourly")
        return typing.cast(typing.Optional["CloudBackupSchedulePolicyItemHourly"], result)

    @builtins.property
    def policy_item_monthly(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CloudBackupSchedulePolicyItemMonthly"]]]:
        '''policy_item_monthly block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#policy_item_monthly CloudBackupSchedule#policy_item_monthly}
        '''
        result = self._values.get("policy_item_monthly")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CloudBackupSchedulePolicyItemMonthly"]]], result)

    @builtins.property
    def policy_item_weekly(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CloudBackupSchedulePolicyItemWeekly"]]]:
        '''policy_item_weekly block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#policy_item_weekly CloudBackupSchedule#policy_item_weekly}
        '''
        result = self._values.get("policy_item_weekly")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CloudBackupSchedulePolicyItemWeekly"]]], result)

    @builtins.property
    def policy_item_yearly(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CloudBackupSchedulePolicyItemYearly"]]]:
        '''policy_item_yearly block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#policy_item_yearly CloudBackupSchedule#policy_item_yearly}
        '''
        result = self._values.get("policy_item_yearly")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["CloudBackupSchedulePolicyItemYearly"]]], result)

    @builtins.property
    def reference_hour_of_day(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#reference_hour_of_day CloudBackupSchedule#reference_hour_of_day}.'''
        result = self._values.get("reference_hour_of_day")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def reference_minute_of_hour(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#reference_minute_of_hour CloudBackupSchedule#reference_minute_of_hour}.'''
        result = self._values.get("reference_minute_of_hour")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def restore_window_days(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#restore_window_days CloudBackupSchedule#restore_window_days}.'''
        result = self._values.get("restore_window_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def update_snapshots(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#update_snapshots CloudBackupSchedule#update_snapshots}.'''
        result = self._values.get("update_snapshots")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def use_org_and_group_names_in_export_prefix(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#use_org_and_group_names_in_export_prefix CloudBackupSchedule#use_org_and_group_names_in_export_prefix}.'''
        result = self._values.get("use_org_and_group_names_in_export_prefix")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudBackupScheduleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.cloudBackupSchedule.CloudBackupScheduleCopySettings",
    jsii_struct_bases=[],
    name_mapping={
        "cloud_provider": "cloudProvider",
        "frequencies": "frequencies",
        "region_name": "regionName",
        "replication_spec_id": "replicationSpecId",
        "should_copy_oplogs": "shouldCopyOplogs",
        "zone_id": "zoneId",
    },
)
class CloudBackupScheduleCopySettings:
    def __init__(
        self,
        *,
        cloud_provider: typing.Optional[builtins.str] = None,
        frequencies: typing.Optional[typing.Sequence[builtins.str]] = None,
        region_name: typing.Optional[builtins.str] = None,
        replication_spec_id: typing.Optional[builtins.str] = None,
        should_copy_oplogs: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        zone_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param cloud_provider: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#cloud_provider CloudBackupSchedule#cloud_provider}.
        :param frequencies: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#frequencies CloudBackupSchedule#frequencies}.
        :param region_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#region_name CloudBackupSchedule#region_name}.
        :param replication_spec_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#replication_spec_id CloudBackupSchedule#replication_spec_id}.
        :param should_copy_oplogs: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#should_copy_oplogs CloudBackupSchedule#should_copy_oplogs}.
        :param zone_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#zone_id CloudBackupSchedule#zone_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__523ec0e1143e0b37cea1ae9f41baa4a823609e844ca2216d3b575fa477a53630)
            check_type(argname="argument cloud_provider", value=cloud_provider, expected_type=type_hints["cloud_provider"])
            check_type(argname="argument frequencies", value=frequencies, expected_type=type_hints["frequencies"])
            check_type(argname="argument region_name", value=region_name, expected_type=type_hints["region_name"])
            check_type(argname="argument replication_spec_id", value=replication_spec_id, expected_type=type_hints["replication_spec_id"])
            check_type(argname="argument should_copy_oplogs", value=should_copy_oplogs, expected_type=type_hints["should_copy_oplogs"])
            check_type(argname="argument zone_id", value=zone_id, expected_type=type_hints["zone_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cloud_provider is not None:
            self._values["cloud_provider"] = cloud_provider
        if frequencies is not None:
            self._values["frequencies"] = frequencies
        if region_name is not None:
            self._values["region_name"] = region_name
        if replication_spec_id is not None:
            self._values["replication_spec_id"] = replication_spec_id
        if should_copy_oplogs is not None:
            self._values["should_copy_oplogs"] = should_copy_oplogs
        if zone_id is not None:
            self._values["zone_id"] = zone_id

    @builtins.property
    def cloud_provider(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#cloud_provider CloudBackupSchedule#cloud_provider}.'''
        result = self._values.get("cloud_provider")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def frequencies(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#frequencies CloudBackupSchedule#frequencies}.'''
        result = self._values.get("frequencies")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def region_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#region_name CloudBackupSchedule#region_name}.'''
        result = self._values.get("region_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def replication_spec_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#replication_spec_id CloudBackupSchedule#replication_spec_id}.'''
        result = self._values.get("replication_spec_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def should_copy_oplogs(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#should_copy_oplogs CloudBackupSchedule#should_copy_oplogs}.'''
        result = self._values.get("should_copy_oplogs")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def zone_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#zone_id CloudBackupSchedule#zone_id}.'''
        result = self._values.get("zone_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudBackupScheduleCopySettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudBackupScheduleCopySettingsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cloudBackupSchedule.CloudBackupScheduleCopySettingsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7ba95d2bbab2e4bf013b27626b79a288a76c1c196880a6880d53a02ecd51552a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "CloudBackupScheduleCopySettingsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3dbd459f21bdd406a1f873c82a928af564b748662d41f93e3fa61dce39565e93)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("CloudBackupScheduleCopySettingsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63fa3b892593dd84988c57454c8adbcc6fd10ce0b4996c822fc811133da589b8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0ee1759a8650f29359e4529b2e4b09838a37e24fe26083ddec2d6adeaa1818da)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ca688f529545bec1eaf38daf102e2ae5d5d101e0dd78ad2c6cab37a9e4e7aa07)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CloudBackupScheduleCopySettings]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CloudBackupScheduleCopySettings]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CloudBackupScheduleCopySettings]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d93408b829c1f2f868279e1badf10e581c4a0172ee1619d7fd01308d3e9cf2a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class CloudBackupScheduleCopySettingsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cloudBackupSchedule.CloudBackupScheduleCopySettingsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a2c20dcd7132993a43ce66149f4490c7d193f777bca8e7b6fc53a4cfaad53c01)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetCloudProvider")
    def reset_cloud_provider(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCloudProvider", []))

    @jsii.member(jsii_name="resetFrequencies")
    def reset_frequencies(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFrequencies", []))

    @jsii.member(jsii_name="resetRegionName")
    def reset_region_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegionName", []))

    @jsii.member(jsii_name="resetReplicationSpecId")
    def reset_replication_spec_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReplicationSpecId", []))

    @jsii.member(jsii_name="resetShouldCopyOplogs")
    def reset_should_copy_oplogs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetShouldCopyOplogs", []))

    @jsii.member(jsii_name="resetZoneId")
    def reset_zone_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetZoneId", []))

    @builtins.property
    @jsii.member(jsii_name="cloudProviderInput")
    def cloud_provider_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cloudProviderInput"))

    @builtins.property
    @jsii.member(jsii_name="frequenciesInput")
    def frequencies_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "frequenciesInput"))

    @builtins.property
    @jsii.member(jsii_name="regionNameInput")
    def region_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionNameInput"))

    @builtins.property
    @jsii.member(jsii_name="replicationSpecIdInput")
    def replication_spec_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "replicationSpecIdInput"))

    @builtins.property
    @jsii.member(jsii_name="shouldCopyOplogsInput")
    def should_copy_oplogs_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "shouldCopyOplogsInput"))

    @builtins.property
    @jsii.member(jsii_name="zoneIdInput")
    def zone_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "zoneIdInput"))

    @builtins.property
    @jsii.member(jsii_name="cloudProvider")
    def cloud_provider(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cloudProvider"))

    @cloud_provider.setter
    def cloud_provider(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3623b3ddbf2208aa613431a38d6b0fcb69ab9e21a0c709bf0e741f9c644d01f7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cloudProvider", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="frequencies")
    def frequencies(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "frequencies"))

    @frequencies.setter
    def frequencies(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbce39f2dd790a77905b806ae2cb7bbcb70cf30e6f8a4df84dbf944af7f67862)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "frequencies", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="regionName")
    def region_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "regionName"))

    @region_name.setter
    def region_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__608bcd1148905688b36fdb8fad236902bf52cb40b68360b451c54a57ad880750)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "regionName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="replicationSpecId")
    def replication_spec_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "replicationSpecId"))

    @replication_spec_id.setter
    def replication_spec_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ac6cca473e3382b7fe1ef0c855769183dc299889efc6632ff2eebbe8b29f489)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "replicationSpecId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="shouldCopyOplogs")
    def should_copy_oplogs(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "shouldCopyOplogs"))

    @should_copy_oplogs.setter
    def should_copy_oplogs(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8d1c67e363cbfc48164155df3b07d4aedaae212f34478505f960257f8c16d10)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "shouldCopyOplogs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="zoneId")
    def zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "zoneId"))

    @zone_id.setter
    def zone_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2aef3937155d106eff66645db30dbdb001f49120190f149398efa7f59e83c526)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "zoneId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CloudBackupScheduleCopySettings]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CloudBackupScheduleCopySettings]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CloudBackupScheduleCopySettings]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d99b13f1303d8e582583f112bafd3d6b6c02978abe83da7ae9d3f7f1e2fafa94)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.cloudBackupSchedule.CloudBackupScheduleExport",
    jsii_struct_bases=[],
    name_mapping={
        "export_bucket_id": "exportBucketId",
        "frequency_type": "frequencyType",
    },
)
class CloudBackupScheduleExport:
    def __init__(
        self,
        *,
        export_bucket_id: typing.Optional[builtins.str] = None,
        frequency_type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param export_bucket_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#export_bucket_id CloudBackupSchedule#export_bucket_id}.
        :param frequency_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#frequency_type CloudBackupSchedule#frequency_type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1af6a8150df3507a6761d405dab5a6503cfad010ccfbc559232f055a8efa3e7b)
            check_type(argname="argument export_bucket_id", value=export_bucket_id, expected_type=type_hints["export_bucket_id"])
            check_type(argname="argument frequency_type", value=frequency_type, expected_type=type_hints["frequency_type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if export_bucket_id is not None:
            self._values["export_bucket_id"] = export_bucket_id
        if frequency_type is not None:
            self._values["frequency_type"] = frequency_type

    @builtins.property
    def export_bucket_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#export_bucket_id CloudBackupSchedule#export_bucket_id}.'''
        result = self._values.get("export_bucket_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def frequency_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#frequency_type CloudBackupSchedule#frequency_type}.'''
        result = self._values.get("frequency_type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudBackupScheduleExport(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudBackupScheduleExportOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cloudBackupSchedule.CloudBackupScheduleExportOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__808d1d36ffd0c9fea4a55909c33de26dc0d429f6d36b1655953d5ec2a67e3ef2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetExportBucketId")
    def reset_export_bucket_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExportBucketId", []))

    @jsii.member(jsii_name="resetFrequencyType")
    def reset_frequency_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFrequencyType", []))

    @builtins.property
    @jsii.member(jsii_name="exportBucketIdInput")
    def export_bucket_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "exportBucketIdInput"))

    @builtins.property
    @jsii.member(jsii_name="frequencyTypeInput")
    def frequency_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "frequencyTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="exportBucketId")
    def export_bucket_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "exportBucketId"))

    @export_bucket_id.setter
    def export_bucket_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e87accae43dabd85a90cea503a46d4b0857c250ba5927f460f7e5551f676c4cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "exportBucketId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="frequencyType")
    def frequency_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "frequencyType"))

    @frequency_type.setter
    def frequency_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92b0af9b3ecd86a551aacbc5d2e688c2da35f67c20259cb06b59db7c744241b1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "frequencyType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CloudBackupScheduleExport]:
        return typing.cast(typing.Optional[CloudBackupScheduleExport], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[CloudBackupScheduleExport]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89a5e5980dfba4530d1b6957b833921b076ad299f769828b4e8e296de9bbc531)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.cloudBackupSchedule.CloudBackupSchedulePolicyItemDaily",
    jsii_struct_bases=[],
    name_mapping={
        "frequency_interval": "frequencyInterval",
        "retention_unit": "retentionUnit",
        "retention_value": "retentionValue",
    },
)
class CloudBackupSchedulePolicyItemDaily:
    def __init__(
        self,
        *,
        frequency_interval: jsii.Number,
        retention_unit: builtins.str,
        retention_value: jsii.Number,
    ) -> None:
        '''
        :param frequency_interval: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#frequency_interval CloudBackupSchedule#frequency_interval}.
        :param retention_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#retention_unit CloudBackupSchedule#retention_unit}.
        :param retention_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#retention_value CloudBackupSchedule#retention_value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d25c48a2f328bb4cfd7f2562fe38665a9e8d5fc0b89ef875a2f33ebd7662c50)
            check_type(argname="argument frequency_interval", value=frequency_interval, expected_type=type_hints["frequency_interval"])
            check_type(argname="argument retention_unit", value=retention_unit, expected_type=type_hints["retention_unit"])
            check_type(argname="argument retention_value", value=retention_value, expected_type=type_hints["retention_value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "frequency_interval": frequency_interval,
            "retention_unit": retention_unit,
            "retention_value": retention_value,
        }

    @builtins.property
    def frequency_interval(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#frequency_interval CloudBackupSchedule#frequency_interval}.'''
        result = self._values.get("frequency_interval")
        assert result is not None, "Required property 'frequency_interval' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def retention_unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#retention_unit CloudBackupSchedule#retention_unit}.'''
        result = self._values.get("retention_unit")
        assert result is not None, "Required property 'retention_unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def retention_value(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#retention_value CloudBackupSchedule#retention_value}.'''
        result = self._values.get("retention_value")
        assert result is not None, "Required property 'retention_value' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudBackupSchedulePolicyItemDaily(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudBackupSchedulePolicyItemDailyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cloudBackupSchedule.CloudBackupSchedulePolicyItemDailyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c7166716842104fd1e7151abcf195c844351d0278e9068a273093ee7df00bfd8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="frequencyType")
    def frequency_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "frequencyType"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="frequencyIntervalInput")
    def frequency_interval_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "frequencyIntervalInput"))

    @builtins.property
    @jsii.member(jsii_name="retentionUnitInput")
    def retention_unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "retentionUnitInput"))

    @builtins.property
    @jsii.member(jsii_name="retentionValueInput")
    def retention_value_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retentionValueInput"))

    @builtins.property
    @jsii.member(jsii_name="frequencyInterval")
    def frequency_interval(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "frequencyInterval"))

    @frequency_interval.setter
    def frequency_interval(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__877c0f969947c5684b9391d90e67aa0367789b98b0eaaa93b810aa9b96026ed7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "frequencyInterval", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retentionUnit")
    def retention_unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "retentionUnit"))

    @retention_unit.setter
    def retention_unit(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7c8324c6f06193c105af1a29bf05ea307815436f8dbc7ab866302e05d8fc0a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retentionUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retentionValue")
    def retention_value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "retentionValue"))

    @retention_value.setter
    def retention_value(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1b45ba57b5aa769b1f665b7347398694118de4b1bbbfb0cb2e8c95821122590)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retentionValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CloudBackupSchedulePolicyItemDaily]:
        return typing.cast(typing.Optional[CloudBackupSchedulePolicyItemDaily], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudBackupSchedulePolicyItemDaily],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75fda124118ad53a7c276ca3150437b3e76787be9727c4bc0bfa8e7da9a8968f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.cloudBackupSchedule.CloudBackupSchedulePolicyItemHourly",
    jsii_struct_bases=[],
    name_mapping={
        "frequency_interval": "frequencyInterval",
        "retention_unit": "retentionUnit",
        "retention_value": "retentionValue",
    },
)
class CloudBackupSchedulePolicyItemHourly:
    def __init__(
        self,
        *,
        frequency_interval: jsii.Number,
        retention_unit: builtins.str,
        retention_value: jsii.Number,
    ) -> None:
        '''
        :param frequency_interval: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#frequency_interval CloudBackupSchedule#frequency_interval}.
        :param retention_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#retention_unit CloudBackupSchedule#retention_unit}.
        :param retention_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#retention_value CloudBackupSchedule#retention_value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__baec4fa18f9131040792083ec19f399a5c14e3c06fbf7ccb512324c5f8d8f629)
            check_type(argname="argument frequency_interval", value=frequency_interval, expected_type=type_hints["frequency_interval"])
            check_type(argname="argument retention_unit", value=retention_unit, expected_type=type_hints["retention_unit"])
            check_type(argname="argument retention_value", value=retention_value, expected_type=type_hints["retention_value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "frequency_interval": frequency_interval,
            "retention_unit": retention_unit,
            "retention_value": retention_value,
        }

    @builtins.property
    def frequency_interval(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#frequency_interval CloudBackupSchedule#frequency_interval}.'''
        result = self._values.get("frequency_interval")
        assert result is not None, "Required property 'frequency_interval' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def retention_unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#retention_unit CloudBackupSchedule#retention_unit}.'''
        result = self._values.get("retention_unit")
        assert result is not None, "Required property 'retention_unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def retention_value(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#retention_value CloudBackupSchedule#retention_value}.'''
        result = self._values.get("retention_value")
        assert result is not None, "Required property 'retention_value' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudBackupSchedulePolicyItemHourly(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudBackupSchedulePolicyItemHourlyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cloudBackupSchedule.CloudBackupSchedulePolicyItemHourlyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2866be1c9d62894df5f2b4b6af02151da12891c1fd742d2667159982263d31e8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="frequencyType")
    def frequency_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "frequencyType"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="frequencyIntervalInput")
    def frequency_interval_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "frequencyIntervalInput"))

    @builtins.property
    @jsii.member(jsii_name="retentionUnitInput")
    def retention_unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "retentionUnitInput"))

    @builtins.property
    @jsii.member(jsii_name="retentionValueInput")
    def retention_value_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retentionValueInput"))

    @builtins.property
    @jsii.member(jsii_name="frequencyInterval")
    def frequency_interval(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "frequencyInterval"))

    @frequency_interval.setter
    def frequency_interval(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5fbfc08390062dc7a7edced2732eedf3bacc5337b42ad4f4a794eb3d487b6c2d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "frequencyInterval", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retentionUnit")
    def retention_unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "retentionUnit"))

    @retention_unit.setter
    def retention_unit(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__381c34845fe9312965a6eb38029fc685111be2b2376aebb2f193277fc99db836)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retentionUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retentionValue")
    def retention_value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "retentionValue"))

    @retention_value.setter
    def retention_value(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7408aaf31788494fe9722aa2c8e8d93a722240d2974247d0f9e7c5ee96d55b3b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retentionValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CloudBackupSchedulePolicyItemHourly]:
        return typing.cast(typing.Optional[CloudBackupSchedulePolicyItemHourly], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CloudBackupSchedulePolicyItemHourly],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2eb82dac0a8ae20b829c747b9550dd7d312e572a74be282f6acfb281cea1f557)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.cloudBackupSchedule.CloudBackupSchedulePolicyItemMonthly",
    jsii_struct_bases=[],
    name_mapping={
        "frequency_interval": "frequencyInterval",
        "retention_unit": "retentionUnit",
        "retention_value": "retentionValue",
    },
)
class CloudBackupSchedulePolicyItemMonthly:
    def __init__(
        self,
        *,
        frequency_interval: jsii.Number,
        retention_unit: builtins.str,
        retention_value: jsii.Number,
    ) -> None:
        '''
        :param frequency_interval: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#frequency_interval CloudBackupSchedule#frequency_interval}.
        :param retention_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#retention_unit CloudBackupSchedule#retention_unit}.
        :param retention_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#retention_value CloudBackupSchedule#retention_value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df461d5dda46eae1e7d72be1adc934b736a6bc02a8e3043ead7919447277b984)
            check_type(argname="argument frequency_interval", value=frequency_interval, expected_type=type_hints["frequency_interval"])
            check_type(argname="argument retention_unit", value=retention_unit, expected_type=type_hints["retention_unit"])
            check_type(argname="argument retention_value", value=retention_value, expected_type=type_hints["retention_value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "frequency_interval": frequency_interval,
            "retention_unit": retention_unit,
            "retention_value": retention_value,
        }

    @builtins.property
    def frequency_interval(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#frequency_interval CloudBackupSchedule#frequency_interval}.'''
        result = self._values.get("frequency_interval")
        assert result is not None, "Required property 'frequency_interval' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def retention_unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#retention_unit CloudBackupSchedule#retention_unit}.'''
        result = self._values.get("retention_unit")
        assert result is not None, "Required property 'retention_unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def retention_value(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#retention_value CloudBackupSchedule#retention_value}.'''
        result = self._values.get("retention_value")
        assert result is not None, "Required property 'retention_value' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudBackupSchedulePolicyItemMonthly(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudBackupSchedulePolicyItemMonthlyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cloudBackupSchedule.CloudBackupSchedulePolicyItemMonthlyList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6e4302cbf07f89580eae9a495d4c063fb9edd5fce288362b15a865de3184d1e9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "CloudBackupSchedulePolicyItemMonthlyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c31a742b4e5608da57c4583e5f050e28ed057fa37ef82a12ba25c35b7937dbf3)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("CloudBackupSchedulePolicyItemMonthlyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7361892d684e03cb0ee578fd433af34fd86c17a014862e4156a04c4bb3899d5c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9ab75e5f7fa757f5571be2d87156bafeedac5309bf8ec86a2ad30ddaa7784024)
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
            type_hints = typing.get_type_hints(_typecheckingstub__74c71857195d8f9657e978939e40824a1b4a2a332f6044c0e97faed6d3226898)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CloudBackupSchedulePolicyItemMonthly]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CloudBackupSchedulePolicyItemMonthly]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CloudBackupSchedulePolicyItemMonthly]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6096ee75b445a2e8d43cc45194486a625b0ff36e36d814a4b4502379b018e9a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class CloudBackupSchedulePolicyItemMonthlyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cloudBackupSchedule.CloudBackupSchedulePolicyItemMonthlyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__196d38373e7e46f3b4e6c3fc330938391e536d27b00dae13fa9f586ce4b7ab40)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="frequencyType")
    def frequency_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "frequencyType"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="frequencyIntervalInput")
    def frequency_interval_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "frequencyIntervalInput"))

    @builtins.property
    @jsii.member(jsii_name="retentionUnitInput")
    def retention_unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "retentionUnitInput"))

    @builtins.property
    @jsii.member(jsii_name="retentionValueInput")
    def retention_value_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retentionValueInput"))

    @builtins.property
    @jsii.member(jsii_name="frequencyInterval")
    def frequency_interval(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "frequencyInterval"))

    @frequency_interval.setter
    def frequency_interval(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5095189969cd908094e31e3f87b78637fd8596fd02f9bd97321267bef02ab56b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "frequencyInterval", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retentionUnit")
    def retention_unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "retentionUnit"))

    @retention_unit.setter
    def retention_unit(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__418db8ff796c84b0972b2fd32c98c389d6177622e8850443f06b4c7ad7f88212)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retentionUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retentionValue")
    def retention_value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "retentionValue"))

    @retention_value.setter
    def retention_value(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__475d630c0516c4793e5849cc06a3a2e0b58f80d0ea65befb53fb50f4298f7bb4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retentionValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CloudBackupSchedulePolicyItemMonthly]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CloudBackupSchedulePolicyItemMonthly]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CloudBackupSchedulePolicyItemMonthly]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33041507c909c6b021f089d772eba8c6e537c84e265d9923e329bc75408090c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.cloudBackupSchedule.CloudBackupSchedulePolicyItemWeekly",
    jsii_struct_bases=[],
    name_mapping={
        "frequency_interval": "frequencyInterval",
        "retention_unit": "retentionUnit",
        "retention_value": "retentionValue",
    },
)
class CloudBackupSchedulePolicyItemWeekly:
    def __init__(
        self,
        *,
        frequency_interval: jsii.Number,
        retention_unit: builtins.str,
        retention_value: jsii.Number,
    ) -> None:
        '''
        :param frequency_interval: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#frequency_interval CloudBackupSchedule#frequency_interval}.
        :param retention_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#retention_unit CloudBackupSchedule#retention_unit}.
        :param retention_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#retention_value CloudBackupSchedule#retention_value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c9db99c70f092c7202d73e0b024308210f4fee6daa3e135a8a07f928effbf62)
            check_type(argname="argument frequency_interval", value=frequency_interval, expected_type=type_hints["frequency_interval"])
            check_type(argname="argument retention_unit", value=retention_unit, expected_type=type_hints["retention_unit"])
            check_type(argname="argument retention_value", value=retention_value, expected_type=type_hints["retention_value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "frequency_interval": frequency_interval,
            "retention_unit": retention_unit,
            "retention_value": retention_value,
        }

    @builtins.property
    def frequency_interval(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#frequency_interval CloudBackupSchedule#frequency_interval}.'''
        result = self._values.get("frequency_interval")
        assert result is not None, "Required property 'frequency_interval' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def retention_unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#retention_unit CloudBackupSchedule#retention_unit}.'''
        result = self._values.get("retention_unit")
        assert result is not None, "Required property 'retention_unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def retention_value(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#retention_value CloudBackupSchedule#retention_value}.'''
        result = self._values.get("retention_value")
        assert result is not None, "Required property 'retention_value' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudBackupSchedulePolicyItemWeekly(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudBackupSchedulePolicyItemWeeklyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cloudBackupSchedule.CloudBackupSchedulePolicyItemWeeklyList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__679552d565b5c1e7c0c8017144168575149bf9e173d91b391b3f537843970d4a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "CloudBackupSchedulePolicyItemWeeklyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33bcd78ee71af8b0094ca3517796709a507a16c5134e64292657dd1b7c29bbdc)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("CloudBackupSchedulePolicyItemWeeklyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__79078bf22804ae765c807b911ed4a156ff816b0f2cf9cf91ba2988b649ec0566)
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
            type_hints = typing.get_type_hints(_typecheckingstub__367eb6e89ac972cebb8b864c594e87f18e33a93fefb296f4de33f114c8f06c45)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d51b9948c5a59b75828f0ff49cc129b1413f4dc3920b1e47c642e9d2ba1e6d61)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CloudBackupSchedulePolicyItemWeekly]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CloudBackupSchedulePolicyItemWeekly]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CloudBackupSchedulePolicyItemWeekly]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25cdada0c818cbab463a5d407b610836261cce9e18d30b56ec50480bd4c1f516)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class CloudBackupSchedulePolicyItemWeeklyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cloudBackupSchedule.CloudBackupSchedulePolicyItemWeeklyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__034927d0185ab35ef83d64bb8f7305d1473ddb2da02fcb52ec0f5c21fc97cd79)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="frequencyType")
    def frequency_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "frequencyType"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="frequencyIntervalInput")
    def frequency_interval_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "frequencyIntervalInput"))

    @builtins.property
    @jsii.member(jsii_name="retentionUnitInput")
    def retention_unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "retentionUnitInput"))

    @builtins.property
    @jsii.member(jsii_name="retentionValueInput")
    def retention_value_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retentionValueInput"))

    @builtins.property
    @jsii.member(jsii_name="frequencyInterval")
    def frequency_interval(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "frequencyInterval"))

    @frequency_interval.setter
    def frequency_interval(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6beb5c127aa403951dcbbf0ffffa4bf0b3470c69f11ce7f68056cc229fbe19a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "frequencyInterval", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retentionUnit")
    def retention_unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "retentionUnit"))

    @retention_unit.setter
    def retention_unit(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd9cecdc24c19891eea81d98296a3c09c8fbe23a6911a4e275e15f53c4f899c1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retentionUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retentionValue")
    def retention_value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "retentionValue"))

    @retention_value.setter
    def retention_value(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2eeebc913a55a0fd835213659386766e8f02458a00fb397ab22c13dfaacc9803)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retentionValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CloudBackupSchedulePolicyItemWeekly]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CloudBackupSchedulePolicyItemWeekly]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CloudBackupSchedulePolicyItemWeekly]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d06d8a632ae8f26e88c2f5138de7412cf2a549e205ab0b9858ebdfeb7458d97)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.cloudBackupSchedule.CloudBackupSchedulePolicyItemYearly",
    jsii_struct_bases=[],
    name_mapping={
        "frequency_interval": "frequencyInterval",
        "retention_unit": "retentionUnit",
        "retention_value": "retentionValue",
    },
)
class CloudBackupSchedulePolicyItemYearly:
    def __init__(
        self,
        *,
        frequency_interval: jsii.Number,
        retention_unit: builtins.str,
        retention_value: jsii.Number,
    ) -> None:
        '''
        :param frequency_interval: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#frequency_interval CloudBackupSchedule#frequency_interval}.
        :param retention_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#retention_unit CloudBackupSchedule#retention_unit}.
        :param retention_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#retention_value CloudBackupSchedule#retention_value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__257130197780f5105d592f4540eb013c3b7346f23333568ce4528c5b2e355b5e)
            check_type(argname="argument frequency_interval", value=frequency_interval, expected_type=type_hints["frequency_interval"])
            check_type(argname="argument retention_unit", value=retention_unit, expected_type=type_hints["retention_unit"])
            check_type(argname="argument retention_value", value=retention_value, expected_type=type_hints["retention_value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "frequency_interval": frequency_interval,
            "retention_unit": retention_unit,
            "retention_value": retention_value,
        }

    @builtins.property
    def frequency_interval(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#frequency_interval CloudBackupSchedule#frequency_interval}.'''
        result = self._values.get("frequency_interval")
        assert result is not None, "Required property 'frequency_interval' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def retention_unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#retention_unit CloudBackupSchedule#retention_unit}.'''
        result = self._values.get("retention_unit")
        assert result is not None, "Required property 'retention_unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def retention_value(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/cloud_backup_schedule#retention_value CloudBackupSchedule#retention_value}.'''
        result = self._values.get("retention_value")
        assert result is not None, "Required property 'retention_value' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudBackupSchedulePolicyItemYearly(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudBackupSchedulePolicyItemYearlyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cloudBackupSchedule.CloudBackupSchedulePolicyItemYearlyList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__74d78881aaec83a47eaf94138653e79a1e7dc101df558fa5080de0ca67571ebe)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "CloudBackupSchedulePolicyItemYearlyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3bdea45f4ec3748e811c3f44f5d9cb56e46963e747db3e4c400d0e73d767cdd9)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("CloudBackupSchedulePolicyItemYearlyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__72b610345e79eb2e0498625fdc0f5d7e7ec5a5b0f8b28303155a499e911f17fe)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7f3dc0e5468080a4b0cc301a92db433c5c6435c12bc687c24051fcfb1a6cb86e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__973fb2f7e05d0267e3436dbabf8592e8a3fcfdc7738834b2ca52cf09ccf3f744)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CloudBackupSchedulePolicyItemYearly]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CloudBackupSchedulePolicyItemYearly]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CloudBackupSchedulePolicyItemYearly]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2a4e5e9d431ea5c2140b517f2ca0af80686d08ce631157f1373209f4b80eab2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class CloudBackupSchedulePolicyItemYearlyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.cloudBackupSchedule.CloudBackupSchedulePolicyItemYearlyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__97ab791d6e273ea1e7dacc3a3b914706163a2729edef3f98af2f5b8e8e83fde3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="frequencyType")
    def frequency_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "frequencyType"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="frequencyIntervalInput")
    def frequency_interval_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "frequencyIntervalInput"))

    @builtins.property
    @jsii.member(jsii_name="retentionUnitInput")
    def retention_unit_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "retentionUnitInput"))

    @builtins.property
    @jsii.member(jsii_name="retentionValueInput")
    def retention_value_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "retentionValueInput"))

    @builtins.property
    @jsii.member(jsii_name="frequencyInterval")
    def frequency_interval(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "frequencyInterval"))

    @frequency_interval.setter
    def frequency_interval(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d6bfccca66329e571c452eca85d4d8b333edf3ded9d4e0de0ffe60e01a0a7d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "frequencyInterval", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retentionUnit")
    def retention_unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "retentionUnit"))

    @retention_unit.setter
    def retention_unit(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de9aa2e667347c506f7f982e37d90434b0a2aa1be6ddeb5c43e0525ee71a46a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retentionUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retentionValue")
    def retention_value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "retentionValue"))

    @retention_value.setter
    def retention_value(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9d5fe3dfe055e8df17accc13b609f5731aa9161be16d2d744e0b2035ccb2375)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retentionValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CloudBackupSchedulePolicyItemYearly]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CloudBackupSchedulePolicyItemYearly]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CloudBackupSchedulePolicyItemYearly]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__906c4904486c51ad72b9d6bd5e57ceab6a55d3b7e50b5cdec57cdce42320599e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "CloudBackupSchedule",
    "CloudBackupScheduleConfig",
    "CloudBackupScheduleCopySettings",
    "CloudBackupScheduleCopySettingsList",
    "CloudBackupScheduleCopySettingsOutputReference",
    "CloudBackupScheduleExport",
    "CloudBackupScheduleExportOutputReference",
    "CloudBackupSchedulePolicyItemDaily",
    "CloudBackupSchedulePolicyItemDailyOutputReference",
    "CloudBackupSchedulePolicyItemHourly",
    "CloudBackupSchedulePolicyItemHourlyOutputReference",
    "CloudBackupSchedulePolicyItemMonthly",
    "CloudBackupSchedulePolicyItemMonthlyList",
    "CloudBackupSchedulePolicyItemMonthlyOutputReference",
    "CloudBackupSchedulePolicyItemWeekly",
    "CloudBackupSchedulePolicyItemWeeklyList",
    "CloudBackupSchedulePolicyItemWeeklyOutputReference",
    "CloudBackupSchedulePolicyItemYearly",
    "CloudBackupSchedulePolicyItemYearlyList",
    "CloudBackupSchedulePolicyItemYearlyOutputReference",
]

publication.publish()

def _typecheckingstub__344c5fd4696fda75905f5944497f97382441a465f6e49e9285991c716c152716(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    cluster_name: builtins.str,
    project_id: builtins.str,
    auto_export_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    copy_settings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CloudBackupScheduleCopySettings, typing.Dict[builtins.str, typing.Any]]]]] = None,
    export: typing.Optional[typing.Union[CloudBackupScheduleExport, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    policy_item_daily: typing.Optional[typing.Union[CloudBackupSchedulePolicyItemDaily, typing.Dict[builtins.str, typing.Any]]] = None,
    policy_item_hourly: typing.Optional[typing.Union[CloudBackupSchedulePolicyItemHourly, typing.Dict[builtins.str, typing.Any]]] = None,
    policy_item_monthly: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CloudBackupSchedulePolicyItemMonthly, typing.Dict[builtins.str, typing.Any]]]]] = None,
    policy_item_weekly: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CloudBackupSchedulePolicyItemWeekly, typing.Dict[builtins.str, typing.Any]]]]] = None,
    policy_item_yearly: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CloudBackupSchedulePolicyItemYearly, typing.Dict[builtins.str, typing.Any]]]]] = None,
    reference_hour_of_day: typing.Optional[jsii.Number] = None,
    reference_minute_of_hour: typing.Optional[jsii.Number] = None,
    restore_window_days: typing.Optional[jsii.Number] = None,
    update_snapshots: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    use_org_and_group_names_in_export_prefix: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__bcc6444f5cde1813546bc6f4bc06fc1f6100117f2811c23678a02adc83794e91(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b108240c1e5259379f0749ec3a296b8944a55d4ae4a263b081c77174b4969eef(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CloudBackupScheduleCopySettings, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__abbf5ebe8b71f98c41aff3ce4766c5aff025adf99f95694749d9cc0fcdc92bd8(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CloudBackupSchedulePolicyItemMonthly, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1c74326e3323660a93ef253615da67dc0f2032f3eccdc9f32f69d8673b998ce(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CloudBackupSchedulePolicyItemWeekly, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3ae06564c667812d33e81b3ff5c34011e45ce6bdd5824405b72635966332ea0(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CloudBackupSchedulePolicyItemYearly, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81c18efeb5ceac87365ac18c191c76193df2442f5188b6e6f58c0e64c8686266(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a149919bf5352a1cbf3ec42e2aeec0dd454c57c8d42432f02feda9ad18c2ac8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd49cb83afc70ba00b9a283a05a297f4a2192737a62e6853bf0cf6ce84dbcce0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16ddcc0dc620ebb7c4bc5e93c4dfa367b6c52ba00efc0dece18ae0b1d1e9c467(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fab4d307e33ff79a4954fc0dbf53536b931186cc30324b2d2c00d83c65b83799(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b408a68f7e5565bf9e3032d53951984b135ce12837c3096decf9a41215f3b05(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b302cabad0c11f12432d965a9932b583759d6561034e1159153bc3b85b424ab7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a05a7af7eef426c8333ce833d9e93614e248877bcf404c11fd08fb6494d6aa63(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61142b778b457438aa0b1af973246df6a895eb4508bd7f3672395eae0392292d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4dc71990a56b772b3bd536feea273f3f9584f44b01a9a6517b02e0efc74bb7f(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    cluster_name: builtins.str,
    project_id: builtins.str,
    auto_export_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    copy_settings: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CloudBackupScheduleCopySettings, typing.Dict[builtins.str, typing.Any]]]]] = None,
    export: typing.Optional[typing.Union[CloudBackupScheduleExport, typing.Dict[builtins.str, typing.Any]]] = None,
    id: typing.Optional[builtins.str] = None,
    policy_item_daily: typing.Optional[typing.Union[CloudBackupSchedulePolicyItemDaily, typing.Dict[builtins.str, typing.Any]]] = None,
    policy_item_hourly: typing.Optional[typing.Union[CloudBackupSchedulePolicyItemHourly, typing.Dict[builtins.str, typing.Any]]] = None,
    policy_item_monthly: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CloudBackupSchedulePolicyItemMonthly, typing.Dict[builtins.str, typing.Any]]]]] = None,
    policy_item_weekly: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CloudBackupSchedulePolicyItemWeekly, typing.Dict[builtins.str, typing.Any]]]]] = None,
    policy_item_yearly: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[CloudBackupSchedulePolicyItemYearly, typing.Dict[builtins.str, typing.Any]]]]] = None,
    reference_hour_of_day: typing.Optional[jsii.Number] = None,
    reference_minute_of_hour: typing.Optional[jsii.Number] = None,
    restore_window_days: typing.Optional[jsii.Number] = None,
    update_snapshots: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    use_org_and_group_names_in_export_prefix: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__523ec0e1143e0b37cea1ae9f41baa4a823609e844ca2216d3b575fa477a53630(
    *,
    cloud_provider: typing.Optional[builtins.str] = None,
    frequencies: typing.Optional[typing.Sequence[builtins.str]] = None,
    region_name: typing.Optional[builtins.str] = None,
    replication_spec_id: typing.Optional[builtins.str] = None,
    should_copy_oplogs: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    zone_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ba95d2bbab2e4bf013b27626b79a288a76c1c196880a6880d53a02ecd51552a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3dbd459f21bdd406a1f873c82a928af564b748662d41f93e3fa61dce39565e93(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63fa3b892593dd84988c57454c8adbcc6fd10ce0b4996c822fc811133da589b8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ee1759a8650f29359e4529b2e4b09838a37e24fe26083ddec2d6adeaa1818da(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca688f529545bec1eaf38daf102e2ae5d5d101e0dd78ad2c6cab37a9e4e7aa07(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d93408b829c1f2f868279e1badf10e581c4a0172ee1619d7fd01308d3e9cf2a2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CloudBackupScheduleCopySettings]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2c20dcd7132993a43ce66149f4490c7d193f777bca8e7b6fc53a4cfaad53c01(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3623b3ddbf2208aa613431a38d6b0fcb69ab9e21a0c709bf0e741f9c644d01f7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbce39f2dd790a77905b806ae2cb7bbcb70cf30e6f8a4df84dbf944af7f67862(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__608bcd1148905688b36fdb8fad236902bf52cb40b68360b451c54a57ad880750(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ac6cca473e3382b7fe1ef0c855769183dc299889efc6632ff2eebbe8b29f489(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8d1c67e363cbfc48164155df3b07d4aedaae212f34478505f960257f8c16d10(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2aef3937155d106eff66645db30dbdb001f49120190f149398efa7f59e83c526(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d99b13f1303d8e582583f112bafd3d6b6c02978abe83da7ae9d3f7f1e2fafa94(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CloudBackupScheduleCopySettings]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1af6a8150df3507a6761d405dab5a6503cfad010ccfbc559232f055a8efa3e7b(
    *,
    export_bucket_id: typing.Optional[builtins.str] = None,
    frequency_type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__808d1d36ffd0c9fea4a55909c33de26dc0d429f6d36b1655953d5ec2a67e3ef2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e87accae43dabd85a90cea503a46d4b0857c250ba5927f460f7e5551f676c4cb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92b0af9b3ecd86a551aacbc5d2e688c2da35f67c20259cb06b59db7c744241b1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89a5e5980dfba4530d1b6957b833921b076ad299f769828b4e8e296de9bbc531(
    value: typing.Optional[CloudBackupScheduleExport],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d25c48a2f328bb4cfd7f2562fe38665a9e8d5fc0b89ef875a2f33ebd7662c50(
    *,
    frequency_interval: jsii.Number,
    retention_unit: builtins.str,
    retention_value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7166716842104fd1e7151abcf195c844351d0278e9068a273093ee7df00bfd8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__877c0f969947c5684b9391d90e67aa0367789b98b0eaaa93b810aa9b96026ed7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7c8324c6f06193c105af1a29bf05ea307815436f8dbc7ab866302e05d8fc0a0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1b45ba57b5aa769b1f665b7347398694118de4b1bbbfb0cb2e8c95821122590(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75fda124118ad53a7c276ca3150437b3e76787be9727c4bc0bfa8e7da9a8968f(
    value: typing.Optional[CloudBackupSchedulePolicyItemDaily],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__baec4fa18f9131040792083ec19f399a5c14e3c06fbf7ccb512324c5f8d8f629(
    *,
    frequency_interval: jsii.Number,
    retention_unit: builtins.str,
    retention_value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2866be1c9d62894df5f2b4b6af02151da12891c1fd742d2667159982263d31e8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fbfc08390062dc7a7edced2732eedf3bacc5337b42ad4f4a794eb3d487b6c2d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__381c34845fe9312965a6eb38029fc685111be2b2376aebb2f193277fc99db836(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7408aaf31788494fe9722aa2c8e8d93a722240d2974247d0f9e7c5ee96d55b3b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2eb82dac0a8ae20b829c747b9550dd7d312e572a74be282f6acfb281cea1f557(
    value: typing.Optional[CloudBackupSchedulePolicyItemHourly],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df461d5dda46eae1e7d72be1adc934b736a6bc02a8e3043ead7919447277b984(
    *,
    frequency_interval: jsii.Number,
    retention_unit: builtins.str,
    retention_value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e4302cbf07f89580eae9a495d4c063fb9edd5fce288362b15a865de3184d1e9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c31a742b4e5608da57c4583e5f050e28ed057fa37ef82a12ba25c35b7937dbf3(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7361892d684e03cb0ee578fd433af34fd86c17a014862e4156a04c4bb3899d5c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ab75e5f7fa757f5571be2d87156bafeedac5309bf8ec86a2ad30ddaa7784024(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74c71857195d8f9657e978939e40824a1b4a2a332f6044c0e97faed6d3226898(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6096ee75b445a2e8d43cc45194486a625b0ff36e36d814a4b4502379b018e9a8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CloudBackupSchedulePolicyItemMonthly]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__196d38373e7e46f3b4e6c3fc330938391e536d27b00dae13fa9f586ce4b7ab40(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5095189969cd908094e31e3f87b78637fd8596fd02f9bd97321267bef02ab56b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__418db8ff796c84b0972b2fd32c98c389d6177622e8850443f06b4c7ad7f88212(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__475d630c0516c4793e5849cc06a3a2e0b58f80d0ea65befb53fb50f4298f7bb4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33041507c909c6b021f089d772eba8c6e537c84e265d9923e329bc75408090c2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CloudBackupSchedulePolicyItemMonthly]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c9db99c70f092c7202d73e0b024308210f4fee6daa3e135a8a07f928effbf62(
    *,
    frequency_interval: jsii.Number,
    retention_unit: builtins.str,
    retention_value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__679552d565b5c1e7c0c8017144168575149bf9e173d91b391b3f537843970d4a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33bcd78ee71af8b0094ca3517796709a507a16c5134e64292657dd1b7c29bbdc(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79078bf22804ae765c807b911ed4a156ff816b0f2cf9cf91ba2988b649ec0566(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__367eb6e89ac972cebb8b864c594e87f18e33a93fefb296f4de33f114c8f06c45(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d51b9948c5a59b75828f0ff49cc129b1413f4dc3920b1e47c642e9d2ba1e6d61(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25cdada0c818cbab463a5d407b610836261cce9e18d30b56ec50480bd4c1f516(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CloudBackupSchedulePolicyItemWeekly]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__034927d0185ab35ef83d64bb8f7305d1473ddb2da02fcb52ec0f5c21fc97cd79(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6beb5c127aa403951dcbbf0ffffa4bf0b3470c69f11ce7f68056cc229fbe19a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd9cecdc24c19891eea81d98296a3c09c8fbe23a6911a4e275e15f53c4f899c1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2eeebc913a55a0fd835213659386766e8f02458a00fb397ab22c13dfaacc9803(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d06d8a632ae8f26e88c2f5138de7412cf2a549e205ab0b9858ebdfeb7458d97(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CloudBackupSchedulePolicyItemWeekly]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__257130197780f5105d592f4540eb013c3b7346f23333568ce4528c5b2e355b5e(
    *,
    frequency_interval: jsii.Number,
    retention_unit: builtins.str,
    retention_value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74d78881aaec83a47eaf94138653e79a1e7dc101df558fa5080de0ca67571ebe(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3bdea45f4ec3748e811c3f44f5d9cb56e46963e747db3e4c400d0e73d767cdd9(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72b610345e79eb2e0498625fdc0f5d7e7ec5a5b0f8b28303155a499e911f17fe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f3dc0e5468080a4b0cc301a92db433c5c6435c12bc687c24051fcfb1a6cb86e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__973fb2f7e05d0267e3436dbabf8592e8a3fcfdc7738834b2ca52cf09ccf3f744(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2a4e5e9d431ea5c2140b517f2ca0af80686d08ce631157f1373209f4b80eab2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[CloudBackupSchedulePolicyItemYearly]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97ab791d6e273ea1e7dacc3a3b914706163a2729edef3f98af2f5b8e8e83fde3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d6bfccca66329e571c452eca85d4d8b333edf3ded9d4e0de0ffe60e01a0a7d7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de9aa2e667347c506f7f982e37d90434b0a2aa1be6ddeb5c43e0525ee71a46a6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9d5fe3dfe055e8df17accc13b609f5731aa9161be16d2d744e0b2035ccb2375(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__906c4904486c51ad72b9d6bd5e57ceab6a55d3b7e50b5cdec57cdce42320599e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, CloudBackupSchedulePolicyItemYearly]],
) -> None:
    """Type checking stubs"""
    pass
