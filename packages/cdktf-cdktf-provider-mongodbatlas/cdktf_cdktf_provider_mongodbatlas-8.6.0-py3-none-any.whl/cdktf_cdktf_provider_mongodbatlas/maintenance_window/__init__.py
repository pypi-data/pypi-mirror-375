r'''
# `mongodbatlas_maintenance_window`

Refer to the Terraform Registry for docs: [`mongodbatlas_maintenance_window`](https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window).
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


class MaintenanceWindow(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.maintenanceWindow.MaintenanceWindow",
):
    '''Represents a {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window mongodbatlas_maintenance_window}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        day_of_week: jsii.Number,
        project_id: builtins.str,
        auto_defer: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        auto_defer_once_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        defer: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        hour_of_day: typing.Optional[jsii.Number] = None,
        id: typing.Optional[builtins.str] = None,
        protected_hours: typing.Optional[typing.Union["MaintenanceWindowProtectedHours", typing.Dict[builtins.str, typing.Any]]] = None,
        start_asap: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window mongodbatlas_maintenance_window} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param day_of_week: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window#day_of_week MaintenanceWindow#day_of_week}.
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window#project_id MaintenanceWindow#project_id}.
        :param auto_defer: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window#auto_defer MaintenanceWindow#auto_defer}.
        :param auto_defer_once_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window#auto_defer_once_enabled MaintenanceWindow#auto_defer_once_enabled}.
        :param defer: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window#defer MaintenanceWindow#defer}.
        :param hour_of_day: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window#hour_of_day MaintenanceWindow#hour_of_day}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window#id MaintenanceWindow#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param protected_hours: protected_hours block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window#protected_hours MaintenanceWindow#protected_hours}
        :param start_asap: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window#start_asap MaintenanceWindow#start_asap}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__597421cc3939eb57333e1c7a9daeca11f08699d3680685bd7ff248c61ad23bf6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = MaintenanceWindowConfig(
            day_of_week=day_of_week,
            project_id=project_id,
            auto_defer=auto_defer,
            auto_defer_once_enabled=auto_defer_once_enabled,
            defer=defer,
            hour_of_day=hour_of_day,
            id=id,
            protected_hours=protected_hours,
            start_asap=start_asap,
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
        '''Generates CDKTF code for importing a MaintenanceWindow resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the MaintenanceWindow to import.
        :param import_from_id: The id of the existing MaintenanceWindow that should be imported. Refer to the {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the MaintenanceWindow to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__244d0884faaa24b695616767e3214cd0067a25f694e9325d6217dcecced6363f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putProtectedHours")
    def put_protected_hours(
        self,
        *,
        end_hour_of_day: jsii.Number,
        start_hour_of_day: jsii.Number,
    ) -> None:
        '''
        :param end_hour_of_day: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window#end_hour_of_day MaintenanceWindow#end_hour_of_day}.
        :param start_hour_of_day: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window#start_hour_of_day MaintenanceWindow#start_hour_of_day}.
        '''
        value = MaintenanceWindowProtectedHours(
            end_hour_of_day=end_hour_of_day, start_hour_of_day=start_hour_of_day
        )

        return typing.cast(None, jsii.invoke(self, "putProtectedHours", [value]))

    @jsii.member(jsii_name="resetAutoDefer")
    def reset_auto_defer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoDefer", []))

    @jsii.member(jsii_name="resetAutoDeferOnceEnabled")
    def reset_auto_defer_once_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoDeferOnceEnabled", []))

    @jsii.member(jsii_name="resetDefer")
    def reset_defer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefer", []))

    @jsii.member(jsii_name="resetHourOfDay")
    def reset_hour_of_day(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHourOfDay", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetProtectedHours")
    def reset_protected_hours(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProtectedHours", []))

    @jsii.member(jsii_name="resetStartAsap")
    def reset_start_asap(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStartAsap", []))

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
    @jsii.member(jsii_name="numberOfDeferrals")
    def number_of_deferrals(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numberOfDeferrals"))

    @builtins.property
    @jsii.member(jsii_name="protectedHours")
    def protected_hours(self) -> "MaintenanceWindowProtectedHoursOutputReference":
        return typing.cast("MaintenanceWindowProtectedHoursOutputReference", jsii.get(self, "protectedHours"))

    @builtins.property
    @jsii.member(jsii_name="timeZoneId")
    def time_zone_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timeZoneId"))

    @builtins.property
    @jsii.member(jsii_name="autoDeferInput")
    def auto_defer_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "autoDeferInput"))

    @builtins.property
    @jsii.member(jsii_name="autoDeferOnceEnabledInput")
    def auto_defer_once_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "autoDeferOnceEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="dayOfWeekInput")
    def day_of_week_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "dayOfWeekInput"))

    @builtins.property
    @jsii.member(jsii_name="deferInput")
    def defer_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "deferInput"))

    @builtins.property
    @jsii.member(jsii_name="hourOfDayInput")
    def hour_of_day_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "hourOfDayInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="protectedHoursInput")
    def protected_hours_input(
        self,
    ) -> typing.Optional["MaintenanceWindowProtectedHours"]:
        return typing.cast(typing.Optional["MaintenanceWindowProtectedHours"], jsii.get(self, "protectedHoursInput"))

    @builtins.property
    @jsii.member(jsii_name="startAsapInput")
    def start_asap_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "startAsapInput"))

    @builtins.property
    @jsii.member(jsii_name="autoDefer")
    def auto_defer(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "autoDefer"))

    @auto_defer.setter
    def auto_defer(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__652eb799a474af817983734101f36fd5b15be934558f8b1d45ed93e249c35c05)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoDefer", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autoDeferOnceEnabled")
    def auto_defer_once_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "autoDeferOnceEnabled"))

    @auto_defer_once_enabled.setter
    def auto_defer_once_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5d7700aeb9389c4fc02bd68ce10740b4e830407091d8a50dbda4e898d39af35)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoDeferOnceEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dayOfWeek")
    def day_of_week(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "dayOfWeek"))

    @day_of_week.setter
    def day_of_week(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca5f98fcc0ed58fde760ff26651ed26ed535fc25626662beb88a4d8991d94b1a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dayOfWeek", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defer")
    def defer(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "defer"))

    @defer.setter
    def defer(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ce34c7fb2ee380f3648d01f63ac593befb41f4009512607840ffcb10fe8b5a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defer", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="hourOfDay")
    def hour_of_day(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "hourOfDay"))

    @hour_of_day.setter
    def hour_of_day(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__35ffc1f3d554c9cc90e19e54cf536fbf1775c4fa03e42ec1a7b88b41dcab11a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hourOfDay", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d3ff4e50ec2a5fac7a7459f1190923905637a5f1e26e9bf525c8dfb8d922101)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c96f3e1a42327b354e2ac10136d4eddd54d7b95eca7c2aab9b389c282a35172)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="startAsap")
    def start_asap(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "startAsap"))

    @start_asap.setter
    def start_asap(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85eaeab953070405855badeb73a73bf608533d10479650f5cf35728283960e6b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "startAsap", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.maintenanceWindow.MaintenanceWindowConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "day_of_week": "dayOfWeek",
        "project_id": "projectId",
        "auto_defer": "autoDefer",
        "auto_defer_once_enabled": "autoDeferOnceEnabled",
        "defer": "defer",
        "hour_of_day": "hourOfDay",
        "id": "id",
        "protected_hours": "protectedHours",
        "start_asap": "startAsap",
    },
)
class MaintenanceWindowConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        day_of_week: jsii.Number,
        project_id: builtins.str,
        auto_defer: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        auto_defer_once_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        defer: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        hour_of_day: typing.Optional[jsii.Number] = None,
        id: typing.Optional[builtins.str] = None,
        protected_hours: typing.Optional[typing.Union["MaintenanceWindowProtectedHours", typing.Dict[builtins.str, typing.Any]]] = None,
        start_asap: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param day_of_week: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window#day_of_week MaintenanceWindow#day_of_week}.
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window#project_id MaintenanceWindow#project_id}.
        :param auto_defer: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window#auto_defer MaintenanceWindow#auto_defer}.
        :param auto_defer_once_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window#auto_defer_once_enabled MaintenanceWindow#auto_defer_once_enabled}.
        :param defer: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window#defer MaintenanceWindow#defer}.
        :param hour_of_day: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window#hour_of_day MaintenanceWindow#hour_of_day}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window#id MaintenanceWindow#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param protected_hours: protected_hours block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window#protected_hours MaintenanceWindow#protected_hours}
        :param start_asap: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window#start_asap MaintenanceWindow#start_asap}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(protected_hours, dict):
            protected_hours = MaintenanceWindowProtectedHours(**protected_hours)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0fd18d6a5a9864c5d51a6ddd1adc3c4017aa9956ee8366e592293e55a409fa95)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument day_of_week", value=day_of_week, expected_type=type_hints["day_of_week"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument auto_defer", value=auto_defer, expected_type=type_hints["auto_defer"])
            check_type(argname="argument auto_defer_once_enabled", value=auto_defer_once_enabled, expected_type=type_hints["auto_defer_once_enabled"])
            check_type(argname="argument defer", value=defer, expected_type=type_hints["defer"])
            check_type(argname="argument hour_of_day", value=hour_of_day, expected_type=type_hints["hour_of_day"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument protected_hours", value=protected_hours, expected_type=type_hints["protected_hours"])
            check_type(argname="argument start_asap", value=start_asap, expected_type=type_hints["start_asap"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "day_of_week": day_of_week,
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
        if auto_defer is not None:
            self._values["auto_defer"] = auto_defer
        if auto_defer_once_enabled is not None:
            self._values["auto_defer_once_enabled"] = auto_defer_once_enabled
        if defer is not None:
            self._values["defer"] = defer
        if hour_of_day is not None:
            self._values["hour_of_day"] = hour_of_day
        if id is not None:
            self._values["id"] = id
        if protected_hours is not None:
            self._values["protected_hours"] = protected_hours
        if start_asap is not None:
            self._values["start_asap"] = start_asap

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
    def day_of_week(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window#day_of_week MaintenanceWindow#day_of_week}.'''
        result = self._values.get("day_of_week")
        assert result is not None, "Required property 'day_of_week' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def project_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window#project_id MaintenanceWindow#project_id}.'''
        result = self._values.get("project_id")
        assert result is not None, "Required property 'project_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auto_defer(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window#auto_defer MaintenanceWindow#auto_defer}.'''
        result = self._values.get("auto_defer")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def auto_defer_once_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window#auto_defer_once_enabled MaintenanceWindow#auto_defer_once_enabled}.'''
        result = self._values.get("auto_defer_once_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def defer(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window#defer MaintenanceWindow#defer}.'''
        result = self._values.get("defer")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def hour_of_day(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window#hour_of_day MaintenanceWindow#hour_of_day}.'''
        result = self._values.get("hour_of_day")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window#id MaintenanceWindow#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def protected_hours(self) -> typing.Optional["MaintenanceWindowProtectedHours"]:
        '''protected_hours block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window#protected_hours MaintenanceWindow#protected_hours}
        '''
        result = self._values.get("protected_hours")
        return typing.cast(typing.Optional["MaintenanceWindowProtectedHours"], result)

    @builtins.property
    def start_asap(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window#start_asap MaintenanceWindow#start_asap}.'''
        result = self._values.get("start_asap")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MaintenanceWindowConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.maintenanceWindow.MaintenanceWindowProtectedHours",
    jsii_struct_bases=[],
    name_mapping={
        "end_hour_of_day": "endHourOfDay",
        "start_hour_of_day": "startHourOfDay",
    },
)
class MaintenanceWindowProtectedHours:
    def __init__(
        self,
        *,
        end_hour_of_day: jsii.Number,
        start_hour_of_day: jsii.Number,
    ) -> None:
        '''
        :param end_hour_of_day: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window#end_hour_of_day MaintenanceWindow#end_hour_of_day}.
        :param start_hour_of_day: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window#start_hour_of_day MaintenanceWindow#start_hour_of_day}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1f8262cfdde4c357a0863695c49c11f94a5971953d6ab7377c2854dcaec73b5)
            check_type(argname="argument end_hour_of_day", value=end_hour_of_day, expected_type=type_hints["end_hour_of_day"])
            check_type(argname="argument start_hour_of_day", value=start_hour_of_day, expected_type=type_hints["start_hour_of_day"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "end_hour_of_day": end_hour_of_day,
            "start_hour_of_day": start_hour_of_day,
        }

    @builtins.property
    def end_hour_of_day(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window#end_hour_of_day MaintenanceWindow#end_hour_of_day}.'''
        result = self._values.get("end_hour_of_day")
        assert result is not None, "Required property 'end_hour_of_day' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def start_hour_of_day(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/maintenance_window#start_hour_of_day MaintenanceWindow#start_hour_of_day}.'''
        result = self._values.get("start_hour_of_day")
        assert result is not None, "Required property 'start_hour_of_day' is missing"
        return typing.cast(jsii.Number, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "MaintenanceWindowProtectedHours(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class MaintenanceWindowProtectedHoursOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.maintenanceWindow.MaintenanceWindowProtectedHoursOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__39c9074924814a50d26318a7437d57603465b14220d331b5dd9b0bbbdbba9a10)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="endHourOfDayInput")
    def end_hour_of_day_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "endHourOfDayInput"))

    @builtins.property
    @jsii.member(jsii_name="startHourOfDayInput")
    def start_hour_of_day_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "startHourOfDayInput"))

    @builtins.property
    @jsii.member(jsii_name="endHourOfDay")
    def end_hour_of_day(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "endHourOfDay"))

    @end_hour_of_day.setter
    def end_hour_of_day(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0dcdc6011825200e28ea139141c56b02461a838702723a95f6920e470bfc5c72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "endHourOfDay", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="startHourOfDay")
    def start_hour_of_day(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "startHourOfDay"))

    @start_hour_of_day.setter
    def start_hour_of_day(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2db63cd1bc48e5243bc7ce9f5e2bbc770a2d1e95bf11d0f82e4d187b623618b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "startHourOfDay", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[MaintenanceWindowProtectedHours]:
        return typing.cast(typing.Optional[MaintenanceWindowProtectedHours], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[MaintenanceWindowProtectedHours],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f506816396550e9013ad58b163b77d3c540f8d09825c445d24030298397b0c3b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "MaintenanceWindow",
    "MaintenanceWindowConfig",
    "MaintenanceWindowProtectedHours",
    "MaintenanceWindowProtectedHoursOutputReference",
]

publication.publish()

def _typecheckingstub__597421cc3939eb57333e1c7a9daeca11f08699d3680685bd7ff248c61ad23bf6(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    day_of_week: jsii.Number,
    project_id: builtins.str,
    auto_defer: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    auto_defer_once_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    defer: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    hour_of_day: typing.Optional[jsii.Number] = None,
    id: typing.Optional[builtins.str] = None,
    protected_hours: typing.Optional[typing.Union[MaintenanceWindowProtectedHours, typing.Dict[builtins.str, typing.Any]]] = None,
    start_asap: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
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

def _typecheckingstub__244d0884faaa24b695616767e3214cd0067a25f694e9325d6217dcecced6363f(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__652eb799a474af817983734101f36fd5b15be934558f8b1d45ed93e249c35c05(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5d7700aeb9389c4fc02bd68ce10740b4e830407091d8a50dbda4e898d39af35(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca5f98fcc0ed58fde760ff26651ed26ed535fc25626662beb88a4d8991d94b1a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ce34c7fb2ee380f3648d01f63ac593befb41f4009512607840ffcb10fe8b5a0(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__35ffc1f3d554c9cc90e19e54cf536fbf1775c4fa03e42ec1a7b88b41dcab11a3(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d3ff4e50ec2a5fac7a7459f1190923905637a5f1e26e9bf525c8dfb8d922101(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c96f3e1a42327b354e2ac10136d4eddd54d7b95eca7c2aab9b389c282a35172(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85eaeab953070405855badeb73a73bf608533d10479650f5cf35728283960e6b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fd18d6a5a9864c5d51a6ddd1adc3c4017aa9956ee8366e592293e55a409fa95(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    day_of_week: jsii.Number,
    project_id: builtins.str,
    auto_defer: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    auto_defer_once_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    defer: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    hour_of_day: typing.Optional[jsii.Number] = None,
    id: typing.Optional[builtins.str] = None,
    protected_hours: typing.Optional[typing.Union[MaintenanceWindowProtectedHours, typing.Dict[builtins.str, typing.Any]]] = None,
    start_asap: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1f8262cfdde4c357a0863695c49c11f94a5971953d6ab7377c2854dcaec73b5(
    *,
    end_hour_of_day: jsii.Number,
    start_hour_of_day: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39c9074924814a50d26318a7437d57603465b14220d331b5dd9b0bbbdbba9a10(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0dcdc6011825200e28ea139141c56b02461a838702723a95f6920e470bfc5c72(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2db63cd1bc48e5243bc7ce9f5e2bbc770a2d1e95bf11d0f82e4d187b623618b3(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f506816396550e9013ad58b163b77d3c540f8d09825c445d24030298397b0c3b(
    value: typing.Optional[MaintenanceWindowProtectedHours],
) -> None:
    """Type checking stubs"""
    pass
