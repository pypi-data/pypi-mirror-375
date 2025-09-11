from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource
from cyberfusion.CoreApiClient.http import DtoResponse


class MailAliases(Resource):
    def create_mail_alias(
        self,
        request: models.MailAliasCreateRequest,
    ) -> DtoResponse[models.MailAliasResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/mail-aliases",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.MailAliasResource)

    def list_mail_aliases(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.MailAliasResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/mail-aliases",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(local_response, models.MailAliasResource)

    def read_mail_alias(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.MailAliasResource]:
        local_response = self.api_connector.send_or_fail(
            "GET", f"/api/v1/mail-aliases/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.MailAliasResource)

    def update_mail_alias(
        self,
        request: models.MailAliasUpdateRequest,
        *,
        id_: int,
    ) -> DtoResponse[models.MailAliasResource]:
        local_response = self.api_connector.send_or_fail(
            "PATCH",
            f"/api/v1/mail-aliases/{id_}",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.MailAliasResource)

    def delete_mail_alias(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.DetailMessage]:
        local_response = self.api_connector.send_or_fail(
            "DELETE", f"/api/v1/mail-aliases/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.DetailMessage)
