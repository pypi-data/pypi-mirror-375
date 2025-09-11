from typing import Optional, List

from cyberfusion.CoreApiClient import models
from cyberfusion.CoreApiClient.interfaces import Resource
from cyberfusion.CoreApiClient.http import DtoResponse


class SecurityTXTPolicies(Resource):
    def create_security_txt_policy(
        self,
        request: models.SecurityTXTPolicyCreateRequest,
    ) -> DtoResponse[models.SecurityTXTPolicyResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/security-txt-policies",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(
            local_response, models.SecurityTXTPolicyResource
        )

    def list_security_txt_policies(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.SecurityTXTPolicyResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/security-txt-policies",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(
            local_response, models.SecurityTXTPolicyResource
        )

    def read_security_txt_policy(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.SecurityTXTPolicyResource]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            f"/api/v1/security-txt-policies/{id_}",
            data=None,
            query_parameters={},
        )

        return DtoResponse.from_response(
            local_response, models.SecurityTXTPolicyResource
        )

    def update_security_txt_policy(
        self,
        request: models.SecurityTXTPolicyUpdateRequest,
        *,
        id_: int,
    ) -> DtoResponse[models.SecurityTXTPolicyResource]:
        local_response = self.api_connector.send_or_fail(
            "PATCH",
            f"/api/v1/security-txt-policies/{id_}",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(
            local_response, models.SecurityTXTPolicyResource
        )

    def delete_security_txt_policy(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.DetailMessage]:
        local_response = self.api_connector.send_or_fail(
            "DELETE",
            f"/api/v1/security-txt-policies/{id_}",
            data=None,
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.DetailMessage)
