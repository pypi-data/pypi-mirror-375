from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource
from cyberfusion.CoreApiClient.http import DtoResponse


class RedisInstances(Resource):
    def create_redis_instance(
        self,
        request: models.RedisInstanceCreateRequest,
    ) -> DtoResponse[models.RedisInstanceResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/redis-instances",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.RedisInstanceResource)

    def list_redis_instances(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.RedisInstanceResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/redis-instances",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(local_response, models.RedisInstanceResource)

    def read_redis_instance(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.RedisInstanceResource]:
        local_response = self.api_connector.send_or_fail(
            "GET", f"/api/v1/redis-instances/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.RedisInstanceResource)

    def update_redis_instance(
        self,
        request: models.RedisInstanceUpdateRequest,
        *,
        id_: int,
    ) -> DtoResponse[models.RedisInstanceResource]:
        local_response = self.api_connector.send_or_fail(
            "PATCH",
            f"/api/v1/redis-instances/{id_}",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.RedisInstanceResource)

    def delete_redis_instance(
        self,
        *,
        id_: int,
        delete_on_cluster: Optional[bool] = None,
    ) -> DtoResponse[models.DetailMessage]:
        local_response = self.api_connector.send_or_fail(
            "DELETE",
            f"/api/v1/redis-instances/{id_}",
            data=None,
            query_parameters={
                "delete_on_cluster": delete_on_cluster,
            },
        )

        return DtoResponse.from_response(local_response, models.DetailMessage)
