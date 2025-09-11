from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.http import DtoResponse
from cyberfusion.CoreApiClient.interfaces import Resource


class CertificateManagers(Resource):
    def create_certificate_manager(
        self,
        request: models.CertificateManagerCreateRequest,
    ) -> DtoResponse[models.CertificateManagerResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/certificate-managers",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(
            local_response, models.CertificateManagerResource
        )

    def list_certificate_managers(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.CertificateManagerResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/certificate-managers",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(
            local_response, models.CertificateManagerResource
        )

    def read_certificate_manager(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.CertificateManagerResource]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            f"/api/v1/certificate-managers/{id_}",
            data=None,
            query_parameters={},
        )

        return DtoResponse.from_response(
            local_response, models.CertificateManagerResource
        )

    def update_certificate_manager(
        self,
        request: models.CertificateManagerUpdateRequest,
        *,
        id_: int,
    ) -> DtoResponse[models.CertificateManagerResource]:
        local_response = self.api_connector.send_or_fail(
            "PATCH",
            f"/api/v1/certificate-managers/{id_}",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(
            local_response, models.CertificateManagerResource
        )

    def delete_certificate_manager(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.DetailMessage]:
        local_response = self.api_connector.send_or_fail(
            "DELETE",
            f"/api/v1/certificate-managers/{id_}",
            data=None,
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.DetailMessage)

    def request_certificate(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.TaskCollectionResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            f"/api/v1/certificate-managers/{id_}/request",
            data=None,
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.TaskCollectionResource)
