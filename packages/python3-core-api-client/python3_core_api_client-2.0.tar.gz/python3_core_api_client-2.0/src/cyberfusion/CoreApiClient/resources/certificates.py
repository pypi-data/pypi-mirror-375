from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.http import DtoResponse
from cyberfusion.CoreApiClient.interfaces import Resource


class Certificates(Resource):
    def create_certificate(
        self,
        request: models.CertificateCreateRequest,
    ) -> DtoResponse[models.CertificateResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/certificates",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.CertificateResource)

    def list_certificates(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.CertificateResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/certificates",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(local_response, models.CertificateResource)

    def read_certificate(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.CertificateResource]:
        local_response = self.api_connector.send_or_fail(
            "GET", f"/api/v1/certificates/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.CertificateResource)

    def delete_certificate(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.DetailMessage]:
        local_response = self.api_connector.send_or_fail(
            "DELETE", f"/api/v1/certificates/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.DetailMessage)
