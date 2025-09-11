from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.http import DtoResponse
from cyberfusion.CoreApiClient.interfaces import Resource


class VirtualHosts(Resource):
    def create_virtual_host(
        self,
        request: models.VirtualHostCreateRequest,
    ) -> DtoResponse[models.VirtualHostResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/virtual-hosts",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.VirtualHostResource)

    def list_virtual_hosts(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.VirtualHostResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/virtual-hosts",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(local_response, models.VirtualHostResource)

    def read_virtual_host(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.VirtualHostResource]:
        local_response = self.api_connector.send_or_fail(
            "GET", f"/api/v1/virtual-hosts/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.VirtualHostResource)

    def update_virtual_host(
        self,
        request: models.VirtualHostUpdateRequest,
        *,
        id_: int,
    ) -> DtoResponse[models.VirtualHostResource]:
        local_response = self.api_connector.send_or_fail(
            "PATCH",
            f"/api/v1/virtual-hosts/{id_}",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.VirtualHostResource)

    def delete_virtual_host(
        self,
        *,
        id_: int,
        delete_on_cluster: Optional[bool] = None,
    ) -> DtoResponse[models.DetailMessage]:
        local_response = self.api_connector.send_or_fail(
            "DELETE",
            f"/api/v1/virtual-hosts/{id_}",
            data=None,
            query_parameters={
                "delete_on_cluster": delete_on_cluster,
            },
        )

        return DtoResponse.from_response(local_response, models.DetailMessage)

    def get_virtual_host_document_root(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.VirtualHostDocumentRoot]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            f"/api/v1/virtual-hosts/{id_}/document-root",
            data=None,
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.VirtualHostDocumentRoot)

    def sync_domain_roots_of_virtual_hosts(
        self,
        *,
        left_virtual_host_id: int,
        right_virtual_host_id: int,
        callback_url: Optional[str] = None,
        exclude_paths: Optional[List[str]] = None,
    ) -> DtoResponse[models.TaskCollectionResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            f"/api/v1/virtual-hosts/{left_virtual_host_id}/domain-root/sync",
            data=None,
            query_parameters={
                "callback_url": callback_url,
                "right_virtual_host_id": right_virtual_host_id,
                "exclude_paths": exclude_paths,
            },
        )

        return DtoResponse.from_response(local_response, models.TaskCollectionResource)
