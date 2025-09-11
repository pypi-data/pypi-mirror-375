from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.http import DtoResponse
from cyberfusion.CoreApiClient.interfaces import Resource


class Customers(Resource):
    def list_customers(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.CustomerResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/customers",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(local_response, models.CustomerResource)

    def read_customer(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.CustomerResource]:
        local_response = self.api_connector.send_or_fail(
            "GET", f"/api/v1/customers/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.CustomerResource)

    def list_ip_addresses_for_customer(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.CustomerIPAddresses]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            f"/api/v1/customers/{id_}/ip-addresses",
            data=None,
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.CustomerIPAddresses)

    def create_ip_address_for_customer(
        self,
        request: models.CustomerIPAddressCreateRequest,
        *,
        id_: int,
    ) -> DtoResponse[models.TaskCollectionResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            f"/api/v1/customers/{id_}/ip-addresses",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.TaskCollectionResource)

    def delete_ip_address_for_customer(
        self,
        *,
        id_: int,
        ip_address: str,
    ) -> DtoResponse[models.TaskCollectionResource]:
        local_response = self.api_connector.send_or_fail(
            "DELETE",
            f"/api/v1/customers/{id_}/ip-addresses/{ip_address}",
            data=None,
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.TaskCollectionResource)

    def get_ip_addresses_products_for_customers(
        self,
    ) -> DtoResponse[list[models.IPAddressProduct]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/customers/ip-addresses/products",
            data=None,
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.IPAddressProduct)
