from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.http import DtoResponse
from cyberfusion.CoreApiClient.interfaces import Resource


class Clusters(Resource):
    def get_common_properties(
        self,
    ) -> DtoResponse[models.ClustersCommonProperties]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/clusters/common-properties",
            data=None,
            query_parameters={},
        )

        return DtoResponse.from_response(
            local_response, models.ClustersCommonProperties
        )

    def create_cluster(
        self,
        request: models.ClusterCreateRequest,
        *,
        callback_url: Optional[str] = None,
    ) -> DtoResponse[models.TaskCollectionResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/clusters",
            data=request.dict(exclude_unset=True),
            query_parameters={
                "callback_url": callback_url,
            },
        )

        return DtoResponse.from_response(local_response, models.TaskCollectionResource)

    def list_clusters(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.ClusterResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/clusters",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(local_response, models.ClusterResource)

    def read_cluster(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.ClusterResource]:
        local_response = self.api_connector.send_or_fail(
            "GET", f"/api/v1/clusters/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.ClusterResource)

    def update_cluster(
        self,
        request: models.ClusterUpdateRequest,
        *,
        id_: int,
    ) -> DtoResponse[models.ClusterResource]:
        local_response = self.api_connector.send_or_fail(
            "PATCH",
            f"/api/v1/clusters/{id_}",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.ClusterResource)

    def get_borg_ssh_key(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.ClusterBorgSSHKey]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            f"/api/v1/clusters/{id_}/borg-ssh-key",
            data=None,
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.ClusterBorgSSHKey)

    def list_ip_addresses_for_cluster(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.ClusterIPAddresses]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            f"/api/v1/clusters/{id_}/ip-addresses",
            data=None,
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.ClusterIPAddresses)

    def create_ip_address_for_cluster(
        self,
        request: models.ClusterIPAddressCreateRequest,
        *,
        id_: int,
    ) -> DtoResponse[models.TaskCollectionResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            f"/api/v1/clusters/{id_}/ip-addresses",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.TaskCollectionResource)

    def delete_ip_address_for_cluster(
        self,
        *,
        id_: int,
        ip_address: str,
    ) -> DtoResponse[models.TaskCollectionResource]:
        local_response = self.api_connector.send_or_fail(
            "DELETE",
            f"/api/v1/clusters/{id_}/ip-addresses/{ip_address}",
            data=None,
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.TaskCollectionResource)

    def enable_l3_ddos_protection_for_ip_address(
        self,
        *,
        id_: int,
        ip_address: str,
    ) -> DtoResponse[models.TaskCollectionResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            f"/api/v1/clusters/{id_}/ip-addresses/{ip_address}/l3-ddos-protection",
            data=None,
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.TaskCollectionResource)

    def disable_l3_ddos_protection_for_ip_address(
        self,
        *,
        id_: int,
        ip_address: str,
    ) -> DtoResponse[models.TaskCollectionResource]:
        local_response = self.api_connector.send_or_fail(
            "DELETE",
            f"/api/v1/clusters/{id_}/ip-addresses/{ip_address}/l3-ddos-protection",
            data=None,
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.TaskCollectionResource)

    def get_ip_addresses_products_for_clusters(
        self,
    ) -> DtoResponse[list[models.IPAddressProduct]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/clusters/ip-addresses/products",
            data=None,
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.IPAddressProduct)

    def list_cluster_deployments_results(
        self,
        *,
        id_: int,
        get_non_running: Optional[bool] = None,
    ) -> DtoResponse[models.ClusterDeploymentResults]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            f"/api/v1/clusters/{id_}/deployments-results",
            data=None,
            query_parameters={
                "get_non_running": get_non_running,
            },
        )

        return DtoResponse.from_response(
            local_response, models.ClusterDeploymentResults
        )

    def list_unix_users_home_directory_usages(
        self,
        *,
        cluster_id: int,
        timestamp: str,
        time_unit: Optional[models.UNIXUsersHomeDirectoryUsageResource] = None,
    ) -> DtoResponse[list[models.UNIXUsersHomeDirectoryUsageResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            f"/api/v1/clusters/unix-users-home-directories/usages/{cluster_id}",
            data=None,
            query_parameters={
                "timestamp": timestamp,
                "time_unit": time_unit,
            },
        )

        return DtoResponse.from_response(
            local_response, models.UNIXUsersHomeDirectoryUsageResource
        )

    def list_nodes_dependencies(
        self, *, id_: int
    ) -> DtoResponse[list[models.NodeDependenciesResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            f"/api/v1/clusters/{id_}/nodes-dependencies",
            data=None,
            query_parameters={},
        )

        return DtoResponse.from_response(
            local_response, models.NodeDependenciesResource
        )

    def get_nodes_specifications(
        self, *, id_: int
    ) -> DtoResponse[list[models.NodeDependenciesResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            f"/api/v1/clusters/{id_}/nodes-specifications",
            data=None,
            query_parameters={},
        )

        return DtoResponse.from_response(
            local_response, models.NodeDependenciesResource
        )
