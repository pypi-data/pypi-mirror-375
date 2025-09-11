from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource
from cyberfusion.CoreApiClient.http import DtoResponse


class HtpasswdUsers(Resource):
    def create_htpasswd_user(
        self,
        request: models.HtpasswdUserCreateRequest,
    ) -> DtoResponse[models.HtpasswdUserResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/htpasswd-users",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.HtpasswdUserResource)

    def list_htpasswd_users(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.HtpasswdUserResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/htpasswd-users",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(local_response, models.HtpasswdUserResource)

    def read_htpasswd_user(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.HtpasswdUserResource]:
        local_response = self.api_connector.send_or_fail(
            "GET", f"/api/v1/htpasswd-users/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.HtpasswdUserResource)

    def update_htpasswd_user(
        self,
        request: models.HtpasswdUserUpdateRequest,
        *,
        id_: int,
    ) -> DtoResponse[models.HtpasswdUserResource]:
        local_response = self.api_connector.send_or_fail(
            "PATCH",
            f"/api/v1/htpasswd-users/{id_}",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.HtpasswdUserResource)

    def delete_htpasswd_user(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.DetailMessage]:
        local_response = self.api_connector.send_or_fail(
            "DELETE",
            f"/api/v1/htpasswd-users/{id_}",
            data=None,
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.DetailMessage)
