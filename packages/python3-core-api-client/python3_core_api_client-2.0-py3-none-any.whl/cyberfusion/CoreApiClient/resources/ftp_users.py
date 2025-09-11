from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource
from cyberfusion.CoreApiClient.http import DtoResponse


class FTPUsers(Resource):
    def create_ftp_user(
        self,
        request: models.FTPUserCreateRequest,
    ) -> DtoResponse[models.FTPUserResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/ftp-users",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.FTPUserResource)

    def list_ftp_users(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.FTPUserResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/ftp-users",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(local_response, models.FTPUserResource)

    def read_ftp_user(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.FTPUserResource]:
        local_response = self.api_connector.send_or_fail(
            "GET", f"/api/v1/ftp-users/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.FTPUserResource)

    def update_ftp_user(
        self,
        request: models.FTPUserUpdateRequest,
        *,
        id_: int,
    ) -> DtoResponse[models.FTPUserResource]:
        local_response = self.api_connector.send_or_fail(
            "PATCH",
            f"/api/v1/ftp-users/{id_}",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.FTPUserResource)

    def delete_ftp_user(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.DetailMessage]:
        local_response = self.api_connector.send_or_fail(
            "DELETE", f"/api/v1/ftp-users/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.DetailMessage)

    def create_temporary_ftp_user(
        self,
        request: models.TemporaryFTPUserCreateRequest,
    ) -> DtoResponse[models.TemporaryFTPUserResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/ftp-users/temporary",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(
            local_response, models.TemporaryFTPUserResource
        )
