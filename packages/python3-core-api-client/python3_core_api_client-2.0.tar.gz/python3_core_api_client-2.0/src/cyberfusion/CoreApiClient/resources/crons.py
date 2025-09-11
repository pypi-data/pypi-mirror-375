from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.http import DtoResponse
from cyberfusion.CoreApiClient.interfaces import Resource


class Crons(Resource):
    def create_cron(
        self,
        request: models.CronCreateRequest,
    ) -> DtoResponse[models.CronResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/crons",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.CronResource)

    def list_crons(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.CronResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/crons",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(local_response, models.CronResource)

    def read_cron(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.CronResource]:
        local_response = self.api_connector.send_or_fail(
            "GET", f"/api/v1/crons/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.CronResource)

    def update_cron(
        self,
        request: models.CronUpdateRequest,
        *,
        id_: int,
    ) -> DtoResponse[models.CronResource]:
        local_response = self.api_connector.send_or_fail(
            "PATCH",
            f"/api/v1/crons/{id_}",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.CronResource)

    def delete_cron(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.DetailMessage]:
        local_response = self.api_connector.send_or_fail(
            "DELETE", f"/api/v1/crons/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.DetailMessage)
