from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource
from cyberfusion.CoreApiClient.http import DtoResponse


class FPMPools(Resource):
    def create_fpm_pool(
        self,
        request: models.FPMPoolCreateRequest,
    ) -> DtoResponse[models.FPMPoolResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/fpm-pools",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.FPMPoolResource)

    def list_fpm_pools(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.FPMPoolResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/fpm-pools",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(local_response, models.FPMPoolResource)

    def read_fpm_pool(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.FPMPoolResource]:
        local_response = self.api_connector.send_or_fail(
            "GET", f"/api/v1/fpm-pools/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.FPMPoolResource)

    def update_fpm_pool(
        self,
        request: models.FPMPoolUpdateRequest,
        *,
        id_: int,
    ) -> DtoResponse[models.FPMPoolResource]:
        local_response = self.api_connector.send_or_fail(
            "PATCH",
            f"/api/v1/fpm-pools/{id_}",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.FPMPoolResource)

    def delete_fpm_pool(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.DetailMessage]:
        local_response = self.api_connector.send_or_fail(
            "DELETE", f"/api/v1/fpm-pools/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.DetailMessage)

    def restart_fpm_pool(
        self,
        *,
        id_: int,
        callback_url: Optional[str] = None,
    ) -> DtoResponse[models.TaskCollectionResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            f"/api/v1/fpm-pools/{id_}/restart",
            data=None,
            query_parameters={
                "callback_url": callback_url,
            },
        )

        return DtoResponse.from_response(local_response, models.TaskCollectionResource)

    def reload_fpm_pool(
        self,
        *,
        id_: int,
        callback_url: Optional[str] = None,
    ) -> DtoResponse[models.TaskCollectionResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            f"/api/v1/fpm-pools/{id_}/reload",
            data=None,
            query_parameters={
                "callback_url": callback_url,
            },
        )

        return DtoResponse.from_response(local_response, models.TaskCollectionResource)
