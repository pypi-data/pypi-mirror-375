from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource
from cyberfusion.CoreApiClient.http import DtoResponse


class UNIXUsers(Resource):
    def create_unix_user(
        self,
        request: models.UNIXUserCreateRequest,
    ) -> DtoResponse[models.UNIXUserResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/unix-users",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.UNIXUserResource)

    def list_unix_users(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.UNIXUserResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/unix-users",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(local_response, models.UNIXUserResource)

    def read_unix_user(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.UNIXUserResource]:
        local_response = self.api_connector.send_or_fail(
            "GET", f"/api/v1/unix-users/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.UNIXUserResource)

    def update_unix_user(
        self,
        request: models.UNIXUserUpdateRequest,
        *,
        id_: int,
    ) -> DtoResponse[models.UNIXUserResource]:
        local_response = self.api_connector.send_or_fail(
            "PATCH",
            f"/api/v1/unix-users/{id_}",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.UNIXUserResource)

    def delete_unix_user(
        self,
        *,
        id_: int,
        delete_on_cluster: Optional[bool] = None,
    ) -> DtoResponse[models.DetailMessage]:
        local_response = self.api_connector.send_or_fail(
            "DELETE",
            f"/api/v1/unix-users/{id_}",
            data=None,
            query_parameters={
                "delete_on_cluster": delete_on_cluster,
            },
        )

        return DtoResponse.from_response(local_response, models.DetailMessage)

    def compare_unix_users(
        self,
        *,
        left_unix_user_id: int,
        right_unix_user_id: int,
    ) -> DtoResponse[models.UNIXUserComparison]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            f"/api/v1/unix-users/{left_unix_user_id}/comparison",
            data=None,
            query_parameters={
                "right_unix_user_id": right_unix_user_id,
            },
        )

        return DtoResponse.from_response(local_response, models.UNIXUserComparison)

    def list_unix_user_usages(
        self,
        *,
        unix_user_id: int,
        timestamp: str,
        time_unit: Optional[models.UNIXUserUsageResource] = None,
    ) -> DtoResponse[list[models.UNIXUserUsageResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            f"/api/v1/unix-users/usages/{unix_user_id}",
            data=None,
            query_parameters={
                "timestamp": timestamp,
                "time_unit": time_unit,
            },
        )

        return DtoResponse.from_response(local_response, models.UNIXUserUsageResource)
