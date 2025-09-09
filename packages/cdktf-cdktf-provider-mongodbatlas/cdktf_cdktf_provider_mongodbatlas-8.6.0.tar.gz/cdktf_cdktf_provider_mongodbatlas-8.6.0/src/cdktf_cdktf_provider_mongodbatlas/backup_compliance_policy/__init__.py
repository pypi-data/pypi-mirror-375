r'''
# `mongodbatlas_backup_compliance_policy`

Refer to the Terraform Registry for docs: [`mongodbatlas_backup_compliance_policy`](https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy).
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


class BackupCompliancePolicy(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.backupCompliancePolicy.BackupCompliancePolicy",
):
    '''Represents a {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy mongodbatlas_backup_compliance_policy}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        authorized_email: builtins.str,
        authorized_user_first_name: builtins.str,
        authorized_user_last_name: builtins.str,
        project_id: builtins.str,
        copy_protection_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        encryption_at_rest_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        on_demand_policy_item: typing.Optional[typing.Union["BackupCompliancePolicyOnDemandPolicyItem", typing.Dict[builtins.str, typing.Any]]] = None,
        pit_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        policy_item_daily: typing.Optional[typing.Union["BackupCompliancePolicyPolicyItemDaily", typing.Dict[builtins.str, typing.Any]]] = None,
        policy_item_hourly: typing.Optional[typing.Union["BackupCompliancePolicyPolicyItemHourly", typing.Dict[builtins.str, typing.Any]]] = None,
        policy_item_monthly: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["BackupCompliancePolicyPolicyItemMonthly", typing.Dict[builtins.str, typing.Any]]]]] = None,
        policy_item_weekly: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["BackupCompliancePolicyPolicyItemWeekly", typing.Dict[builtins.str, typing.Any]]]]] = None,
        policy_item_yearly: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["BackupCompliancePolicyPolicyItemYearly", typing.Dict[builtins.str, typing.Any]]]]] = None,
        restore_window_days: typing.Optional[jsii.Number] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy mongodbatlas_backup_compliance_policy} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param authorized_email: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#authorized_email BackupCompliancePolicy#authorized_email}.
        :param authorized_user_first_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#authorized_user_first_name BackupCompliancePolicy#authorized_user_first_name}.
        :param authorized_user_last_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#authorized_user_last_name BackupCompliancePolicy#authorized_user_last_name}.
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#project_id BackupCompliancePolicy#project_id}.
        :param copy_protection_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#copy_protection_enabled BackupCompliancePolicy#copy_protection_enabled}.
        :param encryption_at_rest_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#encryption_at_rest_enabled BackupCompliancePolicy#encryption_at_rest_enabled}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#id BackupCompliancePolicy#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param on_demand_policy_item: on_demand_policy_item block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#on_demand_policy_item BackupCompliancePolicy#on_demand_policy_item}
        :param pit_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#pit_enabled BackupCompliancePolicy#pit_enabled}.
        :param policy_item_daily: policy_item_daily block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#policy_item_daily BackupCompliancePolicy#policy_item_daily}
        :param policy_item_hourly: policy_item_hourly block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#policy_item_hourly BackupCompliancePolicy#policy_item_hourly}
        :param policy_item_monthly: policy_item_monthly block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#policy_item_monthly BackupCompliancePolicy#policy_item_monthly}
        :param policy_item_weekly: policy_item_weekly block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#policy_item_weekly BackupCompliancePolicy#policy_item_weekly}
        :param policy_item_yearly: policy_item_yearly block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#policy_item_yearly BackupCompliancePolicy#policy_item_yearly}
        :param restore_window_days: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#restore_window_days BackupCompliancePolicy#restore_window_days}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc544bf8d96732f6f2b14a387cba0f716138047462c2ccc95610a51a54b039e7)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = BackupCompliancePolicyConfig(
            authorized_email=authorized_email,
            authorized_user_first_name=authorized_user_first_name,
            authorized_user_last_name=authorized_user_last_name,
            project_id=project_id,
            copy_protection_enabled=copy_protection_enabled,
            encryption_at_rest_enabled=encryption_at_rest_enabled,
            id=id,
            on_demand_policy_item=on_demand_policy_item,
            pit_enabled=pit_enabled,
            policy_item_daily=policy_item_daily,
            policy_item_hourly=policy_item_hourly,
            policy_item_monthly=policy_item_monthly,
            policy_item_weekly=policy_item_weekly,
            policy_item_yearly=policy_item_yearly,
            restore_window_days=restore_window_days,
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
        '''Generates CDKTF code for importing a BackupCompliancePolicy resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the BackupCompliancePolicy to import.
        :param import_from_id: The id of the existing BackupCompliancePolicy that should be imported. Refer to the {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the BackupCompliancePolicy to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__683f5201e19d8b437f93b6fc504ff9b0ab55d957177f6418d1f718ba0db15e11)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putOnDemandPolicyItem")
    def put_on_demand_policy_item(
        self,
        *,
        frequency_interval: jsii.Number,
        retention_unit: builtins.str,
        retention_value: jsii.Number,
    ) -> None:
        '''
        :param frequency_interval: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#frequency_interval BackupCompliancePolicy#frequency_interval}.
        :param retention_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#retention_unit BackupCompliancePolicy#retention_unit}.
        :param retention_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#retention_value BackupCompliancePolicy#retention_value}.
        '''
        value = BackupCompliancePolicyOnDemandPolicyItem(
            frequency_interval=frequency_interval,
            retention_unit=retention_unit,
            retention_value=retention_value,
        )

        return typing.cast(None, jsii.invoke(self, "putOnDemandPolicyItem", [value]))

    @jsii.member(jsii_name="putPolicyItemDaily")
    def put_policy_item_daily(
        self,
        *,
        frequency_interval: jsii.Number,
        retention_unit: builtins.str,
        retention_value: jsii.Number,
    ) -> None:
        '''
        :param frequency_interval: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#frequency_interval BackupCompliancePolicy#frequency_interval}.
        :param retention_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#retention_unit BackupCompliancePolicy#retention_unit}.
        :param retention_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#retention_value BackupCompliancePolicy#retention_value}.
        '''
        value = BackupCompliancePolicyPolicyItemDaily(
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
        :param frequency_interval: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#frequency_interval BackupCompliancePolicy#frequency_interval}.
        :param retention_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#retention_unit BackupCompliancePolicy#retention_unit}.
        :param retention_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#retention_value BackupCompliancePolicy#retention_value}.
        '''
        value = BackupCompliancePolicyPolicyItemHourly(
            frequency_interval=frequency_interval,
            retention_unit=retention_unit,
            retention_value=retention_value,
        )

        return typing.cast(None, jsii.invoke(self, "putPolicyItemHourly", [value]))

    @jsii.member(jsii_name="putPolicyItemMonthly")
    def put_policy_item_monthly(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["BackupCompliancePolicyPolicyItemMonthly", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fcb6a97f80cc678b81d8badcc3c30e3ed2062317fb82de1afdd2a60193a97001)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putPolicyItemMonthly", [value]))

    @jsii.member(jsii_name="putPolicyItemWeekly")
    def put_policy_item_weekly(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["BackupCompliancePolicyPolicyItemWeekly", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c732d61e979e759ed08d383ae53f96298a142633f2c58b77c301ead3ea99ce38)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putPolicyItemWeekly", [value]))

    @jsii.member(jsii_name="putPolicyItemYearly")
    def put_policy_item_yearly(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["BackupCompliancePolicyPolicyItemYearly", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb134c296fe066393a924c8b1d767be0c2079ba88b5e9b77f0cd7ca7d6524934)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putPolicyItemYearly", [value]))

    @jsii.member(jsii_name="resetCopyProtectionEnabled")
    def reset_copy_protection_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCopyProtectionEnabled", []))

    @jsii.member(jsii_name="resetEncryptionAtRestEnabled")
    def reset_encryption_at_rest_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEncryptionAtRestEnabled", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetOnDemandPolicyItem")
    def reset_on_demand_policy_item(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOnDemandPolicyItem", []))

    @jsii.member(jsii_name="resetPitEnabled")
    def reset_pit_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPitEnabled", []))

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

    @jsii.member(jsii_name="resetRestoreWindowDays")
    def reset_restore_window_days(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRestoreWindowDays", []))

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
    @jsii.member(jsii_name="onDemandPolicyItem")
    def on_demand_policy_item(
        self,
    ) -> "BackupCompliancePolicyOnDemandPolicyItemOutputReference":
        return typing.cast("BackupCompliancePolicyOnDemandPolicyItemOutputReference", jsii.get(self, "onDemandPolicyItem"))

    @builtins.property
    @jsii.member(jsii_name="policyItemDaily")
    def policy_item_daily(
        self,
    ) -> "BackupCompliancePolicyPolicyItemDailyOutputReference":
        return typing.cast("BackupCompliancePolicyPolicyItemDailyOutputReference", jsii.get(self, "policyItemDaily"))

    @builtins.property
    @jsii.member(jsii_name="policyItemHourly")
    def policy_item_hourly(
        self,
    ) -> "BackupCompliancePolicyPolicyItemHourlyOutputReference":
        return typing.cast("BackupCompliancePolicyPolicyItemHourlyOutputReference", jsii.get(self, "policyItemHourly"))

    @builtins.property
    @jsii.member(jsii_name="policyItemMonthly")
    def policy_item_monthly(self) -> "BackupCompliancePolicyPolicyItemMonthlyList":
        return typing.cast("BackupCompliancePolicyPolicyItemMonthlyList", jsii.get(self, "policyItemMonthly"))

    @builtins.property
    @jsii.member(jsii_name="policyItemWeekly")
    def policy_item_weekly(self) -> "BackupCompliancePolicyPolicyItemWeeklyList":
        return typing.cast("BackupCompliancePolicyPolicyItemWeeklyList", jsii.get(self, "policyItemWeekly"))

    @builtins.property
    @jsii.member(jsii_name="policyItemYearly")
    def policy_item_yearly(self) -> "BackupCompliancePolicyPolicyItemYearlyList":
        return typing.cast("BackupCompliancePolicyPolicyItemYearlyList", jsii.get(self, "policyItemYearly"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="updatedDate")
    def updated_date(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedDate"))

    @builtins.property
    @jsii.member(jsii_name="updatedUser")
    def updated_user(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedUser"))

    @builtins.property
    @jsii.member(jsii_name="authorizedEmailInput")
    def authorized_email_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authorizedEmailInput"))

    @builtins.property
    @jsii.member(jsii_name="authorizedUserFirstNameInput")
    def authorized_user_first_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authorizedUserFirstNameInput"))

    @builtins.property
    @jsii.member(jsii_name="authorizedUserLastNameInput")
    def authorized_user_last_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authorizedUserLastNameInput"))

    @builtins.property
    @jsii.member(jsii_name="copyProtectionEnabledInput")
    def copy_protection_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "copyProtectionEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="encryptionAtRestEnabledInput")
    def encryption_at_rest_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "encryptionAtRestEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="onDemandPolicyItemInput")
    def on_demand_policy_item_input(
        self,
    ) -> typing.Optional["BackupCompliancePolicyOnDemandPolicyItem"]:
        return typing.cast(typing.Optional["BackupCompliancePolicyOnDemandPolicyItem"], jsii.get(self, "onDemandPolicyItemInput"))

    @builtins.property
    @jsii.member(jsii_name="pitEnabledInput")
    def pit_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "pitEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="policyItemDailyInput")
    def policy_item_daily_input(
        self,
    ) -> typing.Optional["BackupCompliancePolicyPolicyItemDaily"]:
        return typing.cast(typing.Optional["BackupCompliancePolicyPolicyItemDaily"], jsii.get(self, "policyItemDailyInput"))

    @builtins.property
    @jsii.member(jsii_name="policyItemHourlyInput")
    def policy_item_hourly_input(
        self,
    ) -> typing.Optional["BackupCompliancePolicyPolicyItemHourly"]:
        return typing.cast(typing.Optional["BackupCompliancePolicyPolicyItemHourly"], jsii.get(self, "policyItemHourlyInput"))

    @builtins.property
    @jsii.member(jsii_name="policyItemMonthlyInput")
    def policy_item_monthly_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["BackupCompliancePolicyPolicyItemMonthly"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["BackupCompliancePolicyPolicyItemMonthly"]]], jsii.get(self, "policyItemMonthlyInput"))

    @builtins.property
    @jsii.member(jsii_name="policyItemWeeklyInput")
    def policy_item_weekly_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["BackupCompliancePolicyPolicyItemWeekly"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["BackupCompliancePolicyPolicyItemWeekly"]]], jsii.get(self, "policyItemWeeklyInput"))

    @builtins.property
    @jsii.member(jsii_name="policyItemYearlyInput")
    def policy_item_yearly_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["BackupCompliancePolicyPolicyItemYearly"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["BackupCompliancePolicyPolicyItemYearly"]]], jsii.get(self, "policyItemYearlyInput"))

    @builtins.property
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="restoreWindowDaysInput")
    def restore_window_days_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "restoreWindowDaysInput"))

    @builtins.property
    @jsii.member(jsii_name="authorizedEmail")
    def authorized_email(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authorizedEmail"))

    @authorized_email.setter
    def authorized_email(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f0cb7fa66c6da13201c5cbf3cc6591e92ffb985ef68f512a4bce547f1f06a09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authorizedEmail", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="authorizedUserFirstName")
    def authorized_user_first_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authorizedUserFirstName"))

    @authorized_user_first_name.setter
    def authorized_user_first_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a90f4fb7b6fb13d7ca81c309d9307924e424feb11daee4694952c45c6aa1469)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authorizedUserFirstName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="authorizedUserLastName")
    def authorized_user_last_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authorizedUserLastName"))

    @authorized_user_last_name.setter
    def authorized_user_last_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08d5a44820cecff54e99b5a28f1bb79d21c253b46cd0779681f29a9dacd76bd9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authorizedUserLastName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="copyProtectionEnabled")
    def copy_protection_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "copyProtectionEnabled"))

    @copy_protection_enabled.setter
    def copy_protection_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71b8b41d49c1e804f7fa621ab85175fb59b028a14c1a1534ef48e9ef04764032)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "copyProtectionEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="encryptionAtRestEnabled")
    def encryption_at_rest_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "encryptionAtRestEnabled"))

    @encryption_at_rest_enabled.setter
    def encryption_at_rest_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c0b4a10dd85c0c53ffd2427ad6997c21440db11d812c4ce7a851264ca5e19b1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "encryptionAtRestEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ef63e533fc4784bf241f6700608912705855627eb3fcb074a2511ba7b722e30)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pitEnabled")
    def pit_enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "pitEnabled"))

    @pit_enabled.setter
    def pit_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f39f1ded8cc4daa5e83dbb0e0ee740691ca2010bd65e9d36f7a0747d06c570af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pitEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d59289dc3362111ae521b52225b99bdbf4a0759f433f5ed502e185e0e783283)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="restoreWindowDays")
    def restore_window_days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "restoreWindowDays"))

    @restore_window_days.setter
    def restore_window_days(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0455017213a0ddd3a171957a4646d7004c6739c7860f6d2f2c42ea18a91e4ce1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "restoreWindowDays", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.backupCompliancePolicy.BackupCompliancePolicyConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "authorized_email": "authorizedEmail",
        "authorized_user_first_name": "authorizedUserFirstName",
        "authorized_user_last_name": "authorizedUserLastName",
        "project_id": "projectId",
        "copy_protection_enabled": "copyProtectionEnabled",
        "encryption_at_rest_enabled": "encryptionAtRestEnabled",
        "id": "id",
        "on_demand_policy_item": "onDemandPolicyItem",
        "pit_enabled": "pitEnabled",
        "policy_item_daily": "policyItemDaily",
        "policy_item_hourly": "policyItemHourly",
        "policy_item_monthly": "policyItemMonthly",
        "policy_item_weekly": "policyItemWeekly",
        "policy_item_yearly": "policyItemYearly",
        "restore_window_days": "restoreWindowDays",
    },
)
class BackupCompliancePolicyConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        authorized_email: builtins.str,
        authorized_user_first_name: builtins.str,
        authorized_user_last_name: builtins.str,
        project_id: builtins.str,
        copy_protection_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        encryption_at_rest_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        on_demand_policy_item: typing.Optional[typing.Union["BackupCompliancePolicyOnDemandPolicyItem", typing.Dict[builtins.str, typing.Any]]] = None,
        pit_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        policy_item_daily: typing.Optional[typing.Union["BackupCompliancePolicyPolicyItemDaily", typing.Dict[builtins.str, typing.Any]]] = None,
        policy_item_hourly: typing.Optional[typing.Union["BackupCompliancePolicyPolicyItemHourly", typing.Dict[builtins.str, typing.Any]]] = None,
        policy_item_monthly: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["BackupCompliancePolicyPolicyItemMonthly", typing.Dict[builtins.str, typing.Any]]]]] = None,
        policy_item_weekly: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["BackupCompliancePolicyPolicyItemWeekly", typing.Dict[builtins.str, typing.Any]]]]] = None,
        policy_item_yearly: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["BackupCompliancePolicyPolicyItemYearly", typing.Dict[builtins.str, typing.Any]]]]] = None,
        restore_window_days: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param authorized_email: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#authorized_email BackupCompliancePolicy#authorized_email}.
        :param authorized_user_first_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#authorized_user_first_name BackupCompliancePolicy#authorized_user_first_name}.
        :param authorized_user_last_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#authorized_user_last_name BackupCompliancePolicy#authorized_user_last_name}.
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#project_id BackupCompliancePolicy#project_id}.
        :param copy_protection_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#copy_protection_enabled BackupCompliancePolicy#copy_protection_enabled}.
        :param encryption_at_rest_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#encryption_at_rest_enabled BackupCompliancePolicy#encryption_at_rest_enabled}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#id BackupCompliancePolicy#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param on_demand_policy_item: on_demand_policy_item block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#on_demand_policy_item BackupCompliancePolicy#on_demand_policy_item}
        :param pit_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#pit_enabled BackupCompliancePolicy#pit_enabled}.
        :param policy_item_daily: policy_item_daily block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#policy_item_daily BackupCompliancePolicy#policy_item_daily}
        :param policy_item_hourly: policy_item_hourly block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#policy_item_hourly BackupCompliancePolicy#policy_item_hourly}
        :param policy_item_monthly: policy_item_monthly block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#policy_item_monthly BackupCompliancePolicy#policy_item_monthly}
        :param policy_item_weekly: policy_item_weekly block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#policy_item_weekly BackupCompliancePolicy#policy_item_weekly}
        :param policy_item_yearly: policy_item_yearly block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#policy_item_yearly BackupCompliancePolicy#policy_item_yearly}
        :param restore_window_days: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#restore_window_days BackupCompliancePolicy#restore_window_days}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(on_demand_policy_item, dict):
            on_demand_policy_item = BackupCompliancePolicyOnDemandPolicyItem(**on_demand_policy_item)
        if isinstance(policy_item_daily, dict):
            policy_item_daily = BackupCompliancePolicyPolicyItemDaily(**policy_item_daily)
        if isinstance(policy_item_hourly, dict):
            policy_item_hourly = BackupCompliancePolicyPolicyItemHourly(**policy_item_hourly)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09b35143f2ac55f79a3aa6fd1bd412eae94454b69e2f2ee55f3c0873d24936b4)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument authorized_email", value=authorized_email, expected_type=type_hints["authorized_email"])
            check_type(argname="argument authorized_user_first_name", value=authorized_user_first_name, expected_type=type_hints["authorized_user_first_name"])
            check_type(argname="argument authorized_user_last_name", value=authorized_user_last_name, expected_type=type_hints["authorized_user_last_name"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument copy_protection_enabled", value=copy_protection_enabled, expected_type=type_hints["copy_protection_enabled"])
            check_type(argname="argument encryption_at_rest_enabled", value=encryption_at_rest_enabled, expected_type=type_hints["encryption_at_rest_enabled"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument on_demand_policy_item", value=on_demand_policy_item, expected_type=type_hints["on_demand_policy_item"])
            check_type(argname="argument pit_enabled", value=pit_enabled, expected_type=type_hints["pit_enabled"])
            check_type(argname="argument policy_item_daily", value=policy_item_daily, expected_type=type_hints["policy_item_daily"])
            check_type(argname="argument policy_item_hourly", value=policy_item_hourly, expected_type=type_hints["policy_item_hourly"])
            check_type(argname="argument policy_item_monthly", value=policy_item_monthly, expected_type=type_hints["policy_item_monthly"])
            check_type(argname="argument policy_item_weekly", value=policy_item_weekly, expected_type=type_hints["policy_item_weekly"])
            check_type(argname="argument policy_item_yearly", value=policy_item_yearly, expected_type=type_hints["policy_item_yearly"])
            check_type(argname="argument restore_window_days", value=restore_window_days, expected_type=type_hints["restore_window_days"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "authorized_email": authorized_email,
            "authorized_user_first_name": authorized_user_first_name,
            "authorized_user_last_name": authorized_user_last_name,
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
        if copy_protection_enabled is not None:
            self._values["copy_protection_enabled"] = copy_protection_enabled
        if encryption_at_rest_enabled is not None:
            self._values["encryption_at_rest_enabled"] = encryption_at_rest_enabled
        if id is not None:
            self._values["id"] = id
        if on_demand_policy_item is not None:
            self._values["on_demand_policy_item"] = on_demand_policy_item
        if pit_enabled is not None:
            self._values["pit_enabled"] = pit_enabled
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
        if restore_window_days is not None:
            self._values["restore_window_days"] = restore_window_days

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
    def authorized_email(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#authorized_email BackupCompliancePolicy#authorized_email}.'''
        result = self._values.get("authorized_email")
        assert result is not None, "Required property 'authorized_email' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def authorized_user_first_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#authorized_user_first_name BackupCompliancePolicy#authorized_user_first_name}.'''
        result = self._values.get("authorized_user_first_name")
        assert result is not None, "Required property 'authorized_user_first_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def authorized_user_last_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#authorized_user_last_name BackupCompliancePolicy#authorized_user_last_name}.'''
        result = self._values.get("authorized_user_last_name")
        assert result is not None, "Required property 'authorized_user_last_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def project_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#project_id BackupCompliancePolicy#project_id}.'''
        result = self._values.get("project_id")
        assert result is not None, "Required property 'project_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def copy_protection_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#copy_protection_enabled BackupCompliancePolicy#copy_protection_enabled}.'''
        result = self._values.get("copy_protection_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def encryption_at_rest_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#encryption_at_rest_enabled BackupCompliancePolicy#encryption_at_rest_enabled}.'''
        result = self._values.get("encryption_at_rest_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#id BackupCompliancePolicy#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def on_demand_policy_item(
        self,
    ) -> typing.Optional["BackupCompliancePolicyOnDemandPolicyItem"]:
        '''on_demand_policy_item block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#on_demand_policy_item BackupCompliancePolicy#on_demand_policy_item}
        '''
        result = self._values.get("on_demand_policy_item")
        return typing.cast(typing.Optional["BackupCompliancePolicyOnDemandPolicyItem"], result)

    @builtins.property
    def pit_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#pit_enabled BackupCompliancePolicy#pit_enabled}.'''
        result = self._values.get("pit_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def policy_item_daily(
        self,
    ) -> typing.Optional["BackupCompliancePolicyPolicyItemDaily"]:
        '''policy_item_daily block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#policy_item_daily BackupCompliancePolicy#policy_item_daily}
        '''
        result = self._values.get("policy_item_daily")
        return typing.cast(typing.Optional["BackupCompliancePolicyPolicyItemDaily"], result)

    @builtins.property
    def policy_item_hourly(
        self,
    ) -> typing.Optional["BackupCompliancePolicyPolicyItemHourly"]:
        '''policy_item_hourly block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#policy_item_hourly BackupCompliancePolicy#policy_item_hourly}
        '''
        result = self._values.get("policy_item_hourly")
        return typing.cast(typing.Optional["BackupCompliancePolicyPolicyItemHourly"], result)

    @builtins.property
    def policy_item_monthly(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["BackupCompliancePolicyPolicyItemMonthly"]]]:
        '''policy_item_monthly block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#policy_item_monthly BackupCompliancePolicy#policy_item_monthly}
        '''
        result = self._values.get("policy_item_monthly")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["BackupCompliancePolicyPolicyItemMonthly"]]], result)

    @builtins.property
    def policy_item_weekly(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["BackupCompliancePolicyPolicyItemWeekly"]]]:
        '''policy_item_weekly block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#policy_item_weekly BackupCompliancePolicy#policy_item_weekly}
        '''
        result = self._values.get("policy_item_weekly")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["BackupCompliancePolicyPolicyItemWeekly"]]], result)

    @builtins.property
    def policy_item_yearly(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["BackupCompliancePolicyPolicyItemYearly"]]]:
        '''policy_item_yearly block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#policy_item_yearly BackupCompliancePolicy#policy_item_yearly}
        '''
        result = self._values.get("policy_item_yearly")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["BackupCompliancePolicyPolicyItemYearly"]]], result)

    @builtins.property
    def restore_window_days(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#restore_window_days BackupCompliancePolicy#restore_window_days}.'''
        result = self._values.get("restore_window_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BackupCompliancePolicyConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.backupCompliancePolicy.BackupCompliancePolicyOnDemandPolicyItem",
    jsii_struct_bases=[],
    name_mapping={
        "frequency_interval": "frequencyInterval",
        "retention_unit": "retentionUnit",
        "retention_value": "retentionValue",
    },
)
class BackupCompliancePolicyOnDemandPolicyItem:
    def __init__(
        self,
        *,
        frequency_interval: jsii.Number,
        retention_unit: builtins.str,
        retention_value: jsii.Number,
    ) -> None:
        '''
        :param frequency_interval: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#frequency_interval BackupCompliancePolicy#frequency_interval}.
        :param retention_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#retention_unit BackupCompliancePolicy#retention_unit}.
        :param retention_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#retention_value BackupCompliancePolicy#retention_value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45c5e27427fba4a34e4162735ed9e6e50fc8ddac031cb423a356f6887ea7e81e)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#frequency_interval BackupCompliancePolicy#frequency_interval}.'''
        result = self._values.get("frequency_interval")
        assert result is not None, "Required property 'frequency_interval' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def retention_unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#retention_unit BackupCompliancePolicy#retention_unit}.'''
        result = self._values.get("retention_unit")
        assert result is not None, "Required property 'retention_unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def retention_value(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#retention_value BackupCompliancePolicy#retention_value}.'''
        result = self._values.get("retention_value")
        assert result is not None, "Required property 'retention_value' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BackupCompliancePolicyOnDemandPolicyItem(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BackupCompliancePolicyOnDemandPolicyItemOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.backupCompliancePolicy.BackupCompliancePolicyOnDemandPolicyItemOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__717176785022353916b6862b0a2bccfbdb79b1616224be3fab3102ff8dc2dc7e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4a45f2dc1b98de29d8026c60394f13f97cee0275c76d63ffc485a15dbf0e25dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "frequencyInterval", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retentionUnit")
    def retention_unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "retentionUnit"))

    @retention_unit.setter
    def retention_unit(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__118516567638df3865adaca9719391dad2d978000d01d43ab94c9a4e3c9d61c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retentionUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retentionValue")
    def retention_value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "retentionValue"))

    @retention_value.setter
    def retention_value(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c7646d7c826d99e6ee54dfd6d3db207897daecdde04e9c7b382eb1482d3fa0e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retentionValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[BackupCompliancePolicyOnDemandPolicyItem]:
        return typing.cast(typing.Optional[BackupCompliancePolicyOnDemandPolicyItem], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[BackupCompliancePolicyOnDemandPolicyItem],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b72b2bc75b1826ab39bb191d123378a2084fda8fb10715aa54db9cc81aa1d703)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.backupCompliancePolicy.BackupCompliancePolicyPolicyItemDaily",
    jsii_struct_bases=[],
    name_mapping={
        "frequency_interval": "frequencyInterval",
        "retention_unit": "retentionUnit",
        "retention_value": "retentionValue",
    },
)
class BackupCompliancePolicyPolicyItemDaily:
    def __init__(
        self,
        *,
        frequency_interval: jsii.Number,
        retention_unit: builtins.str,
        retention_value: jsii.Number,
    ) -> None:
        '''
        :param frequency_interval: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#frequency_interval BackupCompliancePolicy#frequency_interval}.
        :param retention_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#retention_unit BackupCompliancePolicy#retention_unit}.
        :param retention_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#retention_value BackupCompliancePolicy#retention_value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7f39f19f013cb4223040234600859d45378d6a7d32480525308510ca127a54a)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#frequency_interval BackupCompliancePolicy#frequency_interval}.'''
        result = self._values.get("frequency_interval")
        assert result is not None, "Required property 'frequency_interval' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def retention_unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#retention_unit BackupCompliancePolicy#retention_unit}.'''
        result = self._values.get("retention_unit")
        assert result is not None, "Required property 'retention_unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def retention_value(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#retention_value BackupCompliancePolicy#retention_value}.'''
        result = self._values.get("retention_value")
        assert result is not None, "Required property 'retention_value' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BackupCompliancePolicyPolicyItemDaily(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BackupCompliancePolicyPolicyItemDailyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.backupCompliancePolicy.BackupCompliancePolicyPolicyItemDailyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fdea2e5fe5e3ad62f76f9afa42ba2640afccd2c1af6a2233df01f59fe3d595f4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__df56db6dddaaa82049c76e5675ce49558198140bde01b2f8f667c37ca1f47f87)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "frequencyInterval", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retentionUnit")
    def retention_unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "retentionUnit"))

    @retention_unit.setter
    def retention_unit(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d70869c086cf86bca79776e4a447e9801f6804b9e269e6a0cba9a77e08a0bb8d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retentionUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retentionValue")
    def retention_value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "retentionValue"))

    @retention_value.setter
    def retention_value(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3bd243260a3b418e1569701c40d9e255c5dce78c0be184ed3bad247ed7dfd5cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retentionValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[BackupCompliancePolicyPolicyItemDaily]:
        return typing.cast(typing.Optional[BackupCompliancePolicyPolicyItemDaily], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[BackupCompliancePolicyPolicyItemDaily],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dee4af847bdf60aae9c0528038fcdb371ea64a75cf47a3da6cc49c5f99ddb17b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.backupCompliancePolicy.BackupCompliancePolicyPolicyItemHourly",
    jsii_struct_bases=[],
    name_mapping={
        "frequency_interval": "frequencyInterval",
        "retention_unit": "retentionUnit",
        "retention_value": "retentionValue",
    },
)
class BackupCompliancePolicyPolicyItemHourly:
    def __init__(
        self,
        *,
        frequency_interval: jsii.Number,
        retention_unit: builtins.str,
        retention_value: jsii.Number,
    ) -> None:
        '''
        :param frequency_interval: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#frequency_interval BackupCompliancePolicy#frequency_interval}.
        :param retention_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#retention_unit BackupCompliancePolicy#retention_unit}.
        :param retention_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#retention_value BackupCompliancePolicy#retention_value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3df8df084112669d326d103578db5ef438d55fba090140c29e5430ec37e1ce80)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#frequency_interval BackupCompliancePolicy#frequency_interval}.'''
        result = self._values.get("frequency_interval")
        assert result is not None, "Required property 'frequency_interval' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def retention_unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#retention_unit BackupCompliancePolicy#retention_unit}.'''
        result = self._values.get("retention_unit")
        assert result is not None, "Required property 'retention_unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def retention_value(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#retention_value BackupCompliancePolicy#retention_value}.'''
        result = self._values.get("retention_value")
        assert result is not None, "Required property 'retention_value' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BackupCompliancePolicyPolicyItemHourly(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BackupCompliancePolicyPolicyItemHourlyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.backupCompliancePolicy.BackupCompliancePolicyPolicyItemHourlyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8d276fcfc91fb6f9cac968270387e61c29f30fb83ec3663d454659ffd7eadb78)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b32f0256d7bc9b4d142168059a0e9f9ce0d9caea43d20f7527a591b6823451c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "frequencyInterval", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retentionUnit")
    def retention_unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "retentionUnit"))

    @retention_unit.setter
    def retention_unit(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ec8f4b38883dc8622a3ccd1e2f9f5a662addd2cdbb1cc8688eb6ac302aeb672)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retentionUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retentionValue")
    def retention_value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "retentionValue"))

    @retention_value.setter
    def retention_value(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__451e64d149b7731f809e1aab7094f39b20d679b3a20a01c6d827aa60695f4781)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retentionValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[BackupCompliancePolicyPolicyItemHourly]:
        return typing.cast(typing.Optional[BackupCompliancePolicyPolicyItemHourly], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[BackupCompliancePolicyPolicyItemHourly],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__373c4e9dd95d2c9e329d55856519d3b1e9485682ffed7dab024993e51a5db396)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.backupCompliancePolicy.BackupCompliancePolicyPolicyItemMonthly",
    jsii_struct_bases=[],
    name_mapping={
        "frequency_interval": "frequencyInterval",
        "retention_unit": "retentionUnit",
        "retention_value": "retentionValue",
    },
)
class BackupCompliancePolicyPolicyItemMonthly:
    def __init__(
        self,
        *,
        frequency_interval: jsii.Number,
        retention_unit: builtins.str,
        retention_value: jsii.Number,
    ) -> None:
        '''
        :param frequency_interval: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#frequency_interval BackupCompliancePolicy#frequency_interval}.
        :param retention_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#retention_unit BackupCompliancePolicy#retention_unit}.
        :param retention_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#retention_value BackupCompliancePolicy#retention_value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27a93f256f9b159008f2f6bc50dbadaee121b698bb557fb0fe7de6b849d1747c)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#frequency_interval BackupCompliancePolicy#frequency_interval}.'''
        result = self._values.get("frequency_interval")
        assert result is not None, "Required property 'frequency_interval' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def retention_unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#retention_unit BackupCompliancePolicy#retention_unit}.'''
        result = self._values.get("retention_unit")
        assert result is not None, "Required property 'retention_unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def retention_value(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#retention_value BackupCompliancePolicy#retention_value}.'''
        result = self._values.get("retention_value")
        assert result is not None, "Required property 'retention_value' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BackupCompliancePolicyPolicyItemMonthly(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BackupCompliancePolicyPolicyItemMonthlyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.backupCompliancePolicy.BackupCompliancePolicyPolicyItemMonthlyList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b3b0904d1e6f2627e2e096114997ccfd0b934bd9cef4d1b47766668898566ad0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "BackupCompliancePolicyPolicyItemMonthlyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__08311cf921d66e31adfdf6fa6c9edd251de46e78ddd4d828f3f1351cf8f9d2c2)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("BackupCompliancePolicyPolicyItemMonthlyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ceee95754d21eb89feba7685ffd961177850b917b713e22d642dd1c7c86a1c2c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__79298acf925d32f2762a46deb28e35b40e83bf3875efffab302a06b91f28e511)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e9416bcee5233326720dcd512284b6f19eef4822503f5636bb7a8e93ee435daa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[BackupCompliancePolicyPolicyItemMonthly]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[BackupCompliancePolicyPolicyItemMonthly]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[BackupCompliancePolicyPolicyItemMonthly]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa726d0b95eef0b64ecc6bdc6a322e9f67573d105939e814d32d13142a27acf9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class BackupCompliancePolicyPolicyItemMonthlyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.backupCompliancePolicy.BackupCompliancePolicyPolicyItemMonthlyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c2b75bf99016d9b7f11437e442ddfb3c6f7560e52c3cc4747ad52d3b31558e0d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ad9c71eb47053bb8f6ee33ea499c3533abae5c6c7f5391a0b0680ad98e098bad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "frequencyInterval", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retentionUnit")
    def retention_unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "retentionUnit"))

    @retention_unit.setter
    def retention_unit(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__347ea93fb49ce3feafed048417fbda9c3a661bc58f6cffaa1447a31c148d98e5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retentionUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retentionValue")
    def retention_value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "retentionValue"))

    @retention_value.setter
    def retention_value(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68b442e9902ea4f4e22f61710914ae41628f96e6d05af0401a0ce9424d247c8f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retentionValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, BackupCompliancePolicyPolicyItemMonthly]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, BackupCompliancePolicyPolicyItemMonthly]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, BackupCompliancePolicyPolicyItemMonthly]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5690faac0f6c485db5439ab964a7f9da76d42e23b1a6fa8383cb7e9930f71b69)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.backupCompliancePolicy.BackupCompliancePolicyPolicyItemWeekly",
    jsii_struct_bases=[],
    name_mapping={
        "frequency_interval": "frequencyInterval",
        "retention_unit": "retentionUnit",
        "retention_value": "retentionValue",
    },
)
class BackupCompliancePolicyPolicyItemWeekly:
    def __init__(
        self,
        *,
        frequency_interval: jsii.Number,
        retention_unit: builtins.str,
        retention_value: jsii.Number,
    ) -> None:
        '''
        :param frequency_interval: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#frequency_interval BackupCompliancePolicy#frequency_interval}.
        :param retention_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#retention_unit BackupCompliancePolicy#retention_unit}.
        :param retention_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#retention_value BackupCompliancePolicy#retention_value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68ccc839043431bddb6a3642c23cee31df9d7ef2710440946b1a61112588511c)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#frequency_interval BackupCompliancePolicy#frequency_interval}.'''
        result = self._values.get("frequency_interval")
        assert result is not None, "Required property 'frequency_interval' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def retention_unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#retention_unit BackupCompliancePolicy#retention_unit}.'''
        result = self._values.get("retention_unit")
        assert result is not None, "Required property 'retention_unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def retention_value(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#retention_value BackupCompliancePolicy#retention_value}.'''
        result = self._values.get("retention_value")
        assert result is not None, "Required property 'retention_value' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BackupCompliancePolicyPolicyItemWeekly(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BackupCompliancePolicyPolicyItemWeeklyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.backupCompliancePolicy.BackupCompliancePolicyPolicyItemWeeklyList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1ee5419b496644d9ddf8fa0b6a274db14270755a14889eed2749c1f3c0bf70ec)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "BackupCompliancePolicyPolicyItemWeeklyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5bd9a88e7f0e910f0485acaf05cb3b36436bbc79ba27545733dd54902bcef32d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("BackupCompliancePolicyPolicyItemWeeklyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94f72f2395065cf087d18838a0639b91b901ee760efe3a09137a02c8ab360518)
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
            type_hints = typing.get_type_hints(_typecheckingstub__391935f2c3a0f16bbea6c47b7341a50e02f352d3e442853767894c37afd1a878)
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
            type_hints = typing.get_type_hints(_typecheckingstub__776c059e1d6f9891b400007df15768eff21001cbb834553cc8736f4bb1a0a159)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[BackupCompliancePolicyPolicyItemWeekly]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[BackupCompliancePolicyPolicyItemWeekly]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[BackupCompliancePolicyPolicyItemWeekly]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a2b449a113ec4e5b293553140a21e271110ce43acf4b9c917946b9197749629)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class BackupCompliancePolicyPolicyItemWeeklyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.backupCompliancePolicy.BackupCompliancePolicyPolicyItemWeeklyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ac2bacf94e3db3b7a0d05200552e84c05d34e771acfd1b857c5568bac782e78d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__dada31095f73a86f4ac87ab691b85bc4d433fd3964a874236a18454fd8b5c121)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "frequencyInterval", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retentionUnit")
    def retention_unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "retentionUnit"))

    @retention_unit.setter
    def retention_unit(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b0dd91c43afcfdaebbeca88c3ee4871527af5aa1e8b3d493361d5ce72d8ce1ac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retentionUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retentionValue")
    def retention_value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "retentionValue"))

    @retention_value.setter
    def retention_value(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76a5ff7beae786131df08f062fa530c739412aeaa078f64d9bee7b585f738f79)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retentionValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, BackupCompliancePolicyPolicyItemWeekly]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, BackupCompliancePolicyPolicyItemWeekly]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, BackupCompliancePolicyPolicyItemWeekly]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df5285c034ac573b50758f70a233533bd24621ef02ea9c95df3f181c5b0f9b4f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.backupCompliancePolicy.BackupCompliancePolicyPolicyItemYearly",
    jsii_struct_bases=[],
    name_mapping={
        "frequency_interval": "frequencyInterval",
        "retention_unit": "retentionUnit",
        "retention_value": "retentionValue",
    },
)
class BackupCompliancePolicyPolicyItemYearly:
    def __init__(
        self,
        *,
        frequency_interval: jsii.Number,
        retention_unit: builtins.str,
        retention_value: jsii.Number,
    ) -> None:
        '''
        :param frequency_interval: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#frequency_interval BackupCompliancePolicy#frequency_interval}.
        :param retention_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#retention_unit BackupCompliancePolicy#retention_unit}.
        :param retention_value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#retention_value BackupCompliancePolicy#retention_value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f29fa29e424ddc37fccd57d5680969d6dabe7595af5d8a1c87e1eb745dca4a4f)
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#frequency_interval BackupCompliancePolicy#frequency_interval}.'''
        result = self._values.get("frequency_interval")
        assert result is not None, "Required property 'frequency_interval' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def retention_unit(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#retention_unit BackupCompliancePolicy#retention_unit}.'''
        result = self._values.get("retention_unit")
        assert result is not None, "Required property 'retention_unit' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def retention_value(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/backup_compliance_policy#retention_value BackupCompliancePolicy#retention_value}.'''
        result = self._values.get("retention_value")
        assert result is not None, "Required property 'retention_value' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BackupCompliancePolicyPolicyItemYearly(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class BackupCompliancePolicyPolicyItemYearlyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.backupCompliancePolicy.BackupCompliancePolicyPolicyItemYearlyList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0b2b2e9c4d65a5038f031c257db4fa346879ccf657293c0657e8440cc83db99c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "BackupCompliancePolicyPolicyItemYearlyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__91cc8859dade1ade421a18778f69e3df70e13832372015c1b908c68fbb26f6e2)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("BackupCompliancePolicyPolicyItemYearlyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f238bf36707865db847cd5d327f84df2c32e7ee52d50239c964201075f50ff7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5fa60b7da8606904205c66676364d2d3cd826078538a4f8f97c2af16a90a2f49)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5f1da48511ded3842123660d7fc01287f13810e19de781aec317e9c254f40946)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[BackupCompliancePolicyPolicyItemYearly]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[BackupCompliancePolicyPolicyItemYearly]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[BackupCompliancePolicyPolicyItemYearly]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7212a1f92a7b8a510f1c8c635193732878108384c2cb8fd1073afb9914edeff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class BackupCompliancePolicyPolicyItemYearlyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.backupCompliancePolicy.BackupCompliancePolicyPolicyItemYearlyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__550a3a88f2db2d5ff3a4e17b9aac9e89b98d7c6a7b560d6e619a61a4e199204a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__91fc15f42f1fe8bd5b66627ca94147d84dac843d99e33a6a1c09b4e69814ab58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "frequencyInterval", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retentionUnit")
    def retention_unit(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "retentionUnit"))

    @retention_unit.setter
    def retention_unit(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e015c6944e41e53bb3949e57941ce79ad47706309acd463087b2ae74b76f67e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retentionUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retentionValue")
    def retention_value(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "retentionValue"))

    @retention_value.setter
    def retention_value(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38759c761d7e2e260007b107b1e7c7500f4bb0917fb6e9db69f965316657d29f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retentionValue", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, BackupCompliancePolicyPolicyItemYearly]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, BackupCompliancePolicyPolicyItemYearly]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, BackupCompliancePolicyPolicyItemYearly]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74edf4cbc616157a82f77b357f5fc10241e988aa606d97a2c7f7bb2843e1a83e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "BackupCompliancePolicy",
    "BackupCompliancePolicyConfig",
    "BackupCompliancePolicyOnDemandPolicyItem",
    "BackupCompliancePolicyOnDemandPolicyItemOutputReference",
    "BackupCompliancePolicyPolicyItemDaily",
    "BackupCompliancePolicyPolicyItemDailyOutputReference",
    "BackupCompliancePolicyPolicyItemHourly",
    "BackupCompliancePolicyPolicyItemHourlyOutputReference",
    "BackupCompliancePolicyPolicyItemMonthly",
    "BackupCompliancePolicyPolicyItemMonthlyList",
    "BackupCompliancePolicyPolicyItemMonthlyOutputReference",
    "BackupCompliancePolicyPolicyItemWeekly",
    "BackupCompliancePolicyPolicyItemWeeklyList",
    "BackupCompliancePolicyPolicyItemWeeklyOutputReference",
    "BackupCompliancePolicyPolicyItemYearly",
    "BackupCompliancePolicyPolicyItemYearlyList",
    "BackupCompliancePolicyPolicyItemYearlyOutputReference",
]

