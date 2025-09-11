from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.http import DtoResponse
from cyberfusion.CoreApiClient.interfaces import Resource


class BorgRepositories(Resource):
    def create_borg_repository(
        self,
        request: models.BorgRepositoryCreateRequest,
    ) -> DtoResponse[models.BorgRepositoryResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/borg-repositories",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.BorgRepositoryResource)

    def list_borg_repositories(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.BorgRepositoryResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/borg-repositories",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(local_response, models.BorgRepositoryResource)

    def read_borg_repository(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.BorgRepositoryResource]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            f"/api/v1/borg-repositories/{id_}",
            data=None,
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.BorgRepositoryResource)

    def update_borg_repository(
        self,
        request: models.BorgRepositoryUpdateRequest,
        *,
        id_: int,
    ) -> DtoResponse[models.BorgRepositoryResource]:
        local_response = self.api_connector.send_or_fail(
            "PATCH",
            f"/api/v1/borg-repositories/{id_}",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.BorgRepositoryResource)

    def delete_borg_repository(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.DetailMessage]:
        local_response = self.api_connector.send_or_fail(
            "DELETE",
            f"/api/v1/borg-repositories/{id_}",
            data=None,
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.DetailMessage)

    def prune_borg_repository(
        self,
        *,
        id_: int,
        callback_url: Optional[str] = None,
    ) -> DtoResponse[models.TaskCollectionResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            f"/api/v1/borg-repositories/{id_}/prune",
            data=None,
            query_parameters={
                "callback_url": callback_url,
            },
        )

        return DtoResponse.from_response(local_response, models.TaskCollectionResource)

    def check_borg_repository(
        self,
        *,
        id_: int,
        callback_url: Optional[str] = None,
    ) -> DtoResponse[models.TaskCollectionResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            f"/api/v1/borg-repositories/{id_}/check",
            data=None,
            query_parameters={
                "callback_url": callback_url,
            },
        )

        return DtoResponse.from_response(local_response, models.TaskCollectionResource)

    def get_borg_archives_metadata(
        self,
        *,
        id_: int,
    ) -> DtoResponse[list[models.BorgArchiveMetadata]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            f"/api/v1/borg-repositories/{id_}/archives-metadata",
            data=None,
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.BorgArchiveMetadata)
