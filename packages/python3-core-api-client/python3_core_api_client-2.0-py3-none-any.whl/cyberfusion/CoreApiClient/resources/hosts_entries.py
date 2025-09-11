from cyberfusion.CoreApiClient import models
from typing import Optional, List
from cyberfusion.CoreApiClient.interfaces import Resource
from cyberfusion.CoreApiClient.http import DtoResponse


class HostsEntries(Resource):
    def create_hosts_entry(
        self,
        request: models.HostsEntryCreateRequest,
    ) -> DtoResponse[models.HostsEntryResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/hosts-entries",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.HostsEntryResource)

    def list_hosts_entries(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.HostsEntryResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/hosts-entries",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(local_response, models.HostsEntryResource)

    def read_hosts_entry(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.HostsEntryResource]:
        local_response = self.api_connector.send_or_fail(
            "GET", f"/api/v1/hosts-entries/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.HostsEntryResource)

    def delete_hosts_entry(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.DetailMessage]:
        local_response = self.api_connector.send_or_fail(
            "DELETE", f"/api/v1/hosts-entries/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.DetailMessage)