publication.publish()

def _typecheckingstub__bc544bf8d96732f6f2b14a387cba0f716138047462c2ccc95610a51a54b039e7(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    authorized_email: builtins.str,
    authorized_user_first_name: builtins.str,
    authorized_user_last_name: builtins.str,
    project_id: builtins.str,
    copy_protection_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    encryption_at_rest_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    on_demand_policy_item: typing.Optional[typing.Union[BackupCompliancePolicyOnDemandPolicyItem, typing.Dict[builtins.str, typing.Any]]] = None,
    pit_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    policy_item_daily: typing.Optional[typing.Union[BackupCompliancePolicyPolicyItemDaily, typing.Dict[builtins.str, typing.Any]]] = None,
    policy_item_hourly: typing.Optional[typing.Union[BackupCompliancePolicyPolicyItemHourly, typing.Dict[builtins.str, typing.Any]]] = None,
    policy_item_monthly: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[BackupCompliancePolicyPolicyItemMonthly, typing.Dict[builtins.str, typing.Any]]]]] = None,
    policy_item_weekly: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[BackupCompliancePolicyPolicyItemWeekly, typing.Dict[builtins.str, typing.Any]]]]] = None,
    policy_item_yearly: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[BackupCompliancePolicyPolicyItemYearly, typing.Dict[builtins.str, typing.Any]]]]] = None,
    restore_window_days: typing.Optional[jsii.Number] = None,
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

