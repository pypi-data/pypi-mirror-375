from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.http import DtoResponse
from cyberfusion.CoreApiClient.interfaces import Resource


class DatabaseUserGrants(Resource):
    def create_database_user_grant(
        self,
        request: models.DatabaseUserGrantCreateRequest,
    ) -> DtoResponse[models.DatabaseUserGrantResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/database-user-grants",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(
            local_response, models.DatabaseUserGrantResource
        )

    def list_database_user_grants(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.DatabaseUserGrantResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/database-user-grants",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(
            local_response, models.DatabaseUserGrantResource
        )

    def list_database_user_grants_for_database_users(
        self,
        *,
        database_user_id: int,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.DatabaseUserGrantResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            f"/api/v1/database-user-grants/{database_user_id}",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(
            local_response, models.DatabaseUserGrantResource
        )

    def delete_database_user_grant(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.DetailMessage]:
        local_response = self.api_connector.send_or_fail(
            "DELETE",
            f"/api/v1/database-user-grants/{id_}",
            data=None,
        )

        return DtoResponse.from_response(local_response, models.DetailMessage)
