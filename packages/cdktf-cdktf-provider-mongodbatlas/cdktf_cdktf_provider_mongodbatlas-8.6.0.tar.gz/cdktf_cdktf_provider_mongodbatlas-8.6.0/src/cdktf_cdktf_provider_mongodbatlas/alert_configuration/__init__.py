r'''
# `mongodbatlas_alert_configuration`

Refer to the Terraform Registry for docs: [`mongodbatlas_alert_configuration`](https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration).
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


class AlertConfiguration(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.alertConfiguration.AlertConfiguration",
):
    '''Represents a {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration mongodbatlas_alert_configuration}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        event_type: builtins.str,
        project_id: builtins.str,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        matcher: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AlertConfigurationMatcher", typing.Dict[builtins.str, typing.Any]]]]] = None,
        metric_threshold_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AlertConfigurationMetricThresholdConfig", typing.Dict[builtins.str, typing.Any]]]]] = None,
        notification: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AlertConfigurationNotification", typing.Dict[builtins.str, typing.Any]]]]] = None,
        threshold_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AlertConfigurationThresholdConfig", typing.Dict[builtins.str, typing.Any]]]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration mongodbatlas_alert_configuration} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param event_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#event_type AlertConfiguration#event_type}.
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#project_id AlertConfiguration#project_id}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#enabled AlertConfiguration#enabled}.
        :param matcher: matcher block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#matcher AlertConfiguration#matcher}
        :param metric_threshold_config: metric_threshold_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#metric_threshold_config AlertConfiguration#metric_threshold_config}
        :param notification: notification block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#notification AlertConfiguration#notification}
        :param threshold_config: threshold_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#threshold_config AlertConfiguration#threshold_config}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73d49ff7d0aa74180a7bb7e5a1b541817d3f9b77acd4a111faf74975f8959f3f)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = AlertConfigurationConfig(
            event_type=event_type,
            project_id=project_id,
            enabled=enabled,
            matcher=matcher,
            metric_threshold_config=metric_threshold_config,
            notification=notification,
            threshold_config=threshold_config,
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
        '''Generates CDKTF code for importing a AlertConfiguration resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the AlertConfiguration to import.
        :param import_from_id: The id of the existing AlertConfiguration that should be imported. Refer to the {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the AlertConfiguration to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a15e1586a2943b613515acf42849700cfecaf71d11283a55d0ad081cf0ac058)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putMatcher")
    def put_matcher(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AlertConfigurationMatcher", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2c11ba988ea4e745b1fc94fa49e098a6615b0209cf6a2641a755ce5d84c98be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putMatcher", [value]))

    @jsii.member(jsii_name="putMetricThresholdConfig")
    def put_metric_threshold_config(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AlertConfigurationMetricThresholdConfig", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5d31ef5af4f83eed4ce790b38b076bdd2859b1491d11c86ca8e59f639bd9da6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putMetricThresholdConfig", [value]))

    @jsii.member(jsii_name="putNotification")
    def put_notification(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AlertConfigurationNotification", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85513c79b47bd641de724bd433ada17055b460d5d11744e68fb1d556556bf560)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putNotification", [value]))

    @jsii.member(jsii_name="putThresholdConfig")
    def put_threshold_config(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AlertConfigurationThresholdConfig", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8728bcfdee552dcd6027bed196b1facbb8a7a0a08cf29145226d3736a5d6788e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putThresholdConfig", [value]))

    @jsii.member(jsii_name="resetEnabled")
    def reset_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnabled", []))

    @jsii.member(jsii_name="resetMatcher")
    def reset_matcher(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMatcher", []))

    @jsii.member(jsii_name="resetMetricThresholdConfig")
    def reset_metric_threshold_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMetricThresholdConfig", []))

    @jsii.member(jsii_name="resetNotification")
    def reset_notification(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotification", []))

    @jsii.member(jsii_name="resetThresholdConfig")
    def reset_threshold_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThresholdConfig", []))

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
    @jsii.member(jsii_name="alertConfigurationId")
    def alert_configuration_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "alertConfigurationId"))

    @builtins.property
    @jsii.member(jsii_name="created")
    def created(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "created"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="matcher")
    def matcher(self) -> "AlertConfigurationMatcherList":
        return typing.cast("AlertConfigurationMatcherList", jsii.get(self, "matcher"))

    @builtins.property
    @jsii.member(jsii_name="metricThresholdConfig")
    def metric_threshold_config(self) -> "AlertConfigurationMetricThresholdConfigList":
        return typing.cast("AlertConfigurationMetricThresholdConfigList", jsii.get(self, "metricThresholdConfig"))

    @builtins.property
    @jsii.member(jsii_name="notification")
    def notification(self) -> "AlertConfigurationNotificationList":
        return typing.cast("AlertConfigurationNotificationList", jsii.get(self, "notification"))

    @builtins.property
    @jsii.member(jsii_name="thresholdConfig")
    def threshold_config(self) -> "AlertConfigurationThresholdConfigList":
        return typing.cast("AlertConfigurationThresholdConfigList", jsii.get(self, "thresholdConfig"))

    @builtins.property
    @jsii.member(jsii_name="updated")
    def updated(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updated"))

    @builtins.property
    @jsii.member(jsii_name="enabledInput")
    def enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enabledInput"))

    @builtins.property
    @jsii.member(jsii_name="eventTypeInput")
    def event_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "eventTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="matcherInput")
    def matcher_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AlertConfigurationMatcher"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AlertConfigurationMatcher"]]], jsii.get(self, "matcherInput"))

    @builtins.property
    @jsii.member(jsii_name="metricThresholdConfigInput")
    def metric_threshold_config_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AlertConfigurationMetricThresholdConfig"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AlertConfigurationMetricThresholdConfig"]]], jsii.get(self, "metricThresholdConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="notificationInput")
    def notification_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AlertConfigurationNotification"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AlertConfigurationNotification"]]], jsii.get(self, "notificationInput"))

    @builtins.property
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="thresholdConfigInput")
    def threshold_config_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AlertConfigurationThresholdConfig"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AlertConfigurationThresholdConfig"]]], jsii.get(self, "thresholdConfigInput"))

    @builtins.property
    @jsii.member(jsii_name="enabled")
    def enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enabled"))

    @enabled.setter
    def enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9373a38e079dc76d0cb695e8d78d52f7e9614cdcfe1ab60538d5ce02e6eebba2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="eventType")
    def event_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "eventType"))

    @event_type.setter
    def event_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bca2cab500287f43747605f92ba842345591fffa4a96eecc5a405c20ec033c49)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "eventType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71d5d4f31a31c6d94c93dc49d9c766663f6f45020f4f4168d57f86c8a87aa150)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.alertConfiguration.AlertConfigurationConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "event_type": "eventType",
        "project_id": "projectId",
        "enabled": "enabled",
        "matcher": "matcher",
        "metric_threshold_config": "metricThresholdConfig",
        "notification": "notification",
        "threshold_config": "thresholdConfig",
    },
)
class AlertConfigurationConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        event_type: builtins.str,
        project_id: builtins.str,
        enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        matcher: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AlertConfigurationMatcher", typing.Dict[builtins.str, typing.Any]]]]] = None,
        metric_threshold_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AlertConfigurationMetricThresholdConfig", typing.Dict[builtins.str, typing.Any]]]]] = None,
        notification: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AlertConfigurationNotification", typing.Dict[builtins.str, typing.Any]]]]] = None,
        threshold_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["AlertConfigurationThresholdConfig", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param event_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#event_type AlertConfiguration#event_type}.
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#project_id AlertConfiguration#project_id}.
        :param enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#enabled AlertConfiguration#enabled}.
        :param matcher: matcher block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#matcher AlertConfiguration#matcher}
        :param metric_threshold_config: metric_threshold_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#metric_threshold_config AlertConfiguration#metric_threshold_config}
        :param notification: notification block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#notification AlertConfiguration#notification}
        :param threshold_config: threshold_config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#threshold_config AlertConfiguration#threshold_config}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af921c32823ec3e2c7734a94c19ca5dd9435e80993a7e12e5a78419b10fa4fb6)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument event_type", value=event_type, expected_type=type_hints["event_type"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument enabled", value=enabled, expected_type=type_hints["enabled"])
            check_type(argname="argument matcher", value=matcher, expected_type=type_hints["matcher"])
            check_type(argname="argument metric_threshold_config", value=metric_threshold_config, expected_type=type_hints["metric_threshold_config"])
            check_type(argname="argument notification", value=notification, expected_type=type_hints["notification"])
            check_type(argname="argument threshold_config", value=threshold_config, expected_type=type_hints["threshold_config"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "event_type": event_type,
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
        if enabled is not None:
            self._values["enabled"] = enabled
        if matcher is not None:
            self._values["matcher"] = matcher
        if metric_threshold_config is not None:
            self._values["metric_threshold_config"] = metric_threshold_config
        if notification is not None:
            self._values["notification"] = notification
        if threshold_config is not None:
            self._values["threshold_config"] = threshold_config

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
    def event_type(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#event_type AlertConfiguration#event_type}.'''
        result = self._values.get("event_type")
        assert result is not None, "Required property 'event_type' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def project_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#project_id AlertConfiguration#project_id}.'''
        result = self._values.get("project_id")
        assert result is not None, "Required property 'project_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#enabled AlertConfiguration#enabled}.'''
        result = self._values.get("enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def matcher(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AlertConfigurationMatcher"]]]:
        '''matcher block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#matcher AlertConfiguration#matcher}
        '''
        result = self._values.get("matcher")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AlertConfigurationMatcher"]]], result)

    @builtins.property
    def metric_threshold_config(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AlertConfigurationMetricThresholdConfig"]]]:
        '''metric_threshold_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#metric_threshold_config AlertConfiguration#metric_threshold_config}
        '''
        result = self._values.get("metric_threshold_config")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AlertConfigurationMetricThresholdConfig"]]], result)

    @builtins.property
    def notification(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AlertConfigurationNotification"]]]:
        '''notification block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#notification AlertConfiguration#notification}
        '''
        result = self._values.get("notification")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AlertConfigurationNotification"]]], result)

    @builtins.property
    def threshold_config(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AlertConfigurationThresholdConfig"]]]:
        '''threshold_config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#threshold_config AlertConfiguration#threshold_config}
        '''
        result = self._values.get("threshold_config")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["AlertConfigurationThresholdConfig"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlertConfigurationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.alertConfiguration.AlertConfigurationMatcher",
    jsii_struct_bases=[],
    name_mapping={"field_name": "fieldName", "operator": "operator", "value": "value"},
)
class AlertConfigurationMatcher:
    def __init__(
        self,
        *,
        field_name: builtins.str,
        operator: builtins.str,
        value: builtins.str,
    ) -> None:
        '''
        :param field_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#field_name AlertConfiguration#field_name}.
        :param operator: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#operator AlertConfiguration#operator}.
        :param value: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#value AlertConfiguration#value}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82ea1e79532d907bb882644d8aa10cabea3c028bedd18ec5f5e22ed2047461f6)
            check_type(argname="argument field_name", value=field_name, expected_type=type_hints["field_name"])
            check_type(argname="argument operator", value=operator, expected_type=type_hints["operator"])
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "field_name": field_name,
            "operator": operator,
            "value": value,
        }

    @builtins.property
    def field_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#field_name AlertConfiguration#field_name}.'''
        result = self._values.get("field_name")
        assert result is not None, "Required property 'field_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def operator(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#operator AlertConfiguration#operator}.'''
        result = self._values.get("operator")
        assert result is not None, "Required property 'operator' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def value(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#value AlertConfiguration#value}.'''
        result = self._values.get("value")
        assert result is not None, "Required property 'value' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlertConfigurationMatcher(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AlertConfigurationMatcherList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.alertConfiguration.AlertConfigurationMatcherList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__21cc8d90c06da81a6fe15588bc00a25333d1e2559c44929dbac75be32bb01b00)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "AlertConfigurationMatcherOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed1cdc12f507fd07c79b7ff68a12a61f30d128b25fd7562b2049de3f5b627505)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("AlertConfigurationMatcherOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3fc4fe78bc913b46469eef524350aee841ad89d7ba545a406879dbef8760c447)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a5418844d32133c5ac65e11ebada53ff9ed803590261365ea17885cfd54cbf9b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__57aea812fe30ae923f240b6722255d83fee21a9fe367a99fd1106d7c26c2a381)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AlertConfigurationMatcher]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AlertConfigurationMatcher]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AlertConfigurationMatcher]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6908cc3c7e18565edec8d5b5497ff706de460df7887b8e112a28d5f2b75e1067)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class AlertConfigurationMatcherOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.alertConfiguration.AlertConfigurationMatcherOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c71baa81763cd49827d5494d889ed7ba0fcecc572051b998470ec0579e02fe27)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="fieldNameInput")
    def field_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fieldNameInput"))

    @builtins.property
    @jsii.member(jsii_name="operatorInput")
    def operator_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "operatorInput"))

    @builtins.property
    @jsii.member(jsii_name="valueInput")
    def value_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "valueInput"))

    @builtins.property
    @jsii.member(jsii_name="fieldName")
    def field_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fieldName"))

    @field_name.setter
    def field_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3549e1311c2a699c465cf0c42b00a3c3d46cd854635d7555d038b5ecf0100eeb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fieldName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operator"))

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__186b82d00adcb28ea9dee40a24a39bb6789d2395d692d2d8c561d2e85d728d93)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="value")
    def value(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "value"))

    @value.setter
    def value(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6489f5ffe7f06456b5b2247c299c934da403ecbcc31059cb878047948047a110)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "value", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertConfigurationMatcher]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertConfigurationMatcher]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertConfigurationMatcher]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d064b4afa799aa768486cc96f509d4309f6fc868f8394b6fdf7581eacaf6c473)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.alertConfiguration.AlertConfigurationMetricThresholdConfig",
    jsii_struct_bases=[],
    name_mapping={
        "metric_name": "metricName",
        "mode": "mode",
        "operator": "operator",
        "threshold": "threshold",
        "units": "units",
    },
)
class AlertConfigurationMetricThresholdConfig:
    def __init__(
        self,
        *,
        metric_name: builtins.str,
        mode: typing.Optional[builtins.str] = None,
        operator: typing.Optional[builtins.str] = None,
        threshold: typing.Optional[jsii.Number] = None,
        units: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param metric_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#metric_name AlertConfiguration#metric_name}.
        :param mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#mode AlertConfiguration#mode}.
        :param operator: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#operator AlertConfiguration#operator}.
        :param threshold: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#threshold AlertConfiguration#threshold}.
        :param units: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#units AlertConfiguration#units}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0377325dcb0c22f15884410444202a1106bf9d3b4221466ac64ed37c263e309)
            check_type(argname="argument metric_name", value=metric_name, expected_type=type_hints["metric_name"])
            check_type(argname="argument mode", value=mode, expected_type=type_hints["mode"])
            check_type(argname="argument operator", value=operator, expected_type=type_hints["operator"])
            check_type(argname="argument threshold", value=threshold, expected_type=type_hints["threshold"])
            check_type(argname="argument units", value=units, expected_type=type_hints["units"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "metric_name": metric_name,
        }
        if mode is not None:
            self._values["mode"] = mode
        if operator is not None:
            self._values["operator"] = operator
        if threshold is not None:
            self._values["threshold"] = threshold
        if units is not None:
            self._values["units"] = units

    @builtins.property
    def metric_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#metric_name AlertConfiguration#metric_name}.'''
        result = self._values.get("metric_name")
        assert result is not None, "Required property 'metric_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#mode AlertConfiguration#mode}.'''
        result = self._values.get("mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def operator(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#operator AlertConfiguration#operator}.'''
        result = self._values.get("operator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def threshold(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#threshold AlertConfiguration#threshold}.'''
        result = self._values.get("threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def units(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#units AlertConfiguration#units}.'''
        result = self._values.get("units")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlertConfigurationMetricThresholdConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AlertConfigurationMetricThresholdConfigList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.alertConfiguration.AlertConfigurationMetricThresholdConfigList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2cf2888f08cc7208dc6c74a0a532afb6f502b6829719f58f5c0025eb21a1cd38)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "AlertConfigurationMetricThresholdConfigOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e542794aaa1cf02bec34414dbcfa4c582f9258983dc5bd8169a83fc43f288d05)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("AlertConfigurationMetricThresholdConfigOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af9f939f03e9629e0e29b28e388d53137afcf363ea3bb856186d48e774135fed)
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
            type_hints = typing.get_type_hints(_typecheckingstub__dd5000860ba1cba05d6f6724f57bccffdbb767c244e22f71e950ce7fe7c6b49a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bd2fa7e9f5ca23ebddbe148f496ce3da74721cbf8b66a7f08b892719d1f0c92b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AlertConfigurationMetricThresholdConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AlertConfigurationMetricThresholdConfig]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AlertConfigurationMetricThresholdConfig]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04d125b3f28f9bd652e2ed60b7641be6da3388bd966b2192ed78787c668169bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class AlertConfigurationMetricThresholdConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.alertConfiguration.AlertConfigurationMetricThresholdConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3bfbaf95ce8532f556c7680125dc505516040546990c8db5bf7ceef8dbc76a52)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetMode")
    def reset_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMode", []))

    @jsii.member(jsii_name="resetOperator")
    def reset_operator(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperator", []))

    @jsii.member(jsii_name="resetThreshold")
    def reset_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreshold", []))

    @jsii.member(jsii_name="resetUnits")
    def reset_units(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUnits", []))

    @builtins.property
    @jsii.member(jsii_name="metricNameInput")
    def metric_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "metricNameInput"))

    @builtins.property
    @jsii.member(jsii_name="modeInput")
    def mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modeInput"))

    @builtins.property
    @jsii.member(jsii_name="operatorInput")
    def operator_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "operatorInput"))

    @builtins.property
    @jsii.member(jsii_name="thresholdInput")
    def threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "thresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="unitsInput")
    def units_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "unitsInput"))

    @builtins.property
    @jsii.member(jsii_name="metricName")
    def metric_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "metricName"))

    @metric_name.setter
    def metric_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34dbb066276ff623b5627655b0ee749ea74c4253d74f75092ed51b5501b6bf72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "metricName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mode")
    def mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mode"))

    @mode.setter
    def mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d98b6fbebd7459bcba3ff7910326f537d76205a23326d807286ab1801e35e36)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operator"))

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e032c9f60bbb4719f1fbd7b0505f3bd4791e26f62b82aa0f05b826edc6ea3d1b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threshold"))

    @threshold.setter
    def threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db7e590a7a6c184fcf0395d1aa833d39f905c4e08566062e382806cf9cee4172)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="units")
    def units(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "units"))

    @units.setter
    def units(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09b2aaeb3fcecce19810e366480bfcb8f7734dc9a6c9f0d0f78559a6075e63a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "units", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertConfigurationMetricThresholdConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertConfigurationMetricThresholdConfig]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertConfigurationMetricThresholdConfig]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__974e583ec465dc257dc6020d4da0d42912724985bb18b00bd160e5dc26a1360a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.alertConfiguration.AlertConfigurationNotification",
    jsii_struct_bases=[],
    name_mapping={
        "type_name": "typeName",
        "api_token": "apiToken",
        "channel_name": "channelName",
        "datadog_api_key": "datadogApiKey",
        "datadog_region": "datadogRegion",
        "delay_min": "delayMin",
        "email_address": "emailAddress",
        "email_enabled": "emailEnabled",
        "integration_id": "integrationId",
        "interval_min": "intervalMin",
        "microsoft_teams_webhook_url": "microsoftTeamsWebhookUrl",
        "mobile_number": "mobileNumber",
        "notifier_id": "notifierId",
        "ops_genie_api_key": "opsGenieApiKey",
        "ops_genie_region": "opsGenieRegion",
        "roles": "roles",
        "service_key": "serviceKey",
        "sms_enabled": "smsEnabled",
        "team_id": "teamId",
        "username": "username",
        "victor_ops_api_key": "victorOpsApiKey",
        "victor_ops_routing_key": "victorOpsRoutingKey",
        "webhook_secret": "webhookSecret",
        "webhook_url": "webhookUrl",
    },
)
class AlertConfigurationNotification:
    def __init__(
        self,
        *,
        type_name: builtins.str,
        api_token: typing.Optional[builtins.str] = None,
        channel_name: typing.Optional[builtins.str] = None,
        datadog_api_key: typing.Optional[builtins.str] = None,
        datadog_region: typing.Optional[builtins.str] = None,
        delay_min: typing.Optional[jsii.Number] = None,
        email_address: typing.Optional[builtins.str] = None,
        email_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        integration_id: typing.Optional[builtins.str] = None,
        interval_min: typing.Optional[jsii.Number] = None,
        microsoft_teams_webhook_url: typing.Optional[builtins.str] = None,
        mobile_number: typing.Optional[builtins.str] = None,
        notifier_id: typing.Optional[builtins.str] = None,
        ops_genie_api_key: typing.Optional[builtins.str] = None,
        ops_genie_region: typing.Optional[builtins.str] = None,
        roles: typing.Optional[typing.Sequence[builtins.str]] = None,
        service_key: typing.Optional[builtins.str] = None,
        sms_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        team_id: typing.Optional[builtins.str] = None,
        username: typing.Optional[builtins.str] = None,
        victor_ops_api_key: typing.Optional[builtins.str] = None,
        victor_ops_routing_key: typing.Optional[builtins.str] = None,
        webhook_secret: typing.Optional[builtins.str] = None,
        webhook_url: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param type_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#type_name AlertConfiguration#type_name}.
        :param api_token: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#api_token AlertConfiguration#api_token}.
        :param channel_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#channel_name AlertConfiguration#channel_name}.
        :param datadog_api_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#datadog_api_key AlertConfiguration#datadog_api_key}.
        :param datadog_region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#datadog_region AlertConfiguration#datadog_region}.
        :param delay_min: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#delay_min AlertConfiguration#delay_min}.
        :param email_address: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#email_address AlertConfiguration#email_address}.
        :param email_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#email_enabled AlertConfiguration#email_enabled}.
        :param integration_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#integration_id AlertConfiguration#integration_id}.
        :param interval_min: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#interval_min AlertConfiguration#interval_min}.
        :param microsoft_teams_webhook_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#microsoft_teams_webhook_url AlertConfiguration#microsoft_teams_webhook_url}.
        :param mobile_number: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#mobile_number AlertConfiguration#mobile_number}.
        :param notifier_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#notifier_id AlertConfiguration#notifier_id}.
        :param ops_genie_api_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#ops_genie_api_key AlertConfiguration#ops_genie_api_key}.
        :param ops_genie_region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#ops_genie_region AlertConfiguration#ops_genie_region}.
        :param roles: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#roles AlertConfiguration#roles}.
        :param service_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#service_key AlertConfiguration#service_key}.
        :param sms_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#sms_enabled AlertConfiguration#sms_enabled}.
        :param team_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#team_id AlertConfiguration#team_id}.
        :param username: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#username AlertConfiguration#username}.
        :param victor_ops_api_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#victor_ops_api_key AlertConfiguration#victor_ops_api_key}.
        :param victor_ops_routing_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#victor_ops_routing_key AlertConfiguration#victor_ops_routing_key}.
        :param webhook_secret: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#webhook_secret AlertConfiguration#webhook_secret}.
        :param webhook_url: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#webhook_url AlertConfiguration#webhook_url}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb253cbbe36d0ad4d1a9b1602b66071239cef7366b9373360aaa1eb819fa2137)
            check_type(argname="argument type_name", value=type_name, expected_type=type_hints["type_name"])
            check_type(argname="argument api_token", value=api_token, expected_type=type_hints["api_token"])
            check_type(argname="argument channel_name", value=channel_name, expected_type=type_hints["channel_name"])
            check_type(argname="argument datadog_api_key", value=datadog_api_key, expected_type=type_hints["datadog_api_key"])
            check_type(argname="argument datadog_region", value=datadog_region, expected_type=type_hints["datadog_region"])
            check_type(argname="argument delay_min", value=delay_min, expected_type=type_hints["delay_min"])
            check_type(argname="argument email_address", value=email_address, expected_type=type_hints["email_address"])
            check_type(argname="argument email_enabled", value=email_enabled, expected_type=type_hints["email_enabled"])
            check_type(argname="argument integration_id", value=integration_id, expected_type=type_hints["integration_id"])
            check_type(argname="argument interval_min", value=interval_min, expected_type=type_hints["interval_min"])
            check_type(argname="argument microsoft_teams_webhook_url", value=microsoft_teams_webhook_url, expected_type=type_hints["microsoft_teams_webhook_url"])
            check_type(argname="argument mobile_number", value=mobile_number, expected_type=type_hints["mobile_number"])
            check_type(argname="argument notifier_id", value=notifier_id, expected_type=type_hints["notifier_id"])
            check_type(argname="argument ops_genie_api_key", value=ops_genie_api_key, expected_type=type_hints["ops_genie_api_key"])
            check_type(argname="argument ops_genie_region", value=ops_genie_region, expected_type=type_hints["ops_genie_region"])
            check_type(argname="argument roles", value=roles, expected_type=type_hints["roles"])
            check_type(argname="argument service_key", value=service_key, expected_type=type_hints["service_key"])
            check_type(argname="argument sms_enabled", value=sms_enabled, expected_type=type_hints["sms_enabled"])
            check_type(argname="argument team_id", value=team_id, expected_type=type_hints["team_id"])
            check_type(argname="argument username", value=username, expected_type=type_hints["username"])
            check_type(argname="argument victor_ops_api_key", value=victor_ops_api_key, expected_type=type_hints["victor_ops_api_key"])
            check_type(argname="argument victor_ops_routing_key", value=victor_ops_routing_key, expected_type=type_hints["victor_ops_routing_key"])
            check_type(argname="argument webhook_secret", value=webhook_secret, expected_type=type_hints["webhook_secret"])
            check_type(argname="argument webhook_url", value=webhook_url, expected_type=type_hints["webhook_url"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "type_name": type_name,
        }
        if api_token is not None:
            self._values["api_token"] = api_token
        if channel_name is not None:
            self._values["channel_name"] = channel_name
        if datadog_api_key is not None:
            self._values["datadog_api_key"] = datadog_api_key
        if datadog_region is not None:
            self._values["datadog_region"] = datadog_region
        if delay_min is not None:
            self._values["delay_min"] = delay_min
        if email_address is not None:
            self._values["email_address"] = email_address
        if email_enabled is not None:
            self._values["email_enabled"] = email_enabled
        if integration_id is not None:
            self._values["integration_id"] = integration_id
        if interval_min is not None:
            self._values["interval_min"] = interval_min
        if microsoft_teams_webhook_url is not None:
            self._values["microsoft_teams_webhook_url"] = microsoft_teams_webhook_url
        if mobile_number is not None:
            self._values["mobile_number"] = mobile_number
        if notifier_id is not None:
            self._values["notifier_id"] = notifier_id
        if ops_genie_api_key is not None:
            self._values["ops_genie_api_key"] = ops_genie_api_key
        if ops_genie_region is not None:
            self._values["ops_genie_region"] = ops_genie_region
        if roles is not None:
            self._values["roles"] = roles
        if service_key is not None:
            self._values["service_key"] = service_key
        if sms_enabled is not None:
            self._values["sms_enabled"] = sms_enabled
        if team_id is not None:
            self._values["team_id"] = team_id
        if username is not None:
            self._values["username"] = username
        if victor_ops_api_key is not None:
            self._values["victor_ops_api_key"] = victor_ops_api_key
        if victor_ops_routing_key is not None:
            self._values["victor_ops_routing_key"] = victor_ops_routing_key
        if webhook_secret is not None:
            self._values["webhook_secret"] = webhook_secret
        if webhook_url is not None:
            self._values["webhook_url"] = webhook_url

    @builtins.property
    def type_name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#type_name AlertConfiguration#type_name}.'''
        result = self._values.get("type_name")
        assert result is not None, "Required property 'type_name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def api_token(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#api_token AlertConfiguration#api_token}.'''
        result = self._values.get("api_token")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def channel_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#channel_name AlertConfiguration#channel_name}.'''
        result = self._values.get("channel_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def datadog_api_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#datadog_api_key AlertConfiguration#datadog_api_key}.'''
        result = self._values.get("datadog_api_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def datadog_region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#datadog_region AlertConfiguration#datadog_region}.'''
        result = self._values.get("datadog_region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delay_min(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#delay_min AlertConfiguration#delay_min}.'''
        result = self._values.get("delay_min")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def email_address(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#email_address AlertConfiguration#email_address}.'''
        result = self._values.get("email_address")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def email_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#email_enabled AlertConfiguration#email_enabled}.'''
        result = self._values.get("email_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def integration_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#integration_id AlertConfiguration#integration_id}.'''
        result = self._values.get("integration_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def interval_min(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#interval_min AlertConfiguration#interval_min}.'''
        result = self._values.get("interval_min")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def microsoft_teams_webhook_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#microsoft_teams_webhook_url AlertConfiguration#microsoft_teams_webhook_url}.'''
        result = self._values.get("microsoft_teams_webhook_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def mobile_number(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#mobile_number AlertConfiguration#mobile_number}.'''
        result = self._values.get("mobile_number")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def notifier_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#notifier_id AlertConfiguration#notifier_id}.'''
        result = self._values.get("notifier_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ops_genie_api_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#ops_genie_api_key AlertConfiguration#ops_genie_api_key}.'''
        result = self._values.get("ops_genie_api_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ops_genie_region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#ops_genie_region AlertConfiguration#ops_genie_region}.'''
        result = self._values.get("ops_genie_region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def roles(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#roles AlertConfiguration#roles}.'''
        result = self._values.get("roles")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def service_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#service_key AlertConfiguration#service_key}.'''
        result = self._values.get("service_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sms_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#sms_enabled AlertConfiguration#sms_enabled}.'''
        result = self._values.get("sms_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def team_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#team_id AlertConfiguration#team_id}.'''
        result = self._values.get("team_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def username(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#username AlertConfiguration#username}.'''
        result = self._values.get("username")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def victor_ops_api_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#victor_ops_api_key AlertConfiguration#victor_ops_api_key}.'''
        result = self._values.get("victor_ops_api_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def victor_ops_routing_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#victor_ops_routing_key AlertConfiguration#victor_ops_routing_key}.'''
        result = self._values.get("victor_ops_routing_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def webhook_secret(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#webhook_secret AlertConfiguration#webhook_secret}.'''
        result = self._values.get("webhook_secret")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def webhook_url(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#webhook_url AlertConfiguration#webhook_url}.'''
        result = self._values.get("webhook_url")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlertConfigurationNotification(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AlertConfigurationNotificationList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.alertConfiguration.AlertConfigurationNotificationList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__afe43a3c14db4573256320b8b210f588a3d67318c059656b321ad2960838558e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "AlertConfigurationNotificationOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9548df77c487d8269062dcc75f433ea43514ea875820188ffdf48773742c101c)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("AlertConfigurationNotificationOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__723ee56fbe8a1adac884ded23a8cdedd93ff0fcf374e2d4beab761882679ae3e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3fb60250d14b6b010974ea3ceb4bb8a003590283ef5cd0e6b23d76e40021414c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8762793b3d8f8d9e4b31c1f1616a907b18f7f4cb3a8e9d1c17e4381042001413)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AlertConfigurationNotification]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AlertConfigurationNotification]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AlertConfigurationNotification]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed8585171ac91b9b0a33b7acdccbe0b2948681d9376e0e5358f7c71ccc7e4622)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class AlertConfigurationNotificationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.alertConfiguration.AlertConfigurationNotificationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__24a84feef47cec44f62a5c842a65b0484bde55a9cfb4f084144c6dc2203ac5fa)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetApiToken")
    def reset_api_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApiToken", []))

    @jsii.member(jsii_name="resetChannelName")
    def reset_channel_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetChannelName", []))

    @jsii.member(jsii_name="resetDatadogApiKey")
    def reset_datadog_api_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatadogApiKey", []))

    @jsii.member(jsii_name="resetDatadogRegion")
    def reset_datadog_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatadogRegion", []))

    @jsii.member(jsii_name="resetDelayMin")
    def reset_delay_min(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelayMin", []))

    @jsii.member(jsii_name="resetEmailAddress")
    def reset_email_address(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailAddress", []))

    @jsii.member(jsii_name="resetEmailEnabled")
    def reset_email_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmailEnabled", []))

    @jsii.member(jsii_name="resetIntegrationId")
    def reset_integration_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIntegrationId", []))

    @jsii.member(jsii_name="resetIntervalMin")
    def reset_interval_min(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIntervalMin", []))

    @jsii.member(jsii_name="resetMicrosoftTeamsWebhookUrl")
    def reset_microsoft_teams_webhook_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMicrosoftTeamsWebhookUrl", []))

    @jsii.member(jsii_name="resetMobileNumber")
    def reset_mobile_number(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMobileNumber", []))

    @jsii.member(jsii_name="resetNotifierId")
    def reset_notifier_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotifierId", []))

    @jsii.member(jsii_name="resetOpsGenieApiKey")
    def reset_ops_genie_api_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpsGenieApiKey", []))

    @jsii.member(jsii_name="resetOpsGenieRegion")
    def reset_ops_genie_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpsGenieRegion", []))

    @jsii.member(jsii_name="resetRoles")
    def reset_roles(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRoles", []))

    @jsii.member(jsii_name="resetServiceKey")
    def reset_service_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServiceKey", []))

    @jsii.member(jsii_name="resetSmsEnabled")
    def reset_sms_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSmsEnabled", []))

    @jsii.member(jsii_name="resetTeamId")
    def reset_team_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTeamId", []))

    @jsii.member(jsii_name="resetUsername")
    def reset_username(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsername", []))

    @jsii.member(jsii_name="resetVictorOpsApiKey")
    def reset_victor_ops_api_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVictorOpsApiKey", []))

    @jsii.member(jsii_name="resetVictorOpsRoutingKey")
    def reset_victor_ops_routing_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVictorOpsRoutingKey", []))

    @jsii.member(jsii_name="resetWebhookSecret")
    def reset_webhook_secret(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWebhookSecret", []))

    @jsii.member(jsii_name="resetWebhookUrl")
    def reset_webhook_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWebhookUrl", []))

    @builtins.property
    @jsii.member(jsii_name="teamName")
    def team_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "teamName"))

    @builtins.property
    @jsii.member(jsii_name="apiTokenInput")
    def api_token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiTokenInput"))

    @builtins.property
    @jsii.member(jsii_name="channelNameInput")
    def channel_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "channelNameInput"))

    @builtins.property
    @jsii.member(jsii_name="datadogApiKeyInput")
    def datadog_api_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "datadogApiKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="datadogRegionInput")
    def datadog_region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "datadogRegionInput"))

    @builtins.property
    @jsii.member(jsii_name="delayMinInput")
    def delay_min_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "delayMinInput"))

    @builtins.property
    @jsii.member(jsii_name="emailAddressInput")
    def email_address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailAddressInput"))

    @builtins.property
    @jsii.member(jsii_name="emailEnabledInput")
    def email_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "emailEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="integrationIdInput")
    def integration_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "integrationIdInput"))

    @builtins.property
    @jsii.member(jsii_name="intervalMinInput")
    def interval_min_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "intervalMinInput"))

    @builtins.property
    @jsii.member(jsii_name="microsoftTeamsWebhookUrlInput")
    def microsoft_teams_webhook_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "microsoftTeamsWebhookUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="mobileNumberInput")
    def mobile_number_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "mobileNumberInput"))

    @builtins.property
    @jsii.member(jsii_name="notifierIdInput")
    def notifier_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "notifierIdInput"))

    @builtins.property
    @jsii.member(jsii_name="opsGenieApiKeyInput")
    def ops_genie_api_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "opsGenieApiKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="opsGenieRegionInput")
    def ops_genie_region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "opsGenieRegionInput"))

    @builtins.property
    @jsii.member(jsii_name="rolesInput")
    def roles_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "rolesInput"))

    @builtins.property
    @jsii.member(jsii_name="serviceKeyInput")
    def service_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serviceKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="smsEnabledInput")
    def sms_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "smsEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="teamIdInput")
    def team_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "teamIdInput"))

    @builtins.property
    @jsii.member(jsii_name="typeNameInput")
    def type_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeNameInput"))

    @builtins.property
    @jsii.member(jsii_name="usernameInput")
    def username_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "usernameInput"))

    @builtins.property
    @jsii.member(jsii_name="victorOpsApiKeyInput")
    def victor_ops_api_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "victorOpsApiKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="victorOpsRoutingKeyInput")
    def victor_ops_routing_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "victorOpsRoutingKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="webhookSecretInput")
    def webhook_secret_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "webhookSecretInput"))

    @builtins.property
    @jsii.member(jsii_name="webhookUrlInput")
    def webhook_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "webhookUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="apiToken")
    def api_token(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "apiToken"))

    @api_token.setter
    def api_token(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb6116ccd0f80e551839a7b8abef51fec702a8f0e83c0cf5e4dd63029f9476a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiToken", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="channelName")
    def channel_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "channelName"))

    @channel_name.setter
    def channel_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20bc95a86229007abcbec4d971d910f7a618cb0334f5ea22593352bae7137c23)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "channelName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="datadogApiKey")
    def datadog_api_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "datadogApiKey"))

    @datadog_api_key.setter
    def datadog_api_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a605a6fe98a0f481ff96e2a65ccd9f955c2f0a9eb0b81aff06eb2fd625295d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "datadogApiKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="datadogRegion")
    def datadog_region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "datadogRegion"))

    @datadog_region.setter
    def datadog_region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ce326c1d73fb8eacf45cea7104026d735e8669c6ffd43789747783cf5bbd7b21)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "datadogRegion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="delayMin")
    def delay_min(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "delayMin"))

    @delay_min.setter
    def delay_min(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a9c290e748ef60db00952a49668668eb56654fc07f7f2dac98f78e075afa93f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delayMin", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="emailAddress")
    def email_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailAddress"))

    @email_address.setter
    def email_address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1749e012c96601d8f2aa2c4c9df635dcb3983e73893d2b9acc13de2c4217edc9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emailAddress", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="emailEnabled")
    def email_enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "emailEnabled"))

    @email_enabled.setter
    def email_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b73c686e909307079a56d3f38759c8ac9a72cb5a19983a5f0e77ca5cf7448873)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emailEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="integrationId")
    def integration_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "integrationId"))

    @integration_id.setter
    def integration_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__191927f856c7b708df557647229b3dd4653ff422059896fb8bcbf502b664fa97)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "integrationId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="intervalMin")
    def interval_min(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "intervalMin"))

    @interval_min.setter
    def interval_min(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__faa75cf94c472850f7bf25ecac0b397140c6088fc0f2b52fb35b8073e314ffd5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "intervalMin", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="microsoftTeamsWebhookUrl")
    def microsoft_teams_webhook_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "microsoftTeamsWebhookUrl"))

    @microsoft_teams_webhook_url.setter
    def microsoft_teams_webhook_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9bf06deddd7967f82dcd24a714e143de2cc1cac57b840d438c2e8b2f9bf925bb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "microsoftTeamsWebhookUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="mobileNumber")
    def mobile_number(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "mobileNumber"))

    @mobile_number.setter
    def mobile_number(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74778711db71f26984d0d40ab21f28ecb3596a30d8c08989111ebbdf4c3b8ce1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mobileNumber", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="notifierId")
    def notifier_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notifierId"))

    @notifier_id.setter
    def notifier_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a9e21839be17eaff143f4c1ff327a408079c8eff95ca074a65e91fe1c46628f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notifierId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="opsGenieApiKey")
    def ops_genie_api_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "opsGenieApiKey"))

    @ops_genie_api_key.setter
    def ops_genie_api_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0f667827d90273b6b32d6c12817ebe34610c256f79f49e933d3fc7977b31fbe8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "opsGenieApiKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="opsGenieRegion")
    def ops_genie_region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "opsGenieRegion"))

    @ops_genie_region.setter
    def ops_genie_region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f85b32a52437f3815f4e191e6a105621e6300aa17fab83f0415216c0f0262af3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "opsGenieRegion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="roles")
    def roles(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "roles"))

    @roles.setter
    def roles(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b608e8450af2bc7d677b2e65164ab7cf69d08b1ff27a602a9c221bf5aa641e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "roles", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serviceKey")
    def service_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "serviceKey"))

    @service_key.setter
    def service_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f01ea95cdd0cac57d954163285326bc4d168dde023ef7a02760f8b8263ad9a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serviceKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="smsEnabled")
    def sms_enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "smsEnabled"))

    @sms_enabled.setter
    def sms_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c5831af0e4341ff376abca560fb3e6ca806305a17f6f4ed7cca6158b97303e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "smsEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="teamId")
    def team_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "teamId"))

    @team_id.setter
    def team_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44e34e1062a2822bece85bd4d908d16937dc5491cea3aaf0b800082c2fdd4a40)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "teamId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="typeName")
    def type_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "typeName"))

    @type_name.setter
    def type_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f2c2c40a19139a6dca85463b1a9dae23385f3ca962e29f86f69204e207f98c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "typeName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="username")
    def username(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "username"))

    @username.setter
    def username(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0653542588551ccd4ea2ba2ac2ccb1ecc9beb6195b8d4b8119f58ed1a5b696e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "username", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="victorOpsApiKey")
    def victor_ops_api_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "victorOpsApiKey"))

    @victor_ops_api_key.setter
    def victor_ops_api_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac290f4539432efc51123c7bb854779c5a47192ed70af38b3e94f69f992828c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "victorOpsApiKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="victorOpsRoutingKey")
    def victor_ops_routing_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "victorOpsRoutingKey"))

    @victor_ops_routing_key.setter
    def victor_ops_routing_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de9a6d3fb92fe706ea082296213b0c98c8251bd89be0bbd8a83eeb524d593a78)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "victorOpsRoutingKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="webhookSecret")
    def webhook_secret(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "webhookSecret"))

    @webhook_secret.setter
    def webhook_secret(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__312c8aab5972a33849a6bad1cd977c4794536d54415518251f576883441e8491)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "webhookSecret", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="webhookUrl")
    def webhook_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "webhookUrl"))

    @webhook_url.setter
    def webhook_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18810d0476ffb70016763101c1e51fcd8e58562afee58600303551176fd153a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "webhookUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertConfigurationNotification]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertConfigurationNotification]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertConfigurationNotification]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9afc3ca0ddac6e4f07ff1e48ed1b989f934175e91f53c353f84b1d65d49c45ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-mongodbatlas.alertConfiguration.AlertConfigurationThresholdConfig",
    jsii_struct_bases=[],
    name_mapping={"operator": "operator", "threshold": "threshold", "units": "units"},
)
class AlertConfigurationThresholdConfig:
    def __init__(
        self,
        *,
        operator: typing.Optional[builtins.str] = None,
        threshold: typing.Optional[jsii.Number] = None,
        units: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param operator: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#operator AlertConfiguration#operator}.
        :param threshold: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#threshold AlertConfiguration#threshold}.
        :param units: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#units AlertConfiguration#units}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3aa1d9b324fd47d2928169f4d8b063014b29a8fa47e6691dc93d33e5add02cfe)
            check_type(argname="argument operator", value=operator, expected_type=type_hints["operator"])
            check_type(argname="argument threshold", value=threshold, expected_type=type_hints["threshold"])
            check_type(argname="argument units", value=units, expected_type=type_hints["units"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if operator is not None:
            self._values["operator"] = operator
        if threshold is not None:
            self._values["threshold"] = threshold
        if units is not None:
            self._values["units"] = units

    @builtins.property
    def operator(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#operator AlertConfiguration#operator}.'''
        result = self._values.get("operator")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def threshold(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#threshold AlertConfiguration#threshold}.'''
        result = self._values.get("threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def units(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs/resources/alert_configuration#units AlertConfiguration#units}.'''
        result = self._values.get("units")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlertConfigurationThresholdConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AlertConfigurationThresholdConfigList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.alertConfiguration.AlertConfigurationThresholdConfigList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__88686b3bab80592674cfe62e9d852a8c6cdfeec3dfc97a9bdfb44ba372c3f1cd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "AlertConfigurationThresholdConfigOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a37710a49b0d6d6c5dc344f3d0a21587821ec8c2ddb5c71ea226bdf94580fb2f)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("AlertConfigurationThresholdConfigOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1bd1edb414e8a9f190f428355b7eada4a00b0c61cf0659378957af5b0ec65c53)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a8e3e1a3831e053cb364dae92a3ee20f5fce986ff62c6e6d6cf6a51a0f8b55b1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__43a18123fc2f283314871086dcd988d5881d0d9cec6bb5c9393459e5b12adfb7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AlertConfigurationThresholdConfig]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AlertConfigurationThresholdConfig]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AlertConfigurationThresholdConfig]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cff9f17551c421704620c8c81de705e3510003bf0de79f62a40ab39ae7b7945b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class AlertConfigurationThresholdConfigOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-mongodbatlas.alertConfiguration.AlertConfigurationThresholdConfigOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5e8000ccc11b2ae3dfd67a53bbc2d9b8471b0812ae38b3aed9b03aa36c806c8b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetOperator")
    def reset_operator(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOperator", []))

    @jsii.member(jsii_name="resetThreshold")
    def reset_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreshold", []))

    @jsii.member(jsii_name="resetUnits")
    def reset_units(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUnits", []))

    @builtins.property
    @jsii.member(jsii_name="operatorInput")
    def operator_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "operatorInput"))

    @builtins.property
    @jsii.member(jsii_name="thresholdInput")
    def threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "thresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="unitsInput")
    def units_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "unitsInput"))

    @builtins.property
    @jsii.member(jsii_name="operator")
    def operator(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "operator"))

    @operator.setter
    def operator(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1cdf316a39c3daa4b737b113b61d845cd72dc533e0280818e79d63d6b6d71bb3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "operator", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threshold")
    def threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threshold"))

    @threshold.setter
    def threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a736f376cccec6eb9a1a4354cd36237cefa4ed77c1a693912c276fcaf819e2c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="units")
    def units(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "units"))

    @units.setter
    def units(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94a5e971eaa660f8760d15d0b5c084907c7dbc6178b9fc50d84919924333663a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "units", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertConfigurationThresholdConfig]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertConfigurationThresholdConfig]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertConfigurationThresholdConfig]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41d5ea65f059ca988ee4a3571e7ccad8fa071adfd89f6e8a7146feb771f689a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "AlertConfiguration",
    "AlertConfigurationConfig",
    "AlertConfigurationMatcher",
    "AlertConfigurationMatcherList",
    "AlertConfigurationMatcherOutputReference",
    "AlertConfigurationMetricThresholdConfig",
    "AlertConfigurationMetricThresholdConfigList",
    "AlertConfigurationMetricThresholdConfigOutputReference",
    "AlertConfigurationNotification",
    "AlertConfigurationNotificationList",
    "AlertConfigurationNotificationOutputReference",
    "AlertConfigurationThresholdConfig",
    "AlertConfigurationThresholdConfigList",
    "AlertConfigurationThresholdConfigOutputReference",
]

