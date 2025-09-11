from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource
from cyberfusion.CoreApiClient.http import DtoResponse


class Nodes(Resource):
    def create_node(
        self,
        request: models.NodeCreateRequest,
        *,
        callback_url: Optional[str] = None,
    ) -> DtoResponse[models.TaskCollectionResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/nodes",
            data=request.dict(exclude_unset=True),
            query_parameters={
                "callback_url": callback_url,
            },
        )

        return DtoResponse.from_response(local_response, models.TaskCollectionResource)

    def list_nodes(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.NodeResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/nodes",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(local_response, models.NodeResource)

    def get_node_products(
        self,
    ) -> DtoResponse[list[models.NodeProduct]]:
        local_response = self.api_connector.send_or_fail(
            "GET", "/api/v1/nodes/products", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.NodeProduct)

    def read_node(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.NodeResource]:
        local_response = self.api_connector.send_or_fail(
            "GET", f"/api/v1/nodes/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.NodeResource)

    def update_node(
        self,
        request: models.NodeUpdateRequest,
        *,
        id_: int,
    ) -> DtoResponse[models.NodeResource]:
        local_response = self.api_connector.send_or_fail(
            "PATCH",
            f"/api/v1/nodes/{id_}",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.NodeResource)

    def delete_node(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.DetailMessage]:
        local_response = self.api_connector.send_or_fail(
            "DELETE", f"/api/v1/nodes/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.DetailMessage)

    def upgrade_downgrade_node(
        self,
        *,
        id_: int,
        callback_url: Optional[str] = None,
        product: str,
    ) -> DtoResponse[models.TaskCollectionResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            f"/api/v1/nodes/{id_}/xgrade",
            data=None,
            query_parameters={
                "callback_url": callback_url,
                "product": product,
            },
        )

        return DtoResponse.from_response(local_response, models.TaskCollectionResource)
