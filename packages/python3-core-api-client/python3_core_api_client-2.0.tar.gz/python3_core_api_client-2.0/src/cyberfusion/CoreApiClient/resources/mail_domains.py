from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource
from cyberfusion.CoreApiClient.http import DtoResponse


class MailDomains(Resource):
    def create_mail_domain(
        self,
        request: models.MailDomainCreateRequest,
    ) -> DtoResponse[models.MailDomainResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/mail-domains",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.MailDomainResource)

    def list_mail_domains(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.MailDomainResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/mail-domains",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(local_response, models.MailDomainResource)

    def read_mail_domain(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.MailDomainResource]:
        local_response = self.api_connector.send_or_fail(
            "GET", f"/api/v1/mail-domains/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.MailDomainResource)

    def update_mail_domain(
        self,
        request: models.MailDomainUpdateRequest,
        *,
        id_: int,
    ) -> DtoResponse[models.MailDomainResource]:
        local_response = self.api_connector.send_or_fail(
            "PATCH",
            f"/api/v1/mail-domains/{id_}",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.MailDomainResource)

    def delete_mail_domain(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.DetailMessage]:
        local_response = self.api_connector.send_or_fail(
            "DELETE", f"/api/v1/mail-domains/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.DetailMessage)