publication.publish()

def _typecheckingstub__73d49ff7d0aa74180a7bb7e5a1b541817d3f9b77acd4a111faf74975f8959f3f(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    event_type: builtins.str,
    project_id: builtins.str,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    matcher: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AlertConfigurationMatcher, typing.Dict[builtins.str, typing.Any]]]]] = None,
    metric_threshold_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AlertConfigurationMetricThresholdConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
    notification: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AlertConfigurationNotification, typing.Dict[builtins.str, typing.Any]]]]] = None,
    threshold_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AlertConfigurationThresholdConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
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

def _typecheckingstub__5a15e1586a2943b613515acf42849700cfecaf71d11283a55d0ad081cf0ac058(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2c11ba988ea4e745b1fc94fa49e098a6615b0209cf6a2641a755ce5d84c98be(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AlertConfigurationMatcher, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5d31ef5af4f83eed4ce790b38b076bdd2859b1491d11c86ca8e59f639bd9da6(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AlertConfigurationMetricThresholdConfig, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85513c79b47bd641de724bd433ada17055b460d5d11744e68fb1d556556bf560(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AlertConfigurationNotification, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8728bcfdee552dcd6027bed196b1facbb8a7a0a08cf29145226d3736a5d6788e(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AlertConfigurationThresholdConfig, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9373a38e079dc76d0cb695e8d78d52f7e9614cdcfe1ab60538d5ce02e6eebba2(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bca2cab500287f43747605f92ba842345591fffa4a96eecc5a405c20ec033c49(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71d5d4f31a31c6d94c93dc49d9c766663f6f45020f4f4168d57f86c8a87aa150(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af921c32823ec3e2c7734a94c19ca5dd9435e80993a7e12e5a78419b10fa4fb6(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    event_type: builtins.str,
    project_id: builtins.str,
    enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    matcher: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AlertConfigurationMatcher, typing.Dict[builtins.str, typing.Any]]]]] = None,
    metric_threshold_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AlertConfigurationMetricThresholdConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
    notification: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AlertConfigurationNotification, typing.Dict[builtins.str, typing.Any]]]]] = None,
    threshold_config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[AlertConfigurationThresholdConfig, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82ea1e79532d907bb882644d8aa10cabea3c028bedd18ec5f5e22ed2047461f6(
    *,
    field_name: builtins.str,
    operator: builtins.str,
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21cc8d90c06da81a6fe15588bc00a25333d1e2559c44929dbac75be32bb01b00(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed1cdc12f507fd07c79b7ff68a12a61f30d128b25fd7562b2049de3f5b627505(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fc4fe78bc913b46469eef524350aee841ad89d7ba545a406879dbef8760c447(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5418844d32133c5ac65e11ebada53ff9ed803590261365ea17885cfd54cbf9b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57aea812fe30ae923f240b6722255d83fee21a9fe367a99fd1106d7c26c2a381(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6908cc3c7e18565edec8d5b5497ff706de460df7887b8e112a28d5f2b75e1067(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AlertConfigurationMatcher]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c71baa81763cd49827d5494d889ed7ba0fcecc572051b998470ec0579e02fe27(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3549e1311c2a699c465cf0c42b00a3c3d46cd854635d7555d038b5ecf0100eeb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__186b82d00adcb28ea9dee40a24a39bb6789d2395d692d2d8c561d2e85d728d93(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6489f5ffe7f06456b5b2247c299c934da403ecbcc31059cb878047948047a110(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d064b4afa799aa768486cc96f509d4309f6fc868f8394b6fdf7581eacaf6c473(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertConfigurationMatcher]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0377325dcb0c22f15884410444202a1106bf9d3b4221466ac64ed37c263e309(
    *,
    metric_name: builtins.str,
    mode: typing.Optional[builtins.str] = None,
    operator: typing.Optional[builtins.str] = None,
    threshold: typing.Optional[jsii.Number] = None,
    units: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2cf2888f08cc7208dc6c74a0a532afb6f502b6829719f58f5c0025eb21a1cd38(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e542794aaa1cf02bec34414dbcfa4c582f9258983dc5bd8169a83fc43f288d05(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af9f939f03e9629e0e29b28e388d53137afcf363ea3bb856186d48e774135fed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd5000860ba1cba05d6f6724f57bccffdbb767c244e22f71e950ce7fe7c6b49a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd2fa7e9f5ca23ebddbe148f496ce3da74721cbf8b66a7f08b892719d1f0c92b(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04d125b3f28f9bd652e2ed60b7641be6da3388bd966b2192ed78787c668169bb(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AlertConfigurationMetricThresholdConfig]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3bfbaf95ce8532f556c7680125dc505516040546990c8db5bf7ceef8dbc76a52(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34dbb066276ff623b5627655b0ee749ea74c4253d74f75092ed51b5501b6bf72(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d98b6fbebd7459bcba3ff7910326f537d76205a23326d807286ab1801e35e36(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e032c9f60bbb4719f1fbd7b0505f3bd4791e26f62b82aa0f05b826edc6ea3d1b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db7e590a7a6c184fcf0395d1aa833d39f905c4e08566062e382806cf9cee4172(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09b2aaeb3fcecce19810e366480bfcb8f7734dc9a6c9f0d0f78559a6075e63a1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__974e583ec465dc257dc6020d4da0d42912724985bb18b00bd160e5dc26a1360a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertConfigurationMetricThresholdConfig]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb253cbbe36d0ad4d1a9b1602b66071239cef7366b9373360aaa1eb819fa2137(
    *,
    type_name: builtins.str,
    api_token: typing.Optional[builtins.str] = None,
    channel_name: typing.Optional[builtins.str] = None,
    datadog_api_key: typing.Optional[builtins.str] = None,
    datadog_region: typing.Optional[builtins.str] = None,
    delay_min: typing.Optional[jsii.Number] = None,
    email_address: typing.Optional[builtins.str] = None,
    email_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    integration_id: typing.Optional[builtins.str] = None,
    interval_min: typing.Optional[jsii.Number] = None,
    microsoft_teams_webhook_url: typing.Optional[builtins.str] = None,
    mobile_number: typing.Optional[builtins.str] = None,
    notifier_id: typing.Optional[builtins.str] = None,
    ops_genie_api_key: typing.Optional[builtins.str] = None,
    ops_genie_region: typing.Optional[builtins.str] = None,
    roles: typing.Optional[typing.Sequence[builtins.str]] = None,
    service_key: typing.Optional[builtins.str] = None,
    sms_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    team_id: typing.Optional[builtins.str] = None,
    username: typing.Optional[builtins.str] = None,
    victor_ops_api_key: typing.Optional[builtins.str] = None,
    victor_ops_routing_key: typing.Optional[builtins.str] = None,
    webhook_secret: typing.Optional[builtins.str] = None,
    webhook_url: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afe43a3c14db4573256320b8b210f588a3d67318c059656b321ad2960838558e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9548df77c487d8269062dcc75f433ea43514ea875820188ffdf48773742c101c(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__723ee56fbe8a1adac884ded23a8cdedd93ff0fcf374e2d4beab761882679ae3e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3fb60250d14b6b010974ea3ceb4bb8a003590283ef5cd0e6b23d76e40021414c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8762793b3d8f8d9e4b31c1f1616a907b18f7f4cb3a8e9d1c17e4381042001413(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed8585171ac91b9b0a33b7acdccbe0b2948681d9376e0e5358f7c71ccc7e4622(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AlertConfigurationNotification]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24a84feef47cec44f62a5c842a65b0484bde55a9cfb4f084144c6dc2203ac5fa(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb6116ccd0f80e551839a7b8abef51fec702a8f0e83c0cf5e4dd63029f9476a8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20bc95a86229007abcbec4d971d910f7a618cb0334f5ea22593352bae7137c23(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a605a6fe98a0f481ff96e2a65ccd9f955c2f0a9eb0b81aff06eb2fd625295d8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ce326c1d73fb8eacf45cea7104026d735e8669c6ffd43789747783cf5bbd7b21(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a9c290e748ef60db00952a49668668eb56654fc07f7f2dac98f78e075afa93f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1749e012c96601d8f2aa2c4c9df635dcb3983e73893d2b9acc13de2c4217edc9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b73c686e909307079a56d3f38759c8ac9a72cb5a19983a5f0e77ca5cf7448873(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__191927f856c7b708df557647229b3dd4653ff422059896fb8bcbf502b664fa97(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__faa75cf94c472850f7bf25ecac0b397140c6088fc0f2b52fb35b8073e314ffd5(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9bf06deddd7967f82dcd24a714e143de2cc1cac57b840d438c2e8b2f9bf925bb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74778711db71f26984d0d40ab21f28ecb3596a30d8c08989111ebbdf4c3b8ce1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a9e21839be17eaff143f4c1ff327a408079c8eff95ca074a65e91fe1c46628f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0f667827d90273b6b32d6c12817ebe34610c256f79f49e933d3fc7977b31fbe8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f85b32a52437f3815f4e191e6a105621e6300aa17fab83f0415216c0f0262af3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b608e8450af2bc7d677b2e65164ab7cf69d08b1ff27a602a9c221bf5aa641e0(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f01ea95cdd0cac57d954163285326bc4d168dde023ef7a02760f8b8263ad9a6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c5831af0e4341ff376abca560fb3e6ca806305a17f6f4ed7cca6158b97303e4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44e34e1062a2822bece85bd4d908d16937dc5491cea3aaf0b800082c2fdd4a40(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f2c2c40a19139a6dca85463b1a9dae23385f3ca962e29f86f69204e207f98c6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0653542588551ccd4ea2ba2ac2ccb1ecc9beb6195b8d4b8119f58ed1a5b696e4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac290f4539432efc51123c7bb854779c5a47192ed70af38b3e94f69f992828c4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de9a6d3fb92fe706ea082296213b0c98c8251bd89be0bbd8a83eeb524d593a78(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__312c8aab5972a33849a6bad1cd977c4794536d54415518251f576883441e8491(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18810d0476ffb70016763101c1e51fcd8e58562afee58600303551176fd153a8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9afc3ca0ddac6e4f07ff1e48ed1b989f934175e91f53c353f84b1d65d49c45ef(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertConfigurationNotification]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3aa1d9b324fd47d2928169f4d8b063014b29a8fa47e6691dc93d33e5add02cfe(
    *,
    operator: typing.Optional[builtins.str] = None,
    threshold: typing.Optional[jsii.Number] = None,
    units: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88686b3bab80592674cfe62e9d852a8c6cdfeec3dfc97a9bdfb44ba372c3f1cd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a37710a49b0d6d6c5dc344f3d0a21587821ec8c2ddb5c71ea226bdf94580fb2f(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1bd1edb414e8a9f190f428355b7eada4a00b0c61cf0659378957af5b0ec65c53(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8e3e1a3831e053cb364dae92a3ee20f5fce986ff62c6e6d6cf6a51a0f8b55b1(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43a18123fc2f283314871086dcd988d5881d0d9cec6bb5c9393459e5b12adfb7(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cff9f17551c421704620c8c81de705e3510003bf0de79f62a40ab39ae7b7945b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[AlertConfigurationThresholdConfig]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e8000ccc11b2ae3dfd67a53bbc2d9b8471b0812ae38b3aed9b03aa36c806c8b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1cdf316a39c3daa4b737b113b61d845cd72dc533e0280818e79d63d6b6d71bb3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a736f376cccec6eb9a1a4354cd36237cefa4ed77c1a693912c276fcaf819e2c6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94a5e971eaa660f8760d15d0b5c084907c7dbc6178b9fc50d84919924333663a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41d5ea65f059ca988ee4a3571e7ccad8fa071adfd89f6e8a7146feb771f689a6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, AlertConfigurationThresholdConfig]],
) -> None:
    """Type checking stubs"""
    pass
