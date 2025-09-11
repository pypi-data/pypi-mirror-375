from cyberfusion.CoreApiClient import models
from typing import Optional, List

from cyberfusion.CoreApiClient.interfaces import Resource
from cyberfusion.CoreApiClient.http import DtoResponse


class SSHKeys(Resource):
    def create_public_ssh_key(
        self,
        request: models.SSHKeyCreatePublicRequest,
    ) -> DtoResponse[models.SSHKeyResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/ssh-keys/public",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.SSHKeyResource)

    def create_private_ssh_key(
        self,
        request: models.SSHKeyCreatePrivateRequest,
    ) -> DtoResponse[models.SSHKeyResource]:
        local_response = self.api_connector.send_or_fail(
            "POST",
            "/api/v1/ssh-keys/private",
            data=request.dict(exclude_unset=True),
            query_parameters={},
        )

        return DtoResponse.from_response(local_response, models.SSHKeyResource)

    def list_ssh_keys(
        self,
        *,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        filter_: Optional[List[str]] = None,
        sort: Optional[List[str]] = None,
    ) -> DtoResponse[list[models.SSHKeyResource]]:
        local_response = self.api_connector.send_or_fail(
            "GET",
            "/api/v1/ssh-keys",
            data=None,
            query_parameters={
                "skip": skip,
                "limit": limit,
                "filter": filter_,
                "sort": sort,
            },
        )

        return DtoResponse.from_response(local_response, models.SSHKeyResource)

    def read_ssh_key(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.SSHKeyResource]:
        local_response = self.api_connector.send_or_fail(
            "GET", f"/api/v1/ssh-keys/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.SSHKeyResource)

    def delete_ssh_key(
        self,
        *,
        id_: int,
    ) -> DtoResponse[models.DetailMessage]:
        local_response = self.api_connector.send_or_fail(
            "DELETE", f"/api/v1/ssh-keys/{id_}", data=None, query_parameters={}
        )

        return DtoResponse.from_response(local_response, models.DetailMessage)