def _typecheckingstub__683f5201e19d8b437f93b6fc504ff9b0ab55d957177f6418d1f718ba0db15e11(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fcb6a97f80cc678b81d8badcc3c30e3ed2062317fb82de1afdd2a60193a97001(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[BackupCompliancePolicyPolicyItemMonthly, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c732d61e979e759ed08d383ae53f96298a142633f2c58b77c301ead3ea99ce38(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[BackupCompliancePolicyPolicyItemWeekly, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb134c296fe066393a924c8b1d767be0c2079ba88b5e9b77f0cd7ca7d6524934(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[BackupCompliancePolicyPolicyItemYearly, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f0cb7fa66c6da13201c5cbf3cc6591e92ffb985ef68f512a4bce547f1f06a09(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a90f4fb7b6fb13d7ca81c309d9307924e424feb11daee4694952c45c6aa1469(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08d5a44820cecff54e99b5a28f1bb79d21c253b46cd0779681f29a9dacd76bd9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71b8b41d49c1e804f7fa621ab85175fb59b028a14c1a1534ef48e9ef04764032(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c0b4a10dd85c0c53ffd2427ad6997c21440db11d812c4ce7a851264ca5e19b1(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ef63e533fc4784bf241f6700608912705855627eb3fcb074a2511ba7b722e30(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f39f1ded8cc4daa5e83dbb0e0ee740691ca2010bd65e9d36f7a0747d06c570af(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d59289dc3362111ae521b52225b99bdbf4a0759f433f5ed502e185e0e783283(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0455017213a0ddd3a171957a4646d7004c6739c7860f6d2f2c42ea18a91e4ce1(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09b35143f2ac55f79a3aa6fd1bd412eae94454b69e2f2ee55f3c0873d24936b4(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    authorized_email: builtins.str,
    authorized_user_first_name: builtins.str,
    authorized_user_last_name: builtins.str,
    project_id: builtins.str,
    copy_protection_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    encryption_at_rest_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    on_demand_policy_item: typing.Optional[typing.Union[BackupCompliancePolicyOnDemandPolicyItem, typing.Dict[builtins.str, typing.Any]]] = None,
    pit_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    policy_item_daily: typing.Optional[typing.Union[BackupCompliancePolicyPolicyItemDaily, typing.Dict[builtins.str, typing.Any]]] = None,
    policy_item_hourly: typing.Optional[typing.Union[BackupCompliancePolicyPolicyItemHourly, typing.Dict[builtins.str, typing.Any]]] = None,
    policy_item_monthly: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[BackupCompliancePolicyPolicyItemMonthly, typing.Dict[builtins.str, typing.Any]]]]] = None,
    policy_item_weekly: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[BackupCompliancePolicyPolicyItemWeekly, typing.Dict[builtins.str, typing.Any]]]]] = None,
    policy_item_yearly: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[BackupCompliancePolicyPolicyItemYearly, typing.Dict[builtins.str, typing.Any]]]]] = None,
    restore_window_days: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45c5e27427fba4a34e4162735ed9e6e50fc8ddac031cb423a356f6887ea7e81e(
    *,
    frequency_interval: jsii.Number,
    retention_unit: builtins.str,
    retention_value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__717176785022353916b6862b0a2bccfbdb79b1616224be3fab3102ff8dc2dc7e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a45f2dc1b98de29d8026c60394f13f97cee0275c76d63ffc485a15dbf0e25dc(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__118516567638df3865adaca9719391dad2d978000d01d43ab94c9a4e3c9d61c6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c7646d7c826d99e6ee54dfd6d3db207897daecdde04e9c7b382eb1482d3fa0e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b72b2bc75b1826ab39bb191d123378a2084fda8fb10715aa54db9cc81aa1d703(
    value: typing.Optional[BackupCompliancePolicyOnDemandPolicyItem],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7f39f19f013cb4223040234600859d45378d6a7d32480525308510ca127a54a(
    *,
    frequency_interval: jsii.Number,
    retention_unit: builtins.str,
    retention_value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdea2e5fe5e3ad62f76f9afa42ba2640afccd2c1af6a2233df01f59fe3d595f4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df56db6dddaaa82049c76e5675ce49558198140bde01b2f8f667c37ca1f47f87(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d70869c086cf86bca79776e4a447e9801f6804b9e269e6a0cba9a77e08a0bb8d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3bd243260a3b418e1569701c40d9e255c5dce78c0be184ed3bad247ed7dfd5cc(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dee4af847bdf60aae9c0528038fcdb371ea64a75cf47a3da6cc49c5f99ddb17b(
    value: typing.Optional[BackupCompliancePolicyPolicyItemDaily],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3df8df084112669d326d103578db5ef438d55fba090140c29e5430ec37e1ce80(
    *,
    frequency_interval: jsii.Number,
    retention_unit: builtins.str,
    retention_value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d276fcfc91fb6f9cac968270387e61c29f30fb83ec3663d454659ffd7eadb78(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b32f0256d7bc9b4d142168059a0e9f9ce0d9caea43d20f7527a591b6823451c8(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ec8f4b38883dc8622a3ccd1e2f9f5a662addd2cdbb1cc8688eb6ac302aeb672(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__451e64d149b7731f809e1aab7094f39b20d679b3a20a01c6d827aa60695f4781(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__373c4e9dd95d2c9e329d55856519d3b1e9485682ffed7dab024993e51a5db396(
    value: typing.Optional[BackupCompliancePolicyPolicyItemHourly],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27a93f256f9b159008f2f6bc50dbadaee121b698bb557fb0fe7de6b849d1747c(
    *,
    frequency_interval: jsii.Number,
    retention_unit: builtins.str,
    retention_value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3b0904d1e6f2627e2e096114997ccfd0b934bd9cef4d1b47766668898566ad0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__08311cf921d66e31adfdf6fa6c9edd251de46e78ddd4d828f3f1351cf8f9d2c2(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ceee95754d21eb89feba7685ffd961177850b917b713e22d642dd1c7c86a1c2c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79298acf925d32f2762a46deb28e35b40e83bf3875efffab302a06b91f28e511(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9416bcee5233326720dcd512284b6f19eef4822503f5636bb7a8e93ee435daa(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa726d0b95eef0b64ecc6bdc6a322e9f67573d105939e814d32d13142a27acf9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[BackupCompliancePolicyPolicyItemMonthly]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2b75bf99016d9b7f11437e442ddfb3c6f7560e52c3cc4747ad52d3b31558e0d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad9c71eb47053bb8f6ee33ea499c3533abae5c6c7f5391a0b0680ad98e098bad(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__347ea93fb49ce3feafed048417fbda9c3a661bc58f6cffaa1447a31c148d98e5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68b442e9902ea4f4e22f61710914ae41628f96e6d05af0401a0ce9424d247c8f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5690faac0f6c485db5439ab964a7f9da76d42e23b1a6fa8383cb7e9930f71b69(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, BackupCompliancePolicyPolicyItemMonthly]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68ccc839043431bddb6a3642c23cee31df9d7ef2710440946b1a61112588511c(
    *,
    frequency_interval: jsii.Number,
    retention_unit: builtins.str,
    retention_value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ee5419b496644d9ddf8fa0b6a274db14270755a14889eed2749c1f3c0bf70ec(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5bd9a88e7f0e910f0485acaf05cb3b36436bbc79ba27545733dd54902bcef32d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94f72f2395065cf087d18838a0639b91b901ee760efe3a09137a02c8ab360518(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__391935f2c3a0f16bbea6c47b7341a50e02f352d3e442853767894c37afd1a878(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__776c059e1d6f9891b400007df15768eff21001cbb834553cc8736f4bb1a0a159(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a2b449a113ec4e5b293553140a21e271110ce43acf4b9c917946b9197749629(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[BackupCompliancePolicyPolicyItemWeekly]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac2bacf94e3db3b7a0d05200552e84c05d34e771acfd1b857c5568bac782e78d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dada31095f73a86f4ac87ab691b85bc4d433fd3964a874236a18454fd8b5c121(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0dd91c43afcfdaebbeca88c3ee4871527af5aa1e8b3d493361d5ce72d8ce1ac(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76a5ff7beae786131df08f062fa530c739412aeaa078f64d9bee7b585f738f79(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df5285c034ac573b50758f70a233533bd24621ef02ea9c95df3f181c5b0f9b4f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, BackupCompliancePolicyPolicyItemWeekly]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f29fa29e424ddc37fccd57d5680969d6dabe7595af5d8a1c87e1eb745dca4a4f(
    *,
    frequency_interval: jsii.Number,
    retention_unit: builtins.str,
    retention_value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b2b2e9c4d65a5038f031c257db4fa346879ccf657293c0657e8440cc83db99c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91cc8859dade1ade421a18778f69e3df70e13832372015c1b908c68fbb26f6e2(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f238bf36707865db847cd5d327f84df2c32e7ee52d50239c964201075f50ff7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5fa60b7da8606904205c66676364d2d3cd826078538a4f8f97c2af16a90a2f49(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f1da48511ded3842123660d7fc01287f13810e19de781aec317e9c254f40946(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7212a1f92a7b8a510f1c8c635193732878108384c2cb8fd1073afb9914edeff(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[BackupCompliancePolicyPolicyItemYearly]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__550a3a88f2db2d5ff3a4e17b9aac9e89b98d7c6a7b560d6e619a61a4e199204a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91fc15f42f1fe8bd5b66627ca94147d84dac843d99e33a6a1c09b4e69814ab58(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e015c6944e41e53bb3949e57941ce79ad47706309acd463087b2ae74b76f67e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38759c761d7e2e260007b107b1e7c7500f4bb0917fb6e9db69f965316657d29f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74edf4cbc616157a82f77b357f5fc10241e988aa606d97a2c7f7bb2843e1a83e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, BackupCompliancePolicyPolicyItemYearly]],
) -> None:
    """Type checking stubs"""
    pass
