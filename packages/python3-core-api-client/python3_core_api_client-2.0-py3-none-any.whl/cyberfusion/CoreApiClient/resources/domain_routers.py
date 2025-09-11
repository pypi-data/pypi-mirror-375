from cyberfusion.CoreApiClient import models
from typing import Optional, List
from cyberfusion.CoreApiClient.interfaces import Resource
from cyberfusion.CoreApiClient.http import DtoResponse


class DomainRouters(Resource):
    def list_domain_routers(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.DomainRouterResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/domain-routers",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(local_response, models.DomainRouterResource)

    def update_domain_router(
        self,
        request: models.DomainRouterUpdateRequest,
        *,
        id_: int,
    ) -> DtoResponse[models.DomainRouterResource]:
        local_response = self.api_connector.send_or_fail(
            "PATCH",
            f"/api/v1/domain-routers/{id_}",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.DomainRouterResource)
