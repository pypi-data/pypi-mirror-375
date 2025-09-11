from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource
from cyberfusion.CoreApiClient.http import DtoResponse


class NodeAddOns(Resource):
    def create_node_add_on(
        self,
        request: models.NodeAddOnCreateRequest,
    ) -> DtoResponse[models.TaskCollectionResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/node-add-ons",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.TaskCollectionResource)

    def list_node_add_ons(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.NodeAddOnResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/node-add-ons",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(local_response, models.NodeAddOnResource)

    def get_node_add_on_products(
        self,
    ) -> DtoResponse[list[models.NodeAddOnProduct]]:
        local_response = self.api_connector.send_or_fail(
            "GET", "/api/v1/node-add-ons/products", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.NodeAddOnProduct)

    def read_node_add_on(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.NodeAddOnResource]:
        local_response = self.api_connector.send_or_fail(
            "GET", f"/api/v1/node-add-ons/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.NodeAddOnResource)

    def delete_node_add_on(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.DetailMessage]:
        local_response = self.api_connector.send_or_fail(
            "DELETE", f"/api/v1/node-add-ons/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.DetailMessage)
