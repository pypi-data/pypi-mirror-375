from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource
from cyberfusion.CoreApiClient.http import DtoResponse


class MailHostnames(Resource):
    def create_mail_hostname(
        self,
        request: models.MailHostnameCreateRequest,
    ) -> DtoResponse[models.MailHostnameResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/mail-hostnames",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.MailHostnameResource)

    def list_mail_hostnames(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.MailHostnameResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/mail-hostnames",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(local_response, models.MailHostnameResource)

    def read_mail_hostname(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.MailHostnameResource]:
        local_response = self.api_connector.send_or_fail(
            "GET", f"/api/v1/mail-hostnames/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.MailHostnameResource)

    def update_mail_hostname(
        self,
        request: models.MailHostnameUpdateRequest,
        *,
        id_: int,
    ) -> DtoResponse[models.MailHostnameResource]:
        local_response = self.api_connector.send_or_fail(
            "PATCH",
            f"/api/v1/mail-hostnames/{id_}",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.MailHostnameResource)

    def delete_mail_hostname(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.DetailMessage]:
        local_response = self.api_connector.send_or_fail(
            "DELETE",
            f"/api/v1/mail-hostnames/{id_}",
            data=None,
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.DetailMessage)
