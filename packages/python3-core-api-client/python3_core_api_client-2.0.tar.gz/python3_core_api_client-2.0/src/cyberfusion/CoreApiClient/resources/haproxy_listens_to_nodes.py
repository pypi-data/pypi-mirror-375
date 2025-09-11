from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource
from cyberfusion.CoreApiClient.http import DtoResponse


class HAProxyListensToNodes(Resource):
    def create_haproxy_listen_to_node(
        self,
        request: models.HAProxyListenToNodeCreateRequest,
    ) -> DtoResponse[models.HAProxyListenToNodeResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/haproxy-listens-to-nodes",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(
            local_response, models.HAProxyListenToNodeResource
        )

    def list_haproxy_listens_to_nodes(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.HAProxyListenToNodeResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/haproxy-listens-to-nodes",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(
            local_response, models.HAProxyListenToNodeResource
        )

    def read_haproxy_listen_to_node(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.HAProxyListenToNodeResource]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            f"/api/v1/haproxy-listens-to-nodes/{id_}",
            data=None,
            query_parameters={},
        )

        return DtoResponse.from_response(
            local_response, models.HAProxyListenToNodeResource
        )

    def delete_haproxy_listen_to_node(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.DetailMessage]:
        local_response = self.api_connector.send_or_fail(
            "DELETE",
            f"/api/v1/haproxy-listens-to-nodes/{id_}",
            data=None,
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.DetailMessage)
