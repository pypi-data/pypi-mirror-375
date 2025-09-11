from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.http import DtoResponse
from cyberfusion.CoreApiClient.interfaces import Resource


class Daemons(Resource):
    def create_daemon(
        self,
        request: models.DaemonCreateRequest,
    ) -> DtoResponse[models.DaemonResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/daemons",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.DaemonResource)

    def list_daemons(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.DaemonResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/daemons",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(local_response, models.DaemonResource)

    def read_daemon(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.DaemonResource]:
        local_response = self.api_connector.send_or_fail(
            "GET", f"/api/v1/daemons/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.DaemonResource)

    def update_daemon(
        self,
        request: models.DaemonUpdateRequest,
        *,
        id_: int,
    ) -> DtoResponse[models.DaemonResource]:
        local_response = self.api_connector.send_or_fail(
            "PATCH",
            f"/api/v1/daemons/{id_}",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.DaemonResource)

    def delete_daemon(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.DetailMessage]:
        local_response = self.api_connector.send_or_fail(
            "DELETE", f"/api/v1/daemons/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.DetailMessage)

    def list_logs(
        self,
        *,
        daemon_id: int,
        timestamp: Optional[str] = None,
        sort: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> DtoResponse[list[models.DaemonLogResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            f"/api/v1/daemons/{daemon_id}/logs",
            data=None,
            query_parameters={
                "timestamp": timestamp,
                "sort": sort,
                "limit": limit,
            },
        )

        return DtoResponse.from_response(local_response, models.DaemonLogResource)
