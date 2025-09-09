r'''
# CDKTF prebuilt bindings for mongodb/mongodbatlas provider version 1.41.0

This repo builds and publishes the [Terraform mongodbatlas provider](https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0/docs) bindings for [CDK for Terraform](https://cdk.tf).

## Available Packages

### NPM

The npm package is available at [https://www.npmjs.com/package/@cdktf/provider-mongodbatlas](https://www.npmjs.com/package/@cdktf/provider-mongodbatlas).

`npm install @cdktf/provider-mongodbatlas`

### PyPI

The PyPI package is available at [https://pypi.org/project/cdktf-cdktf-provider-mongodbatlas](https://pypi.org/project/cdktf-cdktf-provider-mongodbatlas).

`pipenv install cdktf-cdktf-provider-mongodbatlas`

### Nuget

The Nuget package is available at [https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Mongodbatlas](https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Mongodbatlas).

`dotnet add package HashiCorp.Cdktf.Providers.Mongodbatlas`

### Maven

The Maven package is available at [https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-mongodbatlas](https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-mongodbatlas).

```
<dependency>
    <groupId>com.hashicorp</groupId>
    <artifactId>cdktf-provider-mongodbatlas</artifactId>
    <version>[REPLACE WITH DESIRED VERSION]</version>
</dependency>
```

### Go

The go package is generated into the [`github.com/cdktf/cdktf-provider-mongodbatlas-go`](https://github.com/cdktf/cdktf-provider-mongodbatlas-go) package.

`go get github.com/cdktf/cdktf-provider-mongodbatlas-go/mongodbatlas/<version>`

Where `<version>` is the version of the prebuilt provider you would like to use e.g. `v11`. The full module name can be found
within the [go.mod](https://github.com/cdktf/cdktf-provider-mongodbatlas-go/blob/main/mongodbatlas/go.mod#L1) file.

## Docs

Find auto-generated docs for this provider here:

* [Typescript](./docs/API.typescript.md)
* [Python](./docs/API.python.md)
* [Java](./docs/API.java.md)
* [C#](./docs/API.csharp.md)
* [Go](./docs/API.go.md)

You can also visit a hosted version of the documentation on [constructs.dev](https://constructs.dev/packages/@cdktf/provider-mongodbatlas).

## Versioning

This project is explicitly not tracking the Terraform mongodbatlas provider version 1:1. In fact, it always tracks `latest` of `~> 1.8` with every release. If there are scenarios where you explicitly have to pin your provider version, you can do so by [generating the provider constructs manually](https://cdk.tf/imports).

These are the upstream dependencies:

* [CDK for Terraform](https://cdk.tf)
* [Terraform mongodbatlas provider](https://registry.terraform.io/providers/mongodb/mongodbatlas/1.41.0)
* [Terraform Engine](https://terraform.io)

If there are breaking changes (backward incompatible) in any of the above, the major version of this project will be bumped.

## Features / Issues / Bugs

Please report bugs and issues to the [CDK for Terraform](https://cdk.tf) project:

* [Create bug report](https://cdk.tf/bug)
* [Create feature request](https://cdk.tf/feature)

## Contributing

### Projen

This is mostly based on [Projen](https://github.com/projen/projen), which takes care of generating the entire repository.

### cdktf-provider-project based on Projen

There's a custom [project builder](https://github.com/cdktf/cdktf-provider-project) which encapsulate the common settings for all `cdktf` prebuilt providers.

### Provider Version

The provider version can be adjusted in [./.projenrc.js](./.projenrc.js).

### Repository Management

The repository is managed by [CDKTF Repository Manager](https://github.com/cdktf/cdktf-repository-manager/).
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

from ._jsii import *

__all__ = [
    "access_list_api_key",
    "advanced_cluster",
    "alert_configuration",
    "api_key",
    "api_key_project_assignment",
    "auditing",
    "backup_compliance_policy",
    "cloud_backup_schedule",
    "cloud_backup_snapshot",
    "cloud_backup_snapshot_export_bucket",
    "cloud_backup_snapshot_export_job",
    "cloud_backup_snapshot_restore_job",
    "cloud_provider_access_authorization",
    "cloud_provider_access_setup",
    "cluster",
    "cluster_outage_simulation",
    "custom_db_role",
    "custom_dns_configuration_cluster_aws",
    "data_lake_pipeline",
    "data_mongodbatlas_access_list_api_key",
    "data_mongodbatlas_access_list_api_keys",
    "data_mongodbatlas_advanced_cluster",
    "data_mongodbatlas_advanced_clusters",
    "data_mongodbatlas_alert_configuration",
    "data_mongodbatlas_alert_configurations",
    "data_mongodbatlas_api_key",
    "data_mongodbatlas_api_key_project_assignment",
    "data_mongodbatlas_api_key_project_assignments",
    "data_mongodbatlas_api_keys",
    "data_mongodbatlas_atlas_user",
    "data_mongodbatlas_atlas_users",
    "data_mongodbatlas_auditing",
    "data_mongodbatlas_backup_compliance_policy",
    "data_mongodbatlas_cloud_backup_schedule",
    "data_mongodbatlas_cloud_backup_snapshot",
    "data_mongodbatlas_cloud_backup_snapshot_export_bucket",
    "data_mongodbatlas_cloud_backup_snapshot_export_buckets",
    "data_mongodbatlas_cloud_backup_snapshot_export_job",
    "data_mongodbatlas_cloud_backup_snapshot_export_jobs",
    "data_mongodbatlas_cloud_backup_snapshot_restore_job",
    "data_mongodbatlas_cloud_backup_snapshot_restore_jobs",
    "data_mongodbatlas_cloud_backup_snapshots",
    "data_mongodbatlas_cloud_provider_access_setup",
    "data_mongodbatlas_cluster",
    "data_mongodbatlas_cluster_outage_simulation",
    "data_mongodbatlas_clusters",
    "data_mongodbatlas_control_plane_ip_addresses",
    "data_mongodbatlas_custom_db_role",
    "data_mongodbatlas_custom_db_roles",
    "data_mongodbatlas_custom_dns_configuration_cluster_aws",
    "data_mongodbatlas_data_lake_pipeline",
    "data_mongodbatlas_data_lake_pipeline_run",
    "data_mongodbatlas_data_lake_pipeline_runs",
    "data_mongodbatlas_data_lake_pipelines",
    "data_mongodbatlas_database_user",
    "data_mongodbatlas_database_users",
    "data_mongodbatlas_encryption_at_rest",
    "data_mongodbatlas_encryption_at_rest_private_endpoint",
    "data_mongodbatlas_encryption_at_rest_private_endpoints",
    "data_mongodbatlas_event_trigger",
    "data_mongodbatlas_event_triggers",
    "data_mongodbatlas_federated_database_instance",
    "data_mongodbatlas_federated_database_instances",
    "data_mongodbatlas_federated_query_limit",
    "data_mongodbatlas_federated_query_limits",
    "data_mongodbatlas_federated_settings",
    "data_mongodbatlas_federated_settings_identity_provider",
    "data_mongodbatlas_federated_settings_identity_providers",
    "data_mongodbatlas_federated_settings_org_config",
    "data_mongodbatlas_federated_settings_org_configs",
    "data_mongodbatlas_federated_settings_org_role_mapping",
    "data_mongodbatlas_federated_settings_org_role_mappings",
    "data_mongodbatlas_flex_cluster",
    "data_mongodbatlas_flex_clusters",
    "data_mongodbatlas_flex_restore_job",
    "data_mongodbatlas_flex_restore_jobs",
    "data_mongodbatlas_flex_snapshot",
    "data_mongodbatlas_flex_snapshots",
    "data_mongodbatlas_global_cluster_config",
    "data_mongodbatlas_ldap_configuration",
    "data_mongodbatlas_ldap_verify",
    "data_mongodbatlas_maintenance_window",
    "data_mongodbatlas_mongodb_employee_access_grant",
    "data_mongodbatlas_network_container",
    "data_mongodbatlas_network_containers",
    "data_mongodbatlas_network_peering",
    "data_mongodbatlas_network_peerings",
    "data_mongodbatlas_online_archive",
    "data_mongodbatlas_online_archives",
    "data_mongodbatlas_org_invitation",
    "data_mongodbatlas_organization",
    "data_mongodbatlas_organizations",
    "data_mongodbatlas_private_endpoint_regional_mode",
    "data_mongodbatlas_privatelink_endpoint",
    "data_mongodbatlas_privatelink_endpoint_service",
    "data_mongodbatlas_privatelink_endpoint_service_data_federation_online_archive",
    "data_mongodbatlas_privatelink_endpoint_service_data_federation_online_archives",
    "data_mongodbatlas_privatelink_endpoint_service_serverless",
    "data_mongodbatlas_privatelink_endpoints_service_serverless",
    "data_mongodbatlas_project",
    "data_mongodbatlas_project_api_key",
    "data_mongodbatlas_project_api_keys",
    "data_mongodbatlas_project_invitation",
    "data_mongodbatlas_project_ip_access_list",
    "data_mongodbatlas_project_ip_addresses",
    "data_mongodbatlas_projects",
    "data_mongodbatlas_push_based_log_export",
    "data_mongodbatlas_resource_policies",
    "data_mongodbatlas_resource_policy",
    "data_mongodbatlas_roles_org_id",
    "data_mongodbatlas_search_deployment",
    "data_mongodbatlas_search_index",
    "data_mongodbatlas_search_indexes",
    "data_mongodbatlas_serverless_instance",
    "data_mongodbatlas_serverless_instances",
    "data_mongodbatlas_shared_tier_restore_job",
    "data_mongodbatlas_shared_tier_restore_jobs",
    "data_mongodbatlas_shared_tier_snapshot",
    "data_mongodbatlas_shared_tier_snapshots",
    "data_mongodbatlas_stream_account_details",
    "data_mongodbatlas_stream_connection",
    "data_mongodbatlas_stream_connections",
    "data_mongodbatlas_stream_instance",
    "data_mongodbatlas_stream_instances",
    "data_mongodbatlas_stream_privatelink_endpoint",
    "data_mongodbatlas_stream_privatelink_endpoints",
    "data_mongodbatlas_stream_processor",
    "data_mongodbatlas_stream_processors",
    "data_mongodbatlas_team",
    "data_mongodbatlas_teams",
    "data_mongodbatlas_third_party_integration",
    "data_mongodbatlas_third_party_integrations",
    "data_mongodbatlas_x509_authentication_database_user",
    "database_user",
    "encryption_at_rest",
    "encryption_at_rest_private_endpoint",
    "event_trigger",
    "federated_database_instance",
    "federated_query_limit",
    "federated_settings_identity_provider",
    "federated_settings_org_config",
    "federated_settings_org_role_mapping",
    "flex_cluster",
    "global_cluster_config",
    "ldap_configuration",
    "ldap_verify",
    "maintenance_window",
    "mongodb_employee_access_grant",
    "network_container",
    "network_peering",
    "online_archive",
    "org_invitation",
    "organization",
    "private_endpoint_regional_mode",
    "privatelink_endpoint",
    "privatelink_endpoint_serverless",
    "privatelink_endpoint_service",
    "privatelink_endpoint_service_data_federation_online_archive",
    "privatelink_endpoint_service_serverless",
    "project",
    "project_api_key",
    "project_invitation",
    "project_ip_access_list",
    "provider",
    "push_based_log_export",
    "resource_policy",
    "search_deployment",
    "search_index",
    "serverless_instance",
    "stream_connection",
    "stream_instance",
    "stream_privatelink_endpoint",
    "stream_processor",
    "team",
    "teams",
    "third_party_integration",
    "x509_authentication_database_user",
]

publication.publish()

# Loading modules to ensure their types are registered with the jsii runtime library
from . import access_list_api_key
from . import advanced_cluster
from . import alert_configuration
from . import api_key
from . import api_key_project_assignment
from . import auditing
from . import backup_compliance_policy
from . import cloud_backup_schedule
from . import cloud_backup_snapshot
from . import cloud_backup_snapshot_export_bucket
from . import cloud_backup_snapshot_export_job
from . import cloud_backup_snapshot_restore_job
from . import cloud_provider_access_authorization
from . import cloud_provider_access_setup
from . import cluster
from . import cluster_outage_simulation
from . import custom_db_role
from . import custom_dns_configuration_cluster_aws
from . import data_lake_pipeline
from . import data_mongodbatlas_access_list_api_key
from . import data_mongodbatlas_access_list_api_keys
from . import data_mongodbatlas_advanced_cluster
from . import data_mongodbatlas_advanced_clusters
from . import data_mongodbatlas_alert_configuration
from . import data_mongodbatlas_alert_configurations
from . import data_mongodbatlas_api_key
from . import data_mongodbatlas_api_key_project_assignment
from . import data_mongodbatlas_api_key_project_assignments
from . import data_mongodbatlas_api_keys
from . import data_mongodbatlas_atlas_user
from . import data_mongodbatlas_atlas_users
from . import data_mongodbatlas_auditing
from . import data_mongodbatlas_backup_compliance_policy
from . import data_mongodbatlas_cloud_backup_schedule
from . import data_mongodbatlas_cloud_backup_snapshot
from . import data_mongodbatlas_cloud_backup_snapshot_export_bucket
from . import data_mongodbatlas_cloud_backup_snapshot_export_buckets
from . import data_mongodbatlas_cloud_backup_snapshot_export_job
from . import data_mongodbatlas_cloud_backup_snapshot_export_jobs
from . import data_mongodbatlas_cloud_backup_snapshot_restore_job
from . import data_mongodbatlas_cloud_backup_snapshot_restore_jobs
from . import data_mongodbatlas_cloud_backup_snapshots
from . import data_mongodbatlas_cloud_provider_access_setup
from . import data_mongodbatlas_cluster
from . import data_mongodbatlas_cluster_outage_simulation
from . import data_mongodbatlas_clusters
from . import data_mongodbatlas_control_plane_ip_addresses
from . import data_mongodbatlas_custom_db_role
from . import data_mongodbatlas_custom_db_roles
from . import data_mongodbatlas_custom_dns_configuration_cluster_aws
from . import data_mongodbatlas_data_lake_pipeline
from . import data_mongodbatlas_data_lake_pipeline_run
from . import data_mongodbatlas_data_lake_pipeline_runs
from . import data_mongodbatlas_data_lake_pipelines
from . import data_mongodbatlas_database_user
from . import data_mongodbatlas_database_users
from . import data_mongodbatlas_encryption_at_rest
from . import data_mongodbatlas_encryption_at_rest_private_endpoint
from . import data_mongodbatlas_encryption_at_rest_private_endpoints
from . import data_mongodbatlas_event_trigger
from . import data_mongodbatlas_event_triggers
from . import data_mongodbatlas_federated_database_instance
from . import data_mongodbatlas_federated_database_instances
from . import data_mongodbatlas_federated_query_limit
from . import data_mongodbatlas_federated_query_limits
from . import data_mongodbatlas_federated_settings
from . import data_mongodbatlas_federated_settings_identity_provider
from . import data_mongodbatlas_federated_settings_identity_providers
from . import data_mongodbatlas_federated_settings_org_config
from . import data_mongodbatlas_federated_settings_org_configs
from . import data_mongodbatlas_federated_settings_org_role_mapping
from . import data_mongodbatlas_federated_settings_org_role_mappings
from . import data_mongodbatlas_flex_cluster
from . import data_mongodbatlas_flex_clusters
from . import data_mongodbatlas_flex_restore_job
from . import data_mongodbatlas_flex_restore_jobs
from . import data_mongodbatlas_flex_snapshot
from . import data_mongodbatlas_flex_snapshots
from . import data_mongodbatlas_global_cluster_config
from . import data_mongodbatlas_ldap_configuration
from . import data_mongodbatlas_ldap_verify
from . import data_mongodbatlas_maintenance_window
from . import data_mongodbatlas_mongodb_employee_access_grant
from . import data_mongodbatlas_network_container
from . import data_mongodbatlas_network_containers
from . import data_mongodbatlas_network_peering
from . import data_mongodbatlas_network_peerings
from . import data_mongodbatlas_online_archive
from . import data_mongodbatlas_online_archives
from . import data_mongodbatlas_org_invitation
from . import data_mongodbatlas_organization
from . import data_mongodbatlas_organizations
from . import data_mongodbatlas_private_endpoint_regional_mode
from . import data_mongodbatlas_privatelink_endpoint
from . import data_mongodbatlas_privatelink_endpoint_service
from . import data_mongodbatlas_privatelink_endpoint_service_data_federation_online_archive
from . import data_mongodbatlas_privatelink_endpoint_service_data_federation_online_archives
from . import data_mongodbatlas_privatelink_endpoint_service_serverless
from . import data_mongodbatlas_privatelink_endpoints_service_serverless
from . import data_mongodbatlas_project
from . import data_mongodbatlas_project_api_key
from . import data_mongodbatlas_project_api_keys
from . import data_mongodbatlas_project_invitation
from . import data_mongodbatlas_project_ip_access_list
from . import data_mongodbatlas_project_ip_addresses
from . import data_mongodbatlas_projects
from . import data_mongodbatlas_push_based_log_export
from . import data_mongodbatlas_resource_policies
from . import data_mongodbatlas_resource_policy
from . import data_mongodbatlas_roles_org_id
from . import data_mongodbatlas_search_deployment
from . import data_mongodbatlas_search_index
from . import data_mongodbatlas_search_indexes
from . import data_mongodbatlas_serverless_instance
from . import data_mongodbatlas_serverless_instances
from . import data_mongodbatlas_shared_tier_restore_job
from . import data_mongodbatlas_shared_tier_restore_jobs
from . import data_mongodbatlas_shared_tier_snapshot
from . import data_mongodbatlas_shared_tier_snapshots
from . import data_mongodbatlas_stream_account_details
from . import data_mongodbatlas_stream_connection
from . import data_mongodbatlas_stream_connections
from . import data_mongodbatlas_stream_instance
from . import data_mongodbatlas_stream_instances
from . import data_mongodbatlas_stream_privatelink_endpoint
from . import data_mongodbatlas_stream_privatelink_endpoints
from . import data_mongodbatlas_stream_processor
from . import data_mongodbatlas_stream_processors
from . import data_mongodbatlas_team
from . import data_mongodbatlas_teams
from . import data_mongodbatlas_third_party_integration
from . import data_mongodbatlas_third_party_integrations
from . import data_mongodbatlas_x509_authentication_database_user
from . import database_user
from . import encryption_at_rest
from . import encryption_at_rest_private_endpoint
from . import event_trigger
from . import federated_database_instance
from . import federated_query_limit
from . import federated_settings_identity_provider
from . import federated_settings_org_config
from . import federated_settings_org_role_mapping
from . import flex_cluster
from . import global_cluster_config
from . import ldap_configuration
from . import ldap_verify
from . import maintenance_window
from . import mongodb_employee_access_grant
from . import network_container
from . import network_peering
from . import online_archive
from . import org_invitation
from . import organization
from . import private_endpoint_regional_mode
from . import privatelink_endpoint
from . import privatelink_endpoint_serverless
from . import privatelink_endpoint_service
from . import privatelink_endpoint_service_data_federation_online_archive
from . import privatelink_endpoint_service_serverless
from . import project
from . import project_api_key
from . import project_invitation
from . import project_ip_access_list
from . import provider
from . import push_based_log_export
from . import resource_policy
from . import search_deployment
from . import search_index
from . import serverless_instance
from . import stream_connection
from . import stream_instance
from . import stream_privatelink_endpoint
from . import stream_processor
from . import team
from . import teams
from . import third_party_integration
from . import x509_authentication_database_user
