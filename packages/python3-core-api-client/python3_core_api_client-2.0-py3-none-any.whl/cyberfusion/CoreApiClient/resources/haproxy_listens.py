from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource
from cyberfusion.CoreApiClient.http import DtoResponse


class HAProxyListens(Resource):
    def create_haproxy_listen(
        self,
        request: models.HAProxyListenCreateRequest,
    ) -> DtoResponse[models.HAProxyListenResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/haproxy-listens",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.HAProxyListenResource)

    def list_haproxy_listens(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.HAProxyListenResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/haproxy-listens",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(local_response, models.HAProxyListenResource)

    def read_haproxy_listen(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.HAProxyListenResource]:
        local_response = self.api_connector.send_or_fail(
            "GET", f"/api/v1/haproxy-listens/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.HAProxyListenResource)

    def delete_haproxy_listen(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.DetailMessage]:
        local_response = self.api_connector.send_or_fail(
            "DELETE",
            f"/api/v1/haproxy-listens/{id_}",
            data=None,
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.DetailMessage)
