from typing import Optional, List

from cyberfusion.CoreApiClient import models
from cyberfusion.CoreApiClient.http import DtoResponse
from cyberfusion.CoreApiClient.interfaces import Resource


class DatabaseUsers(Resource):
    def create_database_user(
        self,
        request: models.DatabaseUserCreateRequest,
    ) -> DtoResponse[models.DatabaseUserResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/database-users",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.DatabaseUserResource)

    def list_database_users(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.DatabaseUserResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/database-users",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(local_response, models.DatabaseUserResource)

    def read_database_user(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.DatabaseUserResource]:
        local_response = self.api_connector.send_or_fail(
            "GET", f"/api/v1/database-users/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.DatabaseUserResource)

    def update_database_user(
        self,
        request: models.DatabaseUserUpdateRequest,
        *,
        id_: int,
    ) -> DtoResponse[models.DatabaseUserResource]:
        local_response = self.api_connector.send_or_fail(
            "PATCH",
            f"/api/v1/database-users/{id_}",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.DatabaseUserResource)

    def delete_database_user(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.DetailMessage]:
        local_response = self.api_connector.send_or_fail(
            "DELETE",
            f"/api/v1/database-users/{id_}",
            data=None,
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.DetailMessage)
