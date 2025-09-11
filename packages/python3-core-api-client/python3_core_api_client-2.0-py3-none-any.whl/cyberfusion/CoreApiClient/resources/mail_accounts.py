from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource
from cyberfusion.CoreApiClient.http import DtoResponse


class MailAccounts(Resource):
    def create_mail_account(
        self,
        request: models.MailAccountCreateRequest,
    ) -> DtoResponse[models.MailAccountResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/mail-accounts",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.MailAccountResource)

    def list_mail_accounts(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.MailAccountResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/mail-accounts",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(local_response, models.MailAccountResource)

    def read_mail_account(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.MailAccountResource]:
        local_response = self.api_connector.send_or_fail(
            "GET", f"/api/v1/mail-accounts/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.MailAccountResource)

    def update_mail_account(
        self,
        request: models.MailAccountUpdateRequest,
        *,
        id_: int,
    ) -> DtoResponse[models.MailAccountResource]:
        local_response = self.api_connector.send_or_fail(
            "PATCH",
            f"/api/v1/mail-accounts/{id_}",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.MailAccountResource)

    def delete_mail_account(
        self,
        *,
        id_: int,
        delete_on_cluster: Optional[bool] = None,
    ) -> DtoResponse[models.DetailMessage]:
        local_response = self.api_connector.send_or_fail(
            "DELETE",
            f"/api/v1/mail-accounts/{id_}",
            data=None,
            query_parameters={
                "delete_on_cluster": delete_on_cluster,
            },
        )

        return DtoResponse.from_response(local_response, models.DetailMessage)

    def list_mail_account_usages(
        self,
        *,
        mail_account_id: int,
        timestamp: str,
        time_unit: Optional[models.MailAccountUsageResource] = None,
    ) -> DtoResponse[list[models.MailAccountUsageResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            f"/api/v1/mail-accounts/usages/{mail_account_id}",
            data=None,
            query_parameters={
                "timestamp": timestamp,
                "time_unit": time_unit,
            },
        )

        return DtoResponse.from_response(
            local_response, models.MailAccountUsageResource
        )
