from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.http import DtoResponse
from cyberfusion.CoreApiClient.interfaces import Resource


class BorgArchives(Resource):
    def create_borg_archive_for_database(
        self,
        request: models.BorgArchiveCreateDatabaseRequest,
        *,
        callback_url: Optional[str] = None,
    ) -> DtoResponse[models.TaskCollectionResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/borg-archives/database",
            data=request.dict(exclude_unset=True),
            query_parameters={
                "callback_url": callback_url,
            },
        )

        return DtoResponse.from_response(local_response, models.TaskCollectionResource)

    def create_borg_archive_for_unix_user(
        self,
        request: models.BorgArchiveCreateUNIXUserRequest,
        *,
        callback_url: Optional[str] = None,
    ) -> DtoResponse[models.TaskCollectionResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/borg-archives/unix-user",
            data=request.dict(exclude_unset=True),
            query_parameters={
                "callback_url": callback_url,
            },
        )

        return DtoResponse.from_response(local_response, models.TaskCollectionResource)

    def list_borg_archives(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.BorgArchiveResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/borg-archives",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(local_response, models.BorgArchiveResource)

    def read_borg_archive(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.BorgArchiveResource]:
        local_response = self.api_connector.send_or_fail(
            "GET", f"/api/v1/borg-archives/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.BorgArchiveResource)

    def get_borg_archive_metadata(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.BorgArchiveMetadata]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            f"/api/v1/borg-archives/{id_}/metadata",
            data=None,
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.BorgArchiveMetadata)

    def restore_borg_archive(
        self,
        *,
        id_: int,
        callback_url: Optional[str] = None,
        path: Optional[str] = None,
    ) -> DtoResponse[models.TaskCollectionResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            f"/api/v1/borg-archives/{id_}/restore",
            data=None,
            query_parameters={
                "callback_url": callback_url,
                "path": path,
            },
        )

        return DtoResponse.from_response(local_response, models.TaskCollectionResource)

    def list_borg_archive_contents(
        self,
        *,
        id_: int,
        path: Optional[str] = None,
    ) -> DtoResponse[list[models.BorgArchiveContent]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            f"/api/v1/borg-archives/{id_}/contents",
            data=None,
            query_parameters={
                "path": path,
            },
        )

        return DtoResponse.from_response(local_response, models.BorgArchiveContent)

    def download_borg_archive(
        self,
        *,
        id_: int,
        callback_url: Optional[str] = None,
        path: Optional[str] = None,
    ) -> DtoResponse[models.TaskCollectionResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            f"/api/v1/borg-archives/{id_}/download",
            data=None,
            query_parameters={
                "callback_url": callback_url,
                "path": path,
            },
        )

        return DtoResponse.from_response(local_response, models.TaskCollectionResource)
